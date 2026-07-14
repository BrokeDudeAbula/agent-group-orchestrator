# ELLM-20260616-02 OSS Scout

## Task ID

ELLM-20260616-02

## Worker Name

oss-scout

## Execution Backend

example-fixture

## Sub-Agent Reference

Not applicable in static fixture.

## Scope

Research competitor LLM inference engines for operator implementation strategy and inference acceleration strategy.

## Inputs Read

- `current/prompt.md`
- `current/agent_outputs/ELLM-20260616-01_repo-explorer.md`
- `memory/PROJECT_FACTS.md`

## Commands Run

None in this static demo. In a real run, inspect upstream repositories, official docs, benchmark scripts, release notes, issues, papers, and licenses.

## Conclusion

Research should compare `trt-edge-llm`, `vLLM`, TensorRT-LLM, SGLang, and MLC-LLM using the same evidence table. Do not treat external benchmark claims as local facts; record source, hardware, model, precision, batch/concurrency, prompt/output lengths, and timing definition for every claim.

Operator research matrix:

| Area | What to inspect | Evidence to capture |
| --- | --- | --- |
| FlashAttention / attention | Kernel provider, paged attention support, prefill/decode split, GQA/MQA, causal mask, long-context behavior | Source path, supported dtypes, layout, benchmark shape |
| MoE routing and top-k | Token dispatch, expert selection, top-k implementation, load balancing, expert parallelism | Routing kernel, sorting/top-k path, token permutation cost |
| MoE MLP | Grouped GEMM, fused activation, expert batching, quantized expert weights | GEMM backend, fusion boundary, workspace and memory layout |
| Dense GEMM | cuBLASLt, CUTLASS, TensorRT engine, Triton, custom CUDA | Tile strategy if visible, dtype, quantization support |
| Activation / norm / RoPE | Fusion with GEMM or attention, custom kernels, framework fallback | Whether memory round trips are avoided |
| Sampling | Top-k/top-p, temperature, repetition penalty, CPU/GPU boundary | Per-token latency and synchronization risk |
| KV cache | Page size, allocator, eviction, prefix reuse, quantized KV | Memory fragmentation, lookup cost, cache hit accounting |

Inference acceleration research matrix:

| Strategy | Questions |
| --- | --- |
| MTP / speculative decoding | Draft model or multi-token head, acceptance logic, target model verification, edge memory overhead |
| Quantization | Weight-only, activation, KV, FP8/INT8/INT4/AWQ/GPTQ, calibration, accuracy and kernel coverage |
| Prefix caching | Hash key, eviction, partial prefix reuse, multi-tenant isolation, timing attribution |
| KV cache | Paged/block cache, contiguous cache, max context, fragmentation, reuse across requests |
| Continuous batching | Scheduler granularity, prefill/decode mixing, fairness, latency-throughput tradeoff |
| CUDA graphs / TensorRT engine | Static shape constraints, capture boundaries, rebuild cost, dynamic batch behavior |
| Edge optimization | Power mode, memory pressure, thermal throttling, binary size, dependency footprint |

## Artifacts

- `current/agent_outputs/ELLM-20260616-02_oss-scout.md`

## Risks or Blockers

External projects may use different hardware, timing windows, tokenizers, output lengths, precision, and scheduler policies. License and dependency compatibility must be checked before reusing ideas.

## Recommended Next Step

Ask `perf-analyst` to turn this research matrix into e2e and module benchmark plans with explicit metric and timing alignment.
