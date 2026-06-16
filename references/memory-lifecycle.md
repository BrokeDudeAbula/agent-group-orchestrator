# Repo Memory Lifecycle

本文定义项目本地 `.codex/agent_group/` 中 repo 记忆的生命周期，重点说明哪些任务记忆必须同步到长期记忆，哪些热记忆可以归档，以及哪些文件不能通过阶段归档移走。

## 核心原则

`current/` 是热记忆，只服务于当前 epic 或当前阶段的快速恢复；`memory/` 是长期记忆，用于跨线程、跨阶段、跨 epic 继承项目事实、任务历史、决策和风险；`archive/` 是历史证据库，用于保存已经完成或被重置阶段的原始上下文。

归档不是删除。归档前必须先把可复用结论同步到 `memory/`，再把旧的 `current/` 文件和 worker evidence 移入 `archive/`。任何阻塞、风险、决策或稳定项目事实都不能因为归档而丢失。

## 需要同步的任务记忆

以下内容在每个任务、阶段或里程碑完成后都需要同步：

| 记忆类型 | 目标文件 | 同步方式 | 说明 |
| --- | --- | --- | --- |
| 当前目标、阶段、阻塞、最新证据、下一步 | `current/STATE.md` | 覆盖为最新热状态 | 只保留当前状态，不复制完整历史。 |
| 当前 epic 的任务状态 | `current/tasks.csv` | 更新 active task 行 | 只保留当前 epic；完成的跨阶段历史同步到 ledger。 |
| worker 原始输出和证据 | `current/agent_outputs/` | 新增或保留文件 | 当前阶段的原始证据；不要直接写入长期 ledger。 |
| 任务级历史 | `memory/TASK_LEDGER.md` | 追加或更新任务记录 | 记录任务范围、状态、输入、输出、验收和最新更新。 |
| 阶段/里程碑进展 | `memory/PROGRESS_LEDGER.md` | 追加摘要 | 记录发生了什么、关键 artifact、阻塞和下一步。 |
| 架构、流程或技术决策 | `memory/DECISIONS.md` | 追加新决策 | 历史决策不可删除；过期时新增 superseding decision。 |
| 风险、阻塞和缓解状态 | `memory/RISKS.md` | 更新状态或追加风险 | 风险只能标记为 `active`、`mitigated`、`closed` 或 `accepted`。 |
| 稳定项目事实 | `memory/PROJECT_FACTS.md` | 更新事实或标记 stale | 记录 repo layout、入口、命令、依赖、环境假设和不确定事实。 |

同步时优先更新热状态，再更新长期记忆：

1. 更新 `current/STATE.md`。
2. 更新 `current/tasks.csv`。
3. 写入或保留 `current/agent_outputs/`。
4. 同步 `memory/TASK_LEDGER.md` 和 `memory/PROGRESS_LEDGER.md`。
5. 同步 `memory/DECISIONS.md`、`memory/RISKS.md`、`memory/PROJECT_FACTS.md`。
6. 运行结构校验。

## 可以归档的记忆

只有阶段性热记忆和当前阶段 worker 原始证据可以归档：

| 路径 | 可以归档 | 归档条件 |
| --- | --- | --- |
| `current/STATE.md` | 是 | 当前阶段结束、切换 epic、或需要重置 hot state；归档前必须把下一步、阻塞和关键证据同步到 `memory/`。 |
| `current/epic.md` | 是 | epic 完成、暂停、废弃或被新 epic 取代。 |
| `current/acceptance.md` | 是 | 对应 epic/阶段的验收条件不再作为当前工作入口。 |
| `current/tasks.csv` | 是 | 当前 active epic 切换或阶段收口；归档前必须把任务状态同步到 `memory/TASK_LEDGER.md`。 |
| `current/tasks.meta.yml` | 是 | 如果存在，随同 `current/tasks.csv` 一起归档。 |
| `current/agent_outputs/*` | 是 | 当前阶段 worker 原始输出已经被长期 ledger 摘要引用。`.gitkeep` 不归档。 |

默认归档目标为：

```text
archive/<yyyymmdd_topic>/
```

推荐归档内容为：

```text
archive/<yyyymmdd_topic>/
├── STATE.md
├── epic.md
├── acceptance.md
├── tasks.csv
├── tasks.meta.yml
└── agent_outputs/
```

`scripts/compact_memory.py` 当前只移动上述 `current/` 文件和 `current/agent_outputs/` 内容；它不会自动更新长期 ledger，也不会自动重建新的 `current/STATE.md` 或 `current/tasks.csv`。因此执行脚本前后仍需要人工或 agent 按 SOP 完成同步和重建。

## 不应归档的记忆

以下内容不属于阶段归档对象：

| 路径 | 不应归档原因 | 正确处理方式 |
| --- | --- | --- |
| `memory/TASK_LEDGER.md` | 长期任务历史，需要跨阶段保留。 | 追加或更新任务记录。 |
| `memory/PROGRESS_LEDGER.md` | 追加式进展历史，是归档后的索引。 | 追加归档事件和阶段摘要。 |
| `memory/DECISIONS.md` | 决策历史不可删除。 | 追加 superseding decision，不重写旧决策。 |
| `memory/RISKS.md` | 风险历史不可隐藏。 | 更新风险状态、缓解和最新进展。 |
| `memory/PROJECT_FACTS.md` | 稳定项目事实需要长期继承。 | 更新事实、标记 stale 或记录不确定性。 |
| `rules/*` | 项目运行策略和门禁规则。 | 修改规则需要明确说明原因，不随阶段归档移动。 |
| `agents/*` | worker 角色定义。 | 修改 worker 需同步 registry，不随阶段归档移动。 |
| `config.yml` | agent_group 实例配置。 | 只在配置变更时编辑，不归档。 |
| `archive/*` | 历史证据库。 | 不二次归档，不删除证据；必要时新增索引。 |

## 归档前检查清单

执行归档前，必须确认：

- `current/STATE.md` 中的 active goal、blockers、latest evidence 和 next step 已同步到长期记忆。
- `current/tasks.csv` 中完成、暂停、阻塞或废弃的任务已同步到 `memory/TASK_LEDGER.md`。
- 阶段级摘要已追加到 `memory/PROGRESS_LEDGER.md`，并包含 archive 目标路径。
- 新决策已写入 `memory/DECISIONS.md`，旧决策如已过期则通过 supersedes 标记。
- 风险和阻塞没有被删除；它们已在 `memory/RISKS.md` 中被关闭、缓解、接受或保持 active。
- 稳定事实已写入 `memory/PROJECT_FACTS.md`，不稳定事实已标记 stale 或 uncertain。
- worker 原始输出留在 `current/agent_outputs/`，并被 ledger 摘要引用。
- 已执行 `compact_memory.py --dry-run` 并检查移动计划。

## 归档后检查清单

执行归档后，必须确认：

- `archive/<yyyymmdd_topic>/` 包含被移动的 `current/` 文件和 `agent_outputs/`。
- `current/agent_outputs/.gitkeep` 存在。
- 新的 `current/STATE.md` 已重建为简洁 hot state。
- 新的 `current/tasks.csv` 只包含当前 active epic 的任务。
- `memory/PROGRESS_LEDGER.md` 记录了本次归档事件和 archive 路径。
- `validate_agent_group.py --strict <agent-group-path>` 通过，或失败项已明确记录为待修复。

## 判断规则

可以用以下规则快速判断某条记忆应该同步还是归档：

- 会影响后续决策、任务恢复、风险判断或项目认知的内容，必须同步到 `memory/`。
- 只服务于当前阶段快速恢复的状态，保留在 `current/`。
- 当前阶段结束后仍需保留但不应占用 hot state 的原始证据，归档到 `archive/`。
- 规则、角色、配置、长期 ledger 和稳定事实不能通过阶段归档移走。
- 如果不确定，先同步摘要到 `memory/`，再归档原始证据；不要直接删除。
