# ELLM-20260616-01 Repo Explorer

## Task ID

ELLM-20260616-01

## Worker Name

repo-explorer

## Execution Backend

example-fixture

## Sub-Agent Reference

Not applicable in static fixture.

## Scope

Map the current repo as an assumed edge-deployed LLM inference engine and identify what must be inspected before competitor comparisons become factual.

## Inputs Read

- `current/prompt.md`
- `current/epic.md`
- `current/acceptance.md`
- `memory/PROJECT_FACTS.md`

## Commands Run

None in this static demo. In a real run, use `rg --files`, `rg`, build metadata, benchmark scripts, and source entrypoints.

## Conclusion

The current repo should be profiled along four axes before comparing competitors: operator stack, runtime scheduler, cache and memory system, and benchmark or timing definitions. The demo treats current-repo capabilities as assumptions until source evidence is gathered.

Required local discovery:

- Model support: dense, MoE, multimodal, quantized variants, max context, batch and concurrency constraints.
- Operator stack: attention kernels, GEMM path, MoE routing and MLP, activation, top-k, normalization, rotary embedding, sampling, and KV update.
- Runtime path: prefill, decode, scheduler loop, batching, cache allocator, stream usage, graph or engine capture.
- Benchmark path: e2e scripts, module benchmark scripts, timing windows, warmup policy, synchronization points, and output artifact schema.
- Edge assumptions: Jetson/Orin/Thor or similar target, power mode, clocks, thermal behavior, memory capacity, driver/CUDA/TensorRT version.

## Artifacts

- `current/agent_outputs/ELLM-20260616-01_repo-explorer.md`
- `memory/PROJECT_FACTS.md`

## Risks or Blockers

Any claim about the current repo is provisional until local source and benchmark scripts are inspected. Remote target runs, long profiling, and power measurements are R4.

## Recommended Next Step

Send the local capability map to `oss-scout` so competitor research can be organized around comparable operator, runtime, and benchmark dimensions.
