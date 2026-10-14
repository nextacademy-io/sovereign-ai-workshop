<script setup lang="ts">
// A labelled aside. Prefer the named wrappers (Prediction, Observation, Takeaway, Warning, Consequence).
defineProps<{ kind: 'prediction' | 'observation' | 'takeaway' | 'warning' | 'consequence' | 'trainer'; title?: string }>()
const NAMES = {
  prediction: 'Prediction',
  observation: 'Observation',
  takeaway: 'Takeaway',
  warning: 'Watch out',
  consequence: 'Production consequence',
  trainer: 'Trainer',
}
</script>

<template>
  <aside class="callout" :class="kind">
    <div class="tag">{{ title ?? NAMES[kind] }}</div>
    <div class="content"><slot /></div>
  </aside>
</template>

<style scoped>
.callout {
  --c: var(--ki-info);
  padding: 12px 20px 14px;
  border-radius: var(--ki-radius);
  border: 1px solid color-mix(in srgb, var(--c) 40%, transparent);
  background: color-mix(in srgb, var(--c) 9%, var(--ki-bg));
  margin: 0 0 14px;
}
.callout.prediction {
  --c: var(--ki-info);
}
.callout.observation {
  --c: var(--ki-runtime);
}
.callout.takeaway {
  --c: var(--ki-good);
}
.callout.warning {
  --c: var(--ki-bad);
}
.callout.consequence {
  --c: var(--ki-infrastructure);
}
.callout.trainer {
  --c: var(--ki-fg-muted);
}
.tag {
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c);
}
.content {
  font-size: var(--ki-text-base);
}
.content :deep(p) {
  margin: 0 0 6px;
}
.content :deep(> :last-child) {
  margin-bottom: 0;
}
</style>
