"""infbench: a small, readable load generator for OpenAI-compatible LLM endpoints.

Measures what a user and an operator care about: time to first token, inter-token
latency, end-to-end latency, per-request and aggregate token throughput, with
percentiles, plus GPU and server-side metrics sampled during the run.
"""

__version__ = "0.1.0"
