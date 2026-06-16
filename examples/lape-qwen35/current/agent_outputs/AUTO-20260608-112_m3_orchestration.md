# AUTO-20260608-112 M3 Orchestration

## 结论

M3 structural grouped dense probe 已完成，但 R0F/R1-probe 继续停在 probe-only hold。原因是 grouped dense fp16 candidate 虽然比 serial per-expert path 快很多，但相对 same-run NNCL grouped W4A16 baseline 仍连续两轮明显 `>1.50x`，远高于目标 `<=1.20x`。

当前状态：

`blocked / M3 grouped_dense_ratio_gt_1p50 / probe-only / not production`

不进入：

- M3 Candidate NCU Isolation
- M4 Grouped/Batched Launch formal probe
- M5 W4A16 feasibility promotion
- R1/R3/production

## 执行内容

本轮在 spike 范围内新增并修正：

- `--mode=routed_grouped_dense_probe`
- CUTLASS `GemmGrouped` TensorOp dense fp16 single-projection candidate
- serial per-expert dense fp16 对照
- same-run NNCL grouped `MoeGroupGemm` baseline
- family B `down_proj` 的预构造 `silu(gate)*up` 输入

所有实现仍在 probe-only 范围内。

## Evidence

目录：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/`

关键文件：

- `build_grouped_dense_probe.log`
- `build_grouped_dense_probe.rc`
- `r0f_m3_grouped_dense_m64_gate.log`
- `r0f_m3_grouped_dense_m64_gate.rc`
- `r0f_m3_grouped_dense_all.csv`
- `r0f_m3_grouped_dense_all.log`
- `r0f_m3_grouped_dense_all.rc`
- `r0f_m3_grouped_dense_all_repeat.csv`
- `r0f_m3_grouped_dense_all_repeat.log`
- `r0f_m3_grouped_dense_all_repeat.rc`

Worker-style outputs：

- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_orin-runner.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_perf-analyst.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_reviewer.md`

## Ratio

第一轮：

- family A grouped/NNCL geomean：`4.442753x`
- family B grouped/NNCL geomean：`4.092893x`
- family A grouped/serial geomean：`0.266817x`
- family B grouped/serial geomean：`0.768473x`

第二轮：

- family A grouped/NNCL geomean：`4.412637x`
- family B grouped/NNCL geomean：`4.208391x`
- family A grouped/serial geomean：`0.264910x`
- family B grouped/serial geomean：`0.753515x`

small/hot repeat：

- M64：A `5.460091x`，B `3.447001x`
- M898：A `3.798590x`，B `3.878818x`

## Field Checks

两轮 10 shape 均满足：

- rows=10
- `precision_pass=true`
- `timing_contaminated=false`
- `nan_count_vs_serial=0`
- `inf_count_vs_serial=0`
- `nan_count_vs_nncl=0`
- `inf_count_vs_nncl=0`
- `nonzero_vs_serial>0`
- `nonzero_vs_nncl>0`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## 归因

M3 证明 serial launch overhead 是问题之一，但不是达到 NNCL baseline 的充分条件：

- family A grouped 相比 serial 显著变快；
- family B grouped 相比 serial 也变快，但幅度较小；
- grouped dense fp16 仍比 NNCL grouped W4A16 慢约 `4x`。

当前主要缺口更接近权重量化/访存和 kernel specialization：

- candidate 使用 dense fp16 dequant weight；
- NNCL baseline 使用 packed W4A16 grouped path；
- candidate 未实现 fused GPTQ W4A16 decode+matmul；
- candidate 不是 MoE small-M/W4A16 专用 kernel。

## 后续边界

本轮不启动 NCU，因为 ratio 已触发停止条件。若继续推进，建议不再沿用 dense fp16 grouped candidate，而是二选一：

- 新建 formal 前置 probe：fused GPTQ W4A16 decode+matmul grouped candidate。
- 转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`，profile NNCL grouped path 周边优化 ROI。

任何正式 candidate 必须新建 task，并重新走 SOP-A/B/C。
