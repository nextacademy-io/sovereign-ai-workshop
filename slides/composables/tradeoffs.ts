// The seven dimensions every optimisation is discussed in (and nothing else is "faster").
export const DIMENSIONS = [
  { key: 'quality', label: 'Quality' },
  { key: 'latency', label: 'Latency' },
  { key: 'throughput', label: 'Throughput' },
  { key: 'concurrency', label: 'Concurrency' },
  { key: 'memory', label: 'Memory' },
  { key: 'cost', label: 'Cost' },
  { key: 'ops', label: 'Ops complexity' },
] as const
