# AUTO-20260608-86 CuTeDSL R0 Blocker Closure Todo Sync

task_id: `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
new_subtask: `Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC`
blocked_subtask: `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
date: `2026-06-08`

## 结论

当前 CuTe/CUTLASS C++ R0 进度已同步到 agent_group 记忆：R0d 已 `done / diagnostic-only`，R0e formal SOP-A/B/C 继续 `blocked / gated`。

本轮新增一个可推进但仍非 formal 的 blocker-closure 诊断任务：

```text
Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC
```

R0D1 的目的不是启动 R0e，而是在 `samples/micro_bench/spike/cute_dsl/` 内补齐两类 R0e blocker closure 证据：

- `topk_policy=nncl_softmax_topk`，对齐 NNCL `SoftmaxTopk<half>` 口径。
- `baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`，同一 run、同一输入、同一 routing/padding/source row 下跑 CuTe/CUTLASS candidate 与 NNCL grouped baseline。

R0D1 仍必须固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。即使 R0D1 通过，也只能进入 reviewer 复核和用户 R4 formal 确认，不得自动把 R0e 改成 `in_progress`。

## Sub-Agent 结论

- Gibbs / repo-explorer / `019ea63d-9d71-7f83-9ea5-f9a9b6af859f`：R0e blocker closure 可行，但不建议直接把 `samples/micro_bench/spike/marlin_moe/main.cc` 或整个 Marlin spike 链进 `cute_dsl` target。推荐新增 `cute_dsl` spike-local NNCL helper，复用 Marlin spike 的 NNCL `SoftmaxTopk<half>`、NNCL GPTQ pack 和 `MoeGroupGemm` 口径；不链 `liblape.so`，不使用 `B_marlin/RepackQweightToMarlin/perm64`。
- Fermat / reviewer / `019ea63d-ca66-72b3-b9f7-6793b514eda8`：R0e blocked 解除必须同时具备 NNCL top-k、same-run paired NNCL baseline、formal SOP-A/B/C 证据包、用户 R4 确认和 reviewer 无 P0/P1。只把 top-k 改成 NNCL 但 baseline 仍是 CSV join，不能启动 R0e。建议新增 `R0D1` diagnostic 任务，R0e 继续保持 `blocked/gated`。

## R0 阶段当前状态

| 阶段 | 状态 | 结论 |
|---|---|---|
| R0a scaffold | `done` | 独立 `cute_dsl` spike target、manifest/toolchain path check 已完成；非 SOP。 |
| R0b Python CuTeDSL toolchain | `blocked` | `cutlass._mlir` 缺失，`nvidia-cutlass-dsl==4.5.0.dev0` Jetson aarch64 wheel 不可得。 |
| CuTe/CUTLASS C++ fallback smoke | `done` | 本地和 `orin_1` CuTe C++ tutorial compile/run PASS。 |
| aligned shape bench | `done / diagnostic-only` | Marlin SOP-C 10 shape synthetic fp16 dense fallback PASS；非 SOP。 |
| R0c projection correctness | `done / diagnostic-only` | `orin_1` 9/9 projection case PASS；非 SOP。 |
| R0d routed grouped micro | `done / diagnostic-only` | `orin_1` 10 shape PASS；top-k 仍是 torch diagnostic，baseline 仍是 formal CSV join；非 SOP。 |
| R0D1 same-run NNCL paired diagnostic | `todo` | 新增 blocker-closure 诊断任务，目标是 NNCL top-k + same-run NNCL paired baseline；仍非 SOP。 |
| R0e formal SOP-A/B/C | `blocked / gated` | 需 R0D1/reviewer/R4/formal package 闭合后才可启动。 |

## R0 待办清单

1. `Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC`
   - 在 `samples/micro_bench/spike/cute_dsl/` 内新增 spike-local NNCL helper。
   - 调用 `alios::nncl::SoftmaxTopk<half>` 重建 top-k metadata，输出 `topk_policy=nncl_softmax_topk`。
   - 明确 `source_row_policy=token_major_source_row_for_replay`，不要把 NNCL 原始 slot-major `source_row` 误当 grouped input index。
   - 新增 cute_dsl-local NNCL GPTQ pack，只保留 NNCL `MoeGroupGemm` 需要的 raw GPTQ -> NNCL layout 路径；禁止引入 Marlin packed layout。
   - 在同一进程、同一输入、同一 routing/padding/source row 下跑 CuTe/CUTLASS candidate 与 NNCL grouped baseline。
   - 输出 diagnostic CSV，固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
   - 本地 build/smoke 后同步 `orin_1` 跑 10 shape diagnostic，并由 reviewer 复核。

2. `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
   - 当前保持 `blocked / gated`。
   - 启动条件：NNCL top-k 口径闭合、same-run paired NNCL baseline 闭合、R0D1 reviewer 无 P0/P1、用户 R4 确认 formal 命令/预计耗时/输出目录/停止条件。
   - formal 输出必须包含 `sop_a_precision.csv`、`sop_b_ncu_summary.csv`、`sop_c_routed_grouped.csv`、`r0_guard_report.md`、`r0_verdict.json`。
   - 复用 Q35-022 SOP-A/B/C gate；不得使用 R0d/R0D1 diagnostic ratio/timing 直接声明 SOP-C 或 tier。

3. Python CuTeDSL route blocker closure
   - 可选，除非用户明确要回到 Python CuTeDSL route。
   - 需要 compatible Jetson CUDA 12.6 / Python 3.10 / aarch64 `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
   - 补齐 wheel 后重跑 R0b import、elementwise、tensorop smoke；C++ fallback PASS 不等于 Python route 可用。

## 禁止边界

- 不修改 production path。
- 不把 R0a/R0b/R0c/R0d/R0D1 任何 diagnostic 输出写成 SOP-A/SOP-C 或 tier evidence。
- 不直接链接 `marlin_moe/main.cc` 到 `cute_dsl` target。
- 不使用 `B_marlin`、`RepackQweightToMarlin()` 或 `perm64` scales layout。
- 不在缺用户 R4 formal 确认时启动 R0e。
