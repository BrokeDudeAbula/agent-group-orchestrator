# Acceptance

- Cover operator implementation strategies for FlashAttention, MoE MLP, MoE routing, GEMM, activation, top-k, and other common LLM kernels.
- Cover inference acceleration strategies including MTP, quantization, prefix caching, KV cache management, batching, and graph or engine capture where applicable.
- Define an e2e comparison method for speed, throughput, TTFT, ITL, latency, and timing semantics between the current repo and researched repos.
- Define a module-level benchmark method for operators, scheduler paths, cache management, quantization kernels, and MoE paths.
- Separate verified facts from hypotheses and mark evidence quality.
- Produce optimization directions for the current repo and record them in `memory/ROADMAP.md`.
- Produce reviewer-checked next steps without making code changes.
