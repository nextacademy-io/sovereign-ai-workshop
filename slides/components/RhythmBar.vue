<script setup lang="ts">
// CONCEPT → SYSTEM → EXPERIMENT → PREDICTION → MEASUREMENT → EXPLANATION → PRODUCTION CONSEQUENCE
import type { RhythmKey } from '../composables/stack'
import { RHYTHM } from '../composables/stack'

defineProps<{ current?: RhythmKey }>()
</script>

<template>
  <ol class="rhythm" aria-label="Teaching rhythm">
    <li v-for="s in RHYTHM" :key="s.key" :class="{ now: s.key === current }">{{ s.label }}</li>
  </ol>
</template>

<style scoped>
.rhythm {
  display: flex;
  gap: 6px;
  list-style: none;
  padding: 0;
  margin: 0 0 22px;
}
.rhythm li {
  flex: 1;
  padding: 5px 4px 6px;
  text-align: center;
  font-size: 13px;
  line-height: 1.15;
  font-weight: 650;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border-top: 3px solid var(--ki-border-strong);
  color: var(--ki-fg-dim);
  margin: 0;
}
.rhythm li::before {
  display: none;
}
.rhythm li.now {
  border-top-color: var(--ki-layer);
  color: var(--ki-layer);
}
</style>
