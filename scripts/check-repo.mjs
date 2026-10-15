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
//   2. config/workshop.yaml: one ordered module path (no days, times or durations), every outcome covered
//   3. tasks/NN-*.md follow the task template and are listed in tasks/README.md
//   4. benchmark/results/**/*.json carry full provenance (hardware, model revision, versions, config, date)
//   5. slides: speaker notes, dividers match the module path, lab slides name their task, every metric component declares its source
//   6. teaching content contains no calendar dates, no day numbers and no clock times (content must stay reusable)
//   7. repo paths mentioned in inline code or links exist

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const RELEASE = process.argv.includes("--release");

const TASK_SECTIONS = [
  "Goal",
  "Context",
  "Scope",
  "Starting Point",
  "Instructions",
  "Expected Result",
  "Validation",
  "If You Get Stuck",
  "Further Exploration",
];
const NOTES_EXEMPT_LAYOUTS = new Set(["cover", "section", "end", "intro"]);
// Components that render numbers and therefore must say where the numbers come from.
const SOURCED_COMPONENTS = ["MetricCard", "ResultChart", "ResultTable", "Benchmark", "MemoryBar"];
const REQUIRED_AT_RELEASE = [
  "README.md",
  "FACILITATOR.md",
  "CONTRIBUTING.md",
  "LICENSE",
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

// vLLM profiles may only serve models that models.yaml pins, at exactly the pinned revision.
if (models) {
  const pinned = new Map();
  for (const m of Object.values(models.models ?? models)) if (m?.repo) pinned.set(m.repo, m.revision);
  for (const [file, doc] of yamlDocs) {
    if (!file.startsWith("config/vllm-profiles/") || !doc?.model) continue;
    if (!pinned.has(doc.model)) err(file, `model '${doc.model}' is not listed in config/models.yaml`);
    else if (doc.revision !== pinned.get(doc.model))
      err(file, `revision ${String(doc.revision).slice(0, 12)} differs from the pin in config/models.yaml (${String(pinned.get(doc.model)).slice(0, 12)})`);
  }
}

// ---------------------------------------------------------------- 2. module path
const workshop = yamlDocs.get("config/workshop.yaml");
const pathTasks = new Set(); // task ids named by the module path
const SCHEDULE_FIELDS = ["day", "days", "start", "minutes", "timebox", "timebox_minutes"];
if (workshop && (workshop.days || !workshop.modules)) err("config/workshop.yaml", "needs an ordered 'modules:' list (the workshop has no days)");
if (workshop?.modules) {
  const coveredOutcomes = new Set();
  const seenIds = new Set();
  for (const p of workshop.prework ?? []) {
    (p.outcomes ?? []).forEach((o) => coveredOutcomes.add(o));
    if (p.task) pathTasks.add(String(p.task));
    for (const k of SCHEDULE_FIELDS) if (k in p) err("config/workshop.yaml", `prework '${p.id}': '${k}' is a schedule field; the material has no times or durations`);
  }
  workshop.modules.forEach((m, i) => {
    const where = `module ${i + 1} '${m.id}'`;
    if (seenIds.has(m.id)) err("config/workshop.yaml", `${where}: duplicate module id`);
    seenIds.add(m.id);
    if (!String(m.id).startsWith(`${String(i + 1).padStart(2, "0")}-`)) err("config/workshop.yaml", `${where}: the id must start with its position '${String(i + 1).padStart(2, "0")}-'`);
    for (const k of SCHEDULE_FIELDS) if (k in m) err("config/workshop.yaml", `${where}: '${k}' is a schedule field; the material has no times or durations`);
    (m.outcomes ?? []).forEach((o) => coveredOutcomes.add(o));
    if (!existsSync(abs("slides/sections", `${m.id}.md`))) guard("config/workshop.yaml", `${where}: no slides/sections/${m.id}.md`);
    for (const e of m.experiments ?? []) if (!existsSync(abs("experiments", e))) guard("config/workshop.yaml", `${where}: no experiments/${e}/`);
    if (m.task) pathTasks.add(String(m.task));
  });
  // The 23 learning outcomes of the workshop (docs/CURRICULUM.md) must each be taught somewhere.
  for (let o = 1; o <= 23; o++)
    if (!coveredOutcomes.has(o)) err("config/workshop.yaml", `learning outcome ${o} is not covered by any module`);
}

// docs/CURRICULUM.md must name every module id, so the curriculum cannot drift from the path.
if (workshop?.modules && existsSync(abs("docs/CURRICULUM.md"))) {
  const curriculum = read(abs("docs/CURRICULUM.md"));
  for (const id of [...(workshop.prework ?? []).map((p) => p.id), ...workshop.modules.map((m) => m.id)])
    if (!curriculum.includes(id)) guard("docs/CURRICULUM.md", `does not mention module '${id}'`);
}

// README.md, FACILITATOR.md and docs/CURRICULUM.md carry module tables generated from workshop.yaml (scripts/gen-agenda.mjs).
if (workshop?.modules) {
  const { applyRegions } = await import("./agenda-tables.mjs");
  for (const file of ["README.md", "FACILITATOR.md", "docs/CURRICULUM.md"]) {
    if (!existsSync(abs(file))) continue;
    const { changed } = applyRegions(read(abs(file)), workshop);
    if (changed) guard(file, "module tables differ from config/workshop.yaml: run `node scripts/gen-agenda.mjs`");
  }
}

// ---------------------------------------------------------------- 3. tasks
const taskFiles = walk(abs("tasks"), (p) => /\/\d\d-[a-z0-9-]+\.md$/.test(p.split("\\").join("/")));
const taskIds = new Set();
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
  taskIds.add(id);
}
for (const id of pathTasks)
  if (!existsSync(abs("tasks", `${id}.md`))) guard("config/workshop.yaml", `task '${id}' has no tasks/${id}.md`);

const tasksReadme = abs("tasks/README.md");
if (existsSync(tasksReadme) && taskFiles.length) {
  const text = read(tasksReadme);
  for (const id of taskIds) if (!text.split("\n").some((l) => l.includes(`${id}.md`))) err("tasks/README.md", `no table row linking ${id}.md`);
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
    if (/<MetricCard\b[^>]*source="measured:/.test(s.content ?? "") && !/<Provenance\b/.test(s.content ?? ""))
      guard(where, "shows measured MetricCards without a <Provenance source=...> line saying where they were measured");
    if (layout === "lab") {
      const id = fm.task;
      if (!id || !taskIds.has(String(id))) err(where, `lab slide references unknown task '${id}'`);
      if ("timebox" in fm) err(where, "lab slides carry no timebox: the material has no durations");
    }
  }
}

// slides.md is a pure manifest of the module path: every module, in path order, and each section opens with a
// divider that carries the module's number, title, layer and objectives (the rail and the section layout read them).
if (workshop?.modules && existsSync(abs("slides/slides.md"))) {
  const manifest = [...read(abs("slides/slides.md")).matchAll(/^src:\s*\.\/sections\/([\w-]+)\.md\s*$/gm)].map((m) => m[1]);
  const modules = workshop.modules;
  if (manifest.join() !== modules.map((m) => m.id).join())
    guard("slides/slides.md", `section manifest differs from the module path in config/workshop.yaml (expected ${modules.length} sections in path order, found ${manifest.length})`);
  if (sectionFiles.length) {
    const { load } = await import("@slidev/parser/fs");
    const data = await load({ roots: [slidesDir], userRoot: slidesDir }, abs("slides/slides.md"));
    modules.forEach((m, i) => {
      const file = abs("slides/sections", `${m.id}.md`);
      const open = data.slides.filter((x) => x.source.filepath === file).sort((a, c) => a.source.index - c.source.index)[0];
      if (!open) return;
      const fm = open.frontmatter ?? {};
      const where = `slides/sections/${m.id}.md slide 1`;
      if (fm.layout !== "section") guard(where, `must open with layout: section (found '${fm.layout}')`);
      if (fm.layer !== m.layer) guard(where, `layer '${fm.layer}' differs from workshop.yaml ('${m.layer}')`);
      if (Number(fm.module) !== i + 1) guard(where, `module ${fm.module} differs from its position in workshop.yaml (${i + 1})`);
      if (fm.heading !== m.title) guard(where, `heading '${fm.heading}' differs from the title in workshop.yaml ('${m.title}')`);
      if (!Array.isArray(fm.can) || fm.can.length < 2 || fm.can.length > 3 || fm.can.some((c) => typeof c !== "string" || !c.trim()))
        guard(where, "needs 'can:' with two or three short statements (what participants can do after the module)");
      for (const k of ["day", "time", "minutes", "timebox"]) if (k in fm) guard(where, `'${k}' is a schedule field; the material has no days, times or durations`);
    });
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

// ---------------------------------------------------------------- 6. calendar dates and schedule words in teaching content
const dateRe = /\b20\d\d-[01]\d-[0-3]\d\b/;
// The material is a module path without days or clock times: these words would tie it to a schedule again.
const SCHEDULE_WORDS = [
  [/\bDay [1-3]\b/, "a day number"],
  [/\b(?:[01]\d|2[0-3]):[0-5]\d\b(?!:)/, "a clock time"],
  [/\b(?:this morning|this afternoon|tomorrow|yesterday|tonight|the day before|end of day)\b/i, "a day-relative phrase"],
];
const contentFiles = [
  ...taskFiles,
  ...sectionFiles,
  ...["FACILITATOR.md", "README.md", "docs/CURRICULUM.md"].filter((f) => existsSync(abs(f))).map((f) => abs(f)),
];
for (const f of contentFiles) {
  const text = read(f).replace(/```[\s\S]*?```/g, ""); // fenced code shows log lines and commands
  const hit = text.match(dateRe);
  if (hit) guard(rel(f), `contains a calendar date (${hit[0]}); teaching content must use relative times only`);
  for (const [re2, what] of SCHEDULE_WORDS) {
    const m = text.match(re2);
    if (m) guard(rel(f), `contains ${what} ('${m[0]}'); the material has no days or times`);
  }
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
