# AUTO-20260608-105 CuTe/CUTLASS R0 current memory sync and R0 todo

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` / `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：agent_group 记忆同步与 R0 待办清单；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 已将 AUTO-104 后的 CuTe/CUTLASS R0 当前进度同步到 agent_group 记忆。
- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 保持 `in_progress / P0-next`。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 保持 `blocked / gated`。
- R0a scaffold、CuTe/CUTLASS C++ fallback smoke、aligned shape bench、R0c projection correctness、R0 design/update report、R0d routed grouped micro、R0D1 same-run NNCL paired diagnostic 均已完成。
- R0b Python CuTeDSL route 仍 blocked：Jetson aarch64 环境缺 `cutlass._mlir` / compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
- AUTO-104 readiness hardening 已纳入当前记忆：SOP-B NCU workload 改绑 `r0e_sop_c_routed_grouped --m_filter=64`，SOP-C formal CSV/guard 加严 raw GPTQ、layout 和 input 字段。

## 已同步文件

- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/memory/TASK_LEDGER.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
- `.codex/agent_group/memory/RISKS.md`
- `.codex/agent_group/current/acceptance.md`

## 当前 R0 剩余待办

1. 等待用户 R4 formal 确认：target、container、remote repo、formal SOP-A/B/C 命令、guard/verdict 命令、预计耗时、本地输出目录和停止条件。
2. 用户 R4 确认后执行 `orin_1` sync/build/help preflight，确认 formal modes、guard 和 runner 远端存在且可运行。
3. 执行 R0E SOP-A formal precision，输出 `sop_a_precision.csv`。
4. 执行 R0E SOP-B formal NCU：用 `ncu` 包住 `r0e_sop_c_routed_grouped --m_filter=64`，回传 `ncu/r0e_sop_b_cutlass.{csv,log}` 和 `sop_b_workload_sop_c_m64.csv`，再生成 `sop_b_ncu_summary.csv`；无真实 NCU evidence 时只能 fail-closed。
5. 执行 full 10 shape SOP-C formal routed grouped，输出新的 formal `sop_c_routed_grouped.csv`；不得直接复用 R0D1 diagnostic CSV。
6. 运行 `cutedsl_r0e_guard.py`，生成 `r0_guard_report.md` 和 `r0_verdict.json`，verdict 必须保留 input CSV metadata/sha。
7. 回传并归档 remote build/help/run/NCU/guard 日志，以及 `r0e_run_manifest.csv`、`binary.sha256`、`help.sha256`、`ncu/r0e_sop_b_ncu_summary.rc`、`r0e_evidence.sha256`。
8. reviewer 复核 remote formal evidence。
9. qwen-architect 基于 SOP-A/B/C formal evidence 做 tier 判定。
10. Python CuTeDSL route blocker closure 保持可选，只有用户要求回到 Python route 并提供 compatible wheel 后才重跑 R0b import/elementwise/tensorop smoke。

## 非 SOP 边界

- AUTO-105 是记忆同步和待办清单，不是 execution evidence。
- AUTO-104 是 readiness hardening，不是 Orin formal evidence。
- R0c/R0d/R0D1、本地 R0E smoke、synthetic NCU、request package、runner token 或 metadata/sha hardening 都不能解除 R0E `blocked / gated`，也不能声明 SOP/tier。
- 缺用户 R4 formal 确认时，不得启动 `orin_1` R0E formal execution。

## 本轮限制

- 尝试创建 reviewer sub-agent 时触发当前线程数上限，未能新增 sub-agent；本轮采用本地主线只读复核和记忆同步。
- 未运行远端 `orin_1`，未运行 NCU，未生成新的 formal package。
