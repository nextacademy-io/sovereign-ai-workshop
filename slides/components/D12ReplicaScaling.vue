<script setup lang="ts">
// D12: two ways to put more GPUs behind one endpoint.
// Left:  replicas. A load balancer in front of N copies of the model, each with its own GPU and KV cache.
// Right: tensor parallelism. One model split across GPUs, which talk to each other in every layer.
// Click 1: the replica side. Click 2: the tensor-parallel side and the contrast.
import DiagramFrame from './DiagramFrame.vue'

const rows = [0, 1, 2]
const rowY = (i: number) => 56 + i * 110
</script>

<template>
  <DiagramFrame label="Replicas against tensor parallelism: N copies of the model behind a load balancer, or one model split across GPUs">
    <text x="0" y="30" class="dg-title">Replicas (data parallel)</text>
    <text x="676" y="30" class="dg-title">Tensor parallel, 2 GPUs</text>

    <!-- replicas -->
    <g v-click="1">
      <rect x="0" y="160" width="130" height="100" rx="10" class="dg-box dg-violet" />
      <text x="65" y="204" text-anchor="middle" class="dg-title">Load</text>
      <text x="65" y="230" text-anchor="middle" class="dg-title">balancer</text>
      <g v-for="i in rows" :key="i">
        <rect x="190" :y="rowY(i)" width="430" height="92" rx="10" class="dg-box dg-teal" />
        <text x="206" :y="rowY(i) + 28" class="dg-text">Replica {{ i + 1 }}</text>
        <rect x="206" :y="rowY(i) + 40" width="120" height="40" rx="6" class="dg-box dg-teal" />
        <text x="266" :y="rowY(i) + 66" text-anchor="middle" class="dg-text-muted">weights</text>
        <rect x="340" :y="rowY(i) + 40" width="140" height="40" rx="6" class="dg-box" />
        <text x="410" :y="rowY(i) + 66" text-anchor="middle" class="dg-text-muted">own KV cache</text>
        <rect x="494" :y="rowY(i) + 40" width="110" height="40" rx="6" class="dg-box dg-teal" />
        <text x="549" :y="rowY(i) + 66" text-anchor="middle" class="dg-text-muted">own GPU</text>
        <path :d="`M134 210 C160 210 160 ${rowY(i) + 46} 186 ${rowY(i) + 46}`" class="dg-line" marker-end="url(#ki-arrow)" />
      </g>
      <text x="0" y="410" class="dg-text">More requests at once.</text>
      <text x="0" y="438" class="dg-text">One request is not faster.</text>
    </g>

    <!-- tensor parallel -->
    <g v-click="2">
      <rect x="676" y="56" width="458" height="312" rx="10" class="dg-box dg-teal" />
      <text x="692" y="86" class="dg-text">One server, one copy of the model</text>
      <rect x="696" y="110" width="180" height="200" rx="8" class="dg-box dg-teal" />
      <text x="786" y="142" text-anchor="middle" class="dg-title">GPU 0</text>
      <text x="786" y="180" text-anchor="middle" class="dg-text-muted">half of every layer</text>
      <text x="786" y="206" text-anchor="middle" class="dg-text-muted">its share of the</text>
      <text x="786" y="228" text-anchor="middle" class="dg-text-muted">KV cache</text>
      <rect x="936" y="110" width="180" height="200" rx="8" class="dg-box dg-teal" />
      <text x="1026" y="142" text-anchor="middle" class="dg-title">GPU 1</text>
      <text x="1026" y="180" text-anchor="middle" class="dg-text-muted">half of every layer</text>
      <text x="1026" y="206" text-anchor="middle" class="dg-text-muted">its share of the</text>
      <text x="1026" y="228" text-anchor="middle" class="dg-text-muted">KV cache</text>
      <path d="M880 210 H932" class="dg-line" marker-start="url(#ki-arrow)" marker-end="url(#ki-arrow)" />
      <text x="906" y="334" text-anchor="middle" class="dg-text-muted">all-reduce in every layer, over PCIe</text>
      <text x="906" y="356" text-anchor="middle" class="dg-text-muted">(no NVLink on this card)</text>
      <text x="676" y="410" class="dg-text">A model larger than one GPU fits.</text>
      <text x="676" y="438" class="dg-text">Latency gain depends on the link.</text>
    </g>
  </DiagramFrame>
</template>
