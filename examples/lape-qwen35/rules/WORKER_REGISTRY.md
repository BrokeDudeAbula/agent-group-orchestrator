---
ag_schema: v1
doc_id: AG-RULE-WORKER-REGISTRY
category: rules
doc_type: worker_registry
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
canonical_path: .codex/agent_group/rules/WORKER_REGISTRY.md
compat_links:
  - .codex/agent_group/WORKER_REGISTRY.md
update_triggers:
  - worker_added
  - worker_removed
  - worker_permission_change
sync_targets:
  - .codex/agent_group/rules/ROUTING_POLICY.md
  - .codex/agent_group/README.md
forbidden_ops:
  - delete
  - archive
  - move_to_current
---

# Worker Registry

本文件定义 main-orchestrator 可调度的 worker 角色、适用场景、权限边界和输出要求。main agent 在自动编排任务时必须先参考本文件。

## Agent 文件映射规则

worker 名称必须与 `.codex/agent_group/agents/<worker-name>.md` 文件名及 frontmatter `name` 字段一致。main-orchestrator 选择 worker 后，应读取对应 `agent_file` 中的角色定义、工具、约束和输出要求。

## main-orchestrator

agent_file：`.codex/agent_group/agents/main-orchestrator.md`

选择触发条件：

- 用户直接提出目标、约束、产物或需要跨 worker 编排。
- 任务需要拆分、定 gate、同步记忆、汇总 worker 输出或与用户沟通。
- 任务涉及 R3/R4 门禁，需要先形成写入范围、命令口径、预计耗时和停止条件。

职责：

- 只和用户直接沟通。
- 将用户目标转成任务 DAG、验收标准和 worker 分工。
- 更新 `.codex/agent_group/TASK_LEDGER.md`、`.codex/agent_group/PROGRESS_LEDGER.md` 和 `.codex/agent_group/current/tasks.csv`。
- 汇总 worker 输出，判断是否进入下一阶段。

权限：

- 可读写 `.codex/agent_group`。
- 不直接修改推理核心代码，除非用户明确要求 main agent 自己执行小范围文档或元数据改动。

## repo-explorer

agent_file：`.codex/agent_group/agents/repo-explorer.md`

选择触发条件：

- 目标涉及未知代码路径、调用链、脚本入口或历史报告。
- 目标中出现 `Qwen3.5`、`MoE`、`GDN`、`attention`、`Orin`、`replay`、`nsys`，但当前任务账本没有足够事实索引。
- main agent 准备让写入型 worker 修改代码前，需要先确认影响范围。

适用场景：

- 用户目标涉及未知代码路径、调用链、脚本入口、历史报告位置。
- 当前任务需要先确认 repo 事实，避免使用旧文档或过期路径。

权限：

- 只读。
- 不修改文件，不跑长任务。

典型输入：

- `src/serve/qwen`
- `src/models/layers`
- `src/models/layers/moe`
- `src/models/layers/fla_gdn`
- `samples/micro_bench`
- `scripts`
- `tools`
- `analysis/qwen35_stage*`
- `analysis/Qwen35_*`

输出：

- 事实索引、调用链、关键路径、不确定点、建议下一步。

## perf-analyst

agent_file：`.codex/agent_group/agents/perf-analyst.md`

选择触发条件：

- 目标涉及性能、baseline、回归、TTFT、TPS、latency、nsys、benchmark、e2e、micro replay。
- 需要比较 `baseline` 和 `current`。
- 需要判断性能结论是否有足够证据，或性能数据是否可比。

适用场景：

- 用户目标涉及 benchmark、micro replay、e2e、nsys、baseline、回归判断、热点归因。
- main agent 需要判断性能结论是否有足够证据。

权限：

- 只读。
- 不修改代码，不生成新的性能结论时不得启动远端任务。

典型输入：

- `analysis/Qwen35_e2e_orin_1_*`
- `analysis/Qwen35_micro_bench_*`
- `analysis/qwen35_stage1_attribution`
- `analysis/qwen35_stage2_prefill_optimization`
- `samples/micro_bench/scripts/compare_bench_results.py`

输出：

- baseline/current 指标摘要、回归判断、证据边界、缺失数据。

## oss-scout

agent_file：`.codex/agent_group/agents/oss-scout.md`

选择触发条件：

- 目标涉及规划、调研、方案、选型、优化方向或“有没有现成实现”。
- 任务需要在 LAPE 自研实现与开源方案之间做取舍。
- qwen-architect 准备制定方案，但缺少外部实现对照。
- 目标涉及通用推理框架、kernel、attention、MoE、GDN、KV cache、scheduler 或 Orin 端侧优化。

适用场景：

- 用户目标涉及规划、调研、技术选型、优化方案或新功能设计。
- 当前 repo 内没有明显成熟方案，需要参考上游、官方或开源实现。
- 任务涉及 MoE、GDN、attention、KV cache、scheduler、kernel fusion、CUTLASS、Triton、TensorRT-LLM、vLLM、SGLang 等可复用生态方案。

权限：

- 只读。
- 可做网页、GitHub、官方文档和本地 `third_party` 源码调研。
- 不修改源码，不引入依赖，不运行外部长任务。

典型输入：

- repo-explorer 输出
- perf-analyst 输出
- `.codex/agent_group/PROJECT_FACTS.md`
- `third_party/flash_attention`
- `third_party/nncl`
- 相关上游开源项目、官方文档、issue/PR 或论文实现

输出：

- 开源候选表、可迁移点、不可迁移点、license/依赖风险、推荐输入。

## qwen-architect

agent_file：`.codex/agent_group/agents/qwen-architect.md`

选择触发条件：

- 目标涉及方案设计、优化优先级、收益假设、风险评估。
- 任务需要在 MoE、GDN、attention、NNCL、CUTLASS、TensorRT/LLM 推理框架之间做取舍。
- repo-explorer、perf-analyst 或 oss-scout 已输出事实，但还没有可执行实现方案。

适用场景：

- 用户目标涉及 Qwen3.5 MoE、hybrid attention、GDN、prefill/TTFT 优化方案。
- 需要判断优化优先级、模块边界、收益假设、风险和验证口径。

权限：

- 只读。
- 不直接改代码。

典型输入：

- `qwen35_moe_optimization_migration_plan.md`
- `.codex/agent_group/PROJECT_FACTS.md`
- perf-analyst 输出
- repo-explorer 输出
- oss-scout 输出

输出：

- 推荐方案、优先级、实现范围、风险、开源方案对照、验证命令或报告口径、不建议事项。

## kernel-dev

agent_file：`.codex/agent_group/agents/kernel-dev.md`

选择触发条件：

- 用户目标明确需要代码、脚本或文档改动。
- main agent 已指定写入范围。
- 对于推理核心代码、CUDA、NNCL、CMake 或构建脚本，用户已确认可以改动。
- 低风险例外：写入范围仅限 `.codex/agent_group` 或明确的文档产物时，可由 main agent 自动派发。

适用场景：

- 方案已明确，且需要修改 C++、CUDA、NNCL、micro bench 或脚本。
- 用户已确认写入范围，或任务明确是 `.codex/agent_group` 内的低风险文档产物。

权限：

- 可写 main agent 指定范围。
- 不得回退他人改动。
- 不得修改未授权模块。
- 不得启动 Orin 长任务。

典型输入：

- qwen-architect 输出
- 写入范围
- 验收标准

输出：

- 代码 diff 摘要、修改文件、行为变化、构建/测试命令、待验证风险。

## orin-runner

agent_file：`.codex/agent_group/agents/orin-runner.md`

选择触发条件：

- 任务需要真实 Orin 设备验证。
- main agent 已明确命令、目标设备、输出目录、预计耗时和停止条件。
- 用户已确认可以启动远端或长时间任务。

适用场景：

- 任务需要 `orin_1` 同步、构建、micro replay、e2e、nsys 或真实设备性能验证。

权限：

- 执行远端验证命令。
- 不修改推理代码。
- 不清理历史 `analysis` 产物。

前置条件：

- main agent 已明确命令口径、预计耗时、输出目录和停止条件。
- 用户确认可以启动远端或长时间任务。
- Orin 同步、构建、Qwen3.5 e2e、micro bench、nsys 或其它测试流程必须使用 `sync-orin-lape-build` skill。

输出：

- 执行命令、本地和远端输出目录、成功/失败 case、精度和性能摘要、阻塞点。

## reviewer

agent_file：`.codex/agent_group/agents/reviewer.md`

选择触发条件：

- 有代码 diff。
- 有最终文档产物。
- 有性能结论、验证报告或 baseline/current 对比结论。
- 准备把任务标记为 `done` 或进入下一阶段。

适用场景：

- 有代码 diff、文档产物、性能结论、验证报告或准备进入下一阶段。
- main agent 需要独立审查 correctness、测试缺口和风险。

权限：

- 只读。
- 不修改文件。

输出：

- Findings、Open Questions、Test Gaps、Conclusion。
