<script setup lang="ts">
// Layered block diagram: application on top of infrastructure on top of runtime.
//   <ArchitectureDiagram :layers='[
//     { "layer": "application", "title": "Application", "items": [{ "label": "RAG" }, { "label": "Agent" }] },
//     { "layer": "runtime", "title": "Runtime", "items": [{ "label": "vLLM" }, { "label": "GPU" }] }
//   ]' />
// Items may carry `sub` (second line) and `hot: true` (accent outline) to draw the eye.
defineProps<{ layers: { layer: string; title: string; items: { label: string; sub?: string; hot?: boolean }[] }[] }>()
</script>

<template>
  <div class="arch">
    <div v-for="l in layers" :key="l.title" class="band" :data-layer="l.layer">
      <div class="band-title">{{ l.title }}</div>
      <div class="items">
        <div v-for="it in l.items" :key="it.label" class="item" :class="{ hot: it.hot }">
          <div class="item-label">{{ it.label }}</div>
          <div v-if="it.sub" class="item-sub">{{ it.sub }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.arch {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.band {
  display: flex;
  align-items: stretch;
  gap: 16px;
  padding: 12px 16px;
  border-radius: var(--ki-radius);
  border: 1px solid color-mix(in srgb, var(--ki-layer) 45%, transparent);
  border-left: 5px solid var(--ki-layer);
  background: var(--ki-layer-bg);
}
.band-title {
  flex: 0 0 150px;
  align-self: center;
  font-size: var(--ki-text-sm);
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--ki-layer);
}
.items {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.item {
  flex: 1 1 140px;
  padding: 8px 12px;
  border-radius: var(--ki-radius-sm);
  background: var(--ki-bg-raised);
  border: 1px solid var(--ki-border-strong);
  text-align: center;
}
.item.hot {
  border-color: var(--ki-layer);
  box-shadow: 0 0 0 1px var(--ki-layer);
}
.item-label {
  font-weight: 650;
  font-size: var(--ki-text-sm);
}
.item-sub {
  color: var(--ki-fg-muted);
  font-size: 15px;
}
</style>
