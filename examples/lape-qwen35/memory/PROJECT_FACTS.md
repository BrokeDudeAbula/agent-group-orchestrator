# Project Facts

最后更新：2026-06-08

## 文档权责边界

本文件是项目级稳定事实索引。

- 权威负责：repo 根路径、长期源码结构、模型/工具/Orin 默认入口、production anchor 语义口径、当前仍可复用的工具事实和已关闭路线索引。
- 不负责：当前工作树是否 dirty、最新 checkpoint、当前任务阻塞点、下一步执行计划、逐任务状态。
- 冲突处理：
  - 当前 HEAD、dirty tree、最新 checkpoint 和下一步以 `current/STATE.md` 为准。
  - 任务状态以 `memory/TASK_LEDGER.md` 和 `current/tasks.csv` 为准。
  - 路线是否关闭、holding 或转主线以 `memory/ROADMAP.md` 与 `memory/DECISIONS.md` 为准。

压缩前完整事实表已归档到：

`.codex/agent_group/archive/20260608_marlin_holding_compaction/memory.before/PROJECT_FACTS.before.md`

## 当前 Repo

- 根目录：`/workspace/liyang/lape_a6d6bfb9`
- 分支：`qwen35_moe_perf`
- 当前 HEAD / working tree / 最新 checkpoint：以 `current/STATE.md` 为准
- 当前 hot spike 路径：`samples/micro_bench/spike/cute_dsl/`
- Marlin holding spike 路径：`samples/micro_bench/spike/marlin_moe/`

## 核心源码结构

- Qwen 模型入口：`src/serve/qwen/`
- Qwen3.5 主模型：`src/serve/qwen/qwen3_5_model.{cc,h}`
- GDN/FLA wrapper：`src/serve/qwen/qwen3_5_gated_delta_net_fla.{cc,h}`
- FLA GDN CUDA kernel：`src/models/layers/fla_gdn/`
- MoE production 路径：`src/models/layers/moe/`
- micro replay：`samples/micro_bench/`
- CuTe/CUTLASS spike：`samples/micro_bench/spike/cute_dsl/`
- Marlin holding spike：`samples/micro_bench/spike/marlin_moe/`
- Orin 产物与报告：`analysis/Qwen35_*`

## Production Baseline / Anchor

- canonical semantic baseline：`analysis/Qwen35_current_semantic_baseline_orin_1_20260528_085712`
- semantic 口径：`norm_topk_prob=true`，显式 `LAPE_QWEN35_GDN_BACKEND=fla`
- production anchor：`aaf6747`
- anchor 指标：MoE 3004 5 轮 cross-confirm median `TTFT=1071.21 ms / p-ntokens/s=2804.31`
- 当前 3000 tok/s 缺口：约 `64 ms TTFT`

## 当前 CuTe/CUTLASS Spike 事实

`samples/micro_bench/spike/cute_dsl/` 当前是 hot spike 路径。

已知事实：

- `CMakeLists.txt`：`LAPE_BUILD_SPIKE_CUTE_DSL` 默认 OFF；spike target 显式锁 `sm_87`。
- `main.cc`：已支持 R0a/R0c/R0d/R0D1/R0E 相关 diagnostic/formal modes；当前 R0F/R1-probe 需从 `cutlass_routed_grouped_micro.cu` 的 dense path 开始。
- `spike_common.h`：CuTe/CUTLASS spike shape/input 常量与 projection 参数。
- `cutlass_shape_bench.cu`：CUTLASS C++ fp16 dense same-shape diagnostic，10/10 Orin PASS，固定非 SOP/tier。
- `cutlass_projection_correctness.cu`：HF raw GPTQ dense-dequant fp16 projection correctness diagnostic，R0c 9/9 Orin PASS，固定非 SOP/tier。
- `cutlass_routed_grouped_micro.cu`：R0d/R0D1/R0E/R0F 相关 routed grouped micro 入口；下一步 Tensor Core sanity 从这里开始。
- Python CuTeDSL route：blocked optional，阻塞点是 `cutlass._mlir` 缺失。
- CuTe/CUTLASS C++ fallback：本地与 `orin_1` smoke PASS，可作为不引入新 Python DSL 依赖的路径。

当前 hot task：

- `Q35-MOE-CUTEDSL-R0F-R1-PROBE`
- 状态：`done / reject_or_hold / probe-only / not production`
- M5 evidence：`analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/report.md`
- 下一步：若继续 CuTe/CUTLASS，必须新建 `Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE`；也可转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`
- 输出边界：`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`

## CuTe/CUTLASS R0E Formal 事实

Evidence：

- `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`

结论：

- Guard：`schema_pass=true`、`status=gate_fail`、`overall_pass=false`、`tier_eligible=false`
- SOP-A PASS：`max_abs=6.661564e-05`、`rmse=2.843369e-06`
- SOP-B PASS：真实 NCU best occupancy `31.060000`
- SOP-C FAIL：family A/B geomean `152.031603/65.925507`
- 状态：`done / tier D / not production`

## Marlin Holding 事实

`Q35-022 M-4 Marlin-MoE Spike R0` 已进入：

`holding / tier D / archived / not production`

归档目录：

- `.codex/agent_group/archive/20260608_marlin_holding_compaction/`

结论：

- SOP-A PASS：`max_abs=0.000120982528`，`rmse=4.56000724e-06`
- SOP-B PASS：fresh Orin NCU best occupancy `33.24% > 30%`
- SOP-C FAIL：family A/B geomean `1.155492/1.287823`
- 不进入 R1/R3/production
- 除非用户明确重开 Marlin，否则不恢复 Marlin candidate-only 参数线

## 已关闭路线

以下路线已关闭、holding 或不在当前热路径中；不要从 hot 文档恢复旧行动项：

- Q35-005：抖动 + 语义口径变化，关闭
- Q35-010-D1：side-stream token-id gate 失败，已放弃
- Q35-016B：GDN beta-sigmoid cache targeted 负结果
- Q35-017：full attention qkv workspace-cache targeted 负结果
- Q35-021：grouped GEMM config sweep 负结果
- Q35-022 M-4：Marlin-MoE `wna16` spike R0 holding / tier D / archived / not production
- Q35-025：ssm_state traffic 占比不足，reject
- Q35-027：decode kernel 非 memory/compute bound，reject
- Q35-029：G-5 cp.async 物理收益不足，reject
- Q35-030：norm_gate+conv 占比不足，reject

## Orin 事实

- 默认 target：`orin_1`
- host：`orin_1`
- Docker：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`
- 标准同步入口：`sync-orin-lape-build`
- 当前 hot spike target 验证：先 sync，再显式构建 `qwen3_5_cute_dsl_spike`

所有 R4 验证必须记录 commit、模型路径、bundle 路径、env、build type、命令、远端和本地输出目录。
