<script setup lang="ts">
import Callout from './Callout.vue'
defineProps<{ title?: string }>()
</script>

<template>
  <Callout kind="observation" :title="title"><slot /></Callout>
</template>
