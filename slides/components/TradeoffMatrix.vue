<script setup lang="ts">
// Qualitative effect of one change on the seven dimensions every optimization trades.
// It states DIRECTION, not size: measured sizes belong in ResultTable / MetricCard.
//   <TradeoffMatrix :rows='[{ "name": "FP8 weights", "effects": { "memory": "up", "latency": "up", "quality": "risk" } }]' />
// effect values: up (improves) | down (worsens) | flat | risk (depends / must be checked) | (absent = not affected)
import { DIMENSIONS } from '../composables/tradeoffs'

defineProps<{ rows: { name: string; effects: Record<string, string>; note?: string }[]; dimensions?: string[] }>()
const SYMBOL: Record<string, string> = { up: '▲', down: '▼', flat: '●', risk: '?' }
const WORD: Record<string, string> = { up: 'improves', down: 'worsens', flat: 'unchanged', risk: 'check it' }
</script>

<template>
  <div class="tm">
    <table>
      <thead>
        <tr>
          <th />
          <th v-for="d in dimensions ?? DIMENSIONS.map((x) => x.key)" :key="d">{{ DIMENSIONS.find((x) => x.key === d)?.label ?? d }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.name">
          <td class="name">{{ r.name }}<div v-if="r.note" class="note">{{ r.note }}</div></td>
          <td v-for="d in dimensions ?? DIMENSIONS.map((x) => x.key)" :key="d" class="cell">
            <span v-if="r.effects[d]" class="eff" :class="r.effects[d]" :title="WORD[r.effects[d]]">{{ SYMBOL[r.effects[d]] }}</span>
            <span v-else class="none">·</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="legend">
      <span class="eff up">▲</span> improves <span class="eff down">▼</span> worsens <span class="eff flat">●</span> unchanged
      <span class="eff risk">?</span> depends, measure it <span class="none">·</span> not affected
      <span class="q">Direction only: sizes come from measurements.</span>
    </div>
  </div>
</template>

<style scoped>
.tm th {
  text-align: center;
  font-size: 13px;
  padding: 8px 6px;
}
.name {
  font-weight: 650;
  font-size: var(--ki-text-sm);
  white-space: nowrap;
}
.note {
  font-weight: 400;
  color: var(--ki-fg-muted);
  font-size: 15px;
  white-space: normal;
}
.cell {
  text-align: center;
}
.eff {
  font-size: 20px;
  font-weight: 700;
}
.eff.up {
  color: var(--ki-good);
}
.eff.down {
  color: var(--ki-bad);
}
.eff.flat {
  color: var(--ki-fg-muted);
}
.eff.risk {
  color: var(--ki-warn);
}
.none {
  color: var(--ki-fg-dim);
}
.legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 14px;
  font-size: 15px;
  color: var(--ki-fg-muted);
}
.legend .eff {
  font-size: 15px;
}
.q {
  margin-left: auto;
  color: var(--ki-fg-dim);
}
</style>
