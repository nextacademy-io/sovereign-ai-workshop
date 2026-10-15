<script setup lang="ts">
// D05: the four memory levels a GPU kernel sees, and where the weights have to live.
// Sizes: per-SM figures for the GB202 die and the 96 GB of VRAM come from docs/RESEARCH.md 6.3 and 6.5 (datasheet and whitepaper).
// NVIDIA publishes no bandwidth for registers, L1 or L2, so none is drawn. Row widths are a schematic, not to scale.
// Click 1: the weights (16.38 GB) only fit in global memory.
// Click 2: every decode step reads all of them from there; the time of that read is bytes ÷ bandwidth (no model-specific result is shown: the module that
// teaches the decode step asks the participants to predict it).
import DiagramFrame from './DiagramFrame.vue'

const levels = [
  { name: 'Registers', size: '256 KB per SM', note: 'private to one thread · bandwidth not published', w: 560, y: 20, tone: '' },
  { name: 'L1 cache + shared memory', size: '128 KB per SM', note: 'inside one SM · bandwidth not published', w: 620, y: 116, tone: '' },
  { name: 'L2 cache', size: '128 MB *', note: 'shared by all 188 SMs · bandwidth not published', w: 680, y: 212, tone: '' },
  { name: 'Global memory = VRAM (GDDR7)', size: '96 GB', note: 'reached by every SM · 1,597 GB/s (datasheet)', w: 740, y: 308, tone: 'dg-teal' },
]
</script>

<template>
  <DiagramFrame label="GPU memory hierarchy: registers, L1 and shared memory, L2, global memory; the weights only fit in global memory">
    <g v-for="l in levels" :key="l.name">
      <rect x="0" :y="l.y" :width="l.w" height="84" rx="10" class="dg-box" :class="l.tone" />
      <text x="20" :y="l.y + 34" class="dg-title">{{ l.name }}</text>
      <text :x="l.w - 20" :y="l.y + 34" text-anchor="end" class="dg-mono">{{ l.size }}</text>
      <text x="20" :y="l.y + 62" class="dg-text-muted">{{ l.note }}</text>
    </g>

    <!-- small and fast at the top, large and slow at the bottom -->
    <text x="0" y="424" class="dg-text-muted">small and close to the math units (top)  →  large and further away (bottom).  Schematic, not to scale.</text>
    <text x="0" y="448" class="dg-text-muted">* Workstation Edition, same GB202 die; no L2 size is published for the Server Edition.</text>

    <!-- weights -->
    <g v-click="1">
      <path d="M790 350 H744" class="dg-line" style="stroke: var(--ki-good)" marker-end="url(#ki-arrow)" />
      <rect x="792" y="308" width="344" height="84" rx="10" class="dg-box dg-green" />
      <text x="964" y="342" text-anchor="middle" class="dg-title">Weights, 16.38 GB</text>
      <text x="964" y="370" text-anchor="middle" class="dg-text-muted">Qwen3-8B in BF16: fits only here</text>
    </g>

    <!-- one decode step -->
    <g v-click="2">
      <rect x="792" y="20" width="344" height="260" rx="10" class="dg-box dg-teal" />
      <text x="812" y="54" class="dg-title">One decode step</text>
      <text x="812" y="86" class="dg-text">reads every weight once</text>
      <text x="812" y="118" class="dg-text">from global memory:</text>
      <text x="812" y="162" class="dg-mono">time ≥ bytes read</text>
      <text x="812" y="196" class="dg-mono">       ÷ 1,597 GB/s</text>
      <text x="812" y="236" class="dg-text-muted">L2 holds 128 MB: about 1/128 of</text>
      <text x="812" y="258" class="dg-text-muted">the weights. No cache can hold them.</text>
    </g>
  </DiagramFrame>
</template>
