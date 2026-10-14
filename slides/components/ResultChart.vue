<script setup lang="ts">
// Line or bar chart of one metric against another, from result files (or typed points marked illustrative).
//   measured:     source="measured:benchmark/results/<dir>" x="concurrency" y="aggregate_tps"
//                 optional: match, kind="line"|"bar", xlabel, ylabel, title, :digits
//   illustrative: source="illustrative" :points='[{"x":1,"y":10,"label":"c=1"}]'
import { computed } from 'vue'
import { fmt, LABELS, measuredDocs, parseSource, pick, provenance } from '../composables/results'
import SourceBadge from './SourceBadge.vue'

interface Point {
  x: number | string
  y: number
}

const props = withDefaults(
  defineProps<{
    source: string
    x?: string
    y?: string
    points?: Point[]
    match?: string
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

const data = computed(() => {
  const src = parseSource(props.source)
  if (src.kind === 'illustrative') return { illustrative: true, pts: props.points ?? [], text: '' }
  const docs = measuredDocs(src.path, props.match)
  const pts: Point[] = []
  for (const { doc } of docs) {
    const px = pick(doc, props.x ?? 'concurrency')
    const py = pick(doc, props.y ?? 'aggregate_tps')
    if (px !== undefined && typeof py === 'number') pts.push({ x: px, y: py })
  }
  return { illustrative: false, pts, text: docs.length ? provenance(docs[0].doc) : '' }
})

const numericX = computed(() => data.value.pts.every((p) => typeof p.x === 'number'))
const ymax = computed(() => {
  const m = Math.max(0, ...data.value.pts.map((p) => p.y))
  const pow = 10 ** Math.floor(Math.log10(m || 1))
  return Math.ceil(m / pow / 0.5) * 0.5 * pow || 1
})
const pw = W - M.l - M.r
const ph = H - M.t - M.b
function px(p: Point, i: number) {
  const n = data.value.pts.length
  if (props.kind === 'bar' || !numericX.value) return M.l + ((i + 0.5) / n) * pw
  const xs = data.value.pts.map((q) => q.x as number)
  const lo = Math.min(...xs)
  const hi = Math.max(...xs)
  // log-ish spacing keeps 1, 4, 8, 16, 32 readable
  const f = (v: number) => Math.log2(v + 1)
  return M.l + 24 + ((f(p.x as number) - f(lo)) / (f(hi) - f(lo) || 1)) * (pw - 48)
}
const py = (v: number) => M.t + ph - (v / ymax.value) * ph
const ticks = computed(() => [0, 0.25, 0.5, 0.75, 1].map((t) => t * ymax.value))
const line = computed(() => data.value.pts.map((p, i) => `${i ? 'L' : 'M'}${px(p, i)},${py(p.y)}`).join(' '))
const barW = computed(() => Math.min(72, (pw / Math.max(data.value.pts.length, 1)) * 0.6))
</script>

<template>
  <figure class="chart">
    <figcaption v-if="title">{{ title }}</figcaption>
    <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="title ?? 'chart'">
      <g v-for="t in ticks" :key="t">
        <line :x1="M.l" :x2="W - M.r" :y1="py(t)" :y2="py(t)" class="grid" />
        <text :x="M.l - 12" :y="py(t) + 5" text-anchor="end" class="tick">{{ fmt(t, t < 10 && t > 0 ? 1 : 0) }}</text>
      </g>
      <template v-if="kind === 'bar'">
        <rect v-for="(p, i) in data.pts" :key="i" :x="px(p, i) - barW / 2" :y="py(p.y)" :width="barW" :height="py(0) - py(p.y)" rx="4" class="bar" />
      </template>
      <path v-else :d="line" class="path" />
      <g v-for="(p, i) in data.pts" :key="`l${i}`">
        <circle v-if="kind === 'line'" :cx="px(p, i)" :cy="py(p.y)" r="6" class="dot" />
        <text :x="px(p, i)" :y="py(p.y) - 14" text-anchor="middle" class="value">{{ fmt(p.y, digits) }}</text>
        <text :x="px(p, i)" :y="H - M.b + 28" text-anchor="middle" class="tick">{{ p.x }}</text>
      </g>
      <text :x="M.l + pw / 2" :y="H - 8" text-anchor="middle" class="axis">{{ xlabel ?? LABELS[x ?? ''] ?? x }}</text>
      <text :x="18" :y="M.t + ph / 2" text-anchor="middle" class="axis" :transform="`rotate(-90 18 ${M.t + ph / 2})`">{{ ylabel ?? LABELS[y ?? ''] ?? y }}</text>
    </svg>
    <div v-if="!data.pts.length" class="err">no data points: check the source path, x and y</div>
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
.err {
  color: var(--ki-bad);
  font-size: var(--ki-text-sm);
}
</style>
