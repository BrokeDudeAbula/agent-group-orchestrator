# AUTO-20260609-131 R0H M3 Packed Scale Pipeline Smoke

## Summary

`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 已推进到 M3 本地结构 smoke 完成。

当前恢复点：

```text
in_progress / M0-M3 local structural smoke done / M4 pending / orin_1_only / spike_only / not_formal
```

## Scope

- Mode: `routed_grouped_r0h_fused_w4a16_packed_scale_pipeline_smoke`
- Candidate kernel: `R0HFusedW4A16PackedScalePipelineWmmaKernel`
- Shape: single expert, `gate_proj`, `M=64`, `K=2048`, `N=512`, `group_size=128`
- Input: synthetic HF raw GPTQ qweight/scales
- Baseline: no same-run NNCL baseline in this local smoke, `nncl_ms=NA`

## Files

- Added:
  - `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_packed_scale_pipeline_smoke.cu`
- Updated:
  - `samples/micro_bench/spike/cute_dsl/main.cc`
  - `samples/micro_bench/spike/cute_dsl/spike_common.h`
  - `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`

## Structural Properties

- packed B/qweight tile is staged through shared buffers
- scale tile is staged through shared buffers
- scale iterator advances at `group_size=128`, equivalent to every 8 WMMA `k16` tiles
- dequant happens inside the WMMA tile/mainloop before Tensor Core MMA
- no full `dense_B_fp16 [K,N]` predecode in the timed candidate path
- candidate launch count is `1`
- candidate does not call or wrap `MoeFCGemm`, `MoeGroupGemmRunner`, or `dispatch_moe_gemm_to_cutlass`

## Local Verification

Build:

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

Result: PASS.

Smoke:

```bash
build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=routed_grouped_r0h_fused_w4a16_packed_scale_pipeline_smoke --m_filter=64 --warmup=1 --iters=1 --projection=gate_proj --output_csv=analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local.csv
```

Result: PASS after local memory pressure was avoided; latest CSV row:

- `candidate_ms=0.213408`
- `reference_ms=0.059072`
- `max_abs=3.05548310e-05`
- `rmse=7.99963300e-06`
- `finite=true`
- `nonzero=32768`
- `precision_pass=true`
- `nncl_ms=NA`

Rerun CSV also passed:

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local_rerun.csv`

## Review

Reviewer initial conclusion: `MINOR`.

Issue: CSV/notes lacked the exact token `paired_nncl_baseline_pending`.

Fix: token was added to `spike_common.h`, then local build and smoke rerun passed.

## Boundary

This is local structural smoke only.

Do not claim:

- formal M3 acceptance
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

M4 should add the MoE grouped problem visitor:

- use `cu_row / total_rows_before_expert`
- support active experts changes
- keep candidate launch count target at 1
- continue to avoid NNCL candidate wrapping

Before any `orin_1` build, smoke, or NCU run, R4 requires explicit command, expected time, output directory, and stop conditions.
