# AUTO-20260608-118 R0G predecode WMMA probe

日期：2026-06-08

## Scope

新增并验证 spike-only `routed_grouped_independent_w4a16_predecode_wmma_smoke`：

- 不修改 production Qwen3.5 推理路径。
- 不调用 NNCL `MoeFCGemm`、`MoeGroupGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 作为 candidate。
- raw HF GPTQ 权重只在 timed loop 外预解码为 row-major fp16，用于归因。
- same-run NNCL `MoeGroupGemm` 只作为 baseline/diff。
- 所有输出保持 probe-only。

## Code Changes

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`

核心实现：

- 新增 mode：`routed_grouped_independent_w4a16_predecode_wmma_smoke`。
- 新增 `PredecodedFp16GroupedWmmaKernel`。
- 复用 HF GPTQ dequant 结果，但在 plan 阶段转为 row-major fp16 weight buffer，避免 timed loop 内 decode。
- 每 iteration 仍为 single grouped WMMA launch。
- CSV `candidate_launches_per_iter=1`。

## Verification

本地构建 PASS：

```text
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

`orin_1` 同步与构建 PASS：

```text
bash sync_orin_lape_build.sh --target orin_1 --source /workspace/liyang/lape_a6d6bfb9 --sync-only
cmake --build /workspace/liyang/workspace/lape/build --target qwen3_5_cute_dsl_spike -j 4
```

Smoke results：

| shape | candidate_ms | nncl_ms | ratio | active_experts | launches/iter | precision_pass |
|---|---:|---:|---:|---:|---:|---|
| A/M64/gate_proj | 2.420152 | 0.321988 | 7.516270 | 37 | 1 | true |
| A/M898/gate_proj | 5.940392 | 0.487489 | 12.185688 | 117 | 1 | true |

Evidence：

- `analysis/Qwen35_cutedsl_r0g_predecode_wmma_probe_20260608_118/report.md`
- `analysis/Qwen35_cutedsl_r0g_predecode_wmma_probe_20260608_118/predecode_wmma_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_predecode_wmma_probe_20260608_118/predecode_wmma_m898_orin1.csv`

## Boundary

CSV/log fields remain:

- `independent_candidate=false`
- `candidate_audit_pending=true`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Decision

Do not promote. Predecode removes raw decode from the timed loop, but ratios remain `7x+` for M64 and `12x+` for M898. This points away from decode-only attribution and toward naive WMMA tile scheduling, especially per-expert 16-row tile padding and poor small-row utilization.

Next useful work is a hybrid/small-row-aware probe or a real CUTLASS-style fused grouped mainloop. This predecode smoke is attribution-only and not formal evidence.
