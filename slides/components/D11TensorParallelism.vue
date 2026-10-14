<script setup lang="ts">
// D11: tensor parallelism next to replicas, on two GPUs.
// Left: one request, one copy of the model, every layer split across both GPUs. After the attention part and after the
//   MLP part of each layer the two GPUs add their partial results (an all-reduce): 2 × 36 layers = 72 per decode step.
// Right: two copies of the model behind a load balancer. Each request runs on one GPU; nothing is exchanged between the GPUs.
// Click 1: tensor parallelism. Click 2: replicas.
import DiagramFrame from './DiagramFrame.vue'

const gpus = [
  { name: 'GPU 0', x: 0 },
  { name: 'GPU 1', x: 390 },
]
const replicas = [
  { name: 'GPU 0', y: 70 },
  { name: 'GPU 1', y: 230 },
]
</script>

<template>
  <DiagramFrame label="Tensor parallelism splits every layer across two GPUs with an all-reduce; replicas run two full copies behind a load balancer">
    <!-- tensor parallel -->
    <g v-click="1">
      <text x="0" y="30" class="dg-title">Tensor parallel, two GPUs</text>
      <text x="0" y="52" class="dg-text-muted">one copy of the model, every layer split in two</text>
      <g v-for="g in gpus" :key="g.name">
        <rect :x="g.x" y="70" width="250" height="296" rx="10" class="dg-box dg-teal" />
        <text :x="g.x + 125" y="96" text-anchor="middle" class="dg-title">{{ g.name }}</text>
        <rect :x="g.x + 20" y="110" width="210" height="52" rx="6" class="dg-box dg-teal" />
        <text :x="g.x + 125" y="133" text-anchor="middle" class="dg-text">attention</text>
        <text :x="g.x + 125" y="153" text-anchor="middle" class="dg-text-muted">half of the heads</text>
        <rect :x="g.x + 20" y="172" width="210" height="40" rx="6" class="dg-box dg-violet" />
        <text :x="g.x + 125" y="198" text-anchor="middle" class="dg-text-muted">sum with the other GPU</text>
        <rect :x="g.x + 20" y="224" width="210" height="52" rx="6" class="dg-box dg-teal" />
        <text :x="g.x + 125" y="247" text-anchor="middle" class="dg-text">MLP</text>
        <text :x="g.x + 125" y="267" text-anchor="middle" class="dg-text-muted">half of each matrix</text>
        <rect :x="g.x + 20" y="286" width="210" height="40" rx="6" class="dg-box dg-violet" />
        <text :x="g.x + 125" y="312" text-anchor="middle" class="dg-text-muted">sum with the other GPU</text>
        <text :x="g.x + 125" y="352" text-anchor="middle" class="dg-text-muted">half the weights, 4 KV heads</text>
      </g>
      <path d="M254 192 H386" class="dg-line" style="stroke: var(--ki-infrastructure)" marker-start="url(#ki-arrow-violet)" marker-end="url(#ki-arrow-violet)" />
      <path d="M254 306 H386" class="dg-line" style="stroke: var(--ki-infrastructure)" marker-start="url(#ki-arrow-violet)" marker-end="url(#ki-arrow-violet)" />
      <text x="320" y="182" text-anchor="middle" class="dg-text-muted">all-reduce</text>
      <text x="320" y="296" text-anchor="middle" class="dg-text-muted">all-reduce</text>
      <text x="0" y="398" class="dg-text">× 36 layers: 72 all-reduces per decode step</text>
      <text x="0" y="426" class="dg-text-muted">link between the cards: PCIe Gen5 x16, 64 GB/s per direction, no NVLink</text>
    </g>

    <!-- replicas -->
    <g v-click="2">
      <text x="696" y="30" class="dg-title">Two replicas</text>
      <text x="696" y="52" class="dg-text-muted">two copies of the model, one request on one GPU</text>
      <rect x="696" y="150" width="110" height="100" rx="10" class="dg-box dg-violet" />
      <text x="751" y="196" text-anchor="middle" class="dg-title">Load</text>
      <text x="751" y="222" text-anchor="middle" class="dg-title">balancer</text>
      <g v-for="(r, i) in replicas" :key="r.name">
        <rect x="860" :y="r.y" width="276" height="130" rx="10" class="dg-box dg-teal" />
        <text x="880" :y="r.y + 28" class="dg-title">{{ r.name }}: a full copy</text>
        <rect x="880" :y="r.y + 44" width="116" height="44" rx="6" class="dg-box dg-teal" />
        <text x="938" :y="r.y + 72" text-anchor="middle" class="dg-text-muted">weights</text>
        <rect x="1004" :y="r.y + 44" width="116" height="44" rx="6" class="dg-box dg-amber" />
        <text x="1062" :y="r.y + 72" text-anchor="middle" class="dg-text-muted">own KV cache</text>
        <text x="880" :y="r.y + 114" class="dg-text-muted">a whole request runs here</text>
        <path :d="`M810 ${i ? 215 : 185} C836 ${i ? 215 : 185} 836 ${r.y + 65} 856 ${r.y + 65}`" class="dg-line" marker-end="url(#ki-arrow)" />
      </g>
      <text x="998" y="220" text-anchor="middle" class="dg-text-muted">no traffic between the GPUs</text>
      <text x="696" y="398" class="dg-text">each request stays on one GPU</text>
      <text x="696" y="426" class="dg-text-muted">twice the requests in flight, at best</text>
    </g>
  </DiagramFrame>
</template>
