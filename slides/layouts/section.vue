<script setup lang="ts">
// layout: section — divider at the start of every module. Declares the module's layer and number;
// the slides after it inherit both (see composables/inherit.ts).
//   heading: string          module title
//   module?: number          position in the module path (config/workshop.yaml)
//   layer: runtime | infrastructure | application | all
//   question?: string        the question this module answers
//   can?: string[]           what participants can do after the module (two or three short statements)
//   topic?: string           short label for the kicker of the following slides (defaults to heading)
import { useLayer } from '../composables/inherit'
import LayerStack from '../components/LayerStack.vue'

defineProps<{
  heading?: string
  module?: number
  question?: string
  can?: string[]
  topic?: string
}>()
const layer = useLayer()
</script>

<template>
  <div class="slidev-layout section">
    <div class="ki-slide sec" :data-layer="layer">
      <div class="ki-kicker">
        <span v-if="module">Module {{ String(module).padStart(2, '0') }}</span>
      </div>
      <h1 class="sec-title">{{ heading }}</h1>
      <p v-if="question" class="sec-question">{{ question }}</p>
      <div v-if="can?.length" class="sec-can">
        <div class="sec-can-label">After this module you can</div>
        <ul>
          <li v-for="c in can" :key="c">{{ c }}</li>
        </ul>
      </div>
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
.sec-can {
  margin-top: 22px;
  max-width: 900px;
}
.sec-can-label {
  font-size: var(--ki-text-xs);
  font-weight: 650;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ki-layer);
  margin-bottom: 8px;
}
.sec-can ul {
  margin: 0;
  padding-left: 22px;
  color: var(--ki-fg);
  font-size: var(--ki-text-sm);
  line-height: 1.5;
}
</style>
