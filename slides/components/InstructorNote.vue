<script setup lang="ts">
import Callout from './Callout.vue'
defineProps<{ title?: string }>()
</script>

<template>
  <Callout kind="trainer" :title="title"><slot /></Callout>
</template>
