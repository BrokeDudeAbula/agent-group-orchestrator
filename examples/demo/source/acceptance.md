# Demo Acceptance

demo 通过标准：

1. `tasks.csv` 中 DMO-001 到 DMO-005 状态最终为 `done` 或有明确阻塞说明。
2. `agent_outputs/` 下至少包含 repo-explorer、perf-analyst、reviewer 三类输出摘要。
3. `output/qwen35_micro_bench_quick_index.md` 存在。
4. quick index 至少包含：
   - micro bench 总说明路径；
   - attention/GDN/MoE replay target 或源码路径；
   - Orin 验证脚本路径；
   - baseline e2e 与 micro bench 报告路径；
   - 哪些操作本地可做，哪些必须在 Orin 上做。
5. reviewer 没有阻塞级事实错误。
6. demo 未修改推理源码，未启动远端 Orin 长任务。
