# AUTO-20260609-130 R0H M3 Gate Checklist

## Scope

本 checklist 用于审查 `Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 的 M3：Scale Iterator + Packed B Pipeline smoke。

M3 仍是 probe-only，不生成 SOP/tier evidence，不生成 `orin_1` 性能结论。

## Required Shape

- single expert
- `gate_proj`
- `K=2048`
- `N=512`
- `group_size=128`
- synthetic input 可接受
- `nncl_ms=NA` 可接受

## Candidate Requirements

- 新 mode 应独立于 M2，例如 `routed_grouped_r0h_fused_w4a16_packed_scale_pipeline_smoke`。
- candidate kernel 不得调用或包装：
  - `MoeFCGemm`
  - `MoeGroupGemmRunner`
  - `dispatch_moe_gemm_to_cutlass`
  - NNCL `cutlass_extensions` fastpath
- timed candidate 内不得：
  - full `dense_B_fp16 [K,N]` predecode
  - `cudaMalloc`
  - host/device copy
  - torch allocation/copy/contiguous
  - inner sync unrelated to kernel timing
- B/qweight tile 必须 staged 到 shared memory 或明确的 shared staging buffer。
- scale tile 必须 staged 到 shared memory 或明确的 shared staging buffer。
- dequant 必须发生在 mainloop/tile 内，并送入 WMMA/Tensor Core。
- `group_size=128` scale row 前进逻辑必须明确。
- `candidate_launches_per_iter=1`。

## CSV / Notes Requirements

必须保守输出：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`
- `independent_candidate=false`
- `nncl_ms=NA`
- `candidate_vs_nncl_ratio=NA`

notes 或列中必须明确：

- `b_tile_shared=true`
- `scale_tile_shared=true`
- `full_b_predecode=false`
- `scale_iterator_group128`
- `paired_nncl_baseline_pending`
- `not_formal`
- `not_tier`

## Local Verification

必须尝试：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

若 build 通过，运行：

```bash
build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=routed_grouped_r0h_fused_w4a16_packed_scale_pipeline_smoke --m_filter=64 --warmup=1 --iters=1 --projection=gate_proj --output_csv=analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local.csv
```

通过条件：

- process exit code `0`
- `precision_pass=true`
- `finite=true`
- `nonzero > 0`
- `nan_count=0`
- `inf_count=0`

## Not Covered

M3 本地 smoke 不要求：

- `orin_1` sync/build
- NCU capture
- same-run NNCL paired baseline
- family A/B 10 shape
- MoE grouped problem visitor

这些属于 M4/M5/M6 或 R4 门禁后的工作。
