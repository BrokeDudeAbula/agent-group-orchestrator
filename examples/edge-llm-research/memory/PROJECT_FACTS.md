# Project Facts

## Repository Layout

- Demo assumption: the target repo is an edge-deployed LLM inference engine.
- Expected areas to inspect in a real run: model loader, runtime scheduler, attention kernels, GEMM and MoE kernels, KV cache, quantization, sampling, benchmark scripts, and deployment docs.

## Important Entrypoints

- E2E inference entrypoint: unknown until the real repo is inspected.
- Module benchmark entrypoint: unknown until benchmark scripts are inspected.
- Timing logic entrypoint: unknown until e2e scripts, server code, and profiling hooks are inspected.

## Validation Commands

- Read-only repo discovery is R0.
- Local short benchmark runs are at least R2 and should record command, model, hardware, warmup, repetitions, and output path.
- Remote device runs, long profiling, power measurement, and dependency installation are R4 and require a gate.

## External Dependencies To Research

- `trt-edge-llm`
- `vLLM`
- TensorRT-LLM
- SGLang
- MLC-LLM

## Uncertain Facts

- Current repo operator implementation details are unknown in this static demo.
- Competitor implementation details must be verified from source, official docs, or benchmark artifacts in a real run.
- Benchmark comparability is unknown until timing windows and workload settings are aligned.
