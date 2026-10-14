<script setup lang="ts">
// D17: agent inference amplification. One user request becomes several model calls, and every call
// sends the whole conversation again. Bar lengths are illustrative; nothing here is measured.
// Start:   model call 1 asks for a tool.
// Click 1: model call 2 sends call 1's request and the tool result along, and asks for another tool.
// Click 2: model call 3 sends everything again and produces the answer.
// Click 3: the ledger: what this does to the inference layer.
import DiagramFrame from './DiagramFrame.vue'

const X0 = 440
const BASE = 200
const OUT = 80
const RES = 100
const GAP = 8

// widths of the segments that make up the prompt of call n (n = 1, 2, 3)
const promptSteps = (n: number) => n - 1
const promptEnd = (n: number) => X0 + BASE + promptSteps(n) * (OUT + RES)
const rowY = (n: number) => 30 + (n - 1) * 98
</script>

<template>
  <DiagramFrame label="Agent amplification: one user request becomes three model calls, and each call sends a longer prompt than the one before">
    <text :x="X0" y="20" class="dg-text-muted">prompt, resent each call</text>
    <text :x="X0 + BASE + GAP" y="20" class="dg-text-muted">output</text>

    <!-- the request -->
    <rect x="0" y="120" width="150" height="100" rx="10" class="dg-box dg-amber" />
    <text x="75" y="164" text-anchor="middle" class="dg-title">One user</text>
    <text x="75" y="192" text-anchor="middle" class="dg-title">request</text>

    <!-- call 1 -->
    <g>
      <path d="M154 170 C 190 170, 190 59, 224 59" class="dg-line" marker-end="url(#ki-arrow)" />
      <text x="232" y="52" class="dg-title">Model call 1</text>
      <text x="232" y="76" class="dg-text-muted">prompt: base</text>
      <rect :x="X0" :y="rowY(1)" :width="BASE" height="58" rx="8" class="dg-box dg-amber" />
      <text :x="X0 + BASE / 2" :y="rowY(1) + 35" text-anchor="middle" class="dg-text-muted">system + question</text>
      <rect :x="promptEnd(1) + GAP" :y="rowY(1)" :width="OUT" height="58" rx="8" class="dg-box dg-teal" />
      <text :x="promptEnd(1) + GAP + OUT / 2" :y="rowY(1) + 35" text-anchor="middle" class="dg-text-muted">request</text>
    </g>

    <!-- call 2 -->
    <g v-click="1">
      <path d="M154 170 C 190 170, 190 157, 224 157" class="dg-line" marker-end="url(#ki-arrow)" />
      <text x="232" y="150" class="dg-title">Model call 2</text>
      <text x="232" y="174" class="dg-text-muted">prompt: base + 1 step</text>
      <rect :x="X0" :y="rowY(2)" :width="BASE" height="58" rx="8" class="dg-box dg-amber" />
      <text :x="X0 + BASE / 2" :y="rowY(2) + 35" text-anchor="middle" class="dg-text-muted">system + question</text>
      <rect :x="X0 + BASE" :y="rowY(2)" :width="OUT" height="58" rx="8" class="dg-box dg-teal" />
      <text :x="X0 + BASE + OUT / 2" :y="rowY(2) + 35" text-anchor="middle" class="dg-text-muted">request</text>
      <rect :x="X0 + BASE + OUT" :y="rowY(2)" :width="RES" height="58" rx="8" class="dg-box dg-amber" />
      <text :x="X0 + BASE + OUT + RES / 2" :y="rowY(2) + 35" text-anchor="middle" class="dg-text-muted">result</text>
      <rect :x="promptEnd(2) + GAP" :y="rowY(2)" :width="OUT" height="58" rx="8" class="dg-box dg-teal" />
      <text :x="promptEnd(2) + GAP + OUT / 2" :y="rowY(2) + 35" text-anchor="middle" class="dg-text-muted">request</text>
    </g>

    <!-- call 3 -->
    <g v-click="2">
      <path d="M154 170 C 190 170, 190 255, 224 255" class="dg-line" marker-end="url(#ki-arrow)" />
      <text x="232" y="248" class="dg-title">Model call 3</text>
      <text x="232" y="272" class="dg-text-muted">prompt: base + 2 steps</text>
      <rect :x="X0" :y="rowY(3)" :width="BASE" height="58" rx="8" class="dg-box dg-amber" />
      <text :x="X0 + BASE / 2" :y="rowY(3) + 35" text-anchor="middle" class="dg-text-muted">system + question</text>
      <rect :x="X0 + BASE" :y="rowY(3)" :width="OUT" height="58" rx="8" class="dg-box dg-teal" />
      <text :x="X0 + BASE + OUT / 2" :y="rowY(3) + 35" text-anchor="middle" class="dg-text-muted">request</text>
      <rect :x="X0 + BASE + OUT" :y="rowY(3)" :width="RES" height="58" rx="8" class="dg-box dg-amber" />
      <text :x="X0 + BASE + OUT + RES / 2" :y="rowY(3) + 35" text-anchor="middle" class="dg-text-muted">result</text>
      <rect :x="X0 + BASE + OUT + RES" :y="rowY(3)" :width="OUT" height="58" rx="8" class="dg-box dg-teal" />
      <text :x="X0 + BASE + OUT + RES + OUT / 2" :y="rowY(3) + 35" text-anchor="middle" class="dg-text-muted">request</text>
      <rect :x="X0 + BASE + 2 * OUT + RES" :y="rowY(3)" :width="RES" height="58" rx="8" class="dg-box dg-amber" />
      <text :x="X0 + BASE + 2 * OUT + RES + RES / 2" :y="rowY(3) + 35" text-anchor="middle" class="dg-text-muted">result</text>
      <rect :x="promptEnd(3) + GAP" :y="rowY(3)" :width="OUT" height="58" rx="8" class="dg-box dg-green" />
      <text :x="promptEnd(3) + GAP + OUT / 2" :y="rowY(3) + 35" text-anchor="middle" class="dg-text-muted">answer</text>
    </g>

    <!-- legend -->
    <rect x="0" y="318" width="18" height="18" rx="4" class="dg-box dg-amber" />
    <text x="26" y="333" class="dg-text-muted">text the application builds: system, question, tool results</text>
    <rect x="520" y="318" width="18" height="18" rx="4" class="dg-box dg-teal" />
    <text x="546" y="333" class="dg-text-muted">model output: a tool request</text>
    <rect x="860" y="318" width="18" height="18" rx="4" class="dg-box dg-green" />
    <text x="886" y="333" class="dg-text-muted">the answer</text>
    <text x="0" y="364" class="dg-text-muted">Bar lengths are illustrative, not measured.</text>

    <!-- click 3: the ledger -->
    <g v-click="3">
      <text x="0" y="426" class="dg-title">ONE USER REQUEST → MULTIPLE MODEL CALLS → MORE TOKENS → MORE GPU LOAD</text>
    </g>
  </DiagramFrame>
</template>
