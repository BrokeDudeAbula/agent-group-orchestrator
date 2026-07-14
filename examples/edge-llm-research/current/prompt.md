# Complete Prompt

Use `agent-group auto-orchestrate` mode for this goal:

We are working in a repository that implements an edge-deployed LLM inference engine. Organize the agent group to research competitor inference engines, especially `trt-edge-llm`, `vLLM`, and other relevant projects such as TensorRT-LLM, SGLang, and MLC-LLM when useful.

Research scope:

1. Operator implementation strategy.
   - Compare common LLM operators and kernels, including FlashAttention, MoE MLP, MoE routing, GEMM, activation functions, top-k, normalization, rotary embedding, sampling, and cache update paths.
   - For each operator, identify whether each repo uses vendor libraries, custom CUDA/CUTLASS/Triton kernels, TensorRT plugins, graph capture, fused kernels, or framework-native kernels.
   - Record shape assumptions, precision support, memory layout, batching behavior, edge-device constraints, and portability risks.

2. Inference acceleration strategy.
   - Research MTP, speculative decoding, quantization, prefix caching, KV cache management, paged attention, continuous batching, CUDA graphs, TensorRT engine build choices, cache eviction, and scheduler behavior.
   - Separate strategies that improve TTFT, decode throughput, memory footprint, or power efficiency.
   - Mark whether a strategy is suitable for edge deployment, server deployment, or both.

3. E2E comparison testing.
   - Design how to compare the current repo with the researched repos for e2e inference speed and throughput.
   - Clarify which metrics should be compared: TTFT, inter-token latency, end-to-end latency, tokens per second, requests per second, peak memory, warmup time, model load time, power, and thermal throttling.
   - Determine whether the current repo and researched repos define timing windows consistently: tokenization included or excluded, model load included or excluded, prefill and decode separated or combined, warmup discarded or included, streaming timestamps source, synchronization points, batch composition, and output length control.
   - Define comparable test cases for prompt length, output length, batch size, concurrency, model family, quantization, context length, and hardware target.

4. Module and operator benchmark testing.
   - Design module-level benchmarks for attention, MoE routing, MoE MLP, GEMM, activation, top-k, sampling, KV cache allocation/update, prefix cache lookup, scheduler iteration, quantization/dequantization, and tokenizer or post-processing if relevant.
   - Specify benchmark inputs, shape matrix, precision, warmup, repetitions, synchronization, correctness checks, memory metrics, and artifact format.
   - Identify how to map competitor benchmark scripts or kernels onto the current repo so results are comparable.

5. Optimization roadmap.
   - Based on the research, propose optimization directions for the current repo.
   - Put optimization directions into `memory/ROADMAP.md`.
   - For each roadmap item, include priority, expected impact, implementation cost, evidence needed, risks, and validation method.

Agent-group routing requirements:

- `repo-explorer`: read the current repo and summarize existing model support, operator stack, scheduler, KV cache, quantization, benchmark scripts, timing logic, and edge hardware assumptions.
- `oss-scout`: research competitor repos and official docs. Do not copy code. Record source links, licenses, and non-transferable assumptions.
- `perf-analyst`: define e2e and module benchmark methodology, timing semantics, metric alignment, and evidence quality requirements.
- `architect`: convert the findings into design tradeoffs and a prioritized roadmap for the current repo.
- `reviewer`: check unsupported claims, missing evidence, benchmark comparability, license risk, and whether roadmap items are actionable.
- `main-orchestrator`: update `current/tasks.csv`, `current/STATE.md`, `memory/TASK_LEDGER.md`, `memory/PROGRESS_LEDGER.md`, `memory/RISKS.md`, `memory/DECISIONS.md`, `memory/PROJECT_FACTS.md`, and `memory/ROADMAP.md`.

Risk gates:

- This is read-only research unless explicitly approved otherwise.
- Do not run remote benchmarks, long profiling jobs, dependency installs, or cost-incurring commands without an R4 gate.
- Do not modify core source code during research.
- For all claims, distinguish verified facts, source-backed observations, and hypotheses.

Expected final report:

- Research coverage summary.
- Workers selected and skipped.
- Files and sources inspected.
- Operator strategy comparison.
- Inference acceleration comparison.
- E2E benchmark comparison plan.
- Module benchmark comparison plan.
- Timing semantics checklist.
- Roadmap items added to `memory/ROADMAP.md`.
- Remaining blockers, risks, and next steps.
