// Module tables generated from config/workshop.yaml, so README.md, FACILITATOR.md and docs/CURRICULUM.md cannot drift from it.
// `node scripts/gen-agenda.mjs` rewrites the marked regions; `pnpm check` fails when a region is out of date.
//
// A region looks like:   <!-- agenda:readme:begin --> ... <!-- agenda:readme:end -->
//                        regions: readme, runsheet (FACILITATOR.md), curriculum (docs/CURRICULUM.md)

const KIND = { lecture: "lecture", demo: "trainer demo", lab: "lab", mixed: "lecture and exercise", discussion: "discussion" };
const LAYER = { runtime: "Runtime", infrastructure: "Infrastructure", application: "Application", all: "All layers" };
const num = (i) => String(i + 1).padStart(2, "0");

export function readmeAgenda(workshop) {
  const out = ["| # | Module | Layer | Kind |", "| --- | --- | --- | --- |"];
  workshop.modules.forEach((m, i) => {
    const name = m.kind === "lab" ? `**${m.title}**` : m.title;
    out.push(`| ${num(i)} | ${name} | ${LAYER[m.layer]} | ${KIND[m.kind]} |`);
  });
  out.push("", "The modules run in this order and fill about three days. There are no fixed times: pace them as the group needs.");
  return out.join("\n");
}

export function runSheet(workshop) {
  const out = ["| # | Module | Kind | Slides | Task and experiments | Skippable |", "| --- | --- | --- | --- | --- | --- |"];
  workshop.modules.forEach((m, i) => {
    const work = [m.task ? `Task \`${m.task}\`` : "", ...(m.experiments ?? []).map((e) => `\`experiments/${e}\``)].filter(Boolean).join("<br>");
    out.push(`| ${num(i)} | **${m.title}** | ${KIND[m.kind]} | \`slides/sections/${m.id}.md\` | ${work} | ${m.skippable ? "yes" : ""} |`);
  });
  return out.join("\n");
}

export function curriculumTable(workshop) {
  const out = ["| Module id | Title | Layer | Kind | Task |", "| --- | --- | --- | --- | --- |"];
  for (const p of workshop.prework ?? []) out.push(`| \`${p.id}\` | Preflight on the participant laptop (before the first module) | all | homework | ${String(p.task).slice(0, 2)} |`);
  for (const m of workshop.modules) {
    const kind = m.skippable ? `${KIND[m.kind]} (skippable)` : KIND[m.kind];
    out.push(`| \`${m.id}\` | ${m.title} | ${m.layer} | ${kind} | ${m.task ? m.task.slice(0, 2) : ""} |`);
  }
  return out.join("\n");
}

export const REGIONS = {
  readme: (w) => readmeAgenda(w),
  runsheet: (w) => runSheet(w),
  curriculum: (w) => curriculumTable(w),
};

const re = (name) => new RegExp(`(<!-- agenda:${name}:begin -->\\n)([\\s\\S]*?)(\\n<!-- agenda:${name}:end -->)`);

/** Returns { text, found, changed } with every known region regenerated. */
export function applyRegions(text, workshop) {
  let changed = false;
  let found = 0;
  for (const [name, make] of Object.entries(REGIONS)) {
    const m = text.match(re(name));
    if (!m) continue;
    found++;
    const body = make(workshop);
    if (m[2] !== body) {
      changed = true;
      text = text.replace(re(name), (_, a, __, c) => `${a}${body}${c}`);
    }
  }
  return { text, found, changed };
}
