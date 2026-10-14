<script setup lang="ts">
// D07: the roofline of the workshop GPU, drawn conceptually on log-log axes (120 px per decade on both axes,
// so the memory roof has slope 1).
//   roof(I) = min(504 TFLOPS, 1,597 GB/s x I)      I = FLOP per byte
//   ridge   = 503.8 TFLOPS / 1,597 GB/s = about 315 FLOP/B        (derived, docs/RESEARCH.md 6.4 and 6.14)
// For BF16 weights a pass over N tokens has intensity about N FLOP/B (2 FLOP per weight per token / 2 bytes per weight).
// The dots are ceilings of that arithmetic, not measurements; a real kernel sits below the roof.
// Click 1: decode with 1 and with 64 sequences. Click 2: prefill of a 1,200-token prompt.
import DiagramFrame from './DiagramFrame.vue'

const X0 = 90
const Y0 = 392
const DEC = 120
const PEAK = 503.8
const BW = 1.597 // TFLOPS per (FLOP/B), i.e. 1,597 GB/s
const x = (intensity: number) => X0 + DEC * Math.log10(intensity)
const y = (tflops: number) => Y0 - DEC * Math.log10(tflops)
const roof = (i: number) => Math.min(PEAK, BW * i)
const ridgeI = PEAK / BW

const xTicks = [1, 10, 100, 1000, 10000]
const yTicks = [1, 10, 100, 1000]
const tickLabel = (v: number) => v.toLocaleString('en-US')

// midpoint of the memory roof, for the rotated label
const midX = (x(1) + x(ridgeI)) / 2
const midY = (y(roof(1)) + y(PEAK)) / 2
</script>

<template>
  <DiagramFrame label="Roofline of the workshop GPU: decode sits left of the ridge point, prefill right of it">
    <!-- axes and grid -->
    <g v-for="t in yTicks" :key="`y${t}`">
      <path :d="`M${X0} ${y(t)} H${x(10000)}`" class="dg-line" style="stroke: var(--ki-border); stroke-width: 1" />
      <text :x="X0 - 12" :y="y(t) + 6" text-anchor="end" class="dg-text-muted">{{ tickLabel(t) }}</text>
    </g>
    <g v-for="t in xTicks" :key="`x${t}`">
      <path :d="`M${x(t)} ${y(1000)} V${y(1)}`" class="dg-line" style="stroke: var(--ki-border); stroke-width: 1" />
      <text :x="x(t)" :y="y(1) + 26" text-anchor="middle" class="dg-text-muted">{{ tickLabel(t) }}</text>
    </g>
    <path :d="`M${X0} ${y(1000)} V${y(1)} H${x(10000)}`" class="dg-line" />
    <text :x="x(100)" :y="y(1) + 56" text-anchor="middle" class="dg-text">arithmetic intensity (FLOP per byte)</text>
    <text x="0" y="14" class="dg-text">attainable TFLOPS</text>

    <!-- the roof -->
    <path :d="`M${x(1)} ${y(roof(1))} L${x(ridgeI)} ${y(PEAK)} H${x(10000)}`" class="dg-line" style="stroke: var(--ki-runtime); stroke-width: 4" />
    <text :transform="`translate(${midX} ${midY}) rotate(-45)`" y="-14" text-anchor="middle" class="dg-text">memory-limited</text>
    <text :x="x(ridgeI) + 14" :y="y(PEAK) + 30" class="dg-text">peak ≈ 504 TFLOPS</text>
    <path :d="`M${x(ridgeI)} ${y(PEAK)} V${y(1)}`" class="dg-line" style="stroke: var(--ki-fg-dim); stroke-dasharray: 6 6" />
    <circle :cx="x(ridgeI)" :cy="y(PEAK)" r="7" class="dg-box" style="fill: var(--ki-bg); stroke: var(--ki-runtime); stroke-width: 3" />
    <text :x="x(ridgeI) - 10" :y="y(1) - 12" text-anchor="end" class="dg-text-muted">ridge ≈ 315</text>

    <!-- decode -->
    <g v-click="1">
      <circle :cx="x(1)" :cy="y(roof(1))" r="9" class="dg-box dg-violet" style="stroke-width: 3" />
      <text :x="x(1) + 14" :y="y(roof(1)) + 22" class="dg-mono">1</text>
      <circle :cx="x(64)" :cy="y(roof(64))" r="9" class="dg-box dg-violet" style="stroke-width: 3" />
      <text :x="x(64) + 16" :y="y(roof(64)) + 28" class="dg-mono">64</text>
    </g>

    <!-- prefill -->
    <g v-click="2">
      <circle :cx="x(1200)" :cy="y(PEAK)" r="9" class="dg-box dg-amber" style="stroke-width: 3" />
      <text :x="x(1200)" :y="y(PEAK) - 18" text-anchor="middle" class="dg-mono">1,200</text>
    </g>

    <!-- reading guide, right column -->
    <text x="660" y="40" class="dg-title">FLOP per byte ≈ tokens per weight read</text>
    <text x="660" y="68" class="dg-text-muted">2 FLOP per weight per token ÷ 2 bytes per weight (BF16)</text>

    <g v-click="1">
      <circle cx="672" cy="130" r="9" class="dg-box dg-violet" style="stroke-width: 3" />
      <text x="696" y="124" class="dg-text">Decode, 1 or 64 sequences</text>
      <text x="696" y="150" class="dg-text-muted">1 and 64 FLOP/B: far left of the ridge</text>
      <text x="696" y="174" class="dg-text-muted">The memory sets the speed.</text>
    </g>

    <g v-click="2">
      <circle cx="672" cy="238" r="9" class="dg-box dg-amber" style="stroke-width: 3" />
      <text x="696" y="232" class="dg-text">Prefill, a 1,200-token prompt</text>
      <text x="696" y="258" class="dg-text-muted">about 1,200 FLOP/B: right of the ridge</text>
      <text x="696" y="282" class="dg-text-muted">The math units set the speed.</text>
    </g>

    <text x="660" y="340" class="dg-text-muted">roof = min(504 TFLOPS dense BF16, 1,597 GB/s × intensity)</text>
    <text x="660" y="364" class="dg-text-muted">ridge = 503.8 TFLOPS ÷ 1,597 GB/s ≈ 315 FLOP/B</text>
    <text x="660" y="404" class="dg-text-muted">Ceilings from datasheet peaks (derived), not</text>
    <text x="660" y="428" class="dg-text-muted">measurements. A real kernel sits below the roof.</text>
  </DiagramFrame>
</template>
