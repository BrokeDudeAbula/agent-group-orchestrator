# AUTO-20260608-119 R0G WMMA shared-A probe

日期：2026-06-08

## Scope

优化并验证 spike-only `routed_grouped_independent_w4a16_wmma_smoke`：

- 不修改 production Qwen3.5 推理路径。
- 不调用 NNCL `MoeFCGemm`、`MoeGroupGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 作为 candidate。
- same-run NNCL `MoeGroupGemm` 只作为 baseline/diff。
- 所有输出保持 probe-only。

## Code Changes

- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`

核心实现：

- `RawGptqW4A16GroupedWmmaKernel` 的 A tile 从 per-warp shared tile 改为 block-shared tile。
- `PredecodedFp16GroupedWmmaKernel` 同步改为 block-shared A tile。
- 同一 block 内 4 个 warp 处理同一 M tile 的 4 个 N tile，A tile 只加载一次后复用，减少重复 global/shared load。

## Verification

本地构建 PASS：

```text
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

`orin_1` 同步与构建 PASS，运行 `routed_grouped_independent_w4a16_wmma_smoke` M64/M898：

| shape | candidate_ms | nncl_ms | ratio | active_experts | launches/iter | precision_pass |
|---|---:|---:|---:|---:|---:|---|
| A/M64/gate_proj | 2.107414 | 0.481990 | 4.372321 | 37 | 1 | true |
| A/M898/gate_proj | 4.136431 | 0.950082 | 4.353763 | 117 | 1 | true |

Evidence：

- `analysis/Qwen35_cutedsl_r0g_wmma_shared_a_probe_20260608_119/report.md`
- `analysis/Qwen35_cutedsl_r0g_wmma_shared_a_probe_20260608_119/wmma_shared_a_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_wmma_shared_a_probe_20260608_119/wmma_shared_a_m898_orin1.csv`

## Boundary

CSV/log fields remain:

- `independent_candidate=false`
- `candidate_audit_pending=true`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Decision

Continue probe; do not promote. Shared-A reuse is a real improvement: M898 candidate drops from AUTO-117 `5.281041 ms` to `4.136431 ms`, and ratio improves to `4.353763x`. It remains far from `<=1.20x`.

Next useful work should target small expert padding / tile scheduling, B tile decode/layout, or a true CUTLASS-style fused grouped mainloop.
