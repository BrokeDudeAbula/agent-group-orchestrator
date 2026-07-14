# ELLM-20260616-03 Perf Analyst

## Task ID

ELLM-20260616-03

## Worker Name

perf-analyst

## Execution Backend

example-fixture

## Sub-Agent Reference

Not applicable in static fixture.

## Scope

Define comparable e2e and module benchmark methodology for the current repo and researched inference engines.

## Inputs Read

- `current/prompt.md`
- `current/agent_outputs/ELLM-20260616-01_repo-explorer.md`
- `current/agent_outputs/ELLM-20260616-02_oss-scout.md`

## Commands Run

None in this static demo. In a real run, inspect benchmark scripts and run only gated local or remote commands.

## Conclusion

Comparable benchmarking requires matching model, tokenizer, weights, precision, prompt/output lengths, batch or concurrency, cache state, hardware, power mode, and timing window. The most important risk is comparing metrics that have the same name but different semantics.

E2E benchmark plan:

| Dimension | Requirement |
| --- | --- |
| Model | Same architecture, tokenizer, weights, rope scaling, max context, quantization, and generation settings |
| Hardware | Same device, clocks, power mode, thermal state, driver, CUDA/TensorRT/runtime versions |
| Workload | Fixed prompt length and output length matrix, batch sizes, concurrency levels, streaming and non-streaming modes |
| Cache state | Cold cache, warm prefix cache, KV reuse, and no-cache runs separated |
| Metrics | TTFT, inter-token latency, end-to-end latency, decode tok/s, total tok/s, requests/s, peak memory, power if available |
| Timing | Explicitly mark tokenization, model load, engine build, warmup, synchronization, stream timestamps, and output postprocess |
| Artifacts | Raw JSON/CSV, command line, git commit, config, environment, prompt set, generated lengths, logs, profiler summary |

Timing semantics checklist:

- Is tokenization included?
- Is model load or TensorRT engine build included?
- Are warmup requests discarded?
- Is prefill measured separately from decode?
- Is TTFT measured at API boundary, scheduler enqueue, GPU start, or first streamed token?
- Are CUDA events synchronized consistently?
- Are prefix-cache hits included in average latency?
- Is throughput reported as output tokens only or input plus output tokens?
- Are failed or truncated requests included?
- Are batch and concurrency equivalent?

Module benchmark plan:

| Module | Benchmark focus |
| --- | --- |
| Attention | Prefill/decode shapes, head dims, GQA/MQA, context lengths, page sizes, causal mask |
| GEMM | Dense and grouped GEMM, dtype, layout, batch/expert shapes, workspace, Tensor Core use |
| MoE routing | Top-k, token permutation, expert grouping, load imbalance, dispatch overhead |
| MoE MLP | Expert GEMM, activation fusion, quantized weights, scatter/gather cost |
| Activation/norm/RoPE | Fusion boundary, memory bandwidth, vectorization, layout compatibility |
| KV cache | Allocation, block lookup, append/update, prefix lookup, eviction, fragmentation |
| Quant/dequant | Weight-only matmul, activation quantization, KV quantization, calibration overhead |
| Scheduler | Iteration cost, prefill/decode mixing, queueing delay, continuous batching decisions |
| Sampling | GPU vs CPU sampling, top-k/top-p, penalties, synchronization overhead |

Benchmark quality gates:

- Include correctness checks against a reference implementation.
- Use warmup plus fixed repetitions.
- Synchronize around GPU timing.
- Report p50/p90/p95/p99, not only mean.
- Save raw artifacts before summarizing.
- Never compare module timings when tensor shapes or dtypes differ.

## Artifacts

- `current/agent_outputs/ELLM-20260616-03_perf-analyst.md`
- `memory/ROADMAP.md`

## Risks or Blockers

Without source-level timing inspection, e2e metrics from different repos are not automatically comparable. Edge devices need thermal and power controls or repeated runs become misleading.

## Recommended Next Step

Ask `architect` to convert the benchmark plan and competitor strategy matrix into a prioritized optimization roadmap for the current repo.
