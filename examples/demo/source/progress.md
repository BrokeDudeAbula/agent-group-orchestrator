# Demo Progress

## 2026-05-27 初始化

- 建立 demo 目标、验收标准和任务表。
- demo 限制为 `.codex/agent_group/demo` 内写入，不修改推理源码，不启动 Orin 任务。

## 当前状态

- demo 已完成，DMO-001 到 DMO-005 均为 `done`。

## 2026-05-27 运行记录

- main-orchestrator 已读取 `epic.md`、`tasks.csv`、`acceptance.md`，并按 demo 范围派出四个子 agent。
- repo-explorer 只读确认了 Qwen3.5 micro bench、attention/GDN/MoE replay target、Orin 验证脚本和本地/Orin 边界；输出为 `agent_outputs/DMO-001_repo-explorer.md`。
- perf-analyst 只读确认了 E2E baseline、micro bench baseline、35B MoE true-shape attention/GDN replay 和 stage1/stage2 归因路径；输出为 `agent_outputs/DMO-002_perf-analyst.md`。
- kernel-dev 仅写入 `output/qwen35_micro_bench_quick_index.md`，未修改源码、脚本、工具或 analysis。
- reviewer 只读审查 quick index，结论为“无阻塞级事实错误”；输出为 `agent_outputs/DMO-004_reviewer.md`。

## 产物

- quick index：`output/qwen35_micro_bench_quick_index.md`
- repo-explorer 摘要：`agent_outputs/DMO-001_repo-explorer.md`
- perf-analyst 摘要：`agent_outputs/DMO-002_perf-analyst.md`
- reviewer 摘要：`agent_outputs/DMO-004_reviewer.md`

## 风险与边界

- 本次 demo 未启动 Orin 同步、远端构建、replay、e2e 或 nsys。
- 本次 demo 未修改 `src`、`samples`、`scripts`、`tools`、`analysis` 下任何文件。
- reviewer 的非阻塞建议：`tools/run_orin1_qwen35_gdn_prefill_validation.sh` 默认输出路径实际包含时间戳，后续正式索引可写为 `analysis/Qwen35_gdn_prefill_validate_<date>_<time>_<backend>`。

## 下一步

- 若要进入真实优化，应从 quick index 指向的 `analysis/qwen35_stage2_prefill_optimization/commands.md`、stage2 baseline 和 Orin 同步 skill 继续，而不是复用本 demo 的低风险只读约束。
