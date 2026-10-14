<script setup lang="ts">
import Callout from './Callout.vue'
defineProps<{ title?: string }>()
</script>

<template>
  <Callout kind="prediction" :title="title"><slot /></Callout>
</template>
