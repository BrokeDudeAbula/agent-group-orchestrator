# Agent Group Demo: 修正 micro bench 文档索引

这个 demo 用一个低风险文档任务演示 main agent 如何管理 sub-agent group。它不会修改 CUDA/C++ 推理核心代码，也不会启动 `orin_1` 长任务。

## Demo 目标

验证当前 repo 的 Qwen3.5 micro bench 文档与脚本索引是否完整，并补充一个轻量说明文件，帮助后续 agent 快速找到：

- Qwen3.5 micro bench/replay 入口；
- baseline 报告；
- Orin 验证脚本；
- 哪些任务需要真实 Orin 环境，哪些可以本地只读完成。

最终产物建议为：

```text
.codex/agent_group/demo/output/qwen35_micro_bench_quick_index.md
```

## 参与 agent

| Agent | 权限 | 本 demo 职责 |
|---|---|---|
| `main-orchestrator` | 读写 `.codex/agent_group/demo` | 拆任务、派工、汇总、更新进度 |
| `repo-explorer` | 只读 repo | 查找 micro bench、Orin、baseline 相关事实 |
| `perf-analyst` | 只读 analysis | 汇总已有 baseline 指标和报告路径 |
| `kernel-dev` | 只写 demo output | 根据前两个 agent 的结论生成 quick index 文档，不改源码 |
| `reviewer` | 只读 | 审查 quick index 是否事实准确、是否误导后续开发 |

## 推荐启动提示词

把下面这段直接发给 main agent：

```text
请使用 .codex/agent_group/demo 运行一次 agent group demo。

目标：生成 .codex/agent_group/demo/output/qwen35_micro_bench_quick_index.md，内容是当前 repo 的 Qwen3.5 micro bench / Orin 验证 / baseline 快速索引。

要求：
1. 先读取 .codex/agent_group/demo/epic.md、tasks.csv、acceptance.md；
2. 派 repo-explorer 只读确认代码、脚本、文档入口；
3. 派 perf-analyst 只读确认已有 baseline 报告路径和关键指标；
4. 派 kernel-dev 只允许写 .codex/agent_group/demo/output/qwen35_micro_bench_quick_index.md；
5. 派 reviewer 只读审查 quick index；
6. main agent 更新 .codex/agent_group/demo/progress.md 和 tasks.csv；
7. 不修改 src、samples、scripts、tools、analysis 下的任何文件，不启动 Orin 任务。
```

## 预期体验

你会看到 main agent 从 `tasks.csv` 恢复状态，给不同 sub-agent 分配明确范围。每个 sub-agent 的输出都落到：

```text
.codex/agent_group/demo/agent_outputs/
```

最后 main agent 只汇报：

- 哪些任务完成；
- 生成了什么文件；
- reviewer 是否通过；
- 后续如果做真实优化，应该接到哪个正式任务。
