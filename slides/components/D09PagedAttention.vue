<script setup lang="ts">
// D09: PagedAttention. One pool of fixed-size blocks instead of one long reservation per request.
// Left (a thought experiment, lengths illustrative): every request reserves room for the longest request it may become.
// Right: blocks of 16 tokens are taken from one pool as a request grows and returned when it ends.
// Click 1: the reservation side. Click 2: the block pool. Click 3: request D takes free blocks wherever they are, request A ends.
import DiagramFrame from './DiagramFrame.vue'

const reservations = [
  { id: 'A', used: 170, cls: 'dg-teal' },
  { id: 'B', used: 95, cls: 'dg-violet' },
  { id: 'C', used: 260, cls: 'dg-amber' },
]
const rowY = (i: number) => 76 + i * 70

// The pool: 8 x 5 blocks. Letters are requests, '.' is a free block.
const rows = ['AB.CCA.B', 'C.AB.CA.', 'BC..A.CB', 'A.CB.AC.', 'CB.AC.BA']
const OWNER: Record<string, string> = { A: 'dg-teal', B: 'dg-violet', C: 'dg-amber', D: 'dg-green' }
const LAST = new Set(['4-7', '4-6', '4-4']) // the newest block of A, B and C: the only one that can be partly empty
const BW = 58
const BH = 46
const cells = rows.flatMap((row, r) =>
  [...row].map((ch, c) => ({
    key: `${r}-${c}`,
    owner: ch === '.' ? '' : ch,
    x: 596 + c * 66,
    y: 70 + r * 56,
    last: LAST.has(`${r}-${c}`),
  })),
)
const others = cells.filter((c) => c.owner !== 'A')
const free = cells.filter((c) => !c.owner)
const taken = free.slice(0, 3) // request D arrives
const ended = cells.filter((c) => c.owner === 'A') // request A finishes
</script>

<template>
  <DiagramFrame label="PagedAttention: fixed-size blocks from one pool, compared with one maximum-length reservation per request">
    <!-- left: reserve the maximum -->
    <g v-click="1">
      <text x="0" y="30" class="dg-title">Reserve the maximum, per request</text>
      <text x="0" y="52" class="dg-text-muted">thought experiment, lengths illustrative</text>
      <g v-for="(r, i) in reservations" :key="r.id">
        <rect x="0" :y="rowY(i)" width="540" height="54" rx="8" class="dg-box" stroke-dasharray="7 5" />
        <rect x="0" :y="rowY(i)" :width="r.used" height="54" rx="8" class="dg-box" :class="r.cls" />
        <text x="16" :y="rowY(i) + 34" class="dg-title">{{ r.id }}</text>
        <text x="524" :y="rowY(i) + 33" text-anchor="end" class="dg-text-muted">reserved, unused</text>
      </g>
      <rect x="0" :y="rowY(3)" width="330" height="54" rx="8" class="dg-box" stroke-dasharray="7 5" />
      <text x="165" :y="rowY(3) + 33" text-anchor="middle" class="dg-text-muted">free, too short for another one</text>
      <text x="0" y="394" class="dg-text">Waste inside each reservation and in the gaps</text>
      <text x="0" y="422" class="dg-text">between them: fragmentation. The pool holds</text>
      <text x="0" y="450" class="dg-text">only as many requests as reservations fit.</text>
    </g>

    <!-- right: blocks from one pool -->
    <g v-click="2">
      <text x="596" y="30" class="dg-title">Blocks of 16 tokens from one pool</text>
      <text x="596" y="52" class="dg-text-muted">a request owns a list of blocks; they need not touch</text>
      <g v-for="c in others" :key="c.key">
        <rect :x="c.x" :y="c.y" :width="BW" :height="BH" rx="6" class="dg-box" :class="OWNER[c.owner]" :stroke-dasharray="c.owner ? undefined : '5 4'" />
        <rect v-if="c.last" :x="c.x + BW * 0.45" :y="c.y + 1" :width="BW * 0.55 - 1" :height="BH - 2" rx="5" class="dg-box" />
        <text v-if="c.owner" :x="c.x + (c.last ? 13 : BW / 2)" :y="c.y + 30" text-anchor="middle" class="dg-mono">{{ c.owner }}</text>
      </g>
      <g v-click.hide="3">
        <g v-for="c in ended" :key="`a${c.key}`">
          <rect :x="c.x" :y="c.y" :width="BW" :height="BH" rx="6" class="dg-box dg-teal" />
          <rect v-if="c.last" :x="c.x + BW * 0.45" :y="c.y + 1" :width="BW * 0.55 - 1" :height="BH - 2" rx="5" class="dg-box" />
          <text :x="c.x + (c.last ? 13 : BW / 2)" :y="c.y + 30" text-anchor="middle" class="dg-mono">A</text>
        </g>
      </g>
      <text x="596" y="394" class="dg-text">Only the newest block of a request can</text>
      <text x="596" y="422" class="dg-text">be partly empty (the half-filled ones).</text>
      <text x="596" y="450" class="dg-mono">16 tokens × 147,456 B = 2.25 MiB per block</text>
    </g>

    <!-- click 3: D arrives, A ends -->
    <g v-click="3">
      <g v-for="c in ended" :key="`e${c.key}`">
        <rect :x="c.x" :y="c.y" :width="BW" :height="BH" rx="6" class="dg-box" stroke-dasharray="5 4" />
      </g>
      <g v-for="c in taken" :key="`d${c.key}`">
        <rect :x="c.x" :y="c.y" :width="BW" :height="BH" rx="6" class="dg-box dg-green" />
        <text :x="c.x + BW / 2" :y="c.y + 30" text-anchor="middle" class="dg-mono">D</text>
      </g>
      <text x="596" y="362" class="dg-text-muted">A ends, D starts: no gap to search for</text>
    </g>
  </DiagramFrame>
</template>
