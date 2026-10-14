<script setup lang="ts">
// Line or bar chart of one metric against another, from result files (or typed points marked illustrative).
//   measured:     source="measured:benchmark/results/<dir>" x="concurrency" y="aggregate_tps"
//                 optional: match="baseline-c" or :match='["baseline-c", "max-seqs"]', kind="line"|"bar", xlabel, ylabel,
//                 title, :digits, and by="configuration.server_profile" to draw one series per profile (with a legend)
//   illustrative: source="illustrative" :points='[{"x":1,"y":10}]'  (no series)
import { computed } from 'vue'
import { fmt, LABELS, measuredDocs, parseSource, pick, provenance } from '../composables/results'
import SourceBadge from './SourceBadge.vue'

interface Point {
  x: number | string
  y: number
}
interface Series {
  label: string
  pts: Point[]
}

const props = withDefaults(
  defineProps<{
    source: string
    x?: string
    y?: string
    points?: Point[]
    match?: string | string[]
    by?: string
    kind?: 'line' | 'bar'
    xlabel?: string
    ylabel?: string
    title?: string
    digits?: number | string
  }>(),
  { kind: 'line', digits: 0 },
)

const W = 760
const H = 360
const M = { l: 84, r: 24, t: 24, b: 64 }
const COLORS = ['var(--ki-runtime)', 'var(--ki-application)', 'var(--ki-infrastructure)', 'var(--ki-info)']

const data = computed(() => {
  const src = parseSource(props.source)
  if (src.kind === 'illustrative')
    return { illustrative: true, series: [{ label: '', pts: props.points ?? [] }] as Series[], text: '' }
  const docs = measuredDocs(src.path, props.match)
  const groups = new Map<string, Point[]>()
  for (const { doc } of docs) {
    const px = pick(doc, props.x ?? 'concurrency')
    const py = pick(doc, props.y ?? 'aggregate_tps')
    if (px === undefined || typeof py !== 'number') continue
    const key = props.by ? String(pick(doc, props.by) ?? '') : ''
    groups.set(key, [...(groups.get(key) ?? []), { x: px, y: py }])
  }
  const series = [...groups].map(([label, pts]) => ({ label, pts }))
  return { illustrative: false, series, text: docs.length ? provenance(docs[0].doc) : '' }
})

const categories = computed(() => {
  const seen: (number | string)[] = []
  for (const s of data.value.series) for (const p of s.pts) if (!seen.includes(p.x)) seen.push(p.x)
  return seen
})
const numericX = computed(() => categories.value.every((c) => typeof c === 'number'))
const ymax = computed(() => {
  const m = Math.max(0, ...data.value.series.flatMap((s) => s.pts.map((p) => p.y)))
  const pow = 10 ** Math.floor(Math.log10(m || 1))
  return Math.ceil(m / pow / 0.5) * 0.5 * pow || 1
})
const pw = W - M.l - M.r
const ph = H - M.t - M.b
const multi = computed(() => data.value.series.length > 1)

function px(x: number | string) {
  const cats = categories.value
  if (props.kind === 'bar' || !numericX.value) return M.l + ((cats.indexOf(x) + 0.5) / cats.length) * pw
  const xs = cats as number[]
  const lo = Math.min(...xs)
  const hi = Math.max(...xs)
  // log-ish spacing keeps 1, 4, 8, 16, 32 readable
  const f = (v: number) => Math.log2(v + 1)
  return M.l + 24 + ((f(x as number) - f(lo)) / (f(hi) - f(lo) || 1)) * (pw - 48)
}
const py = (v: number) => M.t + ph - (v / ymax.value) * ph
const ticks = computed(() => [0, 0.25, 0.5, 0.75, 1].map((t) => t * ymax.value))
const clusterW = computed(() => Math.min(96, (pw / Math.max(categories.value.length, 1)) * 0.7))
const barW = computed(() => clusterW.value / data.value.series.length)
const barX = (s: number, x: number | string) => px(x) - clusterW.value / 2 + s * barW.value
const path = (s: Series) =>
  [...s.pts]
    .sort((a, b) => (typeof a.x === 'number' && typeof b.x === 'number' ? a.x - b.x : 0))
    .map((p, i) => `${i ? 'L' : 'M'}${px(p.x)},${py(p.y)}`)
    .join(' ')
const color = (i: number) => COLORS[i % COLORS.length]
</script>

<template>
  <figure class="chart">
    <figcaption v-if="title">{{ title }}</figcaption>
    <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="title ?? 'chart'">
      <g v-for="t in ticks" :key="t">
        <line :x1="M.l" :x2="W - M.r" :y1="py(t)" :y2="py(t)" class="grid" />
        <text :x="M.l - 12" :y="py(t) + 5" text-anchor="end" class="tick">{{ fmt(t, t < 10 && t > 0 ? 1 : 0) }}</text>
      </g>
      <template v-for="(s, si) in data.series" :key="s.label || si">
        <template v-if="kind === 'bar'">
          <rect
            v-for="p in s.pts"
            :key="String(p.x)"
            :x="barX(si, p.x)"
            :y="py(p.y)"
            :width="barW - 2"
            :height="py(0) - py(p.y)"
            rx="4"
            class="bar"
            :style="{ fill: multi ? color(si) : undefined }"
          />
          <text v-for="p in s.pts" :key="`v${String(p.x)}`" :x="barX(si, p.x) + barW / 2" :y="py(p.y) - 8" text-anchor="middle" class="value">{{ fmt(p.y, digits) }}</text>
        </template>
        <template v-else>
          <path :d="path(s)" class="path" :style="{ stroke: color(si) }" />
          <g v-for="p in s.pts" :key="String(p.x)">
            <circle :cx="px(p.x)" :cy="py(p.y)" r="6" class="dot" :style="{ stroke: color(si) }" />
            <text v-if="!multi" :x="px(p.x)" :y="py(p.y) - 14" text-anchor="middle" class="value">{{ fmt(p.y, digits) }}</text>
          </g>
        </template>
      </template>
      <text v-for="c in categories" :key="`c${c}`" :x="px(c)" :y="H - M.b + 28" text-anchor="middle" class="tick">{{ c }}</text>
      <text :x="M.l + pw / 2" :y="H - 8" text-anchor="middle" class="axis">{{ xlabel ?? LABELS[x ?? ''] ?? x }}</text>
      <text :x="18" :y="M.t + ph / 2" text-anchor="middle" class="axis" :transform="`rotate(-90 18 ${M.t + ph / 2})`">{{ ylabel ?? LABELS[y ?? ''] ?? y }}</text>
    </svg>
    <ul v-if="multi" class="legend">
      <li v-for="(s, si) in data.series" :key="s.label"><i :style="{ background: color(si) }" />{{ s.label }}</li>
    </ul>
    <div v-if="!data.series.some((s) => s.pts.length)" class="err">no data points: check the source path, x and y</div>
    <SourceBadge :illustrative="data.illustrative" :text="data.text" />
  </figure>
</template>

<style scoped>
.chart {
  margin: 0;
}
figcaption {
  font-size: var(--ki-text-sm);
  font-weight: 650;
  margin-bottom: 6px;
}
svg {
  width: 100%;
  height: auto;
  display: block;
}
.grid {
  stroke: var(--ki-border);
  stroke-width: 1;
}
.tick,
.axis {
  fill: var(--ki-fg-muted);
  font-family: var(--ki-font-sans);
  font-size: 15px;
}
.axis {
  font-size: 16px;
  font-weight: 600;
}
.value {
  fill: var(--ki-fg);
  font-family: var(--ki-font-sans);
  font-size: 16px;
  font-weight: 650;
  font-variant-numeric: tabular-nums;
}
.path {
  fill: none;
  stroke: var(--ki-layer, var(--ki-runtime));
  stroke-width: 3;
}
.dot {
  fill: var(--ki-bg);
  stroke: var(--ki-layer, var(--ki-runtime));
  stroke-width: 3;
}
.bar {
  fill: var(--ki-layer, var(--ki-runtime));
  opacity: 0.85;
}
.legend {
  display: flex;
  gap: 8px 24px;
  flex-wrap: wrap;
  padding: 0;
  margin: 4px 0 6px;
  list-style: none;
  font-size: var(--ki-text-sm);
}
.legend li {
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.legend li::before {
  display: none;
}
.legend i {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  display: inline-block;
}
.err {
  color: var(--ki-bad);
  font-size: var(--ki-text-sm);
}
</style>
