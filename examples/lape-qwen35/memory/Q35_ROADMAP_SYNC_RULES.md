---
ag_schema: v1
doc_id: AG-MEM-Q35-ROADMAP-SYNC-RULES
category: memory
doc_type: project_sync_rules
authority: canonical
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
allowed_writers:
  - main-orchestrator
allowed_readers:
  - main-orchestrator
  - reviewer
canonical_path: .codex/agent_group/memory/Q35_ROADMAP_SYNC_RULES.md
compat_links: []
update_triggers:
  - q35_roadmap_task_type_change
  - q35_acceptance_change
  - q35_gate_change
sync_targets:
  - .codex/agent_group/memory/ROADMAP.md
  - .codex/agent_group/memory/TASK_LEDGER.md
  - .codex/agent_group/current/tasks.csv
  - .codex/agent_group/current/STATE.md
  - .codex/agent_group/memory/PROGRESS_LEDGER.md
forbidden_ops:
  - delete
  - archive
  - move_to_current
---

# Q35 Roadmap 专项同步规则

最后更新：2026-06-08

## 目标

本文件保存 Qwen3.5 MoE Roadmap 的项目级同步规则。`Q35-MOE-CUTEDSL-R0F-R1-PROBE` 已在 M5 收口为 `done / reject_or_hold / probe-only / not production`，Marlin 方案已压缩为 `holding / tier D / archived / not production`。

通用记忆同步制度以 `rules/MEMORY_SYNC_SOP.md` 为准。本文件只补充 Q35 当前路线的专项验收、状态判定和同步约束。

压缩前 Marlin R0 SOP-A/B/C/R1 细则已归档到：

`.codex/agent_group/archive/20260608_marlin_holding_compaction/memory.before/Q35_ROADMAP_SYNC_RULES.before.md`

## 文档权责边界

- 权威负责：当前 Q35 hot task 的 gate/sync 规则、holding 路线恢复条件、正式候选升级约束。
- 不负责：通用 agent_group 同步制度、长期 Milestone 排序、逐任务 owner 台账、append-only 历史日志、具体实验报告正文。
- 冲突处理：
  - 通用同步流程以 `rules/MEMORY_SYNC_SOP.md` 为准。
  - 当前 hot epic 的验收摘要以 `current/acceptance.md` 为准。
  - 任务状态以 `memory/TASK_LEDGER.md` 和 `current/tasks.csv` 为准。
  - 长期路线和 Milestone 以 `memory/ROADMAP.md` 为准。

## 总原则

- 禁止把 smoke、partial、invalid、diagnostic-only 或 profile-only 结果写成正式 PASS。
- R0F/R1-probe 只允许输出 diagnostic/probe-only evidence。
- 所有 R0F/R1-probe 输出必须固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- 未新建 formal task 并重新走 SOP-A/B/C 前，不得请求 R3 production 写入授权。
- 当前任务状态更新后，必须同步 `memory/ROADMAP.md`、`memory/TASK_LEDGER.md`、`current/tasks.csv`、`current/STATE.md` 和 `memory/PROGRESS_LEDGER.md`。

## Q35-MOE-CUTEDSL-R0F-R1-PROBE

状态：`done / reject_or_hold / probe-only / not production`

固定顺序：

1. Tensor Core sanity：已通过。
2. Timing hygiene：已完成，但 serial dense fp16 相对 same-run NNCL baseline 连续明显 `>1.50x`。
3. Grouped launch probe：已完成，grouped 相比 serial 有收益，但相对 same-run NNCL baseline 仍连续明显 `>1.50x`。
4. M4-control direct/dispatch：已完成，接近 NNCL baseline，但为 NNCL internal/control path。
5. Candidate NCU isolation：未启动，当前没有 independent candidate kernel。
6. W4A16 feasibility：已完成，决策为 `reject_or_hold`。
7. Formal gate decision：当前 probe 不 promoted；若继续必须新建 formal task 并重走 SOP-A/B/C。

### 阶段同步规则

每完成一个阶段必须同步：

- `current/STATE.md`：更新最新 checkpoint、下一步、阻塞点和禁止事项。
- `current/tasks.csv`：只保留当前 hot task，更新 acceptance 摘要。
- `memory/TASK_LEDGER.md`：同步跨阶段任务状态。
- `memory/PROGRESS_LEDGER.md`：追加 evidence 路径、结论和下一步。
- `memory/RISKS.md`：新增或更新实际触发的风险。

### 阶段验收约束

Tensor Core sanity：

- 必须说明当前 path 是 SIMT 还是 Tensor Core。
- 必须记录 arch/opclass、shape、kernel/path metadata。
- 不得扩大解释为 routed grouped W4A16 MoE PASS。

Timing hygiene：

- 必须记录 timed loop 内剩余同步、分配、layout copy、host/device roundtrip。
- 未清理完前，性能数据必须标注为 contaminated diagnostic。

Candidate NCU isolation：

- 必须证明 NCU 抓到 CuTe/CUTLASS candidate kernel。
- 抓到 NNCL baseline `MoeFCGemm` 或 kernel name 不可审计时，必须 fail-closed。

Grouped launch probe：

- 必须对比 serial launch 与 grouped/batched launch 的 launch count 和 timing。
- 不得直接声明 SOP-C PASS。

W4A16 feasibility：

- 只有前序阶段证明有上限后才能启动。
- 输出只能是 feasibility report；如建议正式化，必须提出新的 formal task id。
- 当前 M5 结论为 `reject_or_hold`；后续只能新建 `Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE`，或转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。

## Formal Candidate 升级规则

若 R0F/R1-probe 建议进入正式候选：

- 必须新建 task id。
- 必须明确写入范围、R3/R4 权限、输出目录和停止条件。
- 必须重新生成 formal evidence 目录。
- 必须重新跑 SOP-A/B/C gate。
- 必须有 guard verdict 和 reviewer 复核。
- 不得复用 R0E tier、R0c/R0d/R0D1 diagnostic、Marlin holding evidence 或 R0F probe 数据作为正式 PASS。

## Holding 路线恢复规则

`Q35-022 M-4 Marlin-MoE Spike R0` 当前为：

`holding / tier D / archived / not production`

只有以下条件之一满足时才允许恢复：

- 用户明确要求重开 Marlin。
- reviewer 判定旧 formal evidence 无效。
- 新结构性 Marlin 方案以新 task id 立项。

恢复时必须：

- 更新 `current/STATE.md`、`current/tasks.csv` 和 `current/acceptance.md`。
- 从 archive 复制或引用必要工具，不得直接把 archived diagnostic 当正式 PASS。
- 重新走 SOP-A/B/C。

## NNCL Targeted Backlog

`Q35-MOE-NNCL-GROUPED-TARGETED-R0` 当前为 P1 backlog。

启动时：

- 首轮只做 targeted profile、ROI 判断和 spike-local 周边优化设计。
- 不改 production path。
- 若进入正式 R0，必须新建 formal task 并复用 SOP-A/B/C gate。
