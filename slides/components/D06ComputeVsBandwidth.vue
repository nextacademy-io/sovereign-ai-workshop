<script setup lang="ts">
// D06: the same model, the same card, two phases. Each phase needs a minimum time for the arithmetic and a
// minimum time to move the weights; the longer of the two is what limits it. Bars share one scale (11 px per ms).
// Inputs (all documented in the repository): 8.2 B parameters and 16.38 GB of BF16 weights (config/models.yaml),
// 1,597 GB/s (datasheet), about 504 TFLOPS dense BF16 (derived, docs/RESEARCH.md 6.14), 2 FLOP per parameter per token.
// Math time   = 2 x 8.2e9 x tokens / 503.8e12 FLOP/s     prefill (1,200 tokens): 39 ms     decode (1 token): 0.03 ms
// Memory time = 16.38e9 B / 1597e9 B/s                   10.3 ms in both phases (the weights are read once per pass)
// Click 1: prefill. Click 2: decode. Click 3: the verdict of each.
import DiagramFrame from './DiagramFrame.vue'

const PX_PER_MS = 11
const px = (ms: number) => Math.max(3, ms * PX_PER_MS)
const prefill = { math: 39, mem: 10.3 }
const decode = { math: 0.03, mem: 10.3 }
</script>

<template>
  <DiagramFrame label="Prefill is limited by arithmetic, decode by reading the weights: minimum time for math and for memory in each phase">
    <!-- prefill panel -->
    <g v-click="1">
      <text x="0" y="30" class="dg-title">Prefill: 1,200 tokens in one pass</text>

      <text x="0" y="78" class="dg-text">Math</text>
      <text x="64" y="78" class="dg-text-muted">2 × 8.2 B × 1,200 ÷ 504 TFLOPS</text>
      <rect x="0" y="90" :width="px(prefill.math)" height="36" rx="6" class="dg-box dg-amber" />
      <text :x="px(prefill.math) + 12" y="115" class="dg-mono">39 ms</text>

      <text x="0" y="170" class="dg-text">Memory</text>
      <text x="102" y="170" class="dg-text-muted">16.38 GB ÷ 1,597 GB/s</text>
      <rect x="0" y="182" :width="px(prefill.mem)" height="36" rx="6" class="dg-box dg-violet" />
      <text :x="px(prefill.mem) + 12" y="207" class="dg-mono">10.3 ms</text>
    </g>

    <!-- decode panel -->
    <g v-click="2">
      <text x="596" y="30" class="dg-title">Decode: 1 token per step</text>

      <text x="596" y="78" class="dg-text">Math</text>
      <text x="660" y="78" class="dg-text-muted">2 × 8.2 B × 1 ÷ 504 TFLOPS</text>
      <rect x="596" y="90" :width="px(decode.math)" height="36" rx="3" class="dg-box dg-amber" />
      <text :x="596 + px(decode.math) + 12" y="115" class="dg-mono">0.03 ms</text>

      <text x="596" y="170" class="dg-text">Memory</text>
      <text x="698" y="170" class="dg-text-muted">16.38 GB ÷ 1,597 GB/s</text>
      <rect x="596" y="182" :width="px(decode.mem)" height="36" rx="6" class="dg-box dg-violet" />
      <text :x="596 + px(decode.mem) + 12" y="207" class="dg-mono">10.3 ms</text>
    </g>

    <!-- verdicts -->
    <g v-click="3">
      <rect x="0" y="258" width="540" height="112" rx="10" class="dg-box dg-amber" />
      <text x="20" y="292" class="dg-title">The math bar is longer</text>
      <text x="20" y="322" class="dg-text">Compute-bound: the memory has slack.</text>
      <text x="20" y="350" class="dg-text-muted">Every weight read serves 1,200 tokens.</text>

      <rect x="596" y="258" width="540" height="112" rx="10" class="dg-box dg-violet" />
      <text x="616" y="292" class="dg-title">The memory bar is longer</text>
      <text x="616" y="322" class="dg-text">Bandwidth-bound: the math units wait.</text>
      <text x="616" y="350" class="dg-text-muted">Every weight read serves 1 token.</text>
    </g>

    <text x="0" y="414" class="dg-text-muted">Lower bounds from datasheet peaks (BF16 dense, derived), drawn to one scale. They are not measurements.</text>
    <text x="0" y="438" class="dg-text-muted">The KV cache read and the attention math are left out; they matter at long context.</text>
  </DiagramFrame>
</template>
