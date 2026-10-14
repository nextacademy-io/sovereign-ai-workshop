<script setup lang="ts">
// layout: statement — one claim, large. Use for the sentence participants should remember.
//   kicker?: string
import { useLayer, useTopic } from '../composables/inherit'

defineProps<{ kicker?: string }>()
const layer = useLayer()
const topic = useTopic()
</script>

<template>
  <div class="slidev-layout statement">
    <div class="ki-slide" :data-layer="layer">
      <div v-if="kicker || topic" class="ki-kicker">{{ kicker ?? topic }}</div>
      <div class="ki-grow stmt"><slot /></div>
    </div>
  </div>
</template>

<style scoped>
.stmt {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.stmt :deep(h1) {
  font-size: var(--ki-text-3xl);
  line-height: 1.08;
  max-width: 1050px;
}
.stmt :deep(p) {
  font-size: var(--ki-text-lg);
  color: var(--ki-fg-muted);
  max-width: 900px;
}
</style>
