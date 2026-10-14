<script setup lang="ts">
// layout: default — a heading and free content. Layer and topic come from the section divider.
//   heading?: string
//   kicker?: string    overrides the topic shown above the heading
import { useLayer, useTopic } from '../composables/inherit'

defineProps<{ heading?: string; kicker?: string }>()
const layer = useLayer()
const topic = useTopic()
</script>

<template>
  <div class="slidev-layout default">
    <div class="ki-slide" :data-layer="layer">
      <div v-if="kicker || topic" class="ki-kicker">{{ kicker ?? topic }}</div>
      <h1 v-if="heading">{{ heading }}</h1>
      <div class="ki-grow body"><slot /></div>
    </div>
  </div>
</template>

<style scoped>
.body {
  display: flex;
  flex-direction: column;
}
</style>
