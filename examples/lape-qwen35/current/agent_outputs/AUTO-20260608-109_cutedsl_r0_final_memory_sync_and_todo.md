# AUTO-20260608-109 CuTe/CUTLASS R0 final memory sync and R0 todo

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` / `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：AUTO-108 formal Orin gate fail 后的 agent_group 记忆同步与当前 R0 待办清单；不生成新的 SOP evidence

## 结论

- 已将 AUTO-108 后的 CuTe/CUTLASS R0 formal 结论同步到 agent_group 记忆。
- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`：`done / tier D / not production`。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`：`done / formal FAIL / gate_fail`。
- R0E formal evidence 目录：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`。
- Guard：`schema_pass=true`、`status=gate_fail`、`overall_pass=false`、`tier_eligible=false`。
- SOP-A PASS，SOP-B PASS，SOP-C FAIL。
- 不允许声明 SOP-C PASS、tier eligible、R1/R3/production。

## 已同步文件

- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/memory/TASK_LEDGER.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
- `.codex/agent_group/memory/RISKS.md`
- `.codex/agent_group/current/acceptance.md`

## Formal gate 摘要

- SOP-A：`max_abs=6.661564e-05`、`rmse=2.843369e-06`、NaN/Inf=0、layout guard PASS。
- SOP-B：真实 NCU `best_occupancy=31.060000`、`ncu_available=true`、`has_duration=true`、`saw_target_workload=true`、`saw_nonzero_output=true`。
- SOP-C：10 rows `precision_pass=true`，但 `valid_for_sop_c=false`、`tier_eligible=false`；family A/B geomean=`152.031603/65.925507`，hot M898=`170.410573/71.708239`，small M64=`94.754880/69.122485`。
- reviewer：evidence schema 和审计完整性无 P0/P1；路线应归档为 tier D / not production。

## 当前 R0 待办

1. CuTe/CUTLASS C++ R0 主线无剩余执行待办；R0E formal 已执行并以 gate_fail 归档。
2. 保留 AUTO-108 evidence、guard/verdict、manifest/sha 和 reviewer 结论作为当前正式事实源。
3. 不得进入 R1/R3/production，不得声明 SOP-C PASS 或 tier eligible。
4. Python CuTeDSL route blocker closure 保持可选：只有用户提供 Jetson CUDA 12.6 / Python 3.10 / aarch64 compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel，并明确要求回到 Python route 时，才重跑 R0b import/elementwise/tensorop smoke。
5. 后续 NNCL grouped targeted R0、dispatch/padding 结构性方案或新的 CuTe/CUTLASS fused W4A16 方案都不属于当前 R0 未完成项；必须新建任务并重新走正式 SOP-A/B/C gate。

## 非 SOP 边界

- AUTO-109 是记忆同步和待办清单，不是新的 execution evidence。
- AUTO-108 的 formal package 不能声明 SOP-C PASS 或 tier eligible。
- R0c/R0d/R0D1 diagnostic timing/ratio 仍不能作为 SOP/tier evidence。
