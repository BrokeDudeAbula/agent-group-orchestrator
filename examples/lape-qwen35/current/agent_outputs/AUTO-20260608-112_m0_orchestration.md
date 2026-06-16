# AUTO-20260608-112 M0 Orchestration

## 结论

本轮已用 `/goal` 启动：

- `Q35-MOE-CUTEDSL-R0F-R1-PROBE: optimize Cute/CUTLASS C++ spike timing toward NNCL baseline, target ratio <=1.20x, probe-only, no production path changes`

当前任务进入 `in_progress / M0 baseline locked / probe-only`。R0E formal gate fail 结论不变，R0F/R1-probe 不生成 SOP/tier 证据。

## 一次性授权范围

用户已选择一次性授权节奏。本轮允许写入范围固定为：

- `samples/micro_bench/spike/cute_dsl/`
- 顶层或 spike 局部 `CMakeLists.txt` 的必要 spike 接入
- `.codex/agent_group/`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_<TS>/`

允许在 `orin_1` 容器 `liyang_lape` 执行：

- 同步源码到 `/workspace/liyang/workspace/lape`
- Release 构建：`LAPE_BUILD_SPIKE_CUTE_DSL=ON`，`CMAKE_CUDA_ARCHITECTURES=87`
- 小规模 micro smoke
- 必要 NCU candidate isolation

预计耗时：

- 单次同步/构建：约 5-20 分钟，取决于远端缓存。
- M1/M2 小规模 smoke：约 1-10 分钟。
- NCU：只在 M3 启动，单 case 约 5-20 分钟。

输出目录：

- 本地：`analysis/Qwen35_cutedsl_r0f_r1_probe_<TS>/`
- worker 输出：`.codex/agent_group/current/agent_outputs/AUTO-20260608-112_<milestone>_<worker>.md`

停止条件：

- 构建失败。
- 输出精度非有限或全零。
- NCU 抓不到 CuTe/CUTLASS candidate kernel，或只抓到 NNCL baseline `MoeFCGemm`。
- ratio 连续两轮明显 `>1.50x`。

## M0 基线事实

- 当前 spike 源码在 `samples/micro_bench/spike/cute_dsl/`，目标 `qwen3_5_cute_dsl_spike` 默认 OFF，不链 `liblape.so`，不改 production path。
- `cutlass_routed_grouped_micro.cu` 当前 dense helper 使用 `OpClassSimt + Sm70`，不是 Orin `sm_87` Tensor Core 上限路径。
- 当前 routed/grouped candidate 仍是 per-expert serial dense GEMM，且 timed loop 中仍有同步、临时 tensor、`.contiguous()`、layout copy 和 host/device roundtrip 风险；M2 前所有 timing 都必须视为 contaminated diagnostic。
- R0D1 diagnostic same-run NNCL baseline evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d1_nncl_paired_orin_1_20260608_083804/`。
- R0E formal failure evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`。

## Baseline 口径

- 主 baseline：same-run NNCL grouped `MoeGroupGemm`，字段 `baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`。
- ratio：`candidate_ms / nncl_ms`。
- 聚合：family A/B 各 5 个 SOP-C shape 的 geomean。
- 当前 probe 目标：family A/B geomean 均 `<=1.20x`，同时 `M64` 和 `M898` 不出现明显灾难性退化。
- R0E formal 失败事实：family A/B geomean `152.031603/65.925507`，hot `M898` 为 `170.410573/71.708239`，small `M64` 为 `94.754880/69.122485`。

## Probe 边界

所有 R0F/R1-probe 输出必须固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

M1 只证明 dense Tensor Core sanity，不证明 W4A16 grouped MoE、SOP-C 或 tier eligibility。若未来值得正式化，必须新建 formal task 并重新走 SOP-A/B/C。

## 下一步

进入 M1：在 `cutlass_routed_grouped_micro.cu` 新增可审计 TensorOp dense path，保留旧 SIMT fallback，并在 probe CSV/log 中标明 `op_class=TensorOp`、`arch=Sm80/Sm87-compatible`、`candidate_path=cutlass_tensorop_dense_fp16`。
