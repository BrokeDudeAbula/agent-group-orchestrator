# AUTO-20260608-96 CuTe/CUTLASS R0 当前记忆同步与待办清单

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
范围：agent_group 记忆同步；不启动远端 R4，不生成新的 SOP/tier evidence

## 当前结论

- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 仍为 `in_progress / P0-next`。
- R0a scaffold、CuTe/CUTLASS C++ fallback smoke、aligned shape bench、R0c projection correctness、R0d routed grouped micro、R0D1 same-run NNCL paired diagnostic 均已完成。
- R0b Python CuTeDSL route 仍 `blocked`，阻塞点是 Jetson aarch64 环境缺 `cutlass._mlir` / compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
- AUTO-95 已把 R0E source-level WIP 推进为本地可编译、可 smoke 的 formal-output candidate modes：`r0e_sop_a_precision`、`r0e_sop_b_occupancy`、`r0e_sop_c_routed_grouped`。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍为 `blocked / gated`，因为缺用户 R4 formal 确认、`orin_1` formal execution、真实 SOP-B NCU、full 10 shape SOP-C formal CSV、remote guard/verdict 和 reviewer remote evidence 复核。

## 本轮同步文件

- `.codex/agent_group/memory/TASK_LEDGER.md`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
- `.codex/agent_group/memory/RISKS.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/current/acceptance.md`

## R0 剩余待办

1. 等待用户 R4 formal 确认：target、container、remote repo、formal SOP-A/B/C 命令、guard/verdict 命令、预计耗时、本地输出目录和停止条件。
2. 用户 R4 确认后，执行 `orin_1` sync/build/help preflight，确认 `qwen3_5_cute_dsl_spike` 的 R0E formal modes 和 guard/runner 在远端存在且可运行。
3. 执行 R0E SOP-A formal precision：必须使用 NNCL `SoftmaxTopk<half>`、full token reduce，对齐 `moe_output_before_combine.pt`，输出 `sop_a_precision.csv`。
4. 执行或回传 R0E SOP-B NCU evidence：必须是真实 Orin NCU summary，输出 `sop_b_ncu_summary.csv`；无 NCU evidence 时只能 fail-closed，不能声明 SOP-B PASS。
5. 执行 R0E SOP-C formal routed grouped：覆盖 Marlin SOP-C 10 shape，使用 same-run NNCL grouped `MoeGroupGemm` paired baseline，输出新的 formal `sop_c_routed_grouped.csv`；不得复用 R0D1 diagnostic CSV 直接判 tier。
6. 运行 `cutedsl_r0e_guard.py`，生成 `r0_guard_report.md` 和 `r0_verdict.json`，区分 `schema_fail`、`gate_fail` 和 `pass`。
7. reviewer 复核 remote formal evidence，确认无 P0/P1 schema、口径、precision、NCU 或 ratio blocker。
8. qwen-architect 基于 SOP-A/B/C formal evidence 做 tier 判定；若 SOP-C ratio gate 失败，则 R0 归档为未达标路线，不进入 production。
9. 只有 formal SOP-A/B/C 全部有效达标且 reviewer 无 P0/P1 时，才允许进入后续 R1/R3 授权流程；本轮不能自动请求 production 写入。
10. Python CuTeDSL route blocker closure 保持可选：只有用户要求回到 Python route并提供 compatible wheel 后，才重跑 R0b import/elementwise/tensorop smoke。

## 非 SOP 边界

- AUTO-95 的本地 SOP-A smoke 不是 Orin R4 formal SOP-A evidence。
- AUTO-95 的 SOP-B fail-closed smoke 不是 SOP-B PASS。
- 本地非 Orin runtime 上的 SOP-C unsupported 不是 formal SOP-C evidence。
- R0c/R0d/R0D1 仍不是 SOP-A、SOP-C 或 tier evidence。
- 不得用 R0D1 `cutedsl_ms/nncl_ms/ratio` 直接声明 SOP-C 或 tier。
- 缺用户 R4 formal 确认时，不得启动 `orin_1` R0E formal execution。
