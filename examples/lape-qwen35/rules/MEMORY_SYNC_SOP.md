---
ag_schema: v1
doc_id: AG-RULE-MEMORY-SYNC-SOP
category: rules
doc_type: memory_sync_sop
authority: canonical
lifecycle: warm
read_policy: before_write
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
allowed_writers:
  - main-orchestrator
allowed_readers:
  - main-orchestrator
  - reviewer
canonical_path: .codex/agent_group/rules/MEMORY_SYNC_SOP.md
compat_links:
  - .codex/agent_group/MEMORY_SYNC_SOP.md
update_triggers:
  - memory_sync_rule_change
  - status_enum_change
  - document_policy_change
sync_targets:
  - .codex/agent_group/README.md
forbidden_ops:
  - delete
  - archive
  - move_to_current
---

# Agent Group 通用记忆同步 SOP

最后更新：2026-06-05

## 目标

本文件定义 agent_group 中通用、稳定的记忆同步规则。它回答一个问题：

> 任一任务、规则、事实、风险或当前状态发生变化后，哪些记忆文件必须一起更新，如何避免状态冲突、历史丢失和过期结论误导。

本 SOP 不绑定某个具体项目、Roadmap、Q35 任务或性能优化路线。项目级或路线级的专项同步规则应放在 `memory/` 下，并引用本 SOP。

本 SOP 只规范 agent_group 记忆同步，不替代代码 review、性能验证、Orin 验证、production gate 或用户授权。

## 结果状态判定

任务或阶段结束后，先把结果归一成一种状态。状态必须反映验收事实，不得把 smoke、partial、invalid 或 diagnostic-only 结果写成 `done`。

| 状态 | 适用场景 |
|---|---|
| `done` | 已通过验收，可作为后续依赖 |
| `blocked` | 需要外部输入、环境、权限或上游任务 |
| `rejected` | 已执行但验收失败，不应继续推进 |
| `closed` | 路线收口，保留结论但不再作为当前热路径 |
| `in_progress` | 已有阶段性产物，但未完成最终验收 |
| `superseded` | 被新路线、新 anchor 或新任务替代 |

## 文档分层

agent_group 记忆按职责分层。同步时先判断改动属于哪一层，再更新对应文件。

| 层级 | 目录或文件 | 职责 |
|---|---|
| 规则层 | `rules/` | 稳定流程、路由、runbook、文档策略；不应包含某个任务的专项细节 |
| 长期记忆层 | `memory/` | Roadmap、任务账本、事实、进度、决策、风险、架构索引 |
| 当前热状态层 | `current/` | 当前 epic、当前任务、验收标准、热启动摘要、worker 输出 |
| 证据层 | `analysis/`、`current/agent_outputs/`、`archive/` | 报告、日志、worker 输出、历史快照 |

## 同步触发类型

| 触发类型 | 必须考虑更新 |
|---|---|
| 当前状态变化 | `current/STATE.md`、`current/tasks.csv`、`memory/PROGRESS_LEDGER.md` |
| 任务状态变化 | `memory/TASK_LEDGER.md`、`current/tasks.csv`、`current/STATE.md`、`memory/PROGRESS_LEDGER.md` |
| Roadmap 或长期路线变化 | `memory/ROADMAP.md`、`memory/TASK_LEDGER.md`、`current/STATE.md`、`memory/PROGRESS_LEDGER.md` |
| 产生长期决策 | `memory/DECISIONS.md`、`current/STATE.md`、`memory/PROGRESS_LEDGER.md` |
| 新增或关闭风险 | `memory/RISKS.md`、`current/STATE.md`、`memory/PROGRESS_LEDGER.md` |
| repo、工具、模型、bundle 或路径事实变化 | `memory/PROJECT_FACTS.md`、必要时 `current/STATE.md` |
| 验收标准变化 | `current/acceptance.md`、`current/STATE.md`、相关任务账本 |
| 规则或文档结构变化 | `rules/*`、`memory/DOC_REGISTRY.yml`、`README.md`、`memory/PROGRESS_LEDGER.md` |
| Orin / 远端验证口径变化 | `rules/RUNBOOK_ORIN1.md`、必要时 `current/STATE.md` |

## 通用同步矩阵

| 文件 | 更新原则 |
|---|---|
| `memory/ROADMAP.md` | 只记录长期路线、Milestone、未完成/已执行工作和验收口径；不要塞入完整日志 |
| `memory/TASK_LEDGER.md` | 记录跨阶段任务状态、owner、输入、输出、验收和更新时间 |
| `current/tasks.csv` | 只记录当前 hot epic 的任务；不得混入多个 epic |
| `current/STATE.md` | 保持短而热；只写当前目标、最新 checkpoint、阻塞点、禁止事项和下一步 |
| `memory/PROGRESS_LEDGER.md` | 追加记录；不重写历史；记录做了什么、证据在哪里、结论和下一步 |
| `memory/DECISIONS.md` | 追加长期决策；旧决策被替代时用新记录 supersede，不删除旧记录 |
| `memory/RISKS.md` | 更新风险状态和缓解措施；不直接删除风险 |
| `memory/PROJECT_FACTS.md` | 刷新 repo 和工具事实；删除或标注过期路径 |
| `current/acceptance.md` | 当前 hot epic 验收标准变化时更新 |
| `current/epic.md` | 当前主目标变化时更新 |
| `rules/RUNBOOK_ORIN1.md` | Orin 设备、命令入口、输出记录规则变化时更新 |
| `memory/DOC_REGISTRY.yml` | 新增、移动、重命名或改变标签策略时更新 |

## 标准同步流程

1. 收集证据路径：analysis 报告、agent output、日志、commit、命令口径、测试输入。
2. 判定结果状态：`done/blocked/rejected/closed/in_progress/superseded`。
3. 按触发类型选择必须更新的文件。
4. 先更新事实源和长期账本，再更新当前热状态。
5. 若任务属于当前 hot epic，同步 `current/tasks.csv`。
6. 更新 `current/STATE.md` 的最新 checkpoint、下一步、阻塞点和禁止事项。
7. 追加 `memory/PROGRESS_LEDGER.md`。
8. 如产生长期决策、风险、事实变化或规则变化，更新对应长期记忆文件。
9. 做一致性检查。
10. 最终汇报列出所有写入文件和关键结论。

## 一致性检查

每次同步后执行只读检查：

```bash
rg -n "<TASK_ID>" .codex/agent_group/memory/ROADMAP.md \
  .codex/agent_group/memory/TASK_LEDGER.md \
  .codex/agent_group/current/tasks.csv \
  .codex/agent_group/current/STATE.md \
  .codex/agent_group/memory/PROGRESS_LEDGER.md
```

检查规则：

- 同一 task id 的状态不能在 `memory/ROADMAP.md`、`memory/TASK_LEDGER.md`、`current/tasks.csv` 中互相冲突。
- `done` 必须有明确产物路径和验收结论。
- `rejected/closed/blocked` 必须写明原因和下一步。
- 当前 hot epic 的下一步必须在 `current/STATE.md` 和 `current/tasks.csv` 中可对应。
- `rules/` 下文件不得承载某个具体任务的专项同步细节；专项规则应放入 `memory/`。
- `memory/ROADMAP.md` 不得被移动到 `current/` 或 `archive/`。

## 维护规则

- `MEMORY_SYNC_SOP.md` 是长期规则文件，真实位置是 `.codex/agent_group/rules/MEMORY_SYNC_SOP.md`。
- `.codex/agent_group/MEMORY_SYNC_SOP.md` 是兼容软链接，保留给旧引用和冷启动习惯。
- 记忆清理、current epic 切换、agent output 归档时，不得移动到 `current/`、删除或归档本文件。
- 如果新增项目级或 Roadmap 级专项规则，应放入 `memory/`，并在 `memory/DOC_REGISTRY.yml` 中登记。
- 如果修改状态枚举、通用同步流程或文档分层规则，必须同步更新 `README.md` 和本 SOP；必要时同步 `memory/DOC_REGISTRY.yml`。
