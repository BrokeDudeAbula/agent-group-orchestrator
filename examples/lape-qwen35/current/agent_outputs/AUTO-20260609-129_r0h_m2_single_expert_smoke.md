# AUTO-20260609-129 R0H M2 Single Expert Smoke

## 结论

`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 已完成 cold-start M0-M2 阶段，状态应更新为：

```text
in_progress / M0-M2 smoke done / orin_1_only / spike_only / not_formal
```

本轮 M2 只建立 single expert fused W4A16 smoke 起点，不生成 SOP/tier evidence，也不生成 `orin_1` 性能结论。

## 子代理

- `repo-explorer`：完成 spike 入口、复用函数和 M2 接入点梳理。
- `perf-analyst`：锁定 same-run NNCL `MoeGroupGemm` baseline 口径和 CSV 字段。
- `oss-scout`：完成 CUTLASS/NNCL 只读对照，建议 NNCL 只作规格参考。
- `qwen-architect`：锁定 HF GPTQ raw `qweight/scales` 语义和 M2/M3/M4 边界。
- `kernel-dev`：实现 M2 single expert fused W4A16 smoke。
- `reviewer`：只读审查 M2 实现，结论 PASS，无 blocker/major。

## M2 实现

新增 mode：

```text
routed_grouped_r0h_fused_w4a16_single_expert_smoke
```

实现边界：

- single expert。
- `gate_proj`。
- `K=2048`、`N=512`、`group_size=128`。
- 使用 HF raw GPTQ `qweight [K/8,N]` 和 `scales [K/128,N]`。
- candidate kernel 在 WMMA K-tile loop 内解 int4 并应用 scale。
- timed candidate 内不做 full `dense_B_fp16` predecode。
- 不调用或包装 `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass`。
- probe flags 固定为 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。

## 验证

本地构建通过：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

结果：

```text
[100%] Built target qwen3_5_cute_dsl_spike
```

本地 synthetic smoke 通过：

```bash
build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=routed_grouped_r0h_fused_w4a16_single_expert_smoke --m_filter=64 --warmup=1 --iters=1 --projection=gate_proj --output_csv=analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m2_single_expert_smoke_local.csv
```

关键输出：

```text
candidate_ms=0.486240 reference_ms=0.098176 max_abs=3.503263e-05 rmse=8.392764e-06 finite=true nonzero=32768 precision_pass=true nncl_ms=NA
```

## 产物

- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_single_expert_smoke.cu`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/m0_goal_baseline_lock.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/nncl_fastpath_spec.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m2_single_expert_smoke_local.csv`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-128_r0h_m0_m1_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-129_r0h_m2_single_expert_smoke.md`

## 限制与下一步

- 未执行 `orin_1` sync/build、NCU 或 long-running R4 实验。
- `nncl_ms=NA`，same-run NNCL paired baseline 仍 pending。
- 当前 smoke 使用 synthetic input，不读取真实 bundle，不覆盖 family A/B 10 shape。
- 下一步是 M3：实现 packed B iterator + scale iterator + shared-memory pipeline，并继续禁止 full B predecode。
- M4 才接 MoE grouped problem visitor。
- M5 之后才允许在 `orin_1` 上做 family A/B paired NNCL probe。
