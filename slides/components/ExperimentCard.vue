<script setup lang="ts">
// The frame of one experiment: what we change, what we hold, what we watch.
//   <ExperimentCard name="prefix-cache" variable="prefix caching on / off" :profiles='["baseline","no-prefix-cache"]'
//     workload="shared-prefix" :metrics='["TTFT", "hit rate"]' />
defineProps<{ name: string; variable: string; profiles?: string[]; workload?: string; metrics?: string[]; hypothesis?: string }>()
</script>

<template>
  <div class="xp">
    <div class="row"><span class="k">Experiment</span><code>experiments/{{ name }}</code></div>
    <div v-if="hypothesis" class="row"><span class="k">Hypothesis</span><span>{{ hypothesis }}</span></div>
    <div class="row"><span class="k">One variable</span><span>{{ variable }}</span></div>
    <div v-if="profiles?.length" class="row">
      <span class="k">Profiles</span>
      <span class="chips"><code v-for="p in profiles" :key="p">{{ p }}</code></span>
    </div>
    <div v-if="workload" class="row"><span class="k">Workload</span><code>{{ workload }}</code></div>
    <div v-if="metrics?.length" class="row"><span class="k">We watch</span><span>{{ metrics.join(' · ') }}</span></div>
  </div>
</template>

<style scoped>
.xp {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px 22px;
  border-radius: var(--ki-radius);
  border: 1px solid var(--ki-border);
  border-left: 4px solid var(--ki-layer, var(--ki-runtime));
  background: var(--ki-bg-raised);
}
.row {
  display: flex;
  gap: 18px;
  align-items: baseline;
}
.k {
  flex: 0 0 130px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ki-fg-muted);
}
.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
