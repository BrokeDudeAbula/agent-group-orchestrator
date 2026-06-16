# AUTO-20260608-112 M0 Perf Analyst

## 结论

R0D1 same-run baseline 口径固定为 NNCL grouped `MoeGroupGemm`：

- `baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`
- `reference_backend=nncl_grouped_moe_group_gemm`
- `reference_source=same_run_nncl_grouped_baseline`
- ratio = `cutedsl_ms / nncl_ms`

R0D1 只可作为 diagnostic timing，不可作为 SOP-C/tier。

## R0D1 数值

R0D1 full 10 shape diagnostic PASS，但 ratio 仍极差：

| family | geomean | M64 | M898 |
|---|---:|---:|---:|
| A | 154.703951 | 89.149916 | 174.683162 |
| B | 61.561112 | 64.301698 | 82.069768 |

## R0E Formal 数值

R0E formal verdict：

- `schema_pass=true`
- `status=gate_fail`
- `overall_pass=false`
- `tier_eligible=false`

SOP-A PASS：`max_abs=6.661564e-05`，`rmse=2.843369e-06`。

SOP-B PASS：NCU `best_occupancy=31.060000`。

SOP-C FAIL：

| family | geomean | M64 | M898 | gate |
|---|---:|---:|---:|---|
| A | 152.031603 | 94.754880 | 170.410573 | FAIL |
| B | 65.925507 | 69.122485 | 71.708239 | FAIL |

旧 formal guard 判据是 family geomean `<=0.90`、hot `M898<=0.85`、small `M64<=1.00`。本 R0F/R1-probe 的用户目标改为更宽松的 family A/B geomean `<=1.20x`，且 `M64/M898` 不出现明显灾难性退化。

## 推荐字段

R0F/R1-probe CSV 建议包含：

`probe_stage,probe_only,formal_evidence,valid_for_sop_a,valid_for_sop_c,tier_eligible,baseline_source,reference_source,candidate_ms,nncl_ms,ratio,family,M,K,N,projection,precision_pass,max_abs,rmse,nan_count,inf_count,nonzero,timing_contaminated,contamination_reason,contamination_flags,notes`

M1 还应包含：

- `candidate_path=cutlass_tensorop_dense_fp16`
- `op_class=TensorOp`
- `arch=Sm80/Sm87-compatible`
- `simt_fallback_retained=true`
- `timing_contaminated=true`，除非 M2 已完成

M2 必须输出 timed loop 残留同步、分配、`.contiguous()`、copy 和 host/device roundtrip 的审计结果；如果未完全清理，必须显式 `timing_contaminated=true`。
