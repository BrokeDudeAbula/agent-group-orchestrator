# AUTO-20260608-112 M2 Orchestration

## 结论

M2 Timing hygiene 完成，但 R0F/R1-probe 在 M2 触发停止条件并暂停推进。

当前状态：

- `blocked / M2 stop_condition_ratio_gt_1p50 / probe-only / not production`

原因：

- paired timed loop 已清理并标记 `timing_contaminated=false`。
- 两轮 Orin same-run NNCL paired micro 都数值正常、非零、probe-only 三项 false。
- 但 ratio 连续两轮明显 `>1.50x`，且远高于目标 `<=1.20x`：
  - 第一轮 family A/B geomean：`13.589240x / 4.937622x`
  - 第二轮 family A/B geomean：`13.388290x / 4.723811x`

按 M0 停止条件，不进入 M3 Candidate NCU Isolation，不进入 M4 Grouped/Batched Launch Probe。

## M2 通过与失败边界

M2 hygiene pass：

| 条件 | 结果 |
|---|---|
| Release/sm87 构建 | PASS：`build_rc=0` |
| paired candidate timed loop 预分配 | PASS |
| paired CSV `timing_contaminated=false` | PASS |
| 输出非零有限 | PASS：`nan_count=0`, `inf_count=0`, `nonzero>0` |
| same-run NNCL baseline | PASS：`baseline_source=nncl_grouped_moe_group_gemm_paired_same_run` |
| probe-only 标记 | PASS：`valid_for_sop_a=false`, `valid_for_sop_c=false`, `tier_eligible=false` |

R0F/R1-probe performance gate fail：

| 判据 | 结果 |
|---|---|
| family A geomean `<=1.20x` | FAIL：`13.589240x` / `13.388290x` |
| family B geomean `<=1.20x` | FAIL：`4.937622x` / `4.723811x` |
| hot `M898` 无灾难性退化 | FAIL：A `19.27x/19.29x`，B `4.55x/4.08x` |
| small `M64` 无灾难性退化 | FAIL：A `5.75x/5.79x`，B `6.73x/7.16x` |
| stop condition：连续两轮明显 `>1.50x` | TRIGGERED |

## Evidence

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m2_timing_hygiene_final.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_repeat.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_repeat.log`

Worker outputs：

- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_orin-runner.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_perf-analyst.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_reviewer.md`

## 归因

M2 结果把“timed loop 内 torch 分配/contiguous/host roundtrip 污染”从主因中基本排除。当前主要差距来自结构性差异：

- candidate 仍是 serial per-expert dense fp16 CUTLASS launch；
- baseline 是 NNCL grouped W4A16 `MoeGroupGemm`；
- candidate 未实现 grouped/batched launch；
- candidate 未实现 fused GPTQ W4A16 decode+matmul。

## 后续边界

本轮不继续 M3/M4。若要恢复，必须先提出新的结构性方案或新 task，例如：

- grouped/batched dense fp16 probe 的独立最小设计；
- fused GPTQ W4A16 decode+matmul candidate；
- 转向 NNCL grouped targeted profile/周边优化路线。

任何正式 candidate 必须另起 formal task 并重新走 SOP-A/B/C。
