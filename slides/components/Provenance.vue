<script setup lang="ts">
// One line under a group of measured numbers: hardware, model, engine version, date.
//   <Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />
import { computed } from 'vue'
import { measuredDocs, parseSource, provenance } from '../composables/results'

const props = defineProps<{ source: string }>()
const text = computed(() => {
  const src = parseSource(props.source)
  if (src.kind === 'illustrative') return ''
  const docs = measuredDocs(src.path)
  return docs.length ? provenance(docs[0].doc) : `no result file at ${src.path}`
})
</script>

<template>
  <p v-if="text" class="prov">measured · {{ text }}</p>
</template>

<style scoped>
.prov {
  margin: 4px 0 14px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--ki-fg-dim);
}
</style>
