# AUTO-20260609-133 R0H M4 Grouped Visitor Smoke

## Summary

`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 已推进到 M4 本地结构 smoke 完成。

当前恢复点：

```text
in_progress / M0-M4 local structural smoke done / M5 pending R4 / orin_1_only / spike_only / not_formal
```

## Scope

- Mode: `routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke`
- Candidate kernel: `R0HFusedW4A16GroupedVisitorWmmaKernel`
- Shape: synthetic grouped `gate_proj`, `K=2048`, `N=512`, `group_size=128`
- Input: synthetic HF raw GPTQ qweight/scales
- Baseline: no same-run NNCL baseline in this local smoke, `nncl_ms=NA`

## Files

- Added:
  - `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_grouped_visitor_smoke.cu`
- Updated:
  - `samples/micro_bench/spike/cute_dsl/main.cc`
  - `samples/micro_bench/spike/cute_dsl/spike_common.h`
  - `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- Evidence:
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local.csv`
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_maincheck.csv`
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_m128.csv`
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_notes.md`

## Structural Properties

- uses `cu_row_prefix` and `padded_cu_row_prefix`
- maps padded global tile row to expert slot and local expert row
- writes compact routed grouped output via `cu_row_prefix`
- keeps packed B/qweight tile staged through shared buffers
- keeps scale tile staged through shared buffers
- dequant happens inside the WMMA tile/mainloop before Tensor Core MMA
- no full `dense_B_fp16 [K,N]` predecode in the timed candidate path
- candidate launch count is `1`
- candidate file does not include NNCL `cutlass_extensions` fastpath headers
- candidate does not call or wrap `MoeFCGemm`, `MoeGroupGemmRunner`, or `dispatch_moe_gemm_to_cutlass`

## Local Verification

Build:

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

Result: PASS.

Worker smoke:

```bash
build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke --m_filter=64 --warmup=1 --iters=1 --projection=gate_proj --output_csv=analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local.csv
```

Result: PASS.

Key fields:

- `active_experts=4`
- `expert_row_counts=7|13|19|25`
- `cu_row_prefix=0|7|20|39|64`
- `padded_cu_row_prefix=0|16|32|64|96`
- `candidate_ms=0.236384`
- `reference_ms=0.060224`
- `max_abs_vs_reference=3.05548310e-05`
- `rmse_vs_reference=8.04463902e-06`
- `precision_pass=true`
- `candidate_launches_per_iter=1`
- `grouped_problem_visitor=true`
- `cu_row_prefix_visitor=true`
- `nncl_ms=NA`

Main-orchestrator smoke rerun:

```bash
build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke --m_filter=64 --warmup=1 --iters=1 --projection=gate_proj --output_csv=analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_maincheck.csv
```

Result: PASS.

Key fields:

- `candidate_ms=0.430688`
- `reference_ms=0.060992`
- `max_abs=3.055483e-05`
- `rmse=8.044639e-06`
- `precision_pass=true`

Active expert variation:

- `m_filter=128` rerun PASS after local GPU memory pressure was avoided.
- `active_experts=3`
- `expert_row_counts=23|43|62`
- `cu_row_prefix=0|23|66|128`
- `candidate_launches_per_iter=1`
- `precision_pass=true`

## Review

Reviewer conclusion: `PASS`.

Reviewer confirmed:

- help/parse/dispatch/CMake are wired for the new mode
- candidate file does not include or call NNCL fastpath symbols
- grouped visitor logic is not single-expert flatten
- CSV/notes contain required conservative fields

## Boundary

This is local structural smoke only.

Do not claim:

- formal M4 acceptance
- SOP-A/SOP-C pass
- tier eligibility
- `orin_1` performance
- same-run NNCL ratio
- NCU candidate isolation

Required conservative flags remain:

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`
- `independent_candidate=false`

## Next Step

M5 is `orin_1` family A/B full probe. Before execution, R4 requires:

- exact command
- expected runtime
- output directory
- stop conditions

No `orin_1` sync/build, NCU, or paired NNCL baseline was run in M4.
