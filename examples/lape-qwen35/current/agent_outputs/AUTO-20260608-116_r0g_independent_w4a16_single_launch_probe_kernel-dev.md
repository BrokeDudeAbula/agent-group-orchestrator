# AUTO-20260608-116 R0G independent W4A16 single-launch probe

日期：2026-06-08

## Scope

实现并验证 spike-local `routed_grouped_independent_w4a16_single_launch_smoke`：

- 不修改 production Qwen3.5 推理路径。
- 不调用 NNCL `MoeFCGemm`、`MoeGroupGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 作为 candidate。
- same-run NNCL `MoeGroupGemm` 只作为 baseline/diff。
- 所有输出保持 probe-only。

## Code Changes

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `samples/micro_bench/spike/cute_dsl/README.md`

核心实现：

- 新增 `RawGptqW4A16GroupedSingleLaunchKernel`。
- 在 timed loop 外预构造 `row_to_expert` 与 raw `qweight/scales` device pointer arrays。
- 每 iteration 只 launch 一个 grouped raw CUDA kernel。
- CSV `candidate_launches_per_iter=1`。

## Verification

本地构建 PASS：

```text
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

`orin_1` 同步与构建 PASS：

```text
bash sync_orin_lape_build.sh --target orin_1 --source /workspace/liyang/lape_a6d6bfb9
cmake .. -DLAPE_BUILD_SPIKE_CUTE_DSL=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87
cmake --build . --target qwen3_5_cute_dsl_spike -j 4
```

Smoke results：

| shape | candidate_ms | nncl_ms | ratio | launches/iter | precision_pass |
|---|---:|---:|---:|---:|---|
| A/M64/gate_proj | 2.766093 | 0.487725 | 5.671422 | 1 | true |
| A/M898/gate_proj | 14.064703 | 1.411296 | 9.965807 | 1 | true |

NCU candidate isolation：

- filter：`regex:RawGptqW4A16GroupedSingleLaunchKernel`
- captured kernel：`unnamed>::RawGptqW4A16GroupedSingleLaunchKernel(...)`
- duration：`716,864 ns / 712,704 ns`
- achieved occupancy：`97.82% / 97.80%`
- no `MoeFCGemm` in NCU output

Evidence：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/report.md`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/single_launch_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/single_launch_m898_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/single_launch_ncu_m64.csv`

## Boundary

CSV/log fields remain:

- `independent_candidate=false`
- `candidate_audit_pending=true`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Decision

Do not promote. Single-launch removed per-expert launch overhead but ratio remains `5.67x/9.97x`, so raw SIMT W4A16 smoke is still far from NNCL. Further useful work requires a true independent TensorCore/int4 W4A16 grouped mainloop or a new formal task; this probe remains not formal and not tier eligible.
