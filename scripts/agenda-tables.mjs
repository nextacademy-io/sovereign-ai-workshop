// Agenda tables generated from config/workshop.yaml, so README.md and FACILITATOR.md cannot drift from it.
// `node scripts/gen-agenda.mjs` rewrites the marked regions; `pnpm check` fails when a region is out of date.
//
// A region looks like:   <!-- agenda:readme:begin --> ... <!-- agenda:readme:end -->
//                        <!-- agenda:runsheet-1:begin --> ... (runsheet-1, -2, -3: one per day)

const KIND = { lecture: "lecture", demo: "trainer demo", lab: "lab", mixed: "lecture and exercise", discussion: "discussion", break: "break" };
const LAYER = { runtime: "Runtime", infrastructure: "Infrastructure", application: "Application", all: "All layers" };

function endTime(start, minutes) {
  const [h, m] = start.split(":").map(Number);
  const t = h * 60 + m + minutes;
  return `${String(Math.floor(t / 60)).padStart(2, "0")}:${String(t % 60).padStart(2, "0")}`;
}

export function readmeAgenda(workshop) {
  const out = [];
  for (const day of workshop.days) {
    out.push(`### Day ${day.day}: ${day.title}`, "", `*${day.question}*`, "", "| Time | Min | Block | Layer |", "| --- | --- | --- | --- |");
    for (const b of day.blocks) {
      const name = b.kind === "break" ? `*${b.title}*` : b.kind === "lab" ? `**${b.title}**` : b.title;
      out.push(`| ${b.start} | ${b.minutes} | ${name} | ${b.kind === "break" ? "" : LAYER[b.layer]} |`);
    }
    out.push("");
  }
  out.push("Times are relative to the start of each day (09:00 in the trainer's time zone). Breaks are included; teaching time is about seven hours per day.");
  return out.join("\n");
}

export function runSheet(workshop, dayNo) {
  const day = workshop.days.find((d) => d.day === dayNo);
  const out = ["| Time | Min | Block | Kind | Slides | Task and experiments | Skippable |", "| --- | --- | --- | --- | --- | --- | --- |"];
  for (const b of day.blocks) {
    const slides = b.kind === "break" ? "" : `\`slides/sections/${b.id}.md\``;
    const work = [b.task ? `Task \`${b.task}\` (${b.timebox_minutes} min)` : "", ...(b.experiments ?? []).map((e) => `\`experiments/${e}\``)].filter(Boolean).join("<br>");
    out.push(`| ${b.start}-${endTime(b.start, b.minutes)} | ${b.minutes} | ${b.kind === "break" ? `*${b.title}*` : `**${b.title}**`} | ${KIND[b.kind]} | ${slides} | ${work} | ${b.skippable ? "yes" : ""} |`);
  }
  return out.join("\n");
}

export const REGIONS = {
  readme: (w) => readmeAgenda(w),
  "runsheet-1": (w) => runSheet(w, 1),
  "runsheet-2": (w) => runSheet(w, 2),
  "runsheet-3": (w) => runSheet(w, 3),
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
