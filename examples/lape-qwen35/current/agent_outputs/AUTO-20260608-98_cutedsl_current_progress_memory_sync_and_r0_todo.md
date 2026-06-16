# AUTO-20260608-98 CuTe/CUTLASS R0 当前进度记忆同步与待办清单

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
范围：agent_group 记忆同步；不启动远端 R4，不生成新的 SOP/tier evidence

## 当前结论

- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 仍为 `in_progress / P0-next`。
- R0 design/update report 已完成：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d_design_20260608/design_update.md`。
- R0a scaffold、CuTe/CUTLASS C++ fallback smoke、aligned shape bench、R0c projection correctness、R0d routed grouped micro、R0D1 same-run NNCL paired diagnostic 均已完成。
- R0b Python CuTeDSL route 仍 `blocked`，阻塞点是 Jetson aarch64 环境缺 `cutlass._mlir` / compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
- AUTO-95 已实现并本地验证 R0E formal-output candidate modes：`r0e_sop_a_precision`、`r0e_sop_b_occupancy`、`r0e_sop_c_routed_grouped`。
- AUTO-97 已补齐 R4 runner 的真实 NCU summary 生成路径，并硬化 SOP-B guard：`sop_b_ncu_summary.csv` 必须来自 NCU CSV/log + workload CSV/log，且 `ncu_available=true`、`has_duration=true`、`saw_target_workload=true`、`saw_nonzero_output=true`、`best_occupancy>=30`。
- reviewer 子代理复核无 P0；其提醒的 SOP-B 真实 NCU path、guard 必填字段和本地 smoke 非 formal evidence 边界已纳入当前记忆。AUTO-97 本地 hardening 尚未经过 `orin_1` remote formal evidence 复核。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍为 `blocked / gated`，因为缺用户 R4 formal 确认、`orin_1` formal execution、真实 SOP-B NCU 回传、full 10 shape SOP-C formal CSV、remote guard/verdict 和 reviewer remote evidence 复核。

## 本轮同步文件

- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/memory/TASK_LEDGER.md`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
- `.codex/agent_group/memory/RISKS.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/current/acceptance.md`

## R0 阶段待办

1. 等待用户 R4 formal 确认：target、container、remote repo、formal SOP-A/B/C 命令、guard/verdict 命令、预计耗时、本地输出目录和停止条件。
2. R4 确认后执行 `orin_1` sync/build/help preflight，确认 `qwen3_5_cute_dsl_spike` 的 `r0e_sop_a_precision`、`r0e_sop_b_occupancy`、`r0e_sop_c_routed_grouped` 以及 guard/runner 脚本在远端存在且可运行。
3. 执行 R0E SOP-A formal precision：使用 NNCL `SoftmaxTopk<half>`、full token weighted reduce，对齐 `moe_output_before_combine.pt`，输出 `sop_a_precision.csv`。
4. 执行 R0E SOP-B formal NCU：用 `ncu` 包住正式 CuTe/CUTLASS workload，回传 `ncu/r0e_sop_b_cutlass.{csv,log}`，再由 `cutedsl_r0e_ncu_summary.py` 生成 `sop_b_ncu_summary.csv`；无真实 NCU evidence 时只能 fail-closed。
5. 执行 R0E SOP-C formal routed grouped：覆盖 Marlin SOP-C 10 shape，使用 same-run NNCL grouped `MoeGroupGemm` paired baseline，输出新的 formal `sop_c_routed_grouped.csv`；不得复用 R0D1 diagnostic CSV 或 R0D1 ratio 判 tier。
6. 运行 `cutedsl_r0e_guard.py`，生成 `r0_guard_report.md` 和 `r0_verdict.json`，明确区分 `schema_fail`、`gate_fail` 和 `pass`。
7. 回传并归档 remote build/help/run/NCU/guard 日志；后续如补 metadata/manifest，需记录 target、container、build command、binary help hash 和 CSV sha256。
8. reviewer 复核 remote formal evidence，确认无 P0/P1 schema、口径、precision、NCU、SOP-C ratio 或证据追溯 blocker。
9. qwen-architect 基于 formal SOP-A/B/C evidence 做 tier 判定；若 SOP-C ratio gate 失败，则 R0 归档为未达标路线，不进入 production。
10. 只有 formal SOP-A/B/C 全部有效达标且 reviewer 无 P0/P1 时，才允许进入后续 R1/R3 授权流程；当前不能自动请求 production 写入。
11. Python CuTeDSL route blocker closure 保持可选：只有用户要求回到 Python route并提供 compatible Jetson aarch64 wheel 后，才重跑 R0b import/elementwise/tensorop smoke。
12. 可选本地加固：补 synthetic 反例，确保 R0D1 CSV 即使改名为 `sop_c_routed_grouped.csv` 也会被 R0E guard 判为 `schema_fail`；这只提高工具防误用能力，不替代 formal evidence。

## 非 SOP 边界

- AUTO-95 本地 SOP-A smoke 不是 Orin R4 formal SOP-A evidence。
- AUTO-97 synthetic NCU/parser PASS 只证明 parser/guard 行为，不是 SOP-B PASS。
- R0c/R0d/R0D1 仍不是 SOP-A、SOP-C 或 tier evidence。
- 不得用 R0D1 `cutedsl_ms/nncl_ms/ratio`、本地 smoke、synthetic NCU 或 request package 直接声明 SOP-C、SOP-B 或 tier。
- 缺用户 R4 formal 确认时，不得启动 `orin_1` R0E formal execution。
