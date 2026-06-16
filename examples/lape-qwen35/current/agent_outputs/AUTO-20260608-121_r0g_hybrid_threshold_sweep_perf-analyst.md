# AUTO-20260608-121 R0G Hybrid Threshold Sweep

日期：2026-06-08

## Scope

对 `routed_grouped_independent_w4a16_hybrid_smallrow_smoke` 做 threshold sweep，只覆盖 spike/local probe，不修改 production path。

Evidence：

- `analysis/Qwen35_cutedsl_r0g_hybrid_threshold_sweep_20260608_121/`
- `analysis/Qwen35_cutedsl_r0g_hybrid_threshold_sweep_20260608_121/report.md`

## Guard

12 条 CSV 均通过：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `independent_candidate=false`
- `candidate_audit_pending=true`
- `precision_pass=true`

## Results

| threshold | M64 ratio | M898 ratio | geomean |
|---:|---:|---:|---:|
| 1 | 3.346587 | 4.754960 | 3.989096 |
| 2 | 2.910517 | 3.762374 | 3.309147 |
| 4 | 3.798328 | 3.281669 | 3.530560 |
| 8 | 2.962878 | 5.609194 | 4.076685 |
| 12 | 2.565185 | 8.028260 | 4.538058 |
| 15 | 3.004421 | 7.592198 | 4.775998 |

## Verdict

最佳 common threshold 为 `2`，geomean `3.309147x`；最佳单点 M64 为 threshold `12`，ratio `2.565185x`；最佳单点 M898 为 threshold `4`，ratio `3.281669x`。

判定：

- `done / probe-only / not formal`
- `not tier`
- 不 promoted

threshold tuning 无法达到 `<=1.20x`；它只证明 small-row 分流有局部收益，不证明当前 raw CUDA/WMMA attribution kernel 可成为 formal candidate。
