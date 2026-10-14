<script setup lang="ts">
// layout: cover — the title slide.
//   heading: string (the deck title; `title` is reserved by Slidev), subtitle?: string, author?: string, meta?: string[]
withDefaults(defineProps<{ heading?: string; subtitle?: string; author?: string; meta?: string[] }>(), {
  meta: () => [],
})
</script>

<template>
  <div class="slidev-layout cover">
    <div class="ki-slide cover-slide">
      <div class="ki-kicker" style="--ki-layer: var(--ki-runtime)">Heise Academy workshop</div>
      <h1 class="title">{{ heading }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      <div class="stack-line"><slot /></div>
      <div class="byline">
        <span v-if="author" class="author">{{ author }}</span>
        <span v-for="m in meta" :key="m" class="meta">{{ m }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cover-slide {
  justify-content: center;
  padding-bottom: var(--ki-pad-top);
  background:
    radial-gradient(900px 500px at 85% 15%, rgb(45 212 191 / 0.1), transparent 70%),
    radial-gradient(700px 500px at 100% 100%, rgb(167 139 250 / 0.1), transparent 70%),
    var(--ki-bg);
}
.title {
  font-size: var(--ki-text-4xl) !important;
  letter-spacing: -0.03em;
  margin-bottom: 18px !important;
}
.subtitle {
  font-size: var(--ki-text-xl);
  color: var(--ki-fg-muted);
  max-width: 900px;
  line-height: 1.25;
  margin-bottom: 40px;
}
.stack-line {
  margin-bottom: 40px;
}
.byline {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 28px;
  align-items: baseline;
  color: var(--ki-fg-muted);
  font-size: var(--ki-text-sm);
}
.author {
  color: var(--ki-fg);
  font-weight: 650;
  font-size: var(--ki-text-base);
}
</style>
