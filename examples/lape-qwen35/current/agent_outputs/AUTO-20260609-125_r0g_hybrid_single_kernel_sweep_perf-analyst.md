# AUTO-20260609-125 R0G Hybrid Single-Kernel Sweep - perf-analyst

## 摘要

在 AUTO-124 的 `--hybrid_single_kernel=1` 和 `--wmma_packed_loader=1` 基础上，扫描：

- `hybrid_small_row_threshold={1,2,4,8,12,15}`
- `wmma_n_warps={8,16}`
- M64/M898，`gate_proj`

本轮没有新增代码改动，复用 AUTO-124 已验证的 spike binary。

## Evidence

- 远端/本地输出目录：
  `analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_sweep_20260609_125/`
- 报告：
  `analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_sweep_20260609_125/report.md`

## Guard

- CSV 文件：24
- CSV 行：24
- `guard_errors=0`
- 所有行 `precision_pass=true`
- 所有行 `candidate_launches_per_iter=1`
- 所有行固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`
- 所有行固定 `independent_candidate=false`、`candidate_audit_pending=true`
- candidate NNCL usage flags 均为 false；baseline NNCL usage flag 为 true

## 结果

Best common combo：

| threshold | wmma_n_warps | geomean | M64 ratio | M898 ratio |
|---:|---:|---:|---:|---:|
| 1 | 16 | 2.180785x | 2.548206x | 1.866342x |

Per-shape best：

| M | best threshold | best warps | ratio | candidate_ms | nncl_ms |
|---:|---:|---:|---:|---:|---:|
| 64 | 2 | 8 | 2.212469x | 1.066032 | 0.481829 |
| 898 | 1 | 16 | 1.866342x | 2.112904 | 1.132109 |

## 结论

AUTO-125 比 AUTO-124 最佳 geomean `2.492910x` 有改善，达到 `2.180785x`，但仍远高于目标 `<=1.20x`。这证明 single-kernel 后 threshold/warps 最佳点确实变化，但参数微调仍不能闭合性能差距。

状态：`done / probe-only / not formal / not tier / not production`。

建议停止泛参数微调当前 raw CUDA/WMMA hybrid kernel；若继续，应转向小行 SIMT rewrite 或真正 independent CUTLASS-style fused GPTQ W4A16 grouped mainloop，并新建 formal task 重走 SOP-A/B/C。
