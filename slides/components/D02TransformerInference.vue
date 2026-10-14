<script setup lang="ts">
// D02: the transformer inference loop. Tokens in, layers, scores for the next token, sampling, append, repeat.
// Click 1: one forward pass gives a score for every possible next token.
// Click 2: the sampler turns the scores into ONE token.
// Click 3: the token is appended and the whole pass runs again.
import DiagramFrame from './DiagramFrame.vue'

// Bar heights only show that every vocabulary entry gets a score and that a few dominate.
// They are not model output.
const bars = [22, 64, 30, 104, 46, 16, 74, 28]
const BAR_X = (i: number) => 612 + i * 29
</script>

<template>
  <DiagramFrame label="Transformer inference loop: tokens in, layers, scores for the next token, sampling, append, repeat">
    <!-- tokens so far (always visible) -->
    <text x="0" y="28" class="dg-text-muted">Tokens so far</text>
    <rect x="0" y="40" width="180" height="190" rx="10" class="dg-box" />
    <g v-for="(t, i) in ['t1', 't2', 't3', 't4']" :key="t">
      <rect :x="12 + (i % 2) * 84" :y="52 + Math.floor(i / 2) * 50" width="72" height="40" rx="8" class="dg-box dg-teal" />
      <text :x="48 + (i % 2) * 84" :y="78 + Math.floor(i / 2) * 50" text-anchor="middle" class="dg-mono">{{ t }}</text>
    </g>
    <text x="90" y="220" text-anchor="middle" class="dg-text-muted">prompt, then output</text>

    <!-- 1: one forward pass -->
    <g v-click="1">
      <path d="M182 135 H238" class="dg-line" marker-end="url(#ki-arrow)" />
      <rect x="240" y="40" width="290" height="190" rx="10" class="dg-box dg-teal" />
      <text x="385" y="72" text-anchor="middle" class="dg-title">Transformer layers</text>
      <rect x="260" y="88" width="250" height="34" rx="6" class="dg-box" />
      <text x="385" y="111" text-anchor="middle" class="dg-text-muted">Layer 1</text>
      <text x="385" y="148" text-anchor="middle" class="dg-title">⋮</text>
      <rect x="260" y="156" width="250" height="34" rx="6" class="dg-box" />
      <text x="385" y="179" text-anchor="middle" class="dg-text-muted">Layer 36</text>
      <text x="385" y="214" text-anchor="middle" class="dg-text-muted">attention + feed-forward</text>

      <path d="M532 135 H588" class="dg-line" marker-end="url(#ki-arrow)" />
      <rect x="590" y="40" width="262" height="190" rx="10" class="dg-box dg-teal" />
      <text x="721" y="72" text-anchor="middle" class="dg-text">Next-token scores</text>
      <rect v-for="(h, i) in bars" :key="i" :x="BAR_X(i)" :y="196 - h" width="22" :height="h" rx="3" class="dg-box" :class="i === 3 ? 'dg-green' : ''" />
      <text x="721" y="219" text-anchor="middle" class="dg-text-muted">one score per vocabulary entry</text>
      <text x="0" y="388" class="dg-text"><tspan class="num">1</tspan><tspan x="28">One forward pass: every layer, then a score for every possible next token</tspan></text>
    </g>

    <!-- 2: sampling -->
    <g v-click="2">
      <path d="M854 135 H898" class="dg-line" marker-end="url(#ki-arrow)" />
      <rect x="900" y="40" width="236" height="190" rx="10" class="dg-box" />
      <text x="1018" y="72" text-anchor="middle" class="dg-title">Sampling</text>
      <text x="1018" y="108" text-anchor="middle" class="dg-mono">temperature</text>
      <text x="1018" y="134" text-anchor="middle" class="dg-mono">top-p · top-k</text>
      <rect x="944" y="162" width="148" height="40" rx="8" class="dg-box dg-green" />
      <text x="1018" y="188" text-anchor="middle" class="dg-mono">one token</text>
      <text x="0" y="418" class="dg-text"><tspan class="num">2</tspan><tspan x="28">The sampler turns the scores into one token; temperature and top-p set how adventurous</tspan></text>
    </g>

    <!-- 3: append and repeat -->
    <g v-click="3">
      <rect x="12" y="152" width="72" height="40" rx="8" class="dg-box dg-green new-token" />
      <text x="48" y="178" text-anchor="middle" class="dg-mono">t5</text>
      <path d="M1018 232 V330 H90 V234" class="dg-line loop" marker-end="url(#ki-arrow)" />
      <text x="350" y="320" class="dg-text">append the new token, run the whole pass again</text>
      <text x="350" y="356" class="dg-text-muted">first pass over the prompt: prefill · every later pass: decode</text>
      <text x="0" y="448" class="dg-text"><tspan class="num">3</tspan><tspan x="28">Repeat until the end-of-sequence token or the token limit</tspan></text>
    </g>
  </DiagramFrame>
</template>

<style scoped>
.loop {
  stroke: var(--ki-good);
}
.new-token {
  stroke-dasharray: 5 4;
}
.num {
  fill: var(--ki-good);
  font-weight: 700;
}
</style>
