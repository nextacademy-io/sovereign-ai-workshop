<script setup lang="ts">
// The rail at the bottom of every content slide: where in the stack are we?
// Layer and day come from the nearest section divider; `stage:` narrows the highlight.
import { useNav } from '@slidev/client'
import { computed } from 'vue'
import { useDay, useLayer, useStages } from './composables/inherit'
import { STAGES } from './composables/stack'

const { currentLayout, currentPage, total } = useNav()
const layer = useLayer()
const day = useDay()
const picked = useStages()

const hidden = computed(() => ['cover', 'end', 'section'].includes(currentLayout.value))

function state(stage: (typeof STAGES)[number]): 'lit' | 'on' | 'off' {
  if (picked.value.length) return picked.value.includes(stage.key) ? 'lit' : 'off'
  if (layer.value === 'all') return 'on'
  return stage.layer === layer.value ? 'on' : 'off'
}
</script>

<template>
  <div v-if="!hidden" class="rail" :data-layer="layer" role="presentation">
    <div class="rail-left">KI ohne Cloud<span v-if="day"> · Day {{ day }}</span></div>
    <div class="rail-stages">
      <template v-for="(s, i) in STAGES" :key="s.key">
        <span v-if="i" class="rail-arrow">›</span>
        <span class="rail-chip" :class="state(s)" :data-layer="s.layer">{{ s.short }}</span>
      </template>
    </div>
    <div class="rail-right">{{ currentPage }} / {{ total }}</div>
  </div>
</template>

<style scoped>
.rail {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: var(--ki-rail-h);
  padding: 0 var(--ki-pad-x);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  border-top: 1px solid var(--ki-border);
  background: var(--ki-bg);
  font-family: var(--ki-font-sans);
  font-size: 14px;
  letter-spacing: 0.08em;
  color: var(--ki-fg-dim);
  z-index: 50;
}
.rail-left,
.rail-right {
  min-width: 190px;
  text-transform: uppercase;
  font-weight: 600;
}
.rail-right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.rail-stages {
  display: flex;
  align-items: center;
  gap: 8px;
}
.rail-arrow {
  color: var(--ki-fg-dim);
}
.rail-chip {
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid transparent;
  font-weight: 600;
  white-space: nowrap;
}
.rail-chip.off {
  color: var(--ki-fg-dim);
  opacity: 0.55;
}
.rail-chip.on,
.rail-chip.lit {
  color: var(--chip);
  border-color: color-mix(in srgb, var(--chip) 45%, transparent);
  background: color-mix(in srgb, var(--chip) 10%, transparent);
}
.rail-chip.lit {
  border-color: var(--chip);
  background: color-mix(in srgb, var(--chip) 22%, transparent);
}
.rail-chip[data-layer='runtime'] {
  --chip: var(--ki-runtime);
}
.rail-chip[data-layer='infrastructure'] {
  --chip: var(--ki-infrastructure);
}
.rail-chip[data-layer='application'] {
  --chip: var(--ki-application);
}
</style>
