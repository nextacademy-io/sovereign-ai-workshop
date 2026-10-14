import type { ComputedRef } from 'vue'
import { useNav } from '@slidev/client'
import { computed } from 'vue'
import type { LayerKey } from './stack'
import { isLayer } from './stack'

/**
 * The nearest value of a frontmatter key on this slide or an earlier one.
 * Section dividers declare `layer` and `day` once; the slides after them inherit it.
 */
export function useInherited<T = unknown>(key: string, accept: (v: unknown) => v is T): ComputedRef<T | undefined> {
  const { slides, currentPage } = useNav()
  return computed(() => {
    for (let i = currentPage.value - 1; i >= 0; i--) {
      const value = slides.value[i]?.meta?.slide?.frontmatter?.[key]
      if (accept(value)) return value
    }
    return undefined
  })
}

export function useLayer(): ComputedRef<LayerKey> {
  const inherited = useInherited<LayerKey>('layer', isLayer)
  return computed(() => inherited.value ?? 'all')
}

export function useDay(): ComputedRef<number | undefined> {
  return useInherited<number>('day', (v): v is number => typeof v === 'number')
}

/** Stage keys a slide singles out (frontmatter `stage: gpu` or `stage: [gpu, engine]`). */
export function useStages(): ComputedRef<string[]> {
  const { currentSlideRoute } = useNav()
  return computed(() => {
    const raw = currentSlideRoute.value?.meta?.slide?.frontmatter?.stage
    if (!raw) return []
    return Array.isArray(raw) ? raw.map(String) : [String(raw)]
  })
}

/** Title of the block this slide belongs to: the heading of the nearest section divider. */
export function useTopic(): ComputedRef<string | undefined> {
  const { slides, currentPage } = useNav()
  return computed(() => {
    for (let i = currentPage.value - 1; i >= 0; i--) {
      const fm = slides.value[i]?.meta?.slide?.frontmatter
      if (fm?.layout === 'section') return (fm.topic ?? fm.heading) as string | undefined
    }
    return undefined
  })
}
