<script setup lang="ts">
// D08: the same four slots and the same requests under two scheduling policies. A constructed example: the step
// counts and output lengths are made up to show the mechanism, not measured.
// Always visible: static batching. A batch starts together and runs until its slowest request is done.
// Click 1: continuous batching. A finished request leaves and a waiting one takes its slot at the next step.
// Click 2: what changes for the waiting requests.
import DiagramFrame from './DiagramFrame.vue'

type Run = { slot: number; start: number; len: number; name: string; late?: boolean }

const STEPS = 12
const X0 = 128
const PITCH = 82
const W = 76
const colX = (step: number) => X0 + (step - 1) * PITCH
const slots = [0, 1, 2, 3]

// Static: batch one (A to D) runs until C ends at step 8; batch two (E to H) starts at step 9. H is cut at step 12.
const staticRuns: Run[] = [
  { slot: 0, start: 1, len: 3, name: 'A' },
  { slot: 1, start: 1, len: 5, name: 'B' },
  { slot: 2, start: 1, len: 8, name: 'C' },
  { slot: 3, start: 1, len: 4, name: 'D' },
  { slot: 0, start: 9, len: 4, name: 'E' },
  { slot: 1, start: 9, len: 3, name: 'F' },
  { slot: 2, start: 9, len: 4, name: 'G' },
  { slot: 3, start: 9, len: 6, name: 'H' },
]
// Continuous: a slot is refilled in the step after its request ends.
const contRuns: Run[] = [
  { slot: 0, start: 1, len: 3, name: 'A' },
  { slot: 0, start: 4, len: 4, name: 'E', late: true },
  { slot: 0, start: 8, len: 5, name: 'I', late: true },
  { slot: 1, start: 1, len: 5, name: 'B' },
  { slot: 1, start: 6, len: 3, name: 'F', late: true },
  { slot: 1, start: 9, len: 4, name: 'J', late: true },
  { slot: 2, start: 1, len: 8, name: 'C' },
  { slot: 2, start: 9, len: 4, name: 'G', late: true },
  { slot: 3, start: 1, len: 4, name: 'D' },
  { slot: 3, start: 5, len: 6, name: 'H', late: true },
  { slot: 3, start: 11, len: 2, name: 'K', late: true },
]

// idle spans of the static panel: the cells of a slot that no run covers
const idle = slots.flatMap((slot) => {
  const covered = new Set<number>()
  for (const r of staticRuns.filter((x) => x.slot === slot)) for (let s = r.start; s < r.start + r.len; s++) covered.add(s)
  const spans: { slot: number; start: number; len: number }[] = []
  let from = 0
  for (let s = 1; s <= STEPS + 1; s++) {
    const free = s <= STEPS && !covered.has(s)
    if (free && !from) from = s
    if (!free && from) {
      spans.push({ slot, start: from, len: s - from })
      from = 0
    }
  }
  return spans
})

const rowY1 = (slot: number) => 56 + slot * 36
const rowY2 = (slot: number) => 278 + slot * 36
const rx = (r: { start: number; len: number }) => colX(r.start)
const rw = (r: { start: number; len: number }) => (Math.min(r.start + r.len - 1, STEPS) - r.start) * PITCH + W
</script>

<template>
  <DiagramFrame label="Static batching leaves slots idle until the slowest request ends; continuous batching refills a slot in the step after its request ends">
    <!-- static panel (always visible) -->
    <text x="0" y="20" class="dg-title">Static batching</text>
    <text x="196" y="20" class="dg-text-muted">the batch runs until its slowest request is done (constructed example, 4 slots)</text>
    <g v-for="s in STEPS" :key="`h${s}`">
      <text :x="colX(s) + W / 2" y="46" text-anchor="middle" class="dg-text-muted">{{ s }}</text>
    </g>
    <text x="0" y="46" class="dg-text-muted">step</text>
    <g v-for="slot in slots" :key="`l1${slot}`">
      <text x="0" :y="rowY1(slot) + 21" class="dg-text-muted">slot {{ slot + 1 }}</text>
    </g>
    <g v-for="(i, k) in idle" :key="`i1${k}`">
      <rect :x="rx(i)" :y="rowY1(i.slot)" :width="rw(i)" height="30" rx="6" class="dg-box" stroke-dasharray="5 4" style="fill: none" />
      <text v-if="i.len >= 2" :x="rx(i) + rw(i) / 2" :y="rowY1(i.slot) + 21" text-anchor="middle" class="dg-text-muted">idle</text>
    </g>
    <g v-for="r in staticRuns" :key="`s${r.name}`">
      <rect :x="rx(r)" :y="rowY1(r.slot)" :width="rw(r)" height="30" rx="6" class="dg-box dg-teal" />
      <text :x="rx(r) + 12" :y="rowY1(r.slot) + 21" class="dg-mono">{{ r.name }}</text>
    </g>
    <text :x="colX(12) + W + 6" :y="rowY1(3) + 21" class="dg-text-muted">→</text>
    <text :x="colX(9) - 6" y="220" text-anchor="end" class="dg-text">A, B and D wait for C. E to H wait in the queue until step 9.</text>

    <!-- continuous panel -->
    <g v-click="1">
      <text x="0" y="262" class="dg-title">Continuous batching</text>
      <text x="250" y="262" class="dg-text-muted">same requests; a finished request leaves, a waiting one joins at the next step</text>
      <g v-for="slot in slots" :key="`l2${slot}`">
        <text x="0" :y="rowY2(slot) + 21" class="dg-text-muted">slot {{ slot + 1 }}</text>
      </g>
      <g v-for="r in contRuns" :key="`c${r.name}`">
        <rect :x="rx(r)" :y="rowY2(r.slot)" :width="rw(r)" height="30" rx="6" class="dg-box" :class="r.late ? 'dg-green' : 'dg-teal'" />
        <text :x="rx(r) + 12" :y="rowY2(r.slot) + 21" class="dg-mono">{{ r.name }}</text>
      </g>
    </g>

    <!-- click 2: what changes -->
    <g v-click="2">
      <text x="128" y="440" class="dg-text">E starts at step 4 instead of 9, F at 6, H at 5. No slot waits for the slowest request.</text>
    </g>
  </DiagramFrame>
</template>
