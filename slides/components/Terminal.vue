<script setup lang="ts">
// A terminal window around a code block of shell commands or output.
//   <Terminal title="gpu-01 · anna">  ```bash ... ```  </Terminal>
defineProps<{ title?: string }>()
</script>

<template>
  <div class="term">
    <div class="bar">
      <span class="dot r" /><span class="dot y" /><span class="dot g" />
      <span v-if="title" class="title">{{ title }}</span>
    </div>
    <div class="screen"><slot /></div>
  </div>
</template>

<style scoped>
.term {
  border: 1px solid var(--ki-border-strong);
  border-radius: var(--ki-radius);
  overflow: hidden;
  background: var(--ki-bg-sunken);
  margin-bottom: 14px;
}
.bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  background: var(--ki-bg-raised-2);
  border-bottom: 1px solid var(--ki-border);
}
.dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--ki-fg-dim);
  opacity: 0.6;
}
.title {
  margin-left: 10px;
  font-family: var(--ki-font-mono);
  font-size: 14px;
  color: var(--ki-fg-muted);
}
.screen :deep(.slidev-code),
.screen :deep(pre) {
  border: 0;
  border-radius: 0;
  margin: 0;
}
</style>
