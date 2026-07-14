# Agent Group Orchestrator

Reusable Codex plugin for project-local multi-agent orchestration.

This plugin turns a project-local `agent_group` workflow into a generic package:

- `skills/` contains the Codex-facing workflows.
- `references/` contains reusable policies and contracts loaded on demand.
- `assets/templates/instance/` contains a starter `.codex/agent_group` instance.
- `scripts/` contains deterministic initialization, validation, and compaction helpers.
- `examples/sample/` contains a neutral sample instance for regression and documentation.

The plugin should not keep live project state at its root. Project-specific state belongs in a target repository instance, usually `.codex/agent_group/`.

## 执行模型

`agent-group` 的默认模式是 `auto-orchestrate`。主 agent 只作为 `main-orchestrator` 监督任务：负责目标澄清、任务拆解、worker 选择、sub-agent 派发、进度监督、风险门禁、记忆同步、证据抽查和结果汇总。

除 `main-orchestrator` 以外，所有被选中的 worker 都必须通过兼容的 sub-agent 后端执行。当前规则按后端中立方式描述，要求同时适配 Codex 和 Claude Code CLI 的 sub-agent 机制。主 agent 不应直接代替 worker 做开发、测试、benchmark、代码 review、仓库调研、竞品调研或架构分析；如果当前环境没有可用 sub-agent 机制，应把任务标记为 blocked 或要求用户切换到支持 sub-agent 的后端。

## 使用方式

### 1. 获取插件源码

```bash
git clone <agent-group-orchestrator-repository-url>
cd agent-group-orchestrator
```

这个仓库本身是一个 Codex plugin root，插件清单位于 `.codex-plugin/plugin.json`。

### 2. 作为 Codex 本地插件安装

Codex 插件需要通过 marketplace 入口安装。最常见的个人本地插件布局是：

```text
~/.agents/plugins/marketplace.json
~/plugins/agent-group-orchestrator/
```

将本仓库放到 `~/plugins/agent-group-orchestrator` 后，在 `~/.agents/plugins/marketplace.json` 中加入插件条目：

```json
{
  "name": "personal",
  "interface": {
    "displayName": "Personal"
  },
  "plugins": [
    {
      "name": "agent-group-orchestrator",
      "source": {
        "source": "local",
        "path": "./plugins/agent-group-orchestrator"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

然后安装插件：

```bash
codex plugin add agent-group-orchestrator@personal
```

安装后请开启一个新的 Codex 线程，让 Codex 重新加载插件提供的 skills。

> 说明：本仓库不是 marketplace root，因此不要直接把本仓库路径传给 `codex plugin marketplace add`。如果你使用团队级 marketplace，应在团队 marketplace 的 `plugins[]` 中引用本插件目录，再执行 `codex plugin marketplace add <marketplace-root>`。

### 3. 初始化项目本地 agent_group 实例

在目标项目仓库中创建 `.codex/agent_group`：

```bash
python3 /path/to/agent-group-orchestrator/scripts/init_agent_group.py \
  --target .codex/agent_group \
  --project-name <your-project-name>
```

初始化后校验目录结构：

```bash
python3 /path/to/agent-group-orchestrator/scripts/validate_agent_group.py .codex/agent_group
```

严格校验记忆文件形态：

```bash
python3 /path/to/agent-group-orchestrator/scripts/validate_agent_group.py --strict .codex/agent_group
```

### 4. 在 Codex 中触发工作流

插件安装并新开线程后，可以直接用自然语言触发对应 skill：

```text
Initialize an agent group workspace for this repo.
```

用于初始化 `.codex/agent_group`。

```text
Use agent-group auto-orchestrate mode for this goal: <your-goal>
```

用于让 Codex 按 worker registry、routing policy、sub-agent execution、risk gate 和 memory sync 规则拆解并推进任务。

```text
Validate this repo's agent group memory structure.
```

用于校验当前项目的 agent group 结构和记忆文件一致性。

```text
Review this agent group worker output and memory update.
```

用于对 worker 输出、风险门禁、证据链和记忆同步结果做 review。

### 5. 常用维护命令

从 `current/tasks.csv` 渲染 Mermaid 任务图；如果任务表包含 `depends_on` 列，脚本会生成依赖边：

```bash
python3 /path/to/agent-group-orchestrator/scripts/render_task_dag.py \
  .codex/agent_group/current/tasks.csv
```

归档当前阶段记忆，先 dry-run：

```bash
python3 /path/to/agent-group-orchestrator/scripts/compact_memory.py \
  --target .codex/agent_group \
  --archive-name 20260616_example \
  --dry-run
```

确认无误后执行归档：

```bash
python3 /path/to/agent-group-orchestrator/scripts/compact_memory.py \
  --target .codex/agent_group \
  --archive-name 20260616_example
```

归档脚本默认会重建空的 `current/STATE.md`、`current/epic.md`、`current/acceptance.md` 和 `current/tasks.csv`，确保实例仍可通过严格校验。只有在另一个工具会立即重建这些 hot state 文件时，才使用 `--no-reset-current`。

公开或提交前扫描当前工作区中的凭证、真实用户路径、主机标识、线程 UUID 和误粘贴任务提示：

```bash
python3 scripts/check_public_safety.py .
python3 scripts/check_public_safety.py --git-history .
```

第一条命令覆盖未跟踪文本文件，以便在 `git add` 前发现风险；第二条还会检查所有本地可达历史及提交元数据，应用于正式发布前。真实项目报告和运行时状态应保存在插件仓库之外。

### 6. 目录约定

项目内的运行时状态应放在目标仓库的 `.codex/agent_group/`，不要写回插件根目录。

- `current/STATE.md`：当前活跃目标、阶段、阻塞点和下一步。
- `current/tasks.csv`：当前 epic 的任务清单。
- `current/agent_outputs/`：当前阶段 worker 输出和证据。
- `memory/TASK_LEDGER.md`：长期任务台账。
- `memory/PROGRESS_LEDGER.md`：追加式进展记录。
- `memory/DECISIONS.md`：架构与流程决策。
- `memory/RISKS.md`：风险、缓解和关闭记录。
- `rules/`：项目本地 worker、sub-agent 执行、路由、同步和 runbook 规则。
