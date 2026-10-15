#!/usr/bin/env node
// Renders the BUILT deck (slides/dist) in a real browser and reports slides whose content leaves the
// slide area, so overflow is found by a machine and not by a trainer in front of the room.
//
//   pnpm --filter slides build && node scripts/check-slides-layout.mjs [--shots DIR] [--range 1-20]
//   Private preview (several people work at once): slides/preview-<name>.md holds a manifest of only your sections;
//   pnpm --filter slides exec slidev build preview-<name>.md --out dist-<name>
//   node scripts/check-slides-layout.mjs --entry preview-<name>.md --dist dist-<name> --range 1-30 --shots /tmp/shots
//
// Browser: set CHROME_PATH to a Chrome/Chromium binary, or install Playwright's with
//   pnpm --filter slides exec playwright-chromium install chromium
// Exit code 1 when any slide overflows. --shots writes one PNG per slide (final click state).
import { createRequire } from "node:module";
import http from "node:http";
import { existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const opt = (name) => (args.includes(name) ? args[args.indexOf(name) + 1] : undefined);
const DIST = join(ROOT, "slides", opt("--dist") ?? "dist");
const ENTRY = opt("--entry") ?? "slides.md";
const shots = opt("--shots");
const range = opt("--range");

const require = createRequire(join(ROOT, "slides/package.json"));
const { chromium } = require("playwright-chromium");

if (!existsSync(join(DIST, "index.html"))) {
  console.error(`${DIST} is missing: build the deck first`);
  process.exit(2);
}

const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".woff2": "font/woff2", ".json": "application/json", ".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp" };
const server = http
  .createServer((req, res) => {
    let p = join(DIST, decodeURIComponent(req.url.split("?")[0]));
    if (!p.startsWith(DIST) || !existsSync(p) || statSync(p).isDirectory()) p = join(DIST, "index.html");
    res.writeHead(200, { "content-type": TYPES[extname(p)] ?? "application/octet-stream" });
    res.end(readFileSync(p));
  })
  .listen(0);
const port = server.address().port;

const chromePath = process.env.CHROME_PATH || (existsSync("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome") ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" : undefined);
const browser = await chromium.launch(chromePath ? { executablePath: chromePath } : {});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const base = `http://localhost:${port}`;

await page.goto(`${base}/1`);
await page.waitForSelector(".slidev-page-1 .slidev-layout");
// Only the current slide and its neighbours are in the DOM, so the count comes from the parsed source.
const { load } = await import("@slidev/parser/fs");
const slidesDir = join(ROOT, "slides");
const total = (await load({ roots: [slidesDir], userRoot: slidesDir }, join(slidesDir, ENTRY))).slides.length;
const [from, to] = range ? range.split("-").map(Number) : [1, total];
if (shots) mkdirSync(shots, { recursive: true });

const RAIL = 52; // keep in sync with --ki-rail-h in slides/styles/tokens.css
const problems = [];
for (let n = from; n <= (to ?? from); n++) {
  await page.goto(`${base}/${n}?clicks=99`);
  await page.waitForSelector(`.slidev-page-${n} .slidev-layout`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(250);
  const found = await page.evaluate(([rail, no]) => {
    const layout = document.querySelector(`.slidev-page-${no} .slidev-layout`);
    const name = [...layout.classList].find((c) => c !== "slidev-layout") ?? "default";
    const hasRail = !["cover", "end", "section"].includes(name);
    const bottomLimit = 720 - (hasRail ? rail : 0) + 2;
    const out = [];
    const visible = (el) => {
      const s = getComputedStyle(el);
      return s.display !== "none" && s.visibility !== "hidden" && Number(s.opacity) > 0;
    };
    for (const el of layout.querySelectorAll("*")) {
      // .ki-slide spans the whole canvas by design (its padding keeps content clear of the rail)
      if (el.classList.contains("ki-slide") || !visible(el) || (el.closest("svg") && el.tagName !== "svg")) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      const label = `${el.tagName.toLowerCase()}${el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : ""} "${(el.textContent || "").trim().slice(0, 40)}"`;
      if (r.bottom > bottomLimit || r.right > 1280 + 1 || r.left < -1 || r.top < -1) out.push({ kind: "outside", label, bottom: Math.round(r.bottom), right: Math.round(r.right) });
      else if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflowX !== "visible") out.push({ kind: "clipped", label });
      // Content taller than its box while the box hides or scrolls the rest (a code block cut off at the bottom).
      else if (el.clientHeight > 0 && el.scrollHeight > el.clientHeight + 3 && ["hidden", "clip", "auto", "scroll"].includes(getComputedStyle(el).overflowY))
        out.push({ kind: "clipped vertically", label: `${label}  by ${el.scrollHeight - el.clientHeight}px` });
    }
    // A measured component that could not find its data says so in red (.err or .note.error): never ship that.
    for (const el of layout.querySelectorAll(".err, .note.error")) if (visible(el) && (el.textContent || "").trim()) out.push({ kind: "component error", label: (el.textContent || "").trim().slice(0, 80) });
    // The bottom rail is a global component outside the layout: its counter must not run off the canvas.
    if (hasRail)
      for (const el of document.querySelectorAll(".rail > *")) {
        const r = el.getBoundingClientRect();
        if (r.right > 1280 - 8 || r.left < 8) out.push({ kind: "rail clipped", label: `${el.className} "${(el.textContent || "").trim().slice(0, 30)}"`, right: Math.round(r.right) });
      }
    return { name, hasRail, out: out.slice(0, 6) };
  }, [RAIL, n]);
  if (found.out.length) problems.push({ slide: n, layout: found.name, items: found.out });
  if (shots) await page.screenshot({ path: join(shots, `${String(n).padStart(3, "0")}.png`) });
}
await browser.close();
server.close();

if (problems.length) {
  for (const p of problems) {
    console.log(`slide ${p.slide} (${p.layout})`);
    for (const i of p.items) console.log(`   ${i.kind}: ${i.label}${i.bottom ? `  bottom=${i.bottom}` : ""}${i.right ? ` right=${i.right}` : ""}`);
  }
  console.log(`\n${problems.length} of ${(to ?? from) - from + 1} slides have content outside the slide area`);
  process.exit(1);
}
console.log(`check-slides-layout: ok, ${(to ?? from) - from + 1} slides inspected`);
