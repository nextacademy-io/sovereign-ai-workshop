<script setup lang="ts">
// A horizontal chain of boxes: CLIENT → API → vLLM → MODEL → GPU.
//   <Flow :items='[{ "label": "Client" }, { "label": "vLLM", "sub": "OpenAI API", "layer": "runtime" }]' />
// Items can be revealed one by one with `click` (v-click).
defineProps<{ items: { label: string; sub?: string; layer?: string; note?: string }[]; click?: boolean }>()
</script>

<template>
  <div class="flow">
    <template v-for="(it, i) in items" :key="i">
      <span v-if="i" class="arrow" aria-hidden="true">→</span>
      <div class="node" :data-layer="it.layer" :class="{ colored: it.layer }">
        <div class="label">{{ it.label }}</div>
        <div v-if="it.sub" class="sub">{{ it.sub }}</div>
        <div v-if="it.note" class="note">{{ it.note }}</div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.flow {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin-bottom: 16px;
}
.arrow {
  align-self: center;
  color: var(--ki-fg-dim);
  font-size: 26px;
}
.node {
  flex: 1 1 0;
  min-width: 0;
  padding: 14px 16px;
  border-radius: var(--ki-radius);
  border: 1px solid var(--ki-border-strong);
  background: var(--ki-bg-raised);
  text-align: center;
}
.node.colored {
  border-color: var(--ki-layer);
  background: var(--ki-layer-bg);
}
.label {
  font-weight: 650;
  font-size: var(--ki-text-base);
}
.sub {
  color: var(--ki-fg-muted);
  font-size: 16px;
  margin-top: 2px;
}
.note {
  color: var(--ki-fg-muted);
  font-size: 15px;
  margin-top: 6px;
}
</style>
