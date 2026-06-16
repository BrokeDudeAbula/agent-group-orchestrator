---
ag_schema: v1
doc_id: AG-RULE-RUNBOOK-ORIN1
category: rules
doc_type: runbook
authority: canonical
lifecycle: warm
read_policy: on_demand
write_policy: controlled_update
risk_level: R1
owner: main-orchestrator
allowed_writers:
  - main-orchestrator
  - orin-runner
allowed_readers:
  - main-orchestrator
  - orin-runner
  - reviewer
canonical_path: .codex/agent_group/rules/RUNBOOK_ORIN1.md
compat_links:
  - .codex/agent_group/RUNBOOK_ORIN1.md
update_triggers:
  - orin_command_change
  - target_device_change
  - skill_entrypoint_change
sync_targets:
  - .codex/agent_group/rules/BOOTSTRAP.md
forbidden_ops:
  - delete
  - archive
  - move_to_current
---

# Orin 1 Runbook

本文件是 `orin_1` 验证的 agent_group 薄封装，不复制 Orin 同步、构建、Qwen3.5 e2e、micro bench、nsys 或其它测试流程。所有测试流程统一委托给 skill：

- skill：`sync-orin-lape-build`
- skill 文件：`/home/titan/.codex/skills/sync-orin-lape-build/SKILL.md`
- 统一脚本：`~/.codex/skills/sync-orin-lape-build/scripts/sync_orin_lape_build.sh`

## 默认目标

- target：`orin_1`
- host：`orin_1`
- container：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`

## 执行门禁

任何 Orin、nsys、远端构建或长时间验证都属于 R4。执行前 main-orchestrator 必须明确：

- 用户已确认可以启动远端或长时间任务；
- 目标设备为 `orin_1`；
- 命令口径明确；
- 预计耗时明确；
- 本地输出目录明确，默认应写入 `analysis/`；
- 停止条件明确。

未满足以上条件时，orin-runner 不得启动远端任务。

## 统一入口

orin-runner 必须使用 `sync-orin-lape-build` skill 的统一脚本，避免手写 `ssh`、`docker exec`、`cmake`、`make` 或远端测试命令。

```bash
SKILL_SCRIPT=~/.codex/skills/sync-orin-lape-build/scripts/sync_orin_lape_build.sh
```

## Spike Target 例外

Q35-022 M-4 R0 spike target `qwen3_5_marlin_moe_spike` 不是 production 默认构建目标。该路径仍必须先用 `sync-orin-lape-build` 做同步；但构建 spike target 时允许按 action plan 使用：

1. `sync-orin-lape-build --sync-only`
2. `ssh orin_1 'docker exec liyang_lape ... cmake -DLAPE_BUILD_SPIKE_MARLIN_MOE=ON ... && cmake --build build --target qwen3_5_marlin_moe_spike ...'`

这属于 R4，执行前仍需用户确认命令口径、预计耗时、本地输出目录和停止条件。orin-runner 必须把 sync 命令和后续 explicit target build 命令都记录到报告中。

同步并编译：

```bash
bash "$SKILL_SCRIPT" \
  --target orin_1 \
  --source <repo-root>
```

全量 Qwen3.5 e2e：

```bash
bash "$SKILL_SCRIPT" \
  --target orin_1 \
  --source <repo-root> \
  --full-test
```

指定 Qwen3.5 e2e 模型集合：

```bash
bash "$SKILL_SCRIPT" \
  --target orin_1 \
  --source <repo-root> \
  --qwen35-e2e-test \
  --qwen35-e2e-models dense,moe,omni
```

全量 Qwen3.5 micro bench：

```bash
bash "$SKILL_SCRIPT" \
  --target orin_1 \
  --source <repo-root> \
  --qwen35-micro-bench
```

## 输出记录要求

每次 Orin 验证完成后，orin-runner 必须记录：

- 使用的入口：`sync-orin-lape-build` skill；
- 完整执行命令；
- 本地输出目录；
- 远端输出目录或临时目录；
- git commit 或 diff 摘要；
- 模型路径；
- bundle 路径；
- warmup/iters 或 e2e 模型集合；
- 环境变量；
- 成功/失败 case；
- NaN 和精度误差摘要；
- 性能变化摘要；
- 失败时的日志路径和关键错误。
