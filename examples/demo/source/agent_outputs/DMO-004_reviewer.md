# DMO-004 reviewer 审查摘要

## 审查结论

quick index 整体满足 `.codex/agent_group/demo/acceptance.md` 中对 `output/qwen35_micro_bench_quick_index.md` 的内容清单要求。已只读对照 `DMO-001_repo-explorer.md`、`DMO-002_perf-analyst.md` 及少量源码/脚本/报告路径，未执行 Orin 同步、构建、replay、e2e 或 nsys。

## Acceptance 清单核对

| 项目 | 结论 | 说明 |
|---|---|---|
| micro bench 总说明路径 | 通过 | 已包含 `samples/micro_bench/README.md` 和 `samples/micro_bench/qwen3_5_micro_replay.md` |
| attention/GDN/MoE replay target 或源码路径 | 通过 | 已列出 `qwen3_5_full_attention_micro_replay`、`qwen3_5_gdn_micro_replay`、`qwen3_5_moe_block_micro_replay`、`qwen3_5_routed_moe_micro_replay` 及对应源码 |
| Orin 验证脚本路径 | 通过 | 已列出 `scripts/run_orin1_qwen35_micro_replay.sh` 和 `tools/run_orin1_qwen35_gdn_prefill_validation.sh` |
| baseline e2e 与 micro bench 报告路径 | 通过 | 已列出 `analysis/Qwen35_e2e_orin_1_20260526/report.md`、`analysis/Qwen35_micro_bench_20260525/bench_report.md` 等路径 |
| 本地可做 vs 必须 Orin 上做 | 通过 | 已明确区分只读索引、本地依赖前提、Orin 真实复现、远端同步构建、nsys 采集边界 |
| reviewer 无阻塞级事实错误 | 通过 | 见下节 |
| demo 未修改推理源码、未启动远端长任务 | 本次 reviewer 未发现 quick index 存在诱导长任务的表述；本次审查也未执行长任务 |

## 阻塞级事实错误

无阻塞级事实错误。

## 非阻塞建议

1. `tools/run_orin1_qwen35_gdn_prefill_validation.sh` 的默认输出实际包含时间戳，形如 `analysis/Qwen35_gdn_prefill_validate_<date>_<time>_<backend>`；quick index 写为 `<date>_<backend>`，不影响定位，但建议后续更精确。
2. quick index 的“本地可做”中提到“本地构建或 replay”是有前提条件的，当前 demo/reviewer 约束禁止运行；建议后续给新 agent 的版本补一句“若任务明确禁止长任务，则仅做只读检查”。
3. acceptance 第 1 条涉及 `tasks.csv` 状态最终更新；当前 quick index 本身无法满足该项，需要 DMO-005/main-orchestrator 后续处理，不属于 quick index 事实错误。

## Orin 长任务风险确认

未发现会误导后续 agent 启动 Orin 长任务的表述。quick index 已把 `scripts/run_orin1_qwen35_micro_replay.sh`、`tools/run_orin1_qwen35_gdn_prefill_validation.sh`、`--run-nsys` 和依赖 Orin Docker/远端模型路径的验证明确归类到“必须在 Orin 上做”。
