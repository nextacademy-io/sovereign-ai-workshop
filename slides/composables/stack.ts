// The mental model used on every slide: three layers, seven stages.
export type LayerKey = 'runtime' | 'infrastructure' | 'application' | 'all'

export interface Stage {
  key: string
  label: string
  short: string
  layer: Exclude<LayerKey, 'all'>
}

export const STAGES: Stage[] = [
  { key: 'model', label: 'MODEL', short: 'MODEL', layer: 'runtime' },
  { key: 'runtime', label: 'RUNTIME', short: 'RUNTIME', layer: 'runtime' },
  { key: 'gpu', label: 'GPU', short: 'GPU', layer: 'runtime' },
  { key: 'engine', label: 'INFERENCE ENGINE', short: 'ENGINE', layer: 'runtime' },
  { key: 'serving', label: 'SERVING', short: 'SERVING', layer: 'infrastructure' },
  { key: 'observability', label: 'OBSERVABILITY', short: 'OBSERVABILITY', layer: 'infrastructure' },
  { key: 'application', label: 'APPLICATION', short: 'APPLICATION', layer: 'application' },
]

export const LAYERS: { key: Exclude<LayerKey, 'all'>; label: string; blurb: string }[] = [
  { key: 'runtime', label: 'Runtime layer', blurb: 'model · GPU · inference engine' },
  { key: 'infrastructure', label: 'Infrastructure layer', blurb: 'containers · networking · scaling · monitoring · security' },
  { key: 'application', label: 'Application layer', blurb: 'APIs · structured output · tools · RAG · MCP · agents' },
]

export const RHYTHM = [
  { key: 'concept', label: 'Concept' },
  { key: 'system', label: 'System' },
  { key: 'experiment', label: 'Experiment' },
  { key: 'prediction', label: 'Prediction' },
  { key: 'measurement', label: 'Measurement' },
  { key: 'explanation', label: 'Explanation' },
  { key: 'consequence', label: 'Production consequence' },
] as const
export type RhythmKey = (typeof RHYTHM)[number]['key']

export function isLayer(value: unknown): value is LayerKey {
  return value === 'runtime' || value === 'infrastructure' || value === 'application' || value === 'all'
}
