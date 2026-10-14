<script setup lang="ts">
// Before / after of a configuration change. Two named slots hold fenced code blocks.
//   <CodeDiff before-title="baseline.yaml" after-title="fp8.yaml">
//     <template #before> ```yaml ... ``` </template>
//     <template #after> ```yaml ... ``` </template>
//   </CodeDiff>
defineProps<{ beforeTitle?: string; afterTitle?: string }>()
</script>

<template>
  <div class="diff">
    <div class="pane before">
      <div class="cap">{{ beforeTitle ?? 'Before' }}</div>
      <slot name="before" />
    </div>
    <div class="pane after">
      <div class="cap">{{ afterTitle ?? 'After' }}</div>
      <slot name="after" />
    </div>
  </div>
</template>

<style scoped>
.diff {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.pane {
  min-width: 0;
}
.cap {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.before .cap {
  color: var(--ki-fg-muted);
}
.after .cap {
  color: var(--ki-good);
}
.pane :deep(.slidev-code),
.pane :deep(pre) {
  margin: 0;
}
.after :deep(.slidev-code),
.after :deep(pre) {
  border-color: color-mix(in srgb, var(--ki-good) 45%, transparent);
}
</style>
