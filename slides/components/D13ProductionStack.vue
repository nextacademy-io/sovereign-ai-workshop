<script setup lang="ts">
// D13: the production inference stack around one request.
// Start:   the request path, CLIENT -> API gateway -> load balancer -> replicas -> GPU pool.
// Click 1: what surrounds it: observability, and the pinned inputs (registry, secrets, storage).
// Click 2: which parts the workshop pods leave out or simplify (dashed outlines).
import DiagramFrame from './DiagramFrame.vue'

const replicaX = (i: number) => 662 + i * 78
</script>

<template>
  <DiagramFrame label="Production inference stack: the request path, what observes it, what it is built from, and what the workshop pods leave out">
    <text x="0" y="18" class="dg-text-muted">REQUEST PATH</text>

    <!-- request path -->
    <rect x="0" y="30" width="130" height="110" rx="10" class="dg-box dg-amber" />
    <text x="65" y="66" text-anchor="middle" class="dg-title">Client</text>
    <text x="65" y="94" text-anchor="middle" class="dg-text-muted">app or SDK</text>
    <text x="65" y="116" text-anchor="middle" class="dg-text-muted">reads a stream</text>

    <rect x="190" y="30" width="170" height="110" rx="10" class="dg-box dg-violet" />
    <text x="275" y="66" text-anchor="middle" class="dg-title">API gateway</text>
    <text x="275" y="94" text-anchor="middle" class="dg-text-muted">TLS, authentication</text>
    <text x="275" y="116" text-anchor="middle" class="dg-text-muted">rate limits</text>

    <rect x="420" y="30" width="170" height="110" rx="10" class="dg-box dg-violet" />
    <text x="505" y="66" text-anchor="middle" class="dg-title">Load balancer</text>
    <text x="505" y="94" text-anchor="middle" class="dg-text-muted">routing, queue limit</text>
    <text x="505" y="116" text-anchor="middle" class="dg-text-muted">health probes</text>

    <rect x="650" y="30" width="250" height="110" rx="10" class="dg-box dg-teal" />
    <text x="775" y="58" text-anchor="middle" class="dg-title">Inference replicas</text>
    <g v-for="i in 3" :key="i">
      <rect :x="replicaX(i - 1) - 0" y="70" width="68" height="34" rx="6" class="dg-box dg-teal" />
      <text :x="replicaX(i - 1) + 34" y="93" text-anchor="middle" class="dg-mono">vLLM</text>
    </g>
    <text x="775" y="128" text-anchor="middle" class="dg-text-muted">own weights and KV cache each</text>

    <rect x="960" y="30" width="174" height="110" rx="10" class="dg-box dg-teal" />
    <text x="1047" y="66" text-anchor="middle" class="dg-title">GPU pool</text>
    <text x="1047" y="94" text-anchor="middle" class="dg-text-muted">one GPU</text>
    <text x="1047" y="116" text-anchor="middle" class="dg-text-muted">per replica</text>

    <path d="M134 85 H186" class="dg-line" marker-end="url(#ki-arrow)" />
    <path d="M364 85 H416" class="dg-line" marker-end="url(#ki-arrow)" />
    <path d="M594 85 H646" class="dg-line" marker-end="url(#ki-arrow)" />
    <path d="M904 85 H956" class="dg-line" marker-end="url(#ki-arrow)" />

    <!-- what surrounds it -->
    <g v-click="1">
      <text x="0" y="204" class="dg-text-muted">OBSERVE</text>
      <text x="596" y="204" class="dg-text-muted">PIN AND PROTECT</text>

      <rect x="0" y="216" width="170" height="76" rx="10" class="dg-box dg-violet" />
      <text x="85" y="248" text-anchor="middle" class="dg-text">Metrics</text>
      <text x="85" y="272" text-anchor="middle" class="dg-text-muted">Prometheus</text>
      <rect x="185" y="216" width="170" height="76" rx="10" class="dg-box dg-violet" />
      <text x="270" y="248" text-anchor="middle" class="dg-text">Logs</text>
      <text x="270" y="272" text-anchor="middle" class="dg-text-muted">engine, gateway</text>
      <rect x="370" y="216" width="170" height="76" rx="10" class="dg-box dg-violet" />
      <text x="455" y="248" text-anchor="middle" class="dg-text">Traces</text>
      <text x="455" y="272" text-anchor="middle" class="dg-text-muted">one request, all hops</text>

      <rect x="596" y="216" width="170" height="76" rx="10" class="dg-box dg-violet" />
      <text x="681" y="248" text-anchor="middle" class="dg-text">Model registry</text>
      <text x="681" y="272" text-anchor="middle" class="dg-text-muted">pinned revisions</text>
      <rect x="781" y="216" width="170" height="76" rx="10" class="dg-box dg-violet" />
      <text x="866" y="248" text-anchor="middle" class="dg-text">Secrets</text>
      <text x="866" y="272" text-anchor="middle" class="dg-text-muted">keys per client</text>
      <rect x="966" y="216" width="168" height="76" rx="10" class="dg-box dg-violet" />
      <text x="1050" y="248" text-anchor="middle" class="dg-text">Storage</text>
      <text x="1050" y="272" text-anchor="middle" class="dg-text-muted">weights, caches</text>

      <path d="M270 146 V210" class="dg-line" marker-end="url(#ki-arrow)" />
      <text x="284" y="184" class="dg-text-muted">every hop emits</text>
      <path d="M866 210 V146" class="dg-line" marker-end="url(#ki-arrow)" />
      <text x="880" y="184" class="dg-text-muted">inputs at start</text>
    </g>

    <!-- what the workshop pods leave out -->
    <g v-click="2">
      <rect x="186" y="26" width="178" height="118" rx="12" class="dg-line" stroke-dasharray="7 6" />
      <rect x="416" y="26" width="178" height="118" rx="12" class="dg-line" stroke-dasharray="7 6" />
      <rect x="736" y="66" width="156" height="42" rx="8" class="dg-line" stroke-dasharray="7 6" />
      <rect x="366" y="212" width="178" height="84" rx="12" class="dg-line" stroke-dasharray="7 6" />
      <rect x="592" y="212" width="178" height="84" rx="12" class="dg-line" stroke-dasharray="7 6" />

      <rect x="0" y="334" width="40" height="24" rx="6" class="dg-box dg-violet" />
      <text x="54" y="352" class="dg-text-muted">on the pods, in a simpler form</text>
      <rect x="400" y="334" width="40" height="24" rx="6" class="dg-line" stroke-dasharray="7 6" />
      <text x="454" y="352" class="dg-text-muted">not on the pods</text>
      <text x="0" y="404" class="dg-text">Workshop pods: one shared replica on one GPU per group.</text>
      <text x="0" y="432" class="dg-text">No gateway, no balancer: an SSH tunnel and one shared key.</text>
    </g>
  </DiagramFrame>
</template>
