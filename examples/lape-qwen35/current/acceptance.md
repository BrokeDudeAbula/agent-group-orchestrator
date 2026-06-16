# Acceptance Criteria

最后更新：2026-06-09

## 当前 Hot Epic

`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`

本文件定义下一次 agent_group cold start 后的 R0H 验收边界。R0F/R1-probe 已在 M5 收口为 `done / reject_or_hold / probe-only / not production`，不得继续作为当前执行主线。

## Goal Mode

必须使用 `/goal` 模式启动：

```text
/goal Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP: make current repo CuteDSL/CUTLASS spike performance align with same-run NNCL MoeGroupGemm on orin_1 by building an independent fused W4A16 int4-dequant + scale-iterator + grouped-mainloop pipeline
```

## 设备与 Baseline

- 性能测试目标设备固定为 `orin_1`。
- 不允许使用 `orin_cv`、本地 GPU 或其他平台生成性能结论。
- baseline 固定为 same-run NNCL `MoeGroupGemm`。
- ratio 定义为 `candidate_ms / nncl_ms`。
- 主指标为 family A/B geomean ratio。
- 辅助指标必须覆盖 hot `M898` 与 small `M64`。

## 性能 Gate

| gate | requirement |
|---|---|
| 初级结构 gate | family A/B geomean ratio `<=1.50x` |
| 目标 gate | family A/B geomean ratio `<=1.20x` |
| hot/small guard | `M898` 与 `M64` 不出现明显灾难性退化 |

## Scope Guard

允许写：

```text
samples/micro_bench/spike/cute_dsl/
samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/
analysis/Qwen35_cutedsl_r0h_fused_w4a16_<TS>/
.codex/agent_group/
必要的 spike CMakeLists.txt 接入
```

禁止：

- 修改 production Qwen3.5 推理路径。
- 把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 包装成 candidate。
- 使用 NNCL internal runner/template/header/kernel 声明 independent candidate。

## Probe Flags

所有 R0H probe 输出默认固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`

正式 candidate 之前，`independent_candidate` 初始保持 `false`。只有 reviewer 完成独立性审计并新建 formal task 后，才允许调整 formal 证据字段。

## Milestone 验收

### M0：目标初始化与基线锁定

通过条件：

- `/goal` 已启动。
- agent_group sub-agent 编排写入 agent output。
- R3/R4 范围、预计输出目录、`orin_1` 命令口径和停止条件已记录。
- same-run NNCL baseline 口径固定。

### M1：NNCL 快路径反向规格化

通过条件：

- 输出 `analysis/Qwen35_cutedsl_r0h_fused_w4a16_<TS>/nncl_fastpath_spec.md`。
- 明确 packed int4 B iterator、groupwise scale iterator、cp.async pipeline、fused dequant MMA、MoE problem visitor 的规格。
- 明确哪些 NNCL 代码只能作为规格参考，不能作为 candidate path。

### M2：单 expert fused W4A16 mainloop smoke

通过条件：

- 固定单 expert / `gate_proj` / `K=2048,N=512` / `group_size=128`。
- candidate 输出非全零、无 NaN/Inf。
- precision 对 dense 或 NNCL reference 通过。
- NCU 抓到 independent candidate kernel，不是 `MoeFCGemm`。
- probe flags 保持非 SOP / 非 tier。

### M3：Scale Iterator + Packed B Pipeline

通过条件：

- 不允许全量 predecode B 到 fp16。
- scale/B tile 进入 shared memory。
- dequant 在 mainloop 中完成。
- NCU 显示 candidate kernel 有 Tensor Core/MMA evidence。
- M64/M898 smoke ratio 不劣于 AUTO-126 最佳 `2.112438x / 2.273437x`。

### M4：MoE Grouped Problem Visitor

通过条件：

- 使用 `cu_row / total_rows_before_expert`。
- 支持 active experts 数变化。
- 覆盖 `M=64,128,256,512,898`。
- candidate launch count 目标为 1。
- NNCL candidate usage flags 均为 false。

### M5：`orin_1` Full Shape Probe

通过条件：

- 只在 `orin_1` 上执行。
- family A/B 10 shape same-run NNCL 对比完成。
- 输出 geomean、min/max、M64、M898。
- 初级结构 gate 为 `<=1.50x`；目标 gate 为 `<=1.20x`。

### M6：NCU Isolation

通过条件：

- NCU filter 抓到 independent fused candidate kernel。
- 未抓到或未误用 `MoeFCGemm` / `MoeGroupGemm` 作为 candidate。
- 记录 kernel name、launch source、duration、achieved occupancy、Tensor Core utilization、memory throughput、register/thread、shared memory/block。
- workload CSV 与 NCU kernel 绑定。

### M7：Formal 决策

输出只允许三种：

- `promote_to_formal_sop`
- `continue_probe`
- `reject_or_hold`

只有满足 independent candidate 审计、M5 ratio 接近或达到目标、M6 NCU identity 通过、M64/M898 无灾难退化，才允许新建 formal task 并重新走 SOP-A/B/C。

## Stop Conditions

立即停止并回报：

- `orin_1` 构建失败。
- candidate 输出 NaN/Inf/全零。
- NCU 抓不到 independent candidate kernel。
- NCU 只抓到 `MoeFCGemm` / `MoeGroupGemm`。
- ratio 连续两轮 `>1.50x` 且没有明确结构性改进证据。
- 需要修改 production path 才能继续。

## Historical Boundary

以下旧 evidence 不可作为 R0H formal PASS：

- R0E SOP-A/B PASS 但 SOP-C gate_fail evidence。
- R0F/R1 dense fp16 / M4 control / dispatch wrapper evidence。
- AUTO-114 到 AUTO-126 raw CUDA/WMMA probe evidence。
- Marlin archived evidence。

这些 evidence 只能作为设计背景和风险边界。
