<script setup lang="ts">
// The seven-stage stack with the current layer lit. Used on section dividers and the mental-model slides.
import type { LayerKey } from '../composables/stack'
import { LAYERS, STAGES } from '../composables/stack'

withDefaults(defineProps<{ layer?: LayerKey; stage?: string | string[]; labels?: boolean }>(), {
  layer: 'all',
  stage: () => [],
  labels: true,
})

function lit(layer: LayerKey, stage: (typeof STAGES)[number], picked: string | string[]) {
  const list = Array.isArray(picked) ? picked : [picked]
  if (list.length && list[0]) return list.includes(stage.key)
  return layer === 'all' || stage.layer === layer
}
</script>

<template>
  <div class="stack">
    <div class="chain">
      <template v-for="(s, i) in STAGES" :key="s.key">
        <span v-if="i" class="arrow">→</span>
        <span class="chip" :class="{ lit: lit(layer, s, stage) }" :data-layer="s.layer">{{ s.label }}</span>
      </template>
    </div>
    <div v-if="labels" class="bands">
      <div v-for="l in LAYERS" :key="l.key" class="band" :data-layer="l.key" :class="{ lit: layer === 'all' || layer === l.key }">
        <div class="band-name">{{ l.label }}</div>
        <div class="band-blurb">{{ l.blurb }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stack {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.chain {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 10px;
}
.arrow {
  color: var(--ki-fg-dim);
  font-size: 20px;
}
.chip {
  font-size: var(--ki-text-xs);
  font-weight: 650;
  letter-spacing: 0.06em;
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid var(--ki-border);
  color: var(--ki-fg-dim);
  background: var(--ki-bg-raised);
}
.chip.lit {
  color: var(--c);
  border-color: var(--c);
  background: color-mix(in srgb, var(--c) 12%, transparent);
}
.bands {
  display: grid;
  grid-template-columns: 4fr 5fr 3fr;
  gap: 10px;
}
.band {
  padding: 10px 14px;
  border-radius: 8px;
  border-top: 3px solid var(--ki-border-strong);
  background: var(--ki-bg-raised);
  opacity: 0.45;
}
.band.lit {
  opacity: 1;
  border-top-color: var(--c);
}
.band-name {
  font-size: var(--ki-text-sm);
  font-weight: 650;
  color: var(--c);
}
.band-blurb {
  font-size: var(--ki-text-xs);
  color: var(--ki-fg-muted);
  margin-top: 2px;
}
[data-layer='runtime'] {
  --c: var(--ki-runtime);
}
[data-layer='infrastructure'] {
  --c: var(--ki-infrastructure);
}
[data-layer='application'] {
  --c: var(--ki-application);
}
</style>
