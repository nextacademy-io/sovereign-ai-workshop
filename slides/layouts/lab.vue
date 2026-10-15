<script setup lang="ts">
// layout: lab — one of the six tasks. `task` must name an existing tasks/<task>.md (pnpm check verifies it).
//   heading: string
//   task: e.g. 02-first-inference-server
//   artifact?: file participants fill, e.g. workshop-artifacts/inference-report.md
import { useLayer } from '../composables/inherit'

defineProps<{ heading?: string; task?: string; artifact?: string }>()
const layer = useLayer()
</script>

<template>
  <div class="slidev-layout lab">
    <div class="ki-slide" :data-layer="layer">
      <div class="ki-kicker">Lab · hands-on</div>
      <div class="head">
        <h1 v-if="heading">{{ heading }}</h1>
        <div class="badges">
          <span v-if="task" class="ki-pill ki-mono">tasks/{{ task }}.md</span>
        </div>
      </div>
      <div class="ki-grow body"><slot /></div>
      <div v-if="artifact" class="artifact">
        <span class="artifact-label">You produce</span>
        <code>{{ artifact }}</code>
      </div>
    </div>
  </div>
</template>

<style scoped>
.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}
.badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  padding-top: 6px;
  flex-shrink: 0;
}
.body {
  display: flex;
  flex-direction: column;
  margin-top: 14px;
}
.artifact {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--ki-border);
}
.artifact-label {
  font-size: var(--ki-text-xs);
  font-weight: 650;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ki-layer);
}
</style>
