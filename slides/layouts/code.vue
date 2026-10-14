<script setup lang="ts">
// layout: code — a code or output block is the content. A file caption sits above it.
//   heading?: string
//   file?: path shown as a caption (relative to the repository root)
import { useLayer, useTopic } from '../composables/inherit'

defineProps<{ heading?: string; file?: string; kicker?: string }>()
const layer = useLayer()
const topic = useTopic()
</script>

<template>
  <div class="slidev-layout code">
    <div class="ki-slide" :data-layer="layer">
      <div v-if="kicker || topic" class="ki-kicker">{{ kicker ?? topic }}</div>
      <h1 v-if="heading">{{ heading }}</h1>
      <div v-if="file" class="file ki-mono">{{ file }}</div>
      <div class="ki-grow body"><slot /></div>
    </div>
  </div>
</template>

<style scoped>
.file {
  font-size: var(--ki-text-xs);
  color: var(--ki-fg-muted);
  margin-bottom: 10px;
}
.body :deep(.slidev-code) {
  font-size: var(--slidev-code-font-size);
}
</style>
