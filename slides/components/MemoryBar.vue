<script setup lang="ts">
// A VRAM budget as one stacked bar.
//   measured:     source="measured:benchmark/results/reference/baseline/kv-formula-check.json"
//                 :segments='[{ "label": "Weights", "metric": "model_memory_gib", "tone": "runtime" },
//                             { "label": "KV cache", "metric": "available_kv_gib", "tone": "application" },
//                             { "label": "Everything else", "rest": true, "tone": "muted" }]'
//                 total="76.5"  (GiB; the budget the bar is drawn against)
//   illustrative: source="illustrative" with "gib" instead of "metric"
import { computed } from 'vue'
import { fmt, measuredDocs, parseSource, pick, provenance } from '../composables/results'
import SourceBadge from './SourceBadge.vue'

interface Segment {
  label: string
  metric?: string
  gib?: number
  rest?: boolean
  tone?: 'runtime' | 'infrastructure' | 'application' | 'muted' | 'bad' | 'info'
}

const props = defineProps<{ source: string; segments: Segment[]; total: number | string; unit?: string }>()

const data = computed(() => {
  const src = parseSource(props.source)
  const doc = src.kind === 'measured' ? measuredDocs(src.path, undefined)[0]?.doc ?? null : null
  // auxiliary result files hold their numbers at the top level; benchmark results under their own keys
  const value = (s: Segment) => (s.metric && doc ? Number(pick(doc, s.metric)) : (s.gib ?? 0))
  // `total` is a number, or (measured) a metric path in the same file
  const total = typeof props.total === 'string' ? Number(doc ? pick(doc, props.total) : NaN) : props.total
  const known = props.segments.filter((s) => !s.rest).reduce((a, s) => a + value(s), 0)
  const sized = props.segments.map((s) => ({ ...s, v: s.rest ? Math.max(total - known, 0) : value(s) }))
  return { illustrative: src.kind === 'illustrative', text: doc ? provenance(doc) : '', segs: sized, total }
})
</script>

<template>
  <div class="mb">
    <div class="bar" role="img" aria-label="VRAM budget">
      <div v-for="s in data.segs" :key="s.label" class="seg" :class="s.tone ?? 'muted'" :style="{ flexGrow: s.v || 0.0001 }">
        <span v-if="s.v / data.total > 0.07" class="val">{{ fmt(s.v, 1) }}</span>
      </div>
    </div>
    <ul class="legend">
      <li v-for="s in data.segs" :key="s.label"><i :class="s.tone ?? 'muted'" />{{ s.label }} <b>{{ fmt(s.v, 1) }} {{ unit ?? 'GiB' }}</b></li>
    </ul>
    <SourceBadge :illustrative="data.illustrative" :text="data.text" />
  </div>
</template>

<style scoped>
.bar {
  display: flex;
  height: 64px;
  border-radius: var(--ki-radius);
  overflow: hidden;
  border: 1px solid var(--ki-border-strong);
  margin-bottom: 12px;
}
.seg {
  flex-basis: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid var(--ki-bg);
  min-width: 2px;
}
.val {
  font-weight: 650;
  font-size: var(--ki-text-sm);
  font-variant-numeric: tabular-nums;
  color: var(--ki-bg);
}
.runtime {
  background: var(--ki-runtime);
}
.infrastructure {
  background: var(--ki-infrastructure);
}
.application {
  background: var(--ki-application);
}
.bad {
  background: var(--ki-bad);
}
.info {
  background: var(--ki-info);
}
.muted {
  background: var(--ki-border-strong);
}
.muted .val {
  color: var(--ki-fg);
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 26px;
  padding: 0;
  margin: 0 0 8px;
  font-size: var(--ki-text-sm);
  list-style: none;
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
i {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  display: inline-block;
}
</style>
