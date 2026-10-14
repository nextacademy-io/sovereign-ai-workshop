<script setup lang="ts">
// layout: experiment — a step of the teaching rhythm, with the rhythm bar showing where we are.
//   heading: string
//   step: concept | system | experiment | prediction | measurement | explanation | consequence
//   experiment?: string   directory name under experiments/ (shown as a pill)
import type { RhythmKey } from '../composables/stack'
import { useLayer } from '../composables/inherit'
import RhythmBar from '../components/RhythmBar.vue'

defineProps<{ heading?: string; step?: RhythmKey; experiment?: string }>()
const layer = useLayer()
</script>

<template>
  <div class="slidev-layout experiment">
    <div class="ki-slide" :data-layer="layer">
      <RhythmBar :current="step" />
      <div class="head">
        <h1 v-if="heading">{{ heading }}</h1>
        <span v-if="experiment" class="ki-pill ki-mono">experiments/{{ experiment }}</span>
      </div>
      <div class="ki-grow body"><slot /></div>
    </div>
  </div>
</template>

<style scoped>
.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}
.body {
  display: flex;
  flex-direction: column;
}
</style>
