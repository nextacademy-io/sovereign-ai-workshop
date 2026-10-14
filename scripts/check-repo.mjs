#!/usr/bin/env node
// Repository consistency checks for the KI ohne Cloud workshop.
//
//   node scripts/check-repo.mjs            development mode: path references only warn
//   node scripts/check-repo.mjs --release  CI / release mode: warnings that guard the
//                                          workshop promises become errors, and every
//                                          required file must exist
//
// What is checked (each check skips cleanly while its inputs do not exist yet):
//   1. every YAML file parses; config/models.yaml pins full commit SHAs
//   2. config/workshop.yaml: blocks do not overlap, daily teaching time fits ~7 h
//   3. tasks/NN-*.md follow the task template; timeboxes agree with workshop.yaml and tasks/README.md
//   4. benchmark/results/**/*.json carry full provenance (hardware, model revision, versions, config, date)
//   5. slides: speaker notes, lab slides match their task, every metric component declares its source
//   6. teaching content contains no calendar dates (content must stay reusable)
//   7. repo paths mentioned in inline code or links exist

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const RELEASE = process.argv.includes("--release");

const TEACHING_MINUTES = { min: 380, max: 450 };
const TASK_SECTIONS = [
  "Goal",
  "Context",
  "Timebox",
  "Starting Point",
  "Instructions",
  "Expected Result",
  "Validation",
  "If You Get Stuck",
  "Further Exploration",
];
const NOTES_EXEMPT_LAYOUTS = new Set(["cover", "section", "end", "intro"]);
// Components that render numbers and therefore must say where the numbers come from.
const SOURCED_COMPONENTS = ["MetricCard", "ResultChart", "ResultTable", "Benchmark"];
const REQUIRED_AT_RELEASE = [
  "README.md",
  "FACILITATOR.md",
  "CONTRIBUTING.md",
  "LICENSE",
  "LICENSE-CODE",
  ".env.example",
  "config/models.yaml",
  "config/workshop.yaml",
  "infra/README.md",
  "infra/provision.md",
  "infra/machine-setup.sh",
  "infra/verify-machine.sh",
  "infra/reset-machine.sh",
  "infra/cleanup.sh",
  "infra/add-participant-key.sh",
  "infra/revoke-participant-key.sh",
  "infra/participants.example.yaml",
  "scripts/preflight.sh",
  "scripts/start-vllm.sh",
  "scripts/stop-vllm.sh",
  "scripts/benchmark.sh",
  "scripts/gpu-status.sh",
  "scripts/reset.sh",
  "benchmark/README.md",
  "benchmark/run.sh",
  "monitoring/docker-compose.yml",
  "monitoring/README.md",
  "tasks/README.md",
  "tasks/00-preflight.md",
  "tasks/01-model-selection.md",
  "tasks/02-first-inference-server.md",
  "tasks/03-benchmark.md",
  "tasks/04-optimization.md",
  "tasks/05-production-design.md",
  "docs/RESEARCH.md",
  "docs/CURRICULUM.md",
  "docs/SETUP.md",
  "docs/GPU-POOL.md",
  "docs/TROUBLESHOOTING.md",
  "docs/MODEL-SELECTION.md",
  "docs/METRICS.md",
  "docs/SECURITY.md",
  "docs/DIGITAL-SOVEREIGNTY.md",
  "docs/REFERENCES.md",
  "docs/GLOSSARY.md",
  "docs/VALIDATION.md",
  "slides/slides.md",
];

const errors = [];
const warnings = [];
const err = (file, msg) => errors.push(`${file}: ${msg}`);
// Path-reference drift is only an error in release mode.
const guard = (file, msg) => (RELEASE ? err(file, msg) : warnings.push(`${file}: ${msg}`));

const rel = (p) => relative(ROOT, p).split("\\").join("/");
const abs = (...p) => join(ROOT, ...p);
const read = (p) => readFileSync(p, "utf8");

const IGNORED_DIRS = new Set(["node_modules", ".git", "dist", ".slidev", ".venv", "__pycache__"]);

function walk(dir, accept) {
  const out = [];
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    if (IGNORED_DIRS.has(name) || name === "_scratch") continue;
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) out.push(...walk(p, accept));
    else if (accept(p)) out.push(p);
  }
  return out;
}

const parseYamlFile = (p) => {
  try {
    return YAML.parse(read(p));
  } catch (e) {
    err(rel(p), `invalid YAML: ${e.message.split("\n")[0]}`);
    return undefined;
  }
};

// ---------------------------------------------------------------- 0. required files
if (RELEASE) {
  for (const f of REQUIRED_AT_RELEASE) if (!existsSync(abs(f))) err(f, "required file is missing");
}

// ---------------------------------------------------------------- 1. YAML
const yamlFiles = walk(ROOT, (p) => /\.ya?ml$/.test(p) && !p.includes("pnpm-lock"));
const yamlDocs = new Map();
for (const f of yamlFiles) yamlDocs.set(rel(f), parseYamlFile(f));

const models = yamlDocs.get("config/models.yaml");
if (models) {
  const roles = models.models ?? models;
  for (const [role, m] of Object.entries(roles ?? {})) {
    if (!m || typeof m !== "object" || !m.repo) continue;
    if (!/^[0-9a-f]{40}$/.test(String(m.revision ?? "")))
      guard("config/models.yaml", `'${role}.revision' must be a full 40-char commit SHA (got '${m.revision}')`);
    if (!m.license) err("config/models.yaml", `'${role}.license' is missing`);
  }
}

// ---------------------------------------------------------------- 2. agenda
const workshop = yamlDocs.get("config/workshop.yaml");
const taskTimeboxFromAgenda = new Map(); // task id -> minutes
if (workshop?.days) {
  const toMin = (hhmm) => {
    const [h, m] = String(hhmm).split(":").map(Number);
    return h * 60 + m;
  };
  const coveredOutcomes = new Set();
  const seenIds = new Set();
  for (const p of workshop.prework ?? []) {
    (p.outcomes ?? []).forEach((o) => coveredOutcomes.add(o));
    if (p.task) taskTimeboxFromAgenda.set(String(p.task), p.timebox_minutes);
  }
  for (const day of workshop.days) {
    let teaching = 0;
    let prevEnd = -1;
    for (const b of day.blocks ?? []) {
      const where = `day ${day.day} block '${b.id}'`;
      if (seenIds.has(b.id)) err("config/workshop.yaml", `${where}: duplicate block id`);
      seenIds.add(b.id);
      (b.outcomes ?? []).forEach((o) => coveredOutcomes.add(o));
      if (b.kind !== "break") {
        if (!existsSync(abs("slides/sections", `${b.id}.md`))) guard("config/workshop.yaml", `${where}: no slides/sections/${b.id}.md`);
        for (const e of b.experiments ?? [])
          if (!existsSync(abs("experiments", e))) guard("config/workshop.yaml", `${where}: no experiments/${e}/`);
      }
      if (!/^\d{2}:\d{2}$/.test(String(b.start))) err("config/workshop.yaml", `${where}: bad start '${b.start}'`);
      if (!(b.minutes > 0)) err("config/workshop.yaml", `${where}: minutes must be > 0`);
      const start = toMin(b.start);
      if (start < prevEnd) err("config/workshop.yaml", `${where}: overlaps the previous block`);
      prevEnd = start + b.minutes;
      if (b.kind !== "break") teaching += b.minutes;
      if (b.task) {
        if (!(b.timebox_minutes > 0)) err("config/workshop.yaml", `${where}: task needs timebox_minutes`);
        if (b.timebox_minutes > b.minutes)
          err("config/workshop.yaml", `${where}: timebox_minutes (${b.timebox_minutes}) exceeds block length (${b.minutes})`);
        taskTimeboxFromAgenda.set(String(b.task), b.timebox_minutes);
      }
    }
    if (teaching < TEACHING_MINUTES.min || teaching > TEACHING_MINUTES.max)
      err("config/workshop.yaml", `day ${day.day}: ${teaching} teaching minutes, expected ${TEACHING_MINUTES.min}-${TEACHING_MINUTES.max}`);
  }
  // The 23 learning outcomes of the workshop (docs/CURRICULUM.md) must each be taught somewhere.
  for (let o = 1; o <= 23; o++)
    if (!coveredOutcomes.has(o)) err("config/workshop.yaml", `learning outcome ${o} is not covered by any block`);
}

// ---------------------------------------------------------------- 3. tasks
const taskFiles = walk(abs("tasks"), (p) => /\/\d\d-[a-z0-9-]+\.md$/.test(p.split("\\").join("/")));
const taskIds = new Map(); // id -> timebox minutes read from the task file
for (const f of taskFiles) {
  const name = rel(f);
  const id = name.replace(/^tasks\//, "").replace(/\.md$/, "");
  const text = read(f);
  if (!/^# Task \d\d — .+/m.test(text)) err(name, "first heading must look like '# Task NN — Title'");
  const h2 = [...text.matchAll(/^## (.+?)\s*$/gm)].map((m) => m[1]);
  const positions = TASK_SECTIONS.map((s) => h2.indexOf(s));
  TASK_SECTIONS.forEach((s, i) => {
    if (positions[i] === -1) err(name, `missing section '## ${s}'`);
  });
  if (positions.every((p) => p >= 0) && positions.some((p, i) => i > 0 && p < positions[i - 1]))
    err(name, `sections must appear in this order: ${TASK_SECTIONS.join(" > ")}`);

  const tb = text.match(/^## Timebox\s*\n+([\s\S]*?)(?=\n## )/m);
  const minutes = tb ? Number(tb[1].match(/(\d+)\s*minutes?/i)?.[1]) : NaN;
  if (!(minutes > 0)) err(name, "'## Timebox' must state a duration like '35 minutes'");
  else taskIds.set(id, minutes);

  if (taskTimeboxFromAgenda.has(id) && taskTimeboxFromAgenda.get(id) !== minutes)
    err(name, `timebox ${minutes} min differs from config/workshop.yaml (${taskTimeboxFromAgenda.get(id)} min)`);
}
for (const id of taskTimeboxFromAgenda.keys())
  if (!existsSync(abs("tasks", `${id}.md`))) guard("config/workshop.yaml", `task '${id}' has no tasks/${id}.md`);

const tasksReadme = abs("tasks/README.md");
if (existsSync(tasksReadme) && taskFiles.length) {
  const text = read(tasksReadme);
  for (const [id, minutes] of taskIds) {
    const row = text.split("\n").find((l) => l.includes(`${id}.md`));
    if (!row) err("tasks/README.md", `no table row linking ${id}.md`);
    else {
      const m = Number(row.match(/(\d+)\s*min/i)?.[1]);
      if (m !== minutes) err("tasks/README.md", `row for ${id} says ${m || "?"} min, task says ${minutes} min`);
    }
  }
}

// ---------------------------------------------------------------- 4. benchmark results
const resultFiles = walk(abs("benchmark/results"), (p) => p.endsWith(".json"));
const REQUIRED_CONFIG = ["hardware", "model", "model_revision", "engine", "engine_version", "cuda_version", "server_args", "workload", "date"];
const validResults = new Set();
for (const f of resultFiles) {
  const name = rel(f);
  let doc;
  try {
    doc = JSON.parse(read(f));
  } catch (e) {
    err(name, `invalid JSON: ${e.message}`);
    continue;
  }
  const cfg = doc.configuration;
  if (!cfg || typeof cfg !== "object") {
    err(name, "missing top-level 'configuration' object");
    continue;
  }
  const missing = REQUIRED_CONFIG.filter((k) => cfg[k] === undefined || cfg[k] === null || cfg[k] === "");
  if (!cfg.hardware?.gpu && !missing.includes("hardware")) missing.push("hardware.gpu");
  if (missing.length) err(name, `configuration is missing: ${missing.join(", ")}`);
  else validResults.add(name);
}

// ---------------------------------------------------------------- 5. slides
const slidesDir = abs("slides");
const sectionFiles = walk(abs("slides/sections"), (p) => p.endsWith(".md"));
if (sectionFiles.length) {
  const { load } = await import("@slidev/parser/fs");
  const data = await load({ roots: [slidesDir], userRoot: slidesDir }, abs("slides/slides.md"));
  for (const s of data.slides) {
    const where = `${rel(s.source.filepath)} slide ${s.source.index + 1}`;
    const fm = s.frontmatter ?? {};
    const layout = fm.layout;
    if (!NOTES_EXEMPT_LAYOUTS.has(layout) && !fm.noNotes) {
      const note = (s.note ?? "").trim();
      const words = note.split(/\s+/).filter(Boolean).length;
      if (words < 25) guard(where, `speaker notes missing or too short (${words} words; need >= 25)`);
      else {
        for (const label of ["Key", "Transition"])
          if (!new RegExp(`\\*\\*${label}[:.]`, "i").test(note)) guard(where, `speaker notes lack a '**${label}:**' part`);
      }
    }
    if (layout === "lab") {
      const id = fm.task;
      if (!id || !taskIds.has(String(id))) err(where, `lab slide references unknown task '${id}'`);
      else if (Number(fm.timebox) !== taskIds.get(String(id)))
        err(where, `lab slide timebox ${fm.timebox} differs from task '${id}' (${taskIds.get(String(id))} min)`);
    }
  }
}

const slideSources = walk(slidesDir, (p) => /\.(md|vue)$/.test(p));
const tagRe = new RegExp(`<(${SOURCED_COMPONENTS.join("|")})\\b([^>]*)>`, "g");
for (const f of slideSources) {
  const text = read(f);
  for (const m of text.matchAll(tagRe)) {
    const where = `${rel(f)} <${m[1]}>`;
    const source = m[2].match(/\bsource="([^"]*)"/)?.[1];
    if (!source) {
      err(where, `needs source="measured:benchmark/results/<file>.json" or source="illustrative"`);
    } else if (source.startsWith("measured:")) {
      const p = source.slice("measured:".length);
      if (!p.startsWith("benchmark/results/")) err(where, `measured source must live under benchmark/results/ (got '${p}')`);
      else if (!existsSync(abs(p))) err(where, `measured source '${p}' does not exist`);
      else if (!validResults.has(p) && p.endsWith(".json")) err(where, `measured source '${p}' lacks provenance metadata`);
    } else if (source !== "illustrative") {
      err(where, `unknown source '${source}'`);
    }
  }
}

// ---------------------------------------------------------------- 6. calendar dates in teaching content
const dateRe = /\b20\d\d-[01]\d-[0-3]\d\b/;
const contentFiles = [
  ...taskFiles,
  ...sectionFiles,
  ...(existsSync(abs("FACILITATOR.md")) ? [abs("FACILITATOR.md")] : []),
];
for (const f of contentFiles) {
  const hit = read(f).match(dateRe);
  if (hit) guard(rel(f), `contains a calendar date (${hit[0]}); teaching content must use relative times only`);
}

// ---------------------------------------------------------------- 7. referenced repo paths
const TOP = "(?:scripts|infra|benchmark|experiments|apps|monitoring|config|docs|tasks|workshop-states|workshop-artifacts|deploy|slides)";
const pathRe = new RegExp(`^(?:\\./)?${TOP}/[A-Za-z0-9_./-]+$`);
const placeholderRe = /(NN|YYYY|<|>|\*|\{|\}|\$|\.\.\.)/;
const mdFiles = walk(ROOT, (p) => p.endsWith(".md") && !p.endsWith("/LICENSE"));
for (const f of mdFiles) {
  const text = read(f).replace(/```[\s\S]*?```/g, ""); // fenced code shows commands, not links
  const candidates = new Set();
  for (const m of text.matchAll(/`([^`\n]+)`/g)) candidates.add(m[1].trim());
  for (const m of text.matchAll(/\]\(([^)#\s]+)(?:#[^)]*)?\)/g)) {
    if (!/^[a-z]+:/.test(m[1]) && !m[1].startsWith("/")) candidates.add({ link: m[1] });
  }
  for (const c of candidates) {
    if (typeof c === "string") {
      if (!pathRe.test(c) || placeholderRe.test(c)) continue;
      if (!existsSync(abs(c.replace(/^\.\//, "")))) guard(rel(f), `references '${c}' which does not exist`);
    } else if (!existsSync(resolve(dirname(f), c.link))) {
      guard(rel(f), `links to '${c.link}' which does not exist`);
    }
  }
}

// ---------------------------------------------------------------- report
for (const w of warnings) console.warn(`warn  ${w}`);
for (const e of errors) console.error(`error ${e}`);
const summary = `${errors.length} error(s), ${warnings.length} warning(s)${RELEASE ? " [release mode]" : ""}`;
if (errors.length) {
  console.error(`\ncheck-repo: FAILED — ${summary}`);
  process.exit(1);
}
console.log(`check-repo: ok — ${yamlFiles.length} YAML, ${taskFiles.length} task(s), ${resultFiles.length} result file(s), ${sectionFiles.length} slide section(s); ${summary}`);
