<script setup lang="ts">
// D04: what the KV cache stores, and why decode reads it instead of recomputing it.
// Click 1: prefill leaves the keys and values of the prompt in every layer.
// Click 2: a decode step computes ONE new column and reads all the old ones.
import DiagramFrame from './DiagramFrame.vue'

const tokens = ['Explain', 'the', 'KV', 'cache', 'in', 'one', 'line']
const layers = ['Layer 1', 'Layer 2', '⋮', 'Layer 36']
const X0 = 190
const CW = 96
const colX = (i: number) => X0 + i * (CW + 10)
const rowY = (r: number) => 84 + r * 66
</script>

<template>
  <DiagramFrame label="The KV cache holds the keys and values of every processed token in every layer">
    <!-- token header -->
    <g v-for="(t, i) in tokens" :key="t">
      <rect :x="colX(i)" y="20" :width="CW" height="38" rx="8" class="dg-box" :class="i < 6 ? 'dg-teal' : 'dg-amber'" />
      <text :x="colX(i) + CW / 2" y="45" text-anchor="middle" class="dg-mono">{{ t }}</text>
    </g>
    <text x="0" y="45" class="dg-text-muted">token</text>

    <!-- layers -->
    <g v-for="(l, r) in layers" :key="l">
      <text x="0" :y="rowY(r) + 36" :class="l === '⋮' ? 'dg-title' : 'dg-text'">{{ l }}</text>
    </g>

    <!-- cached columns (prefill) -->
    <g v-click="1">
      <g v-for="i in 6" :key="`c${i}`">
        <template v-for="(l, r) in layers" :key="`${i}-${l}`">
          <g v-if="l !== '⋮'">
            <rect :x="colX(i - 1)" :y="rowY(r)" :width="CW / 2" height="50" rx="6" class="dg-box dg-violet" />
            <rect :x="colX(i - 1) + CW / 2" :y="rowY(r)" :width="CW / 2" height="50" rx="6" class="dg-box dg-amber" />
          </g>
        </template>
      </g>
      <text :x="colX(0)" y="372" class="dg-text">Prefill: every prompt token leaves a K and a V in every layer</text>
    </g>

    <!-- the new column (decode) -->
    <g v-click="2">
      <g v-for="(l, r) in layers" :key="`n${l}`">
        <g v-if="l !== '⋮'">
          <rect :x="colX(6)" :y="rowY(r)" :width="CW" height="50" rx="6" class="dg-box dg-green" style="stroke-width: 3" />
        </g>
      </g>
      <path :d="`M${colX(0) + 20} 354 H ${colX(6) + CW / 2}`" class="dg-line" style="stroke: var(--ki-good)" marker-end="url(#ki-arrow)" />
      <text :x="colX(0)" y="406" class="dg-text">Decode: one new column is computed, six are only read</text>
    </g>

    <!-- legend and size -->
    <rect x="190" y="420" width="18" height="18" rx="4" class="dg-box dg-violet" />
    <text x="214" y="435" class="dg-text-muted">K: keys</text>
    <rect x="310" y="420" width="18" height="18" rx="4" class="dg-box dg-amber" />
    <text x="334" y="435" class="dg-text-muted">V: values</text>
    <text x="450" y="435" class="dg-mono">per token = 2 × 36 layers × 8 KV heads × 128 dims × 2 B = 147,456 B</text>
  </DiagramFrame>
</template>
