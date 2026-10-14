<script setup lang="ts">
// D18: who controls what in the workshop's own setup, across the five sovereignty dimensions.
// Source: docs/DIGITAL-SOVEREIGNTY.md section 6.5 (the classification table), in the same words as far as they fit.
// Start:   every component of the setup against data, model, infrastructure, operations and portability.
// Click 1: the weakest dimensions are outlined, with the reason the setup is still acceptable for this workshop.
import DiagramFrame from './DiagramFrame.vue'

type Kind = 'us' | 'shared' | 'third' | 'na'
type Cell = [Kind, string, string]

const dims = ['DATA', 'MODEL', 'INFRASTRUCTURE', 'OPERATIONS', 'PORTABILITY']
const COL0 = 300
const PITCH = 167
const CW = 160
const colX = (i: number) => COL0 + i * PITCH
const rowY = (r: number) => 44 + r * 58

const NA: Cell = ['na', 'n/a', '']
const rows: { name: string; sub: string; cells: Cell[] }[] = [
  {
    name: 'GPU pod',
    sub: 'Runpod Secure Cloud',
    cells: [['third', 'Provider', 'disk and memory'], NA, ['third', 'Provider', 'host, driver, net'], ['shared', 'Shared', 'they host, we run'], ['us', 'Us', 'scripts rebuild it']],
  },
  {
    name: 'vLLM and profiles',
    sub: 'engine, configuration',
    cells: [['us', 'Us', 'request log off'], NA, NA, ['us', 'Us', 'pin and patch'], ['us', 'Us', 'API, image digest']],
  },
  {
    name: 'Model weights',
    sub: 'pinned, Apache-2.0',
    cells: [NA, ['us', 'Us', 'SHA, licence read'], NA, ['us', 'Us', ''], ['us', 'Us', 'no own mirror yet']],
  },
  {
    name: 'Hugging Face Hub',
    sub: 'download source',
    cells: [['third', 'Third party', 'download metadata'], ['third', 'Third party', 'only upstream copy'], ['third', 'Third party', ''], ['third', 'Third party', ''], ['third', 'Weak', 'until mirrored']],
  },
  {
    name: 'Prometheus, Grafana',
    sub: 'monitoring',
    cells: [['us', 'Us', 'metrics only'], NA, ['third', 'Provider', 'runs on the pod'], ['us', 'Us', ''], ['us', 'Us', 'open formats']],
  },
  {
    name: "Trainer's cloud account",
    sub: 'keys, billing',
    cells: [['third', 'Provider', 'billing, account'], NA, ['third', 'Provider', ''], ['us', 'Us', 'keys, spend limits'], ['us', 'Us', 'pod spec only']],
  },
]
const cls = (k: Kind) => ({ us: 'dg-green', shared: 'dg-amber', third: 'dg-red', na: 'na' })[k]
</script>

<template>
  <DiagramFrame label="Who controls what in the workshop setup: six components against data, model, infrastructure, operations and portability, each marked as ours, shared or controlled by a third party">
    <!-- column headers -->
    <text v-for="(d, i) in dims" :key="d" :x="colX(i) + CW / 2" y="26" text-anchor="middle" class="dg-mono">{{ d }}</text>

    <!-- rows -->
    <g v-for="(r, ri) in rows" :key="r.name">
      <text x="0" :y="rowY(ri) + 22" class="dg-text">{{ r.name }}</text>
      <text x="0" :y="rowY(ri) + 44" class="dg-text-muted">{{ r.sub }}</text>
      <g v-for="(c, ci) in r.cells" :key="ci">
        <rect :x="colX(ci)" :y="rowY(ri)" :width="CW" height="52" rx="8" class="dg-box" :class="cls(c[0])" />
        <text :x="colX(ci) + CW / 2" :y="rowY(ri) + (c[2] ? 22 : 31)" text-anchor="middle" class="main" :class="{ muted: c[0] === 'na' }">{{ c[1] }}</text>
        <text v-if="c[2]" :x="colX(ci) + CW / 2" :y="rowY(ri) + 43" text-anchor="middle" class="dg-text-muted">{{ c[2] }}</text>
      </g>
    </g>

    <!-- legend -->
    <rect x="0" y="402" width="18" height="18" rx="4" class="dg-box dg-green" />
    <text x="26" y="417" class="dg-text-muted">we control it</text>
    <rect x="170" y="402" width="18" height="18" rx="4" class="dg-box dg-amber" />
    <text x="196" y="417" class="dg-text-muted">shared</text>
    <rect x="300" y="402" width="18" height="18" rx="4" class="dg-box dg-red" />
    <text x="326" y="417" class="dg-text-muted">a third party controls it</text>
    <text x="570" y="417" class="dg-text-muted">n/a: the dimension does not apply</text>

    <!-- click 1: the weakest dimensions -->
    <g v-click="1">
      <rect :x="colX(0) - 5" y="34" :width="CW + 10" height="356" rx="12" class="dg-line" stroke-dasharray="7 6" style="stroke: var(--ki-bad)" />
      <rect :x="colX(2) - 5" y="34" :width="CW + 10" height="356" rx="12" class="dg-line" stroke-dasharray="7 6" style="stroke: var(--ki-bad)" />
      <text x="0" y="448" class="dg-text">Weakest here: DATA and INFRASTRUCTURE. Acceptable only because the pod data is synthetic.</text>
    </g>
  </DiagramFrame>
</template>

<style scoped>
.main {
  font-family: var(--ki-font-sans);
  fill: var(--ki-fg);
  font-size: 19px;
  font-weight: 650;
}
.main.muted {
  fill: var(--ki-fg-dim);
  font-weight: 400;
}
.na {
  opacity: 0.45;
}
</style>
