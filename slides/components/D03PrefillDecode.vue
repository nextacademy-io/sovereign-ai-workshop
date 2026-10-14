<script setup lang="ts">
// D03: the two phases of one request.
// Click 1: prefill pushes every prompt token through the model in ONE pass and fills the KV cache.
// Click 2: decode repeats one step per output token; the new token becomes the next input.
// Click 3: where the user's metrics sit on this picture (TTFT before the first token, ITL between tokens).
import DiagramFrame from './DiagramFrame.vue'

const prompt = ['Explain', 'the', 'KV', 'cache', '…']
const promptY = (i: number) => 80 + i * 50
const rows = [
  { y: 80, from: 'token 1', to: 'token 2' },
  { y: 180, from: 'token 2', to: 'token 3' },
  { y: 280, from: 'token 3', to: 'token 4' },
]
</script>

<template>
  <DiagramFrame label="Prefill processes the whole prompt in one parallel pass; decode produces one token per step">
    <!-- panel headers (always visible) -->
    <text x="0" y="30" class="dg-title">Prefill</text>
    <text x="104" y="30" class="dg-text-muted">all prompt tokens in one pass</text>
    <text x="520" y="30" class="dg-title">Decode</text>
    <text x="618" y="30" class="dg-text-muted">one token per step, repeated</text>

    <!-- prefill -->
    <g v-click="1">
      <g v-for="(t, i) in prompt" :key="t + i">
        <rect x="0" :y="promptY(i)" width="110" height="38" rx="8" class="dg-box dg-teal" />
        <text x="55" :y="promptY(i) + 25" text-anchor="middle" class="dg-mono">{{ t }}</text>
        <path :d="`M110 ${promptY(i) + 19} H158`" class="dg-line" marker-end="url(#ki-arrow)" />
      </g>
      <rect x="160" y="80" width="130" height="238" rx="10" class="dg-box" />
      <text x="225" y="190" text-anchor="middle" class="dg-title">Model</text>
      <text x="225" y="216" text-anchor="middle" class="dg-text-muted">one pass</text>

      <path d="M290 130 H338" class="dg-line" marker-end="url(#ki-arrow-violet)" />
      <rect x="340" y="100" width="130" height="60" rx="8" class="dg-box dg-violet" />
      <text x="405" y="126" text-anchor="middle" class="dg-text">KV cache</text>
      <text x="405" y="148" text-anchor="middle" class="dg-text-muted">filled</text>

      <path d="M290 250 H338" class="dg-line" marker-end="url(#ki-arrow)" />
      <rect x="340" y="220" width="130" height="60" rx="8" class="dg-box dg-green" />
      <text x="405" y="246" text-anchor="middle" class="dg-text">token 1</text>
      <text x="405" y="268" text-anchor="middle" class="dg-text-muted">first output</text>

      <text x="0" y="352" class="dg-text">1,200 prompt tokens at once:</text>
      <text x="0" y="378" class="dg-text-muted">the weights are read once and used for all of them</text>
    </g>

    <!-- decode -->
    <g v-click="2">
      <path d="M470 250 H495 V99 H518" class="dg-line" marker-end="url(#ki-arrow)" />
      <g v-for="(r, i) in rows" :key="r.from">
        <rect x="520" :y="r.y" width="100" height="38" rx="8" class="dg-box dg-green" />
        <text x="570" :y="r.y + 25" text-anchor="middle" class="dg-mono">{{ r.from }}</text>
        <path :d="`M620 ${r.y + 19} H658`" class="dg-line" marker-end="url(#ki-arrow)" />
        <rect x="660" :y="r.y - 6" width="230" height="50" rx="8" class="dg-box" />
        <text x="775" :y="r.y + 15" text-anchor="middle" class="dg-text">decode step</text>
        <text x="775" :y="r.y + 35" text-anchor="middle" class="dg-text-muted">reads weights + KV cache</text>
        <path :d="`M890 ${r.y + 19} H928`" class="dg-line" marker-end="url(#ki-arrow)" />
        <rect x="930" :y="r.y" width="100" height="38" rx="8" class="dg-box dg-green" />
        <text x="980" :y="r.y + 25" text-anchor="middle" class="dg-mono">{{ r.to }}</text>
        <path v-if="i < rows.length - 1" :d="`M980 ${r.y + 38} V${r.y + 69} H570 V${r.y + 99}`" class="dg-line" marker-end="url(#ki-arrow)" />
      </g>
      <text x="520" y="352" class="dg-text">The new token becomes the next input.</text>
      <text x="520" y="378" class="dg-text-muted">Repeated once per output token: 180 in our workload</text>
    </g>

    <!-- user metrics -->
    <g v-click="3">
      <path d="M0 400 V410 H470 V400" class="dg-line" style="stroke: var(--ki-runtime)" />
      <text x="235" y="436" text-anchor="middle" class="dg-text">TTFT: waiting + prefill, up to token 1</text>
      <path d="M520 400 V410 H1136 V400" class="dg-line" style="stroke: var(--ki-runtime)" />
      <text x="828" y="436" text-anchor="middle" class="dg-text">ITL: the gap between two tokens (one step)</text>
    </g>
  </DiagramFrame>
</template>
