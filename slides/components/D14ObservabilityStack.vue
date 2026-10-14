<script setup lang="ts">
// D14: the observability stack. vLLM /metrics and a GPU exporter -> Prometheus -> Grafana -> your browser.
// Start:   the metric path.
// Click 1: the alert path (Prometheus rules -> Alertmanager -> a person). Dashed: the workshop stack has none.
// Click 2: what runs where: workshop pods (plain processes) against the reference compose stack (containers).
import DiagramFrame from './DiagramFrame.vue'
</script>

<template>
  <DiagramFrame label="Observability stack: vLLM metrics and a GPU exporter feed Prometheus and Grafana; the alert path is not part of the workshop stack">
    <!-- sources -->
    <rect x="0" y="26" width="280" height="104" rx="10" class="dg-box dg-teal" />
    <text x="140" y="62" text-anchor="middle" class="dg-title">vLLM</text>
    <text x="140" y="90" text-anchor="middle" class="dg-text-muted">/metrics on port 8000</text>
    <text x="140" y="112" text-anchor="middle" class="dg-text-muted">open: not behind the API key</text>

    <rect x="0" y="150" width="280" height="104" rx="10" class="dg-box dg-teal" />
    <text x="140" y="186" text-anchor="middle" class="dg-title">GPU exporter</text>
    <text x="140" y="214" text-anchor="middle" class="dg-text-muted">NVML, DCGM metric names</text>
    <text x="140" y="236" text-anchor="middle" class="dg-text-muted">power, VRAM, utilisation</text>

    <!-- pipeline -->
    <rect x="380" y="88" width="220" height="104" rx="10" class="dg-box dg-violet" />
    <text x="490" y="124" text-anchor="middle" class="dg-title">Prometheus</text>
    <text x="490" y="152" text-anchor="middle" class="dg-text-muted">pulls every 5 s</text>
    <text x="490" y="174" text-anchor="middle" class="dg-text-muted">stores the series</text>

    <rect x="700" y="88" width="220" height="104" rx="10" class="dg-box dg-violet" />
    <text x="810" y="124" text-anchor="middle" class="dg-title">Grafana</text>
    <text x="810" y="152" text-anchor="middle" class="dg-text-muted">18 panels in 3 rows</text>
    <text x="810" y="174" text-anchor="middle" class="dg-text-muted">provisioned from files</text>

    <rect x="1000" y="88" width="134" height="104" rx="10" class="dg-box" />
    <text x="1067" y="124" text-anchor="middle" class="dg-title">Browser</text>
    <text x="1067" y="152" text-anchor="middle" class="dg-mono">ssh -L 3000</text>
    <text x="1067" y="174" text-anchor="middle" class="dg-text-muted">your laptop</text>

    <path d="M284 78 C332 78 332 122 376 122" class="dg-line" marker-end="url(#ki-arrow)" />
    <path d="M284 202 C332 202 332 158 376 158" class="dg-line" marker-end="url(#ki-arrow)" />
    <path d="M604 140 H696" class="dg-line" marker-end="url(#ki-arrow)" />
    <text x="650" y="128" text-anchor="middle" class="dg-text-muted">PromQL</text>
    <path d="M924 140 H996" class="dg-line" marker-end="url(#ki-arrow)" />

    <!-- alert path: not in the workshop stack -->
    <g v-click="1">
      <path d="M490 196 V282" class="dg-line" marker-end="url(#ki-arrow)" />
      <rect x="380" y="288" width="220" height="68" rx="10" class="dg-box dg-violet" stroke-dasharray="7 6" />
      <text x="490" y="318" text-anchor="middle" class="dg-text">Alert rules</text>
      <text x="490" y="342" text-anchor="middle" class="dg-text-muted">queue, KV, errors, SLO</text>
      <path d="M604 322 H696" class="dg-line" marker-end="url(#ki-arrow)" />
      <rect x="700" y="288" width="220" height="68" rx="10" class="dg-box dg-violet" stroke-dasharray="7 6" />
      <text x="810" y="318" text-anchor="middle" class="dg-text">Alertmanager</text>
      <text x="810" y="342" text-anchor="middle" class="dg-text-muted">groups, routes</text>
      <path d="M924 322 H996" class="dg-line" marker-end="url(#ki-arrow)" />
      <rect x="1000" y="288" width="134" height="68" rx="10" class="dg-box" stroke-dasharray="7 6" />
      <text x="1067" y="318" text-anchor="middle" class="dg-text">On-call</text>
      <text x="1067" y="342" text-anchor="middle" class="dg-text-muted">page or chat</text>
      <text x="0" y="318" class="dg-text-muted">Dashed: not in the workshop</text>
      <text x="0" y="340" class="dg-text-muted">stack (no rule files).</text>
    </g>

    <!-- what runs where -->
    <g v-click="2">
      <rect x="0" y="376" width="556" height="80" rx="10" class="dg-box dg-teal" />
      <text x="16" y="402" class="dg-title">Workshop pods</text>
      <text x="16" y="426" class="dg-text-muted">plain processes started by wsmon, bound to 127.0.0.1</text>
      <text x="16" y="446" class="dg-text-muted">GPU metrics from monitoring/gpu-exporter/exporter.py</text>
      <rect x="580" y="376" width="554" height="80" rx="10" class="dg-box dg-violet" />
      <text x="596" y="402" class="dg-title">Reference compose stack</text>
      <text x="596" y="426" class="dg-text-muted">containers from monitoring/docker-compose.yml</text>
      <text x="596" y="446" class="dg-text-muted">GPU metrics from NVIDIA dcgm-exporter (SYS_ADMIN)</text>
    </g>
  </DiagramFrame>
</template>
