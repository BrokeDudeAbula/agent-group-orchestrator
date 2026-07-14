# Roadmap

## Optimization Directions

| Priority | Direction | Expected Impact | Cost | Evidence Needed | Risks | Validation Method |
|---|---|---|---|---|---|---|
| P0 | Unify e2e benchmark timing semantics | Prevent invalid competitor comparisons and expose real bottlenecks | Medium | Current repo timing code, competitor timing code, raw benchmark artifacts | Requires agreement on metric definitions | Run fixed prompt/output matrix and publish raw JSON/CSV plus timing window docs |
| P0 | Add module benchmark harness for hot operators | Makes attention, GEMM, MoE, KV, scheduler, and sampling bottlenecks measurable | Medium | Operator entrypoints, shapes, dtypes, correctness references | Shape mismatch can invalidate comparisons | Run shape matrix with warmup, repetitions, CUDA sync, p50/p95/p99, and correctness checks |
| P1 | Improve KV cache and prefix caching strategy | Lower TTFT for repeated prefixes and reduce decode memory pressure | High | Cache hit rate, fragmentation, page/block lookup cost, memory profile | Extra metadata and eviction complexity | Compare cold, warm-prefix, and no-cache workloads with identical prompts |
| P1 | Prioritize attention and decode-path fusion | Improve decode tokens/s and inter-token latency | High | Attention profile, memory bandwidth, kernel launch counts | Kernel specialization may reduce portability | Benchmark prefill/decode attention shapes across context lengths and batch sizes |
| P1 | Evaluate quantization coverage for edge targets | Reduce memory footprint and improve throughput per watt | High | Accuracy tolerance, kernel coverage, calibration data, weight/KV formats | Accuracy loss and unsupported kernels | Compare FP16/BF16, FP8 if available, INT8, and INT4 under same workload |
| P2 | Optimize MoE routing and grouped GEMM | Improve MoE throughput and reduce token dispatch overhead | High | Expert shapes, top-k routing cost, load balance, scatter/gather profile | MoE path may be model-specific | Benchmark routing, permutation, grouped GEMM, and expert MLP separately |
| P2 | Improve scheduler prefill/decode batching | Balance throughput and TTFT under concurrency | Medium | Queueing traces, prefill/decode iteration timing, fairness metrics | Can improve throughput while hurting tail latency | Run concurrency matrix and report TTFT p95 plus decode tok/s |
| P3 | Investigate MTP or speculative decoding | Potentially improve output tokens/s | High | Acceptance rate, draft overhead, memory overhead, model support | Complex implementation and edge memory pressure | Prototype only after benchmark harness exists; compare accepted tokens/s and quality impact |
