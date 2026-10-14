<script setup lang="ts">
// D01: TRAINING ≠ FINE-TUNING ≠ INFERENCE. One question per row: what happens to the weights?
// Click 1: the last row says where this workshop lives (inference is the highlighted column).
import DiagramFrame from './DiagramFrame.vue'

const COL_X = [176, 504, 832]
const CW = 288
const rows = [
  { label: 'Weights', cells: [['Written from scratch:', 'every parameter updated'], ['Updated: a small adapter', 'or a full copy'], ['Read only:', 'never modified']] },
  { label: 'Data in', cells: [['A very large', 'text corpus'], ['Your examples:', 'input and wanted output'], ['A prompt', 'plus the context you add']] },
  { label: 'Result', cells: [['A base model', 'published weights'], ['A variant tied to', 'one base revision'], ['Tokens,', 'streamed back']] },
  { label: 'Who, how often', cells: [['The publisher,', 'once per model'], ['You, if nothing', 'cheaper works'], ['Every request,', 'all day']] },
]
const ROW_Y = (r: number) => 84 + r * 68
const LAST_Y = 84 + rows.length * 68
</script>

<template>
  <DiagramFrame label="Training writes the weights, fine-tuning updates them, inference only reads them">
    <!-- column headers -->
    <g>
      <rect :x="COL_X[0]" y="6" :width="CW" height="60" rx="10" class="dg-box" />
      <text :x="COL_X[0] + CW / 2" y="43" text-anchor="middle" class="dg-title">TRAINING</text>
      <rect :x="COL_X[1]" y="6" :width="CW" height="60" rx="10" class="dg-box" />
      <text :x="COL_X[1] + CW / 2" y="43" text-anchor="middle" class="dg-title">FINE-TUNING</text>
      <rect :x="COL_X[2]" y="6" :width="CW" height="60" rx="10" class="dg-box dg-teal" />
      <text :x="COL_X[2] + CW / 2" y="43" text-anchor="middle" class="dg-title">INFERENCE</text>
      <text :x="(COL_X[0] + CW + COL_X[1]) / 2" y="48" text-anchor="middle" class="neq dg-title">≠</text>
      <text :x="(COL_X[1] + CW + COL_X[2]) / 2" y="48" text-anchor="middle" class="neq dg-title">≠</text>
    </g>

    <!-- rows -->
    <g v-for="(row, r) in rows" :key="row.label">
      <text x="0" :y="ROW_Y(r) + 38" class="dg-text-muted">{{ row.label }}</text>
      <g v-for="(cell, c) in row.cells" :key="c">
        <rect :x="COL_X[c]" :y="ROW_Y(r)" :width="CW" height="58" rx="8" class="dg-box" :class="c === 2 ? 'dg-teal' : ''" />
        <text :x="COL_X[c] + 16" :y="ROW_Y(r) + 25" class="cell">{{ cell[0] }}</text>
        <text :x="COL_X[c] + 16" :y="ROW_Y(r) + 47" class="cell-muted">{{ cell[1] }}</text>
      </g>
    </g>

    <!-- where this workshop lives -->
    <g v-click="1">
      <text x="0" :y="LAST_Y + 38" class="dg-text-muted">In this workshop</text>
      <rect :x="COL_X[0]" :y="LAST_Y" :width="CW" height="58" rx="8" class="dg-box" stroke-dasharray="6 5" />
      <text :x="COL_X[0] + 16" :y="LAST_Y + 25" class="cell">Explained, not run:</text>
      <text :x="COL_X[0] + 16" :y="LAST_Y + 47" class="cell-muted">only what inference needs</text>
      <rect :x="COL_X[1]" :y="LAST_Y" :width="CW" height="58" rx="8" class="dg-box" stroke-dasharray="6 5" />
      <text :x="COL_X[1] + 16" :y="LAST_Y + 25" class="cell">Discussed:</text>
      <text :x="COL_X[1] + 16" :y="LAST_Y + 47" class="cell-muted">what it costs, when not to</text>
      <rect :x="COL_X[2]" :y="LAST_Y" :width="CW" height="58" rx="8" class="dg-box dg-green thick" />
      <text :x="COL_X[2] + 16" :y="LAST_Y + 25" class="cell">Everything we build,</text>
      <text :x="COL_X[2] + 16" :y="LAST_Y + 47" class="cell-muted">measure and operate</text>
    </g>
  </DiagramFrame>
</template>

<style scoped>
.thick {
  stroke-width: 3;
}
.neq {
  font-size: 36px;
  fill: var(--ki-fg-muted);
}
.cell {
  font-family: var(--ki-font-sans);
  fill: var(--ki-fg);
  font-size: 19px;
}
.cell-muted {
  font-family: var(--ki-font-sans);
  fill: var(--ki-fg-muted);
  font-size: 17px;
}
</style>
