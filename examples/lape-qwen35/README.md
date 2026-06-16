# LAPE Agent Group

本目录是 LAPE 长周期开发任务的共享记忆层。目标是让 main agent 管理多个子 agent 时，有稳定的任务账本、事实索引、决策记录和进度记录，避免上下文只存在于单个聊天窗口。

## 性能总目标

agent_group 的核心工程目标是：让 **Qwen3.5 MoE 模型** 在 `orin_1` 上、`inputLen=2500` 的纯文本场景下，**Prefill 吞吐达到 `3000 tok/s`**。

所有 Q35 系列优化、profile、micro replay、Orin e2e 验证和 R0/R1 gate 都应服务于该目标。局部 micro 优化只有在保持正确语义、精度和 e2e 稳定性的前提下，能够推进或解释 `inputLen=2500` Prefill 吞吐目标时，才应进入后续实现或 production patch。

## 快速启动

常规每轮启动只需要读取：

```text
.codex/agent_group/BOOTSTRAP.md
.codex/agent_group/current/STATE.md
```

其它文件是冷配置或历史账本，由 main agent 按需读取。

## 目录分层

为提升长期可维护性和扩展性，agent_group 当前采用分类目录作为真实文件位置，并在根目录保留同名软链接作为兼容入口。旧引用例如 `.codex/agent_group/BOOTSTRAP.md`、`.codex/agent_group/ROADMAP.md` 仍然可用。

```text
.codex/agent_group/
├── rules/       # 启动、路由、worker registry、同步 SOP、Orin runbook
├── memory/      # Roadmap、任务账本、进度、事实、决策、风险、专项规则、注册表
├── current/     # 当前 hot epic 状态、验收、任务和 worker 输出
├── agents/      # worker 角色定义
├── archive/     # 历史压缩与证据归档
├── demo/        # 示例工作流
└── *.md         # 指向 rules/ 或 memory/ 的兼容软链接，README.md 除外
```

维护新文件时优先放入分类目录：

- 规则类、流程类文档放入 `rules/`。
- 长期记忆、账本、事实、风险、决策、专项规则和注册表放入 `memory/`。
- 当前任务热状态仍放入 `current/`。
- 历史证据仍放入 `archive/`。

## 工作流

1. main agent 先读取 `BOOTSTRAP.md` 和 `current/STATE.md`。
2. main agent 默认启用 auto-orchestrate：用户只给目标时，main agent 自行选择 worker、拆分任务和安排顺序。
3. main agent 按需读取 `WORKER_REGISTRY.md`、`ROUTING_POLICY.md`、`PROJECT_FACTS.md`、`TASK_LEDGER.md`、`ROADMAP.md`、`MEMORY_SYNC_SOP.md`、`current/epic.md`、`current/acceptance.md`。
4. main agent 将用户想法拆成可验收任务，更新 `TASK_LEDGER.md` 和 `current/tasks.csv`。
5. 子 agent 只处理自己负责的范围，并将结论写入或汇总到 `current/agent_outputs/`。
6. 规划、调研或方案设计任务中，main agent 需要按路由策略考虑 `oss-scout`，主动补充开源项目、上游实现和 license/迁移风险对照。
7. main agent 汇总子 agent 结果，按 `MEMORY_SYNC_SOP.md` 更新 `ROADMAP.md`、`TASK_LEDGER.md`、`current/tasks.csv`、`current/STATE.md`、`PROGRESS_LEDGER.md`、`DECISIONS.md`、`RISKS.md`。
8. 每次进入新窗口时，先从 `BOOTSTRAP.md` 和 `current/STATE.md` 恢复目标、当前状态、阻塞点和下一步。

## 文件职责

| 文件 | 职责 |
|---|---|
| `rules/BOOTSTRAP.md` (`BOOTSTRAP.md`) | 每轮必读的最小启动规则 |
| `agents/*.md` | worker 角色定义、工具、人设、约束和输出格式 |
| `rules/WORKER_REGISTRY.md` (`WORKER_REGISTRY.md`) | worker 角色、选择触发条件、适用场景、权限边界和输出要求 |
| `rules/ROUTING_POLICY.md` (`ROUTING_POLICY.md`) | main agent 组合 worker 的 DAG、风险等级、任务命名、输出路径和汇报规范 |
| `rules/MEMORY_SYNC_SOP.md` (`MEMORY_SYNC_SOP.md`) | 通用记忆同步 SOP；长期保留，不承载某个具体任务的专项规则 |
| `rules/RUNBOOK_ORIN1.md` (`RUNBOOK_ORIN1.md`) | `orin_1` R4 门禁、默认 target、`sync-orin-lape-build` skill 入口和输出记录要求 |
| `memory/ROADMAP.md` (`ROADMAP.md`) | Qwen3.5 MoE 长期优化路线图、Milestone、未完成工作和历史执行记录；长期保留，不参与 current 记忆清理 |
| `memory/Q35_ROADMAP_SYNC_RULES.md` | Q35 Roadmap 当前专项同步规则，补充 SOP-A/B/C/R1 gate 的项目级约束 |
| `memory/PROJECT_FACTS.md` (`PROJECT_FACTS.md`) | 当前 repo 事实索引，避免使用过期路径和旧架构假设 |
| `memory/TASK_LEDGER.md` (`TASK_LEDGER.md`) | 总任务账本，记录任务状态、owner、输入、输出和验收标准 |
| `memory/PROGRESS_LEDGER.md` (`PROGRESS_LEDGER.md`) | 按时间追加进度、产物、阻塞点和下一步 |
| `memory/DECISIONS.md` (`DECISIONS.md`) | 已确认的架构、实验和流程决策 |
| `memory/RISKS.md` (`RISKS.md`) | 当前风险、触发条件、缓解方式和 owner |
| `current/STATE.md` | 每轮必读的当前状态摘要 |
| `current/epic.md` | 当前主目标 |
| `current/acceptance.md` | 当前主目标验收标准 |
| `current/tasks.csv` | 当前主目标的细分任务 |
| `current/agent_outputs/` | 子 agent 输出、审查结论和临时报告 |

## Agent 输出约定

子 agent 输出文件命名：

```text
current/agent_outputs/<task_id>_<agent_name>_<yyyymmdd_hhmm>.md
```

输出必须包含：

- 任务范围
- 读取的关键文件或命令
- 结论
- 产物路径
- 风险或阻塞
- 建议下一步

## 状态值

`TASK_LEDGER.md` 和 `current/tasks.csv` 使用统一状态：

- `todo`：未开始
- `in_progress`：进行中
- `blocked`：等待外部输入或环境
- `review`：等待审查或验收
- `done`：已完成并通过验收
- `dropped`：明确不再执行

## Auto-Orchestrate 使用方式

推荐用户只给目标、约束和产物，不手动分配 worker。例如：

```text
请按 auto-orchestrate 模式处理：

目标：梳理 Qwen3.5 MoE Stage B 优化进入实现前还缺哪些 baseline 和验证口径。
约束：先只读，不改源码，不启动 Orin。
产物：写入 .codex/agent_group/current/agent_outputs，并更新 STATE.md 和进度账本。
```

main agent 会根据 `ROUTING_POLICY.md` 自动选择 `repo-explorer`、`perf-analyst`、`oss-scout`、`qwen-architect`、`reviewer` 等 worker。涉及规划、调研、方案设计或技术选型时，默认考虑 `oss-scout` 做开源方案对照；涉及推理核心代码或 Orin 长任务时，main agent 必须先形成计划并等待用户确认。

worker 选择触发条件以 `WORKER_REGISTRY.md` 为权威入口；`ROUTING_POLICY.md` 只定义多个 worker 如何组合成任务 DAG、何时应用 R3/R4 门禁以及输出规范。

## Agent 角色位置

worker 角色定义集中在：

```text
.codex/agent_group/agents/
```

`WORKER_REGISTRY.md` 中的 `agent_file` 字段是 main-orchestrator 从 worker 名称映射到具体角色文件的权威入口。worker 名称必须与 `agents/<worker-name>.md` 文件名及 frontmatter `name` 字段一致。

为兼容可能扫描 `.codex/agents` 的 Codex 工具，仓库保留一个软链接：

```text
.codex/agents -> agent_group/agents
```

权威源仍是 `.codex/agent_group/agents/`。

## 记忆清理流程

agent group 的记忆清理不是直接删除历史，而是把当前工作记忆压缩、把历史证据归档、把长期规则和决策保留。

### 清理原则

| 类型 | 建议 | 说明 |
|---|---|---|
| 长期规则 | 保留 | `rules/BOOTSTRAP.md`、`rules/WORKER_REGISTRY.md`、`rules/ROUTING_POLICY.md`、`agents/*.md` 是工作流基础设施 |
| 长期路线图 | 保留并更新 | `memory/ROADMAP.md` 是 Qwen3.5 MoE 长期优化路线图，不随 current epic 清理、归档或删除 |
| 长期同步流程 | 保留并更新 | `rules/MEMORY_SYNC_SOP.md` 是通用记忆同步 SOP，不随 current epic 清理、归档或删除 |
| 项目专项规则 | 按项目维护 | `memory/Q35_ROADMAP_SYNC_RULES.md` 保存 Q35 Roadmap 专项同步规则；专项规则不放入 `rules/` |
| 长期事实 | 刷新 | `memory/PROJECT_FACTS.md` 应更新过期事实，不应直接清空 |
| 长期决策 | 只追加 | `memory/DECISIONS.md` 不删除历史决策；过期决策用新记录 supersede |
| 长期风险 | 改状态 | `memory/RISKS.md` 中风险应标记 `active`、`mitigated`、`closed` 或 `accepted` |
| 当前状态 | 压缩或重写 | `current/STATE.md` 只保留当前目标、阶段、阻塞点和下一步 |
| 当前任务 | 新 epic 时重置 | `current/tasks.csv` 只保存当前主目标的任务 |
| 子 agent 输出 | 归档 | `current/agent_outputs/` 完成后移入 `archive/`，便于 reviewer 复查 |
| 进度历史 | 按阶段归档 | `memory/PROGRESS_LEDGER.md` 保留近期摘要，旧记录移入 `archive/` |

### 推荐归档目录

新阶段或任务完成后创建：

```text
.codex/agent_group/archive/<yyyymmdd>_<topic>/
```

示例：

```text
.codex/agent_group/archive/20260528_qwen35_stage_b_baseline/
```

推荐归档内容：

```text
archive/<name>/
├── STATE.md
├── epic.md
├── acceptance.md
├── tasks.csv
├── PROGRESS_LEDGER.md
└── agent_outputs/
```

### 标准清理步骤

1. 创建归档目录。
2. 将 `current/agent_outputs/*` 移动到 `archive/<name>/agent_outputs/`。
3. 将旧的 `current/epic.md`、`current/acceptance.md`、`current/tasks.csv`、`current/STATE.md` 复制或移动到归档目录。
4. 如 `PROGRESS_LEDGER.md` 过长，将旧阶段记录移动到归档目录，只在主文件保留最近记录和归档路径摘要。
5. 为新 epic 重建 `current/epic.md`、`current/acceptance.md`、`current/tasks.csv`。
6. 重写 `current/STATE.md`，只保留当前目标、当前阶段、active task、阻塞点、最近关键产物和下一步。
7. 更新 `RISKS.md` 的状态，不直接删除风险。
8. 如有旧决策被替代，在 `DECISIONS.md` 追加新决策，不删除旧决策。
9. 在 `PROGRESS_LEDGER.md` 追加本次清理记录。

### 不建议的做法

- 不直接删除 `memory/DECISIONS.md`、`memory/RISKS.md` 或 `memory/PROJECT_FACTS.md`。
- 不移动到 `current/`、删除或归档 `memory/ROADMAP.md`；它是长期路线图，只能就地更新。
- 不移动到 `current/`、删除或归档 `rules/MEMORY_SYNC_SOP.md`；它是通用同步制度，只能就地更新。
- 不把某个具体 Roadmap 或任务的专项规则写入 `rules/MEMORY_SYNC_SOP.md`；专项规则应放入 `memory/` 并在 `DOC_REGISTRY.yml` 登记。
- 不把完整历史塞进 `current/STATE.md`；它是热启动摘要，不是历史仓库。
- 不删除 `current/agent_outputs/` 后丢失证据；应先归档。
- 不混用多个 epic 的任务到同一个 `current/tasks.csv`。

### 自动化建议

后续可以增加脚本：

```text
.codex/agent_group/scripts/compact_memory.py
```

建议参数：

```text
--archive-name <name>
--keep-recent-progress 3
--reset-current
--archive-agent-outputs
--dry-run
```

脚本应先支持 `--dry-run`，列出将移动、重写或保留的文件，再执行真实清理。
