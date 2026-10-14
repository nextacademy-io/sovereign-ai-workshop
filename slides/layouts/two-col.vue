<script setup lang="ts">
// layout: two-col — left column is the default slot, right column follows `::right::`.
//   heading?: string
//   ratio?: '1:1' | '3:2' | '2:3' | '2:1' | '1:2'   default 1:1
import { computed } from 'vue'
import { useLayer, useTopic } from '../composables/inherit'

const props = withDefaults(defineProps<{ heading?: string; kicker?: string; ratio?: string }>(), { ratio: '1:1' })
const layer = useLayer()
const topic = useTopic()
const columns = computed(() => {
  const [a, b] = props.ratio.split(':').map(Number)
  return `${a || 1}fr ${b || 1}fr`
})
</script>

<template>
  <div class="slidev-layout two-col">
    <div class="ki-slide" :data-layer="layer">
      <div v-if="kicker || topic" class="ki-kicker">{{ kicker ?? topic }}</div>
      <h1 v-if="heading">{{ heading }}</h1>
      <div class="ki-grow cols" :style="{ gridTemplateColumns: columns }">
        <div class="col"><slot /></div>
        <div class="col"><slot name="right" /></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cols {
  display: grid;
  gap: 40px;
}
.col {
  min-width: 0;
}
</style>
