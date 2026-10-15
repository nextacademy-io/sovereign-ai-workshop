<script setup lang="ts">
// The trainer slide: photo and a short bio, embedded in the deck (no remote image).
//   <TrainerCard />   everything has a default; override name, role, bio or topics to reuse it.
import photo from '../assets/pawel-sawicki.webp'

withDefaults(
  defineProps<{ name?: string; role?: string; bio?: string; topics?: string[]; source?: string }>(),
  {
    name: 'Paweł Sawicki',
    role: 'Senior Machine Learning Engineer · Software Architect',
    bio: '15+ years building ML systems, from deep learning and NLP to LLMs in production: fine-tuning, RAG, vLLM inference and agents.',
    topics: () => ['vLLM inference', 'RAG', 'Fine-tuning', 'Agents'],
    source: 'nextacademy.io/de/trainers/pawel-sawicki',
  },
)
</script>

<template>
  <div class="trainer ki-card">
    <img class="photo" :src="photo" :alt="`Portrait of ${name}`" width="240" height="240" />
    <div class="text">
      <h2 class="name">{{ name }}</h2>
      <div class="role">{{ role }}</div>
      <p class="bio">{{ bio }}</p>
      <div class="topics">
        <span v-for="t in topics" :key="t" class="ki-pill">{{ t }}</span>
      </div>
      <div class="source">{{ source }}</div>
    </div>
  </div>
</template>

<style scoped>
.trainer {
  display: flex;
  align-items: center;
  gap: 48px;
  padding: 32px 40px;
}
.photo {
  width: 240px;
  height: 240px;
  flex-shrink: 0;
  border-radius: var(--ki-radius);
  border: 1px solid var(--ki-border-strong);
  object-fit: cover;
}
.text {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}
.name {
  margin: 0 !important;
  font-size: var(--ki-text-2xl) !important;
  letter-spacing: -0.02em;
}
.role {
  color: var(--ki-layer, var(--ki-runtime));
  font-weight: 650;
  font-size: var(--ki-text-sm);
  letter-spacing: 0.02em;
}
.bio {
  margin: 4px 0 6px !important;
  font-size: var(--ki-text-base);
  line-height: 1.4;
  color: var(--ki-fg);
}
.topics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.source {
  margin-top: 6px;
  font-family: var(--ki-font-mono);
  font-size: var(--ki-text-xs);
  color: var(--ki-fg-dim);
}
</style>
