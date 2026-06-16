---
ag_schema: v1
doc_id: AG-RULE-ROUTING-POLICY
category: rules
doc_type: routing_policy
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
canonical_path: .codex/agent_group/rules/ROUTING_POLICY.md
compat_links:
  - .codex/agent_group/ROUTING_POLICY.md
update_triggers:
  - worker_change
  - risk_policy_change
  - orchestration_policy_change
sync_targets:
  - .codex/agent_group/rules/BOOTSTRAP.md
  - .codex/agent_group/rules/WORKER_REGISTRY.md
  - .codex/agent_group/README.md
forbidden_ops:
  - delete
  - archive
  - move_to_current
---

# Routing Policy

本文件定义 main-orchestrator 的自动编排规则。用户只给目标时，main agent 必须按本策略自行选择 worker、拆分任务、更新账本并汇总结果。

## 默认模式：auto-orchestrate

当用户没有手动指定 worker 时，main agent 默认启用 auto-orchestrate。

输入格式可以很简单：

```text
目标：……
约束：……
产物：……
```

main agent 需要自行完成：

1. 判断任务类型和风险等级。
2. 选择 worker。
3. 生成任务 DAG。
4. 更新 `.codex/agent_group/current/tasks.csv`。
5. 指派 worker 执行。
6. 收集 worker 输出。
7. 更新 `.codex/agent_group/PROGRESS_LEDGER.md`、必要时更新 `DECISIONS.md` 和 `RISKS.md`。
8. 向用户汇报总进度、产物、阻塞点和下一步。

## Worker 选择入口

worker 的角色定义、权限边界、输入输出要求和选择触发条件以 `WORKER_REGISTRY.md` 为权威入口。

本文件只定义 main-orchestrator 如何组合 worker、如何执行默认 DAG、如何应用风险等级和汇报规范。选择 worker 时，main-orchestrator 应先读取：

```text
.codex/agent_group/rules/WORKER_REGISTRY.md
```

然后根据本文件的 DAG 模板决定执行顺序、是否跳过某个 worker、是否需要用户确认 R3/R4 门禁。

## 默认任务 DAG

### 只读分析任务

```text
repo-explorer
  -> perf-analyst
  -> oss-scout
  -> qwen-architect
  -> reviewer
  -> main-orchestrator 汇总
```

如果不涉及性能，可以跳过 `perf-analyst`。如果是纯本地 bugfix 或证据已经足够明确，可以跳过 `oss-scout`，但 main-orchestrator 需要说明跳过原因。

### 文档或元数据任务

```text
repo-explorer
  -> kernel-dev 或 main-orchestrator 生成文档
  -> reviewer
  -> main-orchestrator 汇总
```

### 推理核心代码改动任务

```text
repo-explorer
  -> perf-analyst
  -> oss-scout
  -> qwen-architect
  -> 用户确认写入范围
  -> kernel-dev
  -> reviewer
  -> 用户确认 Orin 验证
  -> orin-runner
  -> perf-analyst
  -> reviewer
  -> main-orchestrator 汇总
```

### Orin 验证任务

```text
repo-explorer
  -> perf-analyst 确认 baseline
  -> 用户确认远端命令
  -> orin-runner
  -> perf-analyst 对比
  -> reviewer
  -> main-orchestrator 汇总
```

## 风险等级

### R0：只读

- 只读源码、文档、日志、报告。
- 可自动执行，无需用户额外确认。

### R1：`.codex/agent_group` 内文档或元数据写入

- 可自动执行。
- 必须在最终汇报中列出写入文件。

### R2：非核心文档、脚本或报告生成

- main agent 可以提出计划。
- 如果写入范围明确且不影响构建/推理，可自动执行；否则询问用户。

### R3：推理核心代码、CUDA、NNCL、CMake、构建脚本改动

- 必须先让用户确认写入范围。
- 不允许多个写入型 worker 并行修改同一模块。

### R4：远端 Orin、nsys、长时间构建或性能实验

- 必须先让用户确认命令口径、预计耗时和输出目录。

## 任务命名

自动编排任务使用前缀：

```text
AUTO-<yyyymmdd>-<nn>
```

示例：

```text
AUTO-20260527-01
AUTO-20260527-02
```

## Worker 输出路径

默认输出到：

```text
.codex/agent_group/current/agent_outputs/<task_id>_<worker>.md
```

demo 或临时任务可以输出到自己的子目录，例如：

```text
.codex/agent_group/demo/agent_outputs/<task_id>_<worker>.md
```

## 汇报格式

main agent 最终汇报必须包含：

- 目标是否完成；
- 自动选择了哪些 worker，为什么；
- 产物路径；
- 关键结论；
- 阻塞点或风险；
- 下一步建议；
- 如有写入，列出写入文件。
