# AUTO-20260608-111 CuTe/CUTLASS R0F Cold Start Sync

## 结论

本轮按用户要求更新 agent_group 记忆，使下次冷启动直接从当前 CuTe/CUTLASS `Q35-MOE-CUTEDSL-R0F-R1-PROBE` 开始。

冷启动入口现在固定为：

- 任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`
- 状态：`todo / probe-only`
- 第一阶段：Tensor Core sanity
- 范围：post-R0E 性能归因与上限验证

不要从 Marlin R0、CuTe/CUTLASS R0E formal、R0c/R0d/R0D1 diagnostic 或 Python CuTeDSL `_mlir` blocker 重启主线。

## 冷启动读取顺序

1. `.codex/agent_group/current/STATE.md`
2. `.codex/agent_group/current/agent_outputs/AUTO-20260608-110_cutedsl_r0f_r1_probe_plan.md`
3. `.codex/agent_group/current/agent_outputs/AUTO-20260608-111_cutedsl_r0f_cold_start_sync.md`
4. `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
5. `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`

## 固定执行顺序

1. Tensor Core sanity：把 probe 版 dense path 从 `OpClassSimt + Sm70` 改到 Orin 可用 Tensor Core path（`OpClassTensorOp + Sm80/SM87 compatible`），先只跑 single projection / same shapes。
2. Timing hygiene：清理 timed loop 内 `cudaStreamSynchronize`、`torch::empty`、`.contiguous()`、`copy_` 和 host/device roundtrip，预分配 A/B/C/workspace。
3. Candidate NCU isolation：证明 NCU 抓到 CuTe/CUTLASS candidate kernel，不得抓到 NNCL baseline `MoeFCGemm` 后当作 candidate evidence。
4. Grouped launch probe：用 grouped/batched dense fp16 验证减少 per-expert serial launch 的上限。
5. W4A16 feasibility：只有 dense Tensor Core path、timing hygiene 和 grouped launch 上限都成立后，才评估 fused GPTQ W4A16 decode+matmul 或 grouped W4A16 candidate。
6. Formal gate：若要升级正式候选，必须新建 formal 任务并重新走 SOP-A/B/C；不能复用 R0E tier 或 probe 数据。

## 已归档事实

- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`：`done / tier D / not production`。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`：`done / formal FAIL / gate_fail`。
- R0E formal evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`。
- R0E 结论：SOP-A PASS，SOP-B PASS，SOP-C FAIL；`overall_pass=false`、`tier_eligible=false`。

## 非 SOP 边界

- 所有 R0F/R1-probe 输出必须固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- R0F/R1-probe 不得作为 SOP-A/B/C、tier、R1/R3 或 production evidence。
- 修改 CUDA/CUTLASS/CMake 前按 R3 处理；启动 Orin 构建、NCU 或长任务前按 R4 处理，必须先确认命令、预计耗时、输出目录和停止条件。

## 本轮同步文件

- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
- `.codex/agent_group/memory/RISKS.md`
- `.codex/agent_group/current/acceptance.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-111_cutedsl_r0f_cold_start_sync.md`
