<script setup lang="ts">
// A compact card for ONE benchmark run: the numbers a participant reads first.
//   source="measured:benchmark/results/<file>.json"   or   source="illustrative" with :values='{...}'
import { computed } from 'vue'
import { fmt, measuredDocs, parseSource, pick, provenance } from '../composables/results'
import SourceBadge from './SourceBadge.vue'

const props = defineProps<{ source: string; title?: string; values?: Record<string, string | number> }>()

const ROWS: { key: string; label: string; digits: number; unit: string }[] = [
  { key: 'ttft_ms.p50', label: 'TTFT p50', digits: 0, unit: 'ms' },
  { key: 'ttft_ms.p95', label: 'TTFT p95', digits: 0, unit: 'ms' },
  { key: 'itl_ms.p50', label: 'ITL p50', digits: 1, unit: 'ms' },
  { key: 'output_tps_per_request.p50', label: 'Per-request speed', digits: 1, unit: 'tok/s' },
  { key: 'aggregate_tps', label: 'Aggregate throughput', digits: 0, unit: 'tok/s' },
]

const data = computed(() => {
  const src = parseSource(props.source)
  if (src.kind === 'illustrative')
    return { illustrative: true, text: '', load: props.values?.load, get: (k: string) => props.values?.[k] }
  const docs = measuredDocs(src.path)
  const doc = docs[0]?.doc
  return {
    illustrative: false,
    text: doc ? provenance(doc) : '',
    load: doc?.concurrency,
    get: (k: string) => (doc ? pick(doc, k) : undefined),
  }
})
</script>

<template>
  <div class="bench">
    <div class="head">
      <span class="title">{{ title ?? 'Benchmark run' }}</span>
      <span v-if="data.load !== undefined" class="ki-pill">concurrency {{ data.load }}</span>
    </div>
    <dl>
      <template v-for="r in ROWS" :key="r.key">
        <dt>{{ r.label }}</dt>
        <dd>{{ typeof data.get(r.key) === 'number' ? fmt(data.get(r.key) as number, r.digits) : (data.get(r.key) ?? 'n/a') }} <span>{{ r.unit }}</span></dd>
      </template>
    </dl>
    <SourceBadge :illustrative="data.illustrative" :text="data.text" />
  </div>
</template>

<style scoped>
.bench {
  background: var(--ki-bg-raised);
  border: 1px solid var(--ki-border);
  border-radius: var(--ki-radius);
  padding: 18px 22px;
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.title {
  font-weight: 650;
}
dl {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 24px;
  margin: 0 0 10px;
}
dt {
  color: var(--ki-fg-muted);
  font-size: var(--ki-text-sm);
}
dd {
  margin: 0;
  text-align: right;
  font-weight: 650;
  font-variant-numeric: tabular-nums;
}
dd span {
  color: var(--ki-fg-muted);
  font-weight: 500;
  font-size: var(--ki-text-sm);
}
</style>
