<script setup lang="ts">
// A table of measured results, one row per result file (or a typed table marked illustrative).
//   measured:     source="measured:benchmark/results/<dir>" :columns='["concurrency","ttft_ms.p50"]'
//                 optional: match="baseline-c" (only files whose path contains it), :headers, :digits
//   illustrative: source="illustrative" :headers='[...]' :rows='[[...],[...]]'
import { computed } from 'vue'
import { fmt, LABELS, measuredDocs, parseSource, pick, provenance } from '../composables/results'
import SourceBadge from './SourceBadge.vue'

const props = defineProps<{
  source: string
  columns?: string[]
  headers?: string[]
  rows?: (string | number)[][]
  match?: string
  digits?: Record<string, number>
}>()

const table = computed(() => {
  const src = parseSource(props.source)
  if (src.kind === 'illustrative')
    return { illustrative: true, headers: props.headers ?? [], rows: (props.rows ?? []).map((r) => r.map(String)), text: '' }
  const cols = props.columns ?? []
  const docs = measuredDocs(src.path, props.match)
  return {
    illustrative: false,
    headers: props.headers ?? cols.map((c) => LABELS[c] ?? c),
    rows: docs.map(({ doc }) => cols.map((c) => fmt(pick(doc, c), props.digits?.[c] ?? (c.includes('tps') || c.includes('rps') ? 1 : 0)))),
    text: docs.length ? provenance(docs[0].doc) : '',
    empty: docs.length === 0,
  }
})
</script>

<template>
  <div class="rt">
    <table>
      <thead>
        <tr><th v-for="h in table.headers" :key="h">{{ h }}</th></tr>
      </thead>
      <tbody>
        <tr v-for="(r, i) in table.rows" :key="i">
          <td v-for="(c, j) in r" :key="j" :class="{ first: j === 0 }">{{ c }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="table.empty" class="err">no result files match this source</div>
    <SourceBadge :illustrative="table.illustrative" :text="table.text" />
  </div>
</template>

<style scoped>
.rt table {
  margin-bottom: 8px;
}
.rt td {
  font-variant-numeric: tabular-nums;
}
.rt td.first {
  font-weight: 650;
}
.err {
  color: var(--ki-bad);
  font-size: var(--ki-text-sm);
}
</style>
