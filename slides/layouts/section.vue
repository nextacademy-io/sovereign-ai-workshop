<script setup lang="ts">
// layout: section — divider at the start of every block. Declares the block's layer and day;
// the slides after it inherit both (see composables/inherit.ts).
//   heading: string          block title
//   day?: number             only on the first block of a day
//   time?: string            relative start, e.g. "09:30"
//   minutes?: number
//   layer: runtime | infrastructure | application | all
//   question?: string        the question this block answers
//   topic?: string           short label for the kicker of the following slides (defaults to heading)
import { useLayer } from '../composables/inherit'
import LayerStack from '../components/LayerStack.vue'

defineProps<{
  heading?: string
  day?: number
  time?: string
  minutes?: number
  question?: string
  topic?: string
}>()
const layer = useLayer()
</script>

<template>
  <div class="slidev-layout section">
    <div class="ki-slide sec" :data-layer="layer">
      <div class="ki-kicker">
        <span v-if="day">Day {{ day }} · </span><span v-if="time">{{ time }}</span><span v-if="minutes"> · {{ minutes }} min</span>
      </div>
      <h1 class="sec-title">{{ heading }}</h1>
      <p v-if="question" class="sec-question">{{ question }}</p>
      <div class="ki-grow"><slot /></div>
      <LayerStack :layer="layer" />
    </div>
  </div>
</template>

<style scoped>
.sec {
  padding-bottom: 44px;
}
.sec-title {
  font-size: var(--ki-text-3xl) !important;
  letter-spacing: -0.03em;
  max-width: 1000px;
  margin-bottom: 20px !important;
}
.sec-question {
  font-size: var(--ki-text-lg);
  color: var(--ki-fg-muted);
  max-width: 900px;
}
</style>
