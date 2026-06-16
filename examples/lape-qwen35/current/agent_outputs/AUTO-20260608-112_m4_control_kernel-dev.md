# AUTO-20260608-112 M4-Control Kernel-Dev

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 改动范围

仅修改 probe/spike 范围：

- `CMakeLists.txt`
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`

未修改 production Qwen3.5 推理路径。

## 新增模式

新增 `--mode=routed_grouped_moefc_direct_probe`。

该模式直接调用 NNCL internal：

```text
alios::nncl::kernel::cutlass_kernels::MoeGroupGemmRunner<half, cutlass::uint4b_t>
```

参数与 public NNCL `MoeGroupGemm` 对齐：

- same packed GPTQ W4A16 weights
- same fp16 grouped input
- same `cu_row`
- same active experts
- same `CtaShape32x128x64_WarpShape32x32x64 / NO_SPLIT_K / split=1 / stages=3`
- `NnclActType::kNone`
- `group_size=128`

## Timing 处理

direct probe 最终采用 balanced order：

```text
direct -> NNCL -> NNCL -> direct
```

CSV 同时写出：

- `direct_ms`
- `nncl_ms`
- `direct_first_ms`
- `direct_second_ms`
- `nncl_first_ms`
- `nncl_second_ms`

旧实现中 `cudaPeekAtLastError()` 曾被放入 `run_once()` 内，导致 timed loop host-side
检查污染；已移到 warmup 后、timed loop 前，仅作为 launch error precheck。

## Probe-only 标记

所有输出固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `control_probe_only=true`
- `independent_candidate=false`

## 本地验证

本地 Release/sm87 spike build 通过：

```text
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

结果：`Built target qwen3_5_cute_dsl_spike`
