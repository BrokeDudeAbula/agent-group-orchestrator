# AUTO-20260608-110 CuTe/CUTLASS R0F/R1-probe Plan Sync

## 结论

本轮只把 R0E 性能异常诊断后的推荐顺序组织为新任务并同步到 agent_group：

- 新任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`
- 状态：`todo / probe-only`
- 范围：`samples/micro_bench/spike/cute_dsl/`、`.codex/agent_group/`、必要 `analysis/`
- 不启动 Orin 长任务，不生成新性能证据

R0E 正式结论不变：`done / formal FAIL / gate_fail`，CuTe/CUTLASS 主线仍为 `tier D / not production`。R0F/R1-probe 不是 SOP evidence，不是 R1/R3/production 授权。

## 背景

R0E formal package 已在 `orin_1` 执行，evidence 目录：

- `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`

Formal 结论：

- SOP-A PASS
- SOP-B PASS
- SOP-C FAIL
- guard：`schema_pass=true`、`status=gate_fail`、`overall_pass=false`、`tier_eligible=false`

性能异常的当前归因：

- 当前 C++ fallback harness 的 dense path 曾使用 `OpClassSimt + Sm70`，不是 Orin `sm_87` Tensor Core 上限。
- routed grouped micro 仍是 per-expert serial dense GEMM，active experts 约 37 到 117。
- timed path 中存在同步、临时 tensor 分配、layout copy 或 host/device roundtrip 风险。
- NCU filter 存在抓到 NNCL baseline `MoeFCGemm` 而不是 CuTe/CUTLASS candidate 的污染风险。

## 推荐顺序

1. Tensor Core sanity
   - 把 probe 版 `RunCutlassDense` 从 `OpClassSimt + Sm70` 改到 Orin 可用 Tensor Core path（`OpClassTensorOp + Sm80/SM87 compatible`）。
   - 先只跑 single projection / same shapes，对比 `shape_bench`，确认 Tensor Core path 正常。

2. Timing hygiene
   - timed loop 内禁止 `cudaStreamSynchronize`、`torch::empty`、`.contiguous()`、`copy_` 和 host/device roundtrip。
   - 预分配 A/B/C/workspace。

3. Candidate NCU isolation
   - NCU filter 必须抓 candidate kernel。
   - 不得只用宽泛 keyword 抓到 NNCL baseline `MoeFCGemm`。
   - 报告必须记录 kernel name、launch source、workload CSV 和非零输出。

4. Grouped launch probe
   - 做 grouped/batched dense fp16 probe，减少 37-117 个 per-expert serial launch。
   - 只验证 launch 上限，不直接推导 SOP-C。

5. W4A16 feasibility
   - 只有 dense Tensor Core path、timing hygiene 和 grouped launch 上限都成立后，才评估 fused GPTQ W4A16 decode+matmul 或 grouped W4A16 candidate。

6. Formal gate
   - 若要推进正式候选，另起 formal R0G/R1-probe gate。
   - 必须复用 SOP-A/B/C，不复用 R0E tier。

## 非 SOP 边界

- 所有 R0F/R1-probe 输出默认：
  - `valid_for_sop_a=false`
  - `valid_for_sop_c=false`
  - `tier_eligible=false`
- R0F/R1-probe 不得声明：
  - SOP-A/B/C PASS
  - tier eligible
  - R1/R3/production ready
- 执行任何 Orin 长任务前，仍需用户确认命令、预计耗时、输出目录和停止条件。

## 已同步文件

- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/memory/TASK_LEDGER.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
- `.codex/agent_group/memory/RISKS.md`
- `.codex/agent_group/current/acceptance.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-110_cutedsl_r0f_r1_probe_plan.md`
