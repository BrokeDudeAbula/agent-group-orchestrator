# AUTO-20260608-87 CuTeDSL R0 Current Progress Sync

task_id: `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
current_subtask: `Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC`
status: `in_progress / partial implementation, not verified`
date: 2026-06-08

## 结论

当前 CuTe/CUTLASS C++ R0 主线仍为 `in_progress / P0-next`。R0a、CuTe/CUTLASS C++ smoke、aligned shape bench、R0c projection correctness、R0d routed grouped micro 均已完成；R0e formal SOP-A/B/C 仍为 `blocked / gated`。

R0D1 same-run NNCL paired diagnostic 已从纯 `todo` 进入部分实现阶段，但尚未完成、尚未编译验证、尚未本地 smoke、尚未 `orin_1` diagnostic。当前 R0D1 不能作为 SOP-A/SOP-C/tier evidence，也不能解除 R0e gate。

## 当前代码进度

已观察到的本地接线：

- `samples/micro_bench/spike/cute_dsl/spike_common.h`：已声明 `RunRoutedGroupedMicroNnclPaired`。
- `samples/micro_bench/spike/cute_dsl/main.cc`：已在 help、mode 校验和 dispatch 中接入 `--mode=routed_grouped_micro_nncl_paired`。
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`：已把 `third_party/nncl/include` 加入 include，并链接 `nncl`。
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`：已开始加入 NNCL `SoftmaxTopk<half>`、source-row policy、mismatch helper、NNCL GPTQ pack/cache 相关代码。

尚未完成的关键实现：

- `RunNnclGroupedGemm(...)`：包装 NNCL `MoeGroupGemm<half, half, kGPTQFp16Int4Groupwise>`。
- `RunOneShapeNnclPaired(...)`：在同一输入、routing、padding、source row 下执行 CuTe/CUTLASS candidate 与 same-run NNCL grouped baseline。
- R0D1 CSV writer：输出 `topk_policy=nncl_softmax_topk`、`source_row_policy=token_major_source_row_for_replay`、`baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`，并固定非 SOP/tier flags。
- `RunRoutedGroupedMicroNnclPaired(...)` 完整 mode 实现。
- 本地 `py_compile`、CMake configure/build、manifest/shape/R0D1 smoke。
- `orin_1` full diagnostic 回传和 reviewer 复核。

## Gate 边界

- R0D1 必须固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- R0D1 通过后也只能进入 reviewer 复核和用户 R4 formal 确认，不能直接启动 R0e。
- R0e 仍需 formal `sop_a_precision.csv`、`sop_b_ncu_summary.csv`、`sop_c_routed_grouped.csv`、`r0_guard_report.md`、`r0_verdict.json`。
- 继续禁止 `B_marlin`、`RepackQweightToMarlin()`、`perm64` scales layout、直接链接 `samples/micro_bench/spike/marlin_moe/main.cc`，也不修改 production path。

## 当前 R0 待办

1. 完成并验证 `Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC`。
2. R0D1 通过后组织 reviewer 复核，确认没有 P0/P1 blocker。
3. 用户 R4 明确 formal SOP-A/B/C 命令、预计耗时、输出目录和停止条件。
4. 只有前置 gate 全部满足后，才能启动 `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`。
5. Python CuTeDSL route 仍为 optional blocked；除非提供 Jetson aarch64 compatible wheel，否则不作为当前 C++ fallback 主线前置。
