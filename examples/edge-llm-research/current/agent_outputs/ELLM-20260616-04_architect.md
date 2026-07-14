# ELLM-20260616-04 Architect

## Task ID

ELLM-20260616-04

## Worker Name

architect

## Execution Backend

example-fixture

## Sub-Agent Reference

Not applicable in static fixture.

## Scope

Convert research and benchmark methodology into current-repo optimization directions and roadmap entries.

## Inputs Read

- `current/agent_outputs/ELLM-20260616-01_repo-explorer.md`
- `current/agent_outputs/ELLM-20260616-02_oss-scout.md`
- `current/agent_outputs/ELLM-20260616-03_perf-analyst.md`
- `memory/PROJECT_FACTS.md`

## Commands Run

None.

## Conclusion

The highest-value roadmap is to first make measurements comparable, then optimize the hot decode path and memory system. For edge deployment, memory footprint, thermal stability, and dependency footprint should be treated as first-class constraints alongside throughput.

Recommended roadmap themes:

1. Benchmark alignment first.
   - Add a unified e2e benchmark harness with explicit timing windows.
   - Add module benchmark harnesses for attention, GEMM, MoE, KV cache, scheduler, and sampling.

2. Decode-path memory efficiency.
   - Evaluate paged or block KV cache, prefix caching, and optional KV quantization.
   - Track fragmentation, cache hit rate, and per-token memory bandwidth.

3. Operator fusion and kernel coverage.
   - Prioritize attention, MoE routing, grouped GEMM, activation/norm/RoPE fusion, top-k, and sampling.
   - Avoid adding kernels without shape coverage and correctness tests.

4. Quantization and engine specialization.
   - Compare FP16/BF16, FP8 where supported, INT8, and INT4 weight-only paths.
   - For TensorRT-style paths, separate engine build cost from inference timing.

5. Scheduler and batching.
   - Evaluate continuous batching, prefill/decode separation, fairness, and edge latency budgets.

6. MTP or speculative decoding.
   - Treat as high-risk until model compatibility, memory overhead, and acceptance-rate evidence are available.

## Artifacts

- `current/agent_outputs/ELLM-20260616-04_architect.md`
- `memory/ROADMAP.md`
- `memory/DECISIONS.md`

## Risks or Blockers

Roadmap priorities should be re-ranked after real current-repo profiling. Some competitor strategies may be server-oriented and unsuitable for edge memory, power, or static-shape constraints.

## Recommended Next Step

Ask `reviewer` to check that each roadmap item has evidence needed, validation method, and clear risk gate.
