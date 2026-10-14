<script setup lang="ts">
// Frame for the original SVG diagrams (components/D01*.vue ... D18*.vue).
// Diagrams draw in a fixed coordinate space that is exactly the free area of a slide: 1136 wide and
//   460 high under a heading (the default), or 540 high with `:height="540"` on a slide without heading.
// Text must fit inside it: 20 px text is about 10 units per character. Use the .dg-* classes from styles/base.css. Arrow heads: marker-end="url(#ki-arrow)" (+ -teal, -violet, -amber).
defineProps<{ label: string; height?: number }>()
</script>

<template>
  <figure class="dg">
    <svg :viewBox="`0 0 1136 ${height ?? 460}`" role="img" :aria-label="label">
      <defs>
        <marker id="ki-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#5f6b7c" />
        </marker>
        <marker id="ki-arrow-teal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#2dd4bf" />
        </marker>
        <marker id="ki-arrow-violet" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#a78bfa" />
        </marker>
        <marker id="ki-arrow-amber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#f5b14c" />
        </marker>
        <marker id="ki-arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#f87171" />
        </marker>
      </defs>
      <slot />
    </svg>
  </figure>
</template>

<style scoped>
.dg {
  margin: 0;
  width: 100%;
}
svg {
  display: block;
  width: 100%;
  height: auto;
  max-height: 100%;
}
</style>
