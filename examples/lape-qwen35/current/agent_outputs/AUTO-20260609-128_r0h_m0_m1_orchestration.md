# AUTO-20260609-128 R0H M0/M1 Orchestration

## 结论

`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 已在 goal 模式下启动。当前状态建议更新为：

```text
in_progress / M0-M1 complete / M2 pending / orin_1_only / spike_only
```

本轮完成：

- M0 goal、baseline、worker 编排、R3/R4 边界和停止条件锁定。
- M1 NNCL fastpath 反向规格化文档。
- 启动并收集 repo-explorer、perf-analyst、oss-scout、qwen-architect 子代理只读结论。

## 产物

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/m0_goal_baseline_lock.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/nncl_fastpath_spec.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-128_r0h_m0_m1_orchestration.md`

## 子代理摘要

### repo-explorer

- 确认 spike target 为 `qwen3_5_cute_dsl_spike`。
- R0G mode 位于 `samples/micro_bench/spike/cute_dsl/main.cc` 和 `cutlass_routed_grouped_micro.cu`。
- 数据加载可复用 `LoadBundleInfo`、`LoadReplayWeights`、`LoadGptqWeights`、`BuildGroupedRows`、`TimeNnclGroupedGemm`。
- M2 建议新增 mode：`routed_grouped_r0h_fused_w4a16_single_expert_smoke`。
- M2 最小接入点：`main.cc`、`spike_common.h`、`CMakeLists.txt`、`samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/`。

### perf-analyst

- baseline 必须是同一次运行、同一 CSV 行内 paired 的 public NNCL `MoeGroupGemm`。
- ratio 固定为 `candidate_ms / nncl_ms`。
- AUTO-126 M3 guard：M64 `2.112438x`，M898 `2.273437x`，geomean `2.191459x`。
- R0E/R0F/R0G/Marlin 历史 evidence 都不能作为 R0H SOP/tier pass。

### oss-scout

- 本地源码足够，未联网。
- 建议最低风险路线：参考 CUTLASS grouped/mixed-input 模式和 NNCL visitor 语义，不复制 NNCL `DqMmaMultistage` 或包装 NNCL `MoeFCGemm`。
- CUTLASS examples 可作为 API/设计参考，NNCL extension 只能作为规格参考。
- CuTeDSL Python 目录有单独许可提示，不建议作为 candidate 源码来源。

### qwen-architect

- Qwen3.5 MoE W4A16 数据流固定为 HF GPTQ raw `qweight/scales/qzeros/g_idx` 语义。
- M2 只做 single expert / `gate_proj` / `K=2048,N=512,group_size=128`。
- M3 抽象 packed B iterator、scale iterator、shared-memory pipeline。
- M4 再接 `cu_row / total_rows_before_expert` grouped problem visitor。
- probe flags 必须保持 `valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false/candidate_audit_pending=true`。

## 下一步

进入 M2：

1. 由 kernel-dev 在 spike-only 写入范围内实现 single expert fused W4A16 smoke。
2. 本地构建 target `qwen3_5_cute_dsl_spike`。
3. reviewer 审查 candidate 是否误用 NNCL。
4. 如需 `orin_1` sync/build/NCU，由 main-orchestrator 先确认 R4 命令口径、预计耗时、输出目录和停止条件。

## R4 暂不执行

本轮未启动 `orin_1`、NCU 或长时间构建。

