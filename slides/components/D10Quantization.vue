<script setup lang="ts">
// D10: quantization. What is stored at which precision, and which bytes one decode step reads.
// Three bars, one per profile of the quantization experiment, for a step with 16 requests running.
// Bar length = bytes read in one step (arithmetic, not a measurement): the weights, plus the KV cache of 16 requests
// of about 1,290 tokens each (16 × 1,290 × 147,456 B = 3.04 GB; half of that with an FP8 KV cache).
// Floor = bytes ÷ 1,597 GB/s (datasheet bandwidth).
// Click 1: BF16. Click 2: FP8 weights. Click 3: FP8 KV cache.
import DiagramFrame from './DiagramFrame.vue'

const X0 = 210
const S = 32 // px per GB
const GB_PER_BAR = (gb: number) => gb * S
const rows = [
  { label: 'BF16', sub: 'profile baseline', w: 16.38, kv: 3.04, kvText: '3.0', floor: '12.2 ms', note: 'every weight is read once per step; the KV cache is read as well' },
  { label: 'FP8 weights', sub: 'profile fp8', w: 9.44, kv: 3.04, kvText: '3.0', floor: '7.8 ms', note: 'embeddings and output head stay BF16: 9.44 GB, not 8.2 GB' },
  { label: 'FP8 KV cache', sub: 'profile kv-fp8', w: 16.38, kv: 1.52, kvText: '1.5', floor: '11.2 ms', note: 'same weights, half the bytes per cached token' },
]
const rowY = (i: number) => 92 + i * 112
</script>

<template>
  <DiagramFrame label="Quantization: the bytes one decode step reads, with BF16, FP8 weights and an FP8 KV cache">
    <text x="0" y="30" class="dg-title">Bytes read by one decode step, 16 requests running</text>
    <rect x="860" y="14" width="16" height="16" rx="3" class="dg-box dg-teal" />
    <text x="882" y="28" class="dg-text-muted">weights, GB</text>
    <rect x="990" y="14" width="16" height="16" rx="3" class="dg-box dg-amber" />
    <text x="1012" y="28" class="dg-text-muted">KV, GB</text>
    <text x="870" y="76" class="dg-text-muted">floor at 1,597 GB/s</text>

    <g v-for="(r, i) in rows" :key="r.label">
      <g v-click="i + 1">
        <text x="0" :y="rowY(i) + 28" class="dg-title">{{ r.label }}</text>
        <text x="0" :y="rowY(i) + 52" class="dg-text-muted">{{ r.sub }}</text>
        <rect :x="X0" :y="rowY(i)" :width="GB_PER_BAR(r.w)" height="64" rx="8" class="dg-box dg-teal" />
        <text :x="X0 + 16" :y="rowY(i) + 40" class="dg-text">{{ r.w.toFixed(2) }} GB</text>
        <rect :x="X0 + GB_PER_BAR(r.w)" :y="rowY(i)" :width="GB_PER_BAR(r.kv)" height="64" rx="8" class="dg-box dg-amber" />
        <text :x="X0 + GB_PER_BAR(r.w) + GB_PER_BAR(r.kv) / 2" :y="rowY(i) + 40" text-anchor="middle" class="dg-text">{{ r.kvText }}</text>
        <text x="870" :y="rowY(i) + 42" class="dg-title">{{ r.floor }}</text>
        <text :x="X0" :y="rowY(i) + 90" class="dg-text-muted">{{ r.note }}</text>
      </g>
    </g>

    <text x="0" y="448" class="dg-mono">floor = bytes per step ÷ 1,597 GB/s   (arithmetic, not a measurement)</text>
  </DiagramFrame>
</template>
