<script setup lang="ts">
// D16: tool calling as a protocol between model and application, in the order apps/tool-calling-demo runs it.
// Start:   four participants. The application sits between the user, the model and the tool.
// Click 1: model call 1. The model answers with a request (name and arguments), not with text.
// Click 2: the application validates the request, runs the function and keeps the result.
// Click 3: model call 2 gets the whole conversation again, including the result, and answers.
import DiagramFrame from './DiagramFrame.vue'

const lanes = [
  { x: 130, name: 'User', cls: 'dg-box' },
  { x: 420, name: 'Application', cls: 'dg-box dg-amber' },
  { x: 710, name: 'Model (vLLM)', cls: 'dg-box dg-teal' },
  { x: 1000, name: 'Tool', cls: 'dg-box dg-amber' },
]
</script>

<template>
  <DiagramFrame label="Tool calling sequence: the user asks the application, the application calls the model, the model requests a tool, the application runs it, and a second model call produces the answer">
    <!-- participants and lifelines -->
    <g v-for="l in lanes" :key="l.name">
      <rect :x="l.x - 92" y="4" width="184" height="46" rx="10" :class="l.cls" />
      <text :x="l.x" y="34" text-anchor="middle" class="dg-title">{{ l.name }}</text>
      <path :d="`M${l.x} 54 V452`" class="dg-line" stroke-dasharray="4 7" />
    </g>

    <!-- click 1: model call 1 -->
    <g v-click="1">
      <path d="M136 100 H414" class="dg-line" marker-end="url(#ki-arrow)" />
      <text x="275" y="92" text-anchor="middle" class="dg-text">question</text>

      <path d="M426 146 H704" class="dg-line" style="stroke: var(--ki-runtime)" marker-end="url(#ki-arrow-teal)" />
      <text x="565" y="138" text-anchor="middle" class="dg-text" style="font-size: 18px">messages + tool schemas</text>
      <text x="724" y="152" class="dg-text-muted">model call 1</text>

      <path d="M704 192 H426" class="dg-line" style="stroke: var(--ki-runtime)" marker-end="url(#ki-arrow-teal)" />
      <text x="565" y="184" text-anchor="middle" class="dg-text" style="font-size: 18px">tool_calls: name, arguments</text>
      <text x="724" y="198" class="dg-text-muted">a request, not an action</text>
    </g>

    <!-- click 2: the application runs the tool -->
    <g v-click="2">
      <path d="M426 238 H994" class="dg-line" style="stroke: var(--ki-application)" marker-end="url(#ki-arrow-amber)" />
      <text x="724" y="230" class="dg-text" style="font-size: 18px">validate, authorize, run</text>

      <path d="M994 284 H426" class="dg-line" style="stroke: var(--ki-application)" marker-end="url(#ki-arrow-amber)" />
      <text x="724" y="276" class="dg-text" style="font-size: 18px">result, as text</text>
    </g>

    <!-- click 3: model call 2 and the answer -->
    <g v-click="3">
      <path d="M426 330 H704" class="dg-line" style="stroke: var(--ki-runtime)" marker-end="url(#ki-arrow-teal)" />
      <text x="565" y="322" text-anchor="middle" class="dg-text" style="font-size: 18px">messages + tool result</text>
      <text x="724" y="336" class="dg-text-muted">model call 2: full history</text>

      <path d="M704 376 H426" class="dg-line" style="stroke: var(--ki-runtime)" marker-end="url(#ki-arrow-teal)" />
      <text x="565" y="368" text-anchor="middle" class="dg-text" style="font-size: 18px">final answer text</text>
      <text x="724" y="382" class="dg-text-muted">no tool_calls: the loop ends</text>

      <path d="M414 422 H136" class="dg-line" marker-end="url(#ki-arrow)" />
      <text x="275" y="414" text-anchor="middle" class="dg-text">answer</text>
    </g>
  </DiagramFrame>
</template>
