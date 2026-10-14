<script setup lang="ts">
// Marks every number on a slide as measured (with provenance) or illustrative.
defineProps<{ illustrative?: boolean; text?: string }>()
</script>

<template>
  <span class="badge" :class="{ illustrative }">
    <template v-if="illustrative">ILLUSTRATIVE EXAMPLE · not measured</template>
    <template v-else>measured · {{ text }}</template>
  </span>
</template>

<style scoped>
.badge {
  display: inline-block;
  font-size: 13px;
  line-height: 1.3;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--ki-fg-dim);
}
.badge.illustrative {
  color: var(--ki-warn);
  border: 1px solid var(--ki-warn);
  border-radius: 4px;
  padding: 1px 8px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
</style>
