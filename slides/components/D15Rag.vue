<script setup lang="ts">
// D15: the RAG pipeline of apps/rag-demo, with the inference layer highlighted.
// Start:   seven steps, each with what the demo prints for it. Only two of them are model calls (teal).
// Click 1: where those calls run: two vLLM servers on one GPU, one for embeddings and one for generation.
// Click 2: what retrieval costs the generation server: the passages become extra prompt tokens.
import DiagramFrame from './DiagramFrame.vue'

const stages = [
  { name: 'DOCUMENTS', sub: 'files on disk', model: false },
  { name: 'CHUNKING', sub: 'prints N chunks', model: false },
  { name: 'EMBEDDINGS', sub: 'prints seconds', model: true },
  { name: 'INDEX', sub: 'in memory', model: false },
  { name: 'RETRIEVAL', sub: 'ms and scores', model: false },
  { name: 'CONTEXT', sub: 'prompt tokens', model: false },
  { name: 'LLM', sub: 'usage and time', model: true },
]
const W = 134
const X = (i: number) => i * 167
</script>

<template>
  <DiagramFrame label="RAG pipeline from documents to answer: seven steps, of which the embedding step and the generation step are calls to the inference layer">
    <!-- when each step runs -->
    <text x="0" y="16" class="dg-text-muted">INDEX TIME</text>
    <path d="M0 26 H635" class="dg-line" />
    <text x="668" y="16" class="dg-text-muted">QUESTION TIME</text>
    <path d="M668 26 H1136" class="dg-line" />

    <!-- the seven steps -->
    <g v-for="(s, i) in stages" :key="s.name">
      <rect :x="X(i)" y="38" :width="W" height="76" rx="10" class="dg-box" :class="s.model ? 'dg-teal' : 'dg-amber'" />
      <text :x="X(i) + W / 2" y="72" text-anchor="middle" class="dg-mono">{{ s.name }}</text>
      <text :x="X(i) + W / 2" y="96" text-anchor="middle" class="dg-text-muted">{{ s.sub }}</text>
    </g>
    <path v-for="i in 6" :key="`a${i}`" :d="`M${X(i - 1) + W + 3} 76 H${X(i) - 3}`" class="dg-line" marker-end="url(#ki-arrow)" />

    <!-- click 1: the inference layer underneath -->
    <g v-click="1">
      <rect x="0" y="222" width="1136" height="204" rx="12" class="dg-box dg-teal" />
      <text x="16" y="254" class="dg-title">INFERENCE LAYER</text>
      <text x="16" y="280" class="dg-text-muted">one GPU, two vLLM servers</text>

      <rect x="300" y="268" width="460" height="128" rx="10" class="dg-box" />
      <text x="530" y="302" text-anchor="middle" class="dg-title">Embedding server, port 8001</text>
      <text x="530" y="330" text-anchor="middle" class="dg-text-muted">Qwen3-Embedding-0.6B, runner pooling</text>
      <text x="530" y="360" text-anchor="middle" class="dg-mono">POST /v1/embeddings</text>

      <rect x="800" y="268" width="316" height="128" rx="10" class="dg-box" />
      <text x="958" y="302" text-anchor="middle" class="dg-title">Generation server, 8000</text>
      <text x="958" y="330" text-anchor="middle" class="dg-text-muted">Qwen3-8B</text>
      <text x="958" y="360" text-anchor="middle" class="dg-mono">POST /v1/chat/completions</text>

      <path d="M401 118 V264" class="dg-line" style="stroke: var(--ki-runtime)" marker-end="url(#ki-arrow-teal)" />
      <text x="413" y="206" class="dg-text-muted">embed every chunk</text>
      <path d="M735 118 V264" class="dg-line" style="stroke: var(--ki-runtime)" marker-end="url(#ki-arrow-teal)" />
      <text x="747" y="206" class="dg-text-muted">embed the question</text>
      <path d="M1069 118 V264" class="dg-line" style="stroke: var(--ki-runtime)" marker-end="url(#ki-arrow-teal)" />
      <text x="1057" y="206" text-anchor="end" class="dg-text-muted">generate answer</text>
    </g>

    <!-- click 2: what retrieval costs the generation server -->
    <g v-click="2">
      <text x="757" y="148" class="dg-text-muted">the passages go into the prompt:</text>
      <text x="757" y="172" class="dg-text-muted">more prefill, more KV cache</text>
    </g>

    <!-- legend -->
    <rect x="0" y="434" width="18" height="18" rx="4" class="dg-box dg-amber" />
    <text x="26" y="449" class="dg-text-muted">application code: this repository, no framework</text>
    <rect x="470" y="434" width="18" height="18" rx="4" class="dg-box dg-teal" />
    <text x="496" y="449" class="dg-text-muted">model call to the inference layer</text>
  </DiagramFrame>
</template>
