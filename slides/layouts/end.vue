<script setup lang="ts">
// layout: end — the closing slide.
//   heading?: string
defineProps<{ heading?: string }>()
</script>

<template>
  <div class="slidev-layout end">
    <div class="ki-slide end-slide" data-layer="all">
      <h1 v-if="heading">{{ heading }}</h1>
      <div class="ki-grow body"><slot /></div>
    </div>
  </div>
</template>

<style scoped>
.end-slide {
  padding-bottom: var(--ki-pad-top);
}
.body {
  display: flex;
  flex-direction: column;
}
</style>
