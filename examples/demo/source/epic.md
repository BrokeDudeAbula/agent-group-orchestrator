# Demo Epic: Qwen3.5 micro bench 快速索引

## 目标

通过一次低风险 demo，验证 agent group 的协作方式：main agent 拆解任务，sub-agent 各自完成探索、分析、写文档和 review，最终产出一个可用的快速索引文件。

## 范围

允许：

- 读取 repo 中的源码、脚本、文档和 analysis 报告；
- 写入 `.codex/agent_group/demo` 下的进度、agent 输出和最终 demo 文档。

禁止：

- 修改 `src`、`samples`、`scripts`、`tools`、`analysis` 下的任何文件；
- 启动 `orin_1` 同步、构建、replay、e2e 或 nsys；
- 修改正式 Qwen3.5 优化任务的 `current/tasks.csv`。

## 期望产物

```text
.codex/agent_group/demo/output/qwen35_micro_bench_quick_index.md
```

该文档应让一个新 agent 在 3 分钟内知道当前 repo 中 Qwen3.5 micro bench、Orin 验证和 baseline 报告在哪里。
