# AUTO-20260609-132 R0H M4 Gate Checklist

## Scope

本 checklist 用于审查 `Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 的 M4：MoE grouped problem visitor structural smoke。

M4 仍是 probe-only，不生成 SOP/tier evidence，不生成 `orin_1` 性能结论。

## Required Shape

- `gate_proj`
- synthetic HF raw GPTQ qweight/scales 可接受
- 多 active experts，必须 `active_experts > 1`
- row count 必须支持 active experts 变化，不可退化为 single expert
- `nncl_ms=NA` 可接受

## Candidate Requirements

- 新 mode 应独立于 M3，例如 `routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke`。
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
- 必须保留 M3 结构属性：
  - packed B/qweight tile staged to shared buffer
  - scale tile staged to shared buffer
  - dequant in WMMA tile/mainloop
  - `group_size=128` scale iterator
- 必须新增 grouped visitor 属性：
  - `grouped_problem_visitor=true`
  - `cu_row_prefix_visitor=true` 或等价精确说明
  - `total_rows_before_expert` / prefix metadata 明确存在
  - block/tile 根据 global row tile 映射到 expert slot 与 local expert row
  - output row layout 明确是 routed/grouped row prefix
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

- `grouped_problem_visitor=true`
- `cu_row_prefix_visitor=true`
- `active_experts>1`
- `b_tile_shared=true`
- `scale_tile_shared=true`
- `full_b_predecode=false`
- `scale_iterator_group128`
- `packed_b_iterator=true`
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
build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke --m_filter=64 --warmup=1 --iters=1 --projection=gate_proj --output_csv=analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local.csv
```

通过条件：

- process exit code `0`
- `precision_pass=true`
- `finite=true`
- `nonzero > 0`
- `nan_count=0`
- `inf_count=0`
- `active_experts > 1`
- `routed_rows == m_filter` 或 notes 明确解释 synthetic routing row count
- `candidate_launches_per_iter=1`

## Not Covered

M4 本地 smoke 不要求：

- `orin_1` sync/build
- NCU capture
- same-run NNCL paired baseline
- family A/B 10 shape
- formal promotion

这些属于 M5/M6/M7 或 R4 门禁后的工作。
