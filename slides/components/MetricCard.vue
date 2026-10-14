<script setup lang="ts">
// One number. `source` is required:
//   source="measured:benchmark/results/<file>.json" + metric="ttft_ms.p50"   value comes from the file
//   source="illustrative" + value="..."                                      value is typed; badge says so
// A slide with measured cards also carries ONE <Provenance source="..." /> that says where and when.
import { computed } from 'vue'
import { fmt, measuredDocs, parseSource, pick, provenance } from '../composables/results'
import SourceBadge from './SourceBadge.vue'

const props = defineProps<{
  label: string
  source: string
  metric?: string
  value?: string | number
  unit?: string
  digits?: number | string
  note?: string
  tone?: 'good' | 'bad' | 'neutral'
}>()

const resolved = computed(() => {
  const src = parseSource(props.source)
  if (src.kind === 'illustrative') return { illustrative: true, value: props.value, text: '' }
  const docs = measuredDocs(src.path)
  if (docs.length !== 1 || !props.metric)
    return { illustrative: false, value: undefined, text: '', error: `needs exactly one result file and a metric (${docs.length} found)` }
  const v = pick(docs[0].doc, props.metric)
  if (v === undefined) return { illustrative: false, value: undefined, text: '', error: `no '${props.metric}' in ${src.path}` }
  return { illustrative: false, value: v, text: provenance(docs[0].doc) }
})
const shown = computed(() =>
  typeof resolved.value.value === 'number' ? fmt(resolved.value.value, props.digits ?? 0) : (resolved.value.value ?? '–'),
)
</script>

<template>
  <div class="metric" :class="[tone, { missing: resolved.error }]">
    <div class="label">{{ label }}</div>
    <div class="value">
      <span>{{ shown }}</span><span v-if="unit" class="unit">{{ unit }}</span>
    </div>
    <div v-if="note" class="note">{{ note }}</div>
    <div v-if="resolved.error" class="note error">{{ resolved.error }}</div>
    <SourceBadge :illustrative="resolved.illustrative" :text="resolved.illustrative ? '' : 'result file'" :title="resolved.text" />
  </div>
</template>

<style scoped>
.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 20px;
  border-radius: var(--ki-radius);
  background: var(--ki-bg-raised);
  border: 1px solid var(--ki-border);
  border-top: 3px solid var(--ki-layer, var(--ki-runtime));
}
.metric.good {
  border-top-color: var(--ki-good);
}
.metric.bad {
  border-top-color: var(--ki-bad);
}
.metric.missing {
  border-color: var(--ki-bad);
}
.label {
  font-size: var(--ki-text-xs);
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ki-fg-muted);
}
.value {
  font-size: var(--ki-text-2xl);
  font-weight: 650;
  letter-spacing: -0.02em;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}
.unit {
  font-size: var(--ki-text-base);
  font-weight: 500;
  color: var(--ki-fg-muted);
  margin-left: 6px;
}
.note {
  font-size: var(--ki-text-sm);
  color: var(--ki-fg-muted);
}
.note.error {
  color: var(--ki-bad);
}
</style>
