<script setup lang="ts">
// D19: one streamed request on a time axis, with the metrics of the harness drawn on it.
// Always visible: the request itself (queue, prefill, then one text chunk per decode step).
// Click 1: TTFT and end-to-end latency, both from the same clock start.
// Click 2: ITL, the gap between two chunks.
// Click 3: TPOT and tokens per second per request, which exclude the wait for the first token.
import DiagramFrame from './DiagramFrame.vue'

const X0 = 60 // request clock starts (scheduled arrival or send time)
const XQ = 180 // queue ends, prefill starts
const XF = 400 // prefill ends, first text arrives
const XE = 1076 // last token
const PITCH = 46
const BOX = 38
const tokens = Array.from({ length: 12 }, (_, i) => ({ n: i + 1, x: XF + i * PITCH }))
const center = (n: number) => XF + (n - 1) * PITCH + BOX / 2
</script>

<template>
  <DiagramFrame label="One streamed request: queue, prefill, decode steps, with TTFT, ITL, TPOT and end-to-end latency marked on the time axis">
    <g transform="translate(0 -34)">
    <!-- guides from the time marks down to their labels -->
    <path :d="`M${X0} 214 V252`" class="dg-line" stroke-dasharray="4 5" />
    <path :d="`M${XF} 214 V252`" class="dg-line" stroke-dasharray="4 5" />
    <path :d="`M${XE} 214 V252`" class="dg-line" stroke-dasharray="4 5" />

    <!-- the request (always visible) -->
    <rect :x="X0" y="160" :width="XQ - X0 - 4" height="52" rx="8" class="dg-box" stroke-dasharray="6 4" />
    <text :x="(X0 + XQ) / 2 - 2" y="192" text-anchor="middle" class="dg-text-muted">queue</text>
    <rect :x="XQ" y="160" :width="XF - XQ - 4" height="52" rx="8" class="dg-box dg-teal" />
    <text :x="(XQ + XF) / 2 - 2" y="192" text-anchor="middle" class="dg-text">prefill</text>
    <g v-for="t in tokens" :key="t.n">
      <rect :x="t.x" y="160" :width="BOX" height="52" rx="6" class="dg-box dg-green" />
      <text :x="t.x + BOX / 2" y="192" text-anchor="middle" class="dg-mono">{{ t.n }}</text>
    </g>
    <text x="982" y="194" text-anchor="middle" class="dg-text">…</text>
    <rect :x="XE - BOX" y="160" :width="BOX" height="52" rx="6" class="dg-box dg-green" />
    <text :x="XE - BOX / 2" y="192" text-anchor="middle" class="dg-mono">N</text>

    <text :x="X0" y="244" text-anchor="start" class="dg-mono">t_sched</text>
    <text :x="XF" y="244" text-anchor="middle" class="dg-mono">t_first</text>
    <text :x="XE" y="244" text-anchor="end" class="dg-mono">t_end</text>
    <text x="738" y="244" text-anchor="middle" class="dg-text-muted">decode: one step, one text chunk</text>

    <!-- click 1: TTFT and latency -->
    <g v-click="1">
      <path :d="`M${X0} 158 V84 H${XE} V158`" class="dg-line" style="stroke: var(--ki-runtime)" />
      <text x="568" y="68" text-anchor="middle" class="dg-text">End-to-end latency = t_end − t_sched</text>
      <path :d="`M${X0} 158 V128 H${XF} V158`" class="dg-line" style="stroke: var(--ki-runtime)" />
      <text :x="X0 + 14" y="114" class="dg-text">TTFT = t_first − t_sched</text>
      <text :x="XF + 16" y="114" class="dg-text-muted">queue, then prefill, up to the first text</text>
    </g>

    <!-- click 2: ITL -->
    <g v-click="2">
      <path :d="`M${center(4)} 268 V280 H${center(5)} V268`" class="dg-line" style="stroke: var(--ki-runtime)" />
      <text :x="center(5) + 22" y="290" class="dg-text">ITL: gap between two consecutive text chunks</text>
    </g>

    <!-- click 3: TPOT -->
    <g v-click="3">
      <path :d="`M${XF} 322 V334 H${XE} V322`" class="dg-line" style="stroke: var(--ki-runtime)" />
      <text :x="(XF + XE) / 2" y="364" text-anchor="middle" class="dg-text">TPOT = (latency − TTFT) ÷ (N − 1)</text>
      <text :x="(XF + XE) / 2" y="392" text-anchor="middle" class="dg-text">Output tokens per second per request = 1 ÷ TPOT</text>
    </g>

    </g>

    <text x="0" y="408" class="dg-text-muted">N: output tokens as counted by the server (usage block). The clock starts at the scheduled arrival (open loop) or the send time (closed loop).</text>
  </DiagramFrame>
</template>
