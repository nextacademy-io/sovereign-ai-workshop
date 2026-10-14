<script setup lang="ts">
// A formula as coloured terms: WEIGHTS + KV CACHE + OVERHEAD = VRAM.
//   <Formula :terms='[{ "t": "WEIGHTS" }, { "op": "+" }, { "t": "KV CACHE", "hot": true }, { "op": "=" }, { "t": "VRAM" }]' />
defineProps<{ terms: { t?: string; op?: string; sub?: string; hot?: boolean }[] }>()
</script>

<template>
  <div class="formula">
    <template v-for="(x, i) in terms" :key="i">
      <span v-if="x.op" class="op">{{ x.op }}</span>
      <span v-else class="term" :class="{ hot: x.hot }">
        {{ x.t }}<small v-if="x.sub">{{ x.sub }}</small>
      </span>
    </template>
  </div>
</template>

<style scoped>
.formula {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  margin: 8px 0 20px;
}
.term {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  border-radius: var(--ki-radius);
  border: 1px solid var(--ki-border-strong);
  background: var(--ki-bg-raised);
  font-family: var(--ki-font-mono);
  font-size: var(--ki-text-lg);
  font-weight: 600;
}
.term.hot {
  border-color: var(--ki-layer, var(--ki-runtime));
  background: var(--ki-layer-bg, var(--ki-runtime-bg));
  color: var(--ki-layer, var(--ki-runtime));
}
small {
  font-family: var(--ki-font-sans);
  font-weight: 400;
  font-size: 15px;
  color: var(--ki-fg-muted);
}
.op {
  font-size: var(--ki-text-xl);
  color: var(--ki-fg-dim);
}
</style>
