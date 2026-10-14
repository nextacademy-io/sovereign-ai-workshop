<script setup lang="ts">
import Callout from './Callout.vue'
defineProps<{ title?: string }>()
</script>

<template>
  <Callout kind="takeaway" :title="title"><slot /></Callout>
</template>
