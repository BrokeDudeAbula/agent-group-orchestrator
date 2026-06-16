# AUTO-20260608-102 CuTe/CUTLASS R0 current progress sync and R0 todo

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`、`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：agent_group 记忆同步与 R0 剩余待办整理；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 当前 CuTe/CUTLASS R0 主线保持 `in_progress / P0-next`。
- R0a scaffold、CuTe/CUTLASS C++ fallback smoke、aligned shape bench、R0c projection correctness、R0 design/update report、R0d routed grouped micro、R0D1 same-run NNCL paired diagnostic 均已完成。
- R0b Python CuTeDSL route 仍 `blocked`：`orin_1` 缺 `cutlass._mlir` / compatible Jetson aarch64 `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
- R0E local formal-output candidate modes、guard、runner、synthetic、NCU parser 和 evidence metadata/sha hardening 已本地验证到 AUTO-101。
- R0E formal SOP-A/B/C 仍 `blocked / gated`：缺用户 R4 formal 确认、`orin_1` formal execution、真实 SOP-B NCU、full 10 shape SOP-C formal CSV、remote guard/verdict 和 reviewer remote evidence 复核。

## 已同步的权威状态

- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`：`in_progress / P0-next`。
- `Q35-MOE-CUTEDSL-R0A-SCAFFOLD`：`done / scaffold-only`。
- `Q35-MOE-CUTEDSL-R0B-TOOLCHAIN-SMOKE`：`blocked`，Python CuTeDSL import blocker。
- `Q35-MOE-CUTEDSL-CUTE-CPP-SMOKE`：`done / fallback validation`。
- `Q35-MOE-CUTEDSL-ALIGNED-SHAPE-BENCH`：`done / diagnostic-only`。
- `Q35-MOE-CUTEDSL-R0C-SINGLE-PROJECTION-CORRECTNESS`：`done / diagnostic-only`。
- `Q35-MOE-CUTEDSL-R0D-ROUTED-GROUPED-MICRO`：`done / diagnostic-only`。
- `Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC`：`done / diagnostic-only`。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`：`blocked / gated`。

## 当前 R0 剩余待办

1. 等待用户 R4 formal 确认：target、container、remote repo、formal SOP-A/B/C 命令、guard/verdict 命令、预计耗时、本地输出目录和停止条件。
2. 用户 R4 确认后执行 `orin_1` sync/build/help preflight，确认 `qwen3_5_cute_dsl_spike` formal modes、guard 和 runner 在远端存在且可运行。
3. 执行 R0E SOP-A formal precision，输出 `sop_a_precision.csv`；必须使用 NNCL `SoftmaxTopk<half>`、full token reduce，对齐 `moe_output_before_combine.pt`。
4. 执行 R0E SOP-B formal NCU，回传 `ncu/r0e_sop_b_cutlass.{csv,log}`，再由 `cutedsl_r0e_ncu_summary.py` 生成 `sop_b_ncu_summary.csv`；无真实 NCU evidence 时只能 fail-closed。
5. 执行 full 10 shape SOP-C formal routed grouped，输出新的 formal `sop_c_routed_grouped.csv`；不得直接复用 R0D1 diagnostic CSV。
6. 运行 `cutedsl_r0e_guard.py`，生成 `r0_guard_report.md` 和 `r0_verdict.json`；verdict 必须保留 input CSV metadata/sha。
7. 回传并归档 remote build/help/run/NCU/guard 日志，以及 `r0e_run_manifest.csv`、`binary.sha256`、`help.sha256`、`ncu/r0e_sop_b_ncu_summary.rc`、`r0e_evidence.sha256`。
8. reviewer 复核 remote formal evidence，确认无 P0/P1 schema、口径、precision、NCU、SOP-C ratio 或 evidence traceability blocker。
9. qwen-architect 基于 SOP-A/B/C formal evidence 做 tier 判定；若 SOP-C ratio gate 失败，则 R0 归档为未达标路线，不进入 production。
10. Python CuTeDSL route blocker closure 保持可选；只有用户要求回到 Python route 并提供 compatible wheel 后，才重跑 R0b import/elementwise/tensorop smoke。

## 非 SOP 边界

- AUTO-102 是记忆同步与待办清单，不是 execution evidence。
- R0c/R0d/R0D1 均不是 SOP-A、SOP-C 或 tier evidence。
- AUTO-95 本地 SOP-A smoke、AUTO-97 synthetic NCU/parser、AUTO-100 negative synthetic、AUTO-101 metadata/sha hardening 都不能解除 R0E `blocked / gated`。
- 不得用 R0D1 `cutedsl_ms/nncl_ms/ratio`、本地 smoke、synthetic NCU、request package 或 runner token 声明 SOP-B/SOP-C/tier。
- 缺用户 R4 formal 确认时，不得启动 `orin_1` R0E formal execution。
