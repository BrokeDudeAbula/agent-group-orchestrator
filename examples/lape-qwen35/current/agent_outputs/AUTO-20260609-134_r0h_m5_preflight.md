# AUTO-20260609-134 R0H M5 Preflight

日期：2026-06-09

> Superseded note：本文件记录 M5 synthetic A/B runner 之前的 preflight 状态。后续 `AUTO-20260609-135_r0h_m5_synthetic_ab_runner.md` 已关闭 `K/N/projection parameterization` 和 B 族 `down_proj K=512,N=2048` synthetic structural 缺口；当前恢复点以后者和 `STATE.md` 为准。正式 M5 仍缺真实 bundle/HF GPTQ weights + same-run NNCL paired baseline。

## 结论

R0H M5 本地 preflight/scaffold 已完成，结论为：

```text
needs_local_runner_work / fail-closed / no_candidate_kernel / no_nncl_ratio / not_m5_pass / not_formal
```

本次没有启动 `orin_1`，没有运行 NCU，没有执行 same-run NNCL paired baseline，也没有修改 production Qwen3.5 推理路径。

## 新增内容

新增 mode：

```text
routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_preflight
```

新增文件：

- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_m5_preflight.cc`

更新文件：

- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`

新增 evidence：

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local_maincheck.csv`

## 验证

本地 build 通过：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

main-orchestrator 复跑通过：

```bash
./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_preflight \
  --output_csv=analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local_maincheck.csv
```

输出确认：

- CSV 为 1 行 header + 10 行数据。
- family A 覆盖 `M=64/128/256/512/898, K=2048, N=512, projection=gate_proj`。
- family B 覆盖 `M=64/128/256/512/898, K=512, N=2048, projection=down_proj`。
- 所有行 `runner_ready=false`。
- 所有行 `nncl_paired_ready=false`。
- 所有行 `valid_for_sop_a=false`。
- 所有行 `valid_for_sop_c=false`。
- 所有行 `tier_eligible=false`。
- 所有行 `candidate_audit_pending=true`。
- 所有行 `independent_candidate=false`。

## 关键字段语义

family A：

- `candidate_shape_supported=true`
- reason 包含 `same_run_NNCL_baseline_missing`
- 含义：M4 已有 synthetic `gate_proj K=2048,N=512` local structural smoke，但仍缺 same-run NNCL paired baseline 和正式 M5 runner。

family B：

- `candidate_shape_supported=false`
- reason 包含 `K_N_projection_parameterization_missing`
- 含义：当前 R0H M4 grouped visitor 尚未支持 `down_proj K=512,N=2048` 的 K/N/projection 参数化 runner。

## Reviewer

Reviewer 子代理结论：`PASS`。

审查确认：

- mode 已接入 help / parse / dispatch / CMake。
- CSV 恰好覆盖 family A/B 10 shape。
- 所有 fail-closed flags 符合要求。
- preflight 文件没有 include/call/wrap NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 `cutlass_extensions` 作为 candidate。
- 整个 spike target 仍因其他 probe mode 链接 `nncl`，但 preflight mode 本身未把 NNCL/CUTLASS extension 当 candidate。
- 未发现把本地 preflight 误标为 M5 pass、SOP/tier/formal 或性能结论的风险。

## 下一步

真正 M5 full probe 仍未就绪。进入 `orin_1` R4 前必须先补本地 runner：

1. 将 R0H grouped visitor candidate 参数化为 `K,N,projection`。
2. 支持 family B `down_proj K=512,N=2048` 的 packed weight/scale 访问、tile 布局和输出路径。
3. 在同一 CSV row 中加入 same-run NNCL `MoeGroupGemm` baseline，但不得把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 包装成 candidate。
4. 补齐 correctness、timing、candidate-vs-NNCL ratio、candidate identity/audit 字段后，才能准备 R4 `orin_1` command/time/output/stop package。

因此当前冷启动恢复点更新为：

```text
in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 runner work pending / orin_1_only / spike_only / not_formal
```
