// Measured numbers on slides come from benchmark/results/**.json, never from the slide text.
// A component declares `source="measured:benchmark/results/<path>"` (a file, or a directory
// holding several result files) or `source="illustrative"`. `pnpm check` verifies the path
// exists and that the result carries provenance metadata.
const modules = import.meta.glob('../../benchmark/results/**/*.json', { eager: true, import: 'default' }) as Record<
  string,
  any
>

const results: Record<string, any> = {}
for (const [key, doc] of Object.entries(modules)) results[key.replace('../../', '')] = doc

export type Source = { kind: 'illustrative' } | { kind: 'measured'; path: string }

export function parseSource(source: string | undefined): Source {
  if (source === 'illustrative') return { kind: 'illustrative' }
  if (source?.startsWith('measured:')) return { kind: 'measured', path: source.slice('measured:'.length) }
  throw new Error(`source must be "illustrative" or "measured:benchmark/results/..." (got "${source}")`)
}

/** Result documents under a file or directory path, in path order (natural sort: c2 before c10). `match` keeps the
 * paths that contain it (a list means: contain any of them). */
export function measuredDocs(path: string, match?: string | string[]): { path: string; doc: any }[] {
  const wanted = match === undefined ? [] : Array.isArray(match) ? match : [match]
  const prefix = path.endsWith('/') || path.endsWith('.json') ? path : `${path}/`
  return Object.entries(results)
    .filter(([p, doc]) => (p === path || p.startsWith(prefix)) && doc?.configuration && (!wanted.length || wanted.some((m) => p.includes(m))))
    .sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
    .map(([p, doc]) => ({ path: p, doc }))
}

export function pick(doc: any, metric: string): number | string | undefined {
  let cur = doc
  for (const part of metric.split('.')) {
    if (cur == null) return undefined
    cur = cur[part]
  }
  return typeof cur === 'number' || typeof cur === 'string' ? cur : undefined
}

export function provenance(doc: any): string {
  const c = doc?.configuration ?? {}
  const parts = [
    c.hardware?.gpu,
    c.model,
    c.engine && c.engine_version ? `${c.engine} ${c.engine_version}` : undefined,
    typeof c.date === 'string' ? c.date.slice(0, 10) : undefined,
  ]
  return parts.filter(Boolean).join(' · ')
}

export function fmt(value: number | string | undefined, digits: number | string = 0): string {
  if (value === undefined) return 'n/a'
  if (typeof value === 'string') return value
  const d = Number(digits)
  return value.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d })
}

export const LABELS: Record<string, string> = {
  concurrency: 'Concurrency',
  requests: 'Requests',
  'ttft_ms.p50': 'TTFT p50 (ms)',
  'ttft_ms.p95': 'TTFT p95 (ms)',
  'ttft_ms.p99': 'TTFT p99 (ms)',
  'itl_ms.p50': 'ITL p50 (ms)',
  'itl_ms.p95': 'ITL p95 (ms)',
  'latency_ms.p50': 'Latency p50 (ms)',
  'latency_ms.p95': 'Latency p95 (ms)',
  output_tps: 'Output tok/s per request',
  'output_tps_per_request.p50': 'Output tok/s per request (p50)',
  aggregate_tps: 'Aggregate tok/s',
  request_throughput_rps: 'Requests/s',
  'gpu.utilization_pct.mean': 'GPU util (%)',
  'gpu.memory_used_mib.max': 'VRAM max (MiB)',
}
