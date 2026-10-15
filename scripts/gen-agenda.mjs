#!/usr/bin/env node
// Rewrites the module-table regions in README.md, FACILITATOR.md and docs/CURRICULUM.md from config/workshop.yaml.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";
import { applyRegions } from "./agenda-tables.mjs";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const workshop = YAML.parse(readFileSync(join(ROOT, "config/workshop.yaml"), "utf8"));

for (const file of ["README.md", "FACILITATOR.md", "docs/CURRICULUM.md"]) {
  const path = join(ROOT, file);
  if (!existsSync(path)) continue;
  const { text, found, changed } = applyRegions(readFileSync(path, "utf8"), workshop);
  if (changed) writeFileSync(path, text);
  console.log(`${file}: ${found} agenda region(s), ${changed ? "updated" : "already current"}`);
}
