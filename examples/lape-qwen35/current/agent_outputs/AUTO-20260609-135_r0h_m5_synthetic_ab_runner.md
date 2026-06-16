# AUTO-20260609-135 R0H M5 Synthetic A/B Runner

日期：2026-06-09

## 结论

R0H M5 本地 synthetic A/B structural runner 已完成，结论为：

```text
M5 synthetic A/B runner done / K,N,projection parameterization done / same-run NNCL paired runner pending / not_m5_full_probe / not_formal
```

本次没有启动 `orin_1`，没有运行 NCU，没有执行 same-run NNCL paired baseline，也没有修改 production Qwen3.5 推理路径。

## 新增能力

新增 mode：

```text
routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic
```

该 mode 遍历 `SopCShapes()`，覆盖 family A/B 10 shape：

- A：`M=64/128/256/512/898, K=2048, N=512, projection=gate_proj`
- B：`M=64/128/256/512/898, K=512, N=2048, projection=down_proj`

R0H grouped visitor kernel/host path 已从固定 `K=2048,N=512,gate_proj` 参数化到 `problem.k/problem.n/problem.projection`：

- host buffer：A 为 `[M,K]`，qweight 为 `[active_experts,K/8,N]`，scales 为 `[active_experts,K/128,N]`，D 为 `[M,N]`
- kernel：grid.x 使用 `ceil(N/16)`，K loop 使用运行时 `K`，A/B/scales/D stride 使用运行时 `K/N`
- CSV：`family,M,K,N,projection` 来自当前 `SopCShape`

M4 旧 mode 仍保留并回归通过。

## Evidence

Build：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

M5 synthetic main CSV：

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local.csv`

M5 synthetic maincheck CSV：

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_maincheck.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_maincheck_after_helpfix.csv`

M4 post-change regression CSV：

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_post_m5synthetic.csv`

Updated M5 preflight CSV：

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local_after_m5synthetic.csv`

## Verification

M5 synthetic 10 行全部通过：

- `precision_pass=true`
- `runner_ready=false`
- `candidate_shape_supported=true`
- `nncl_paired_ready=false`
- `nncl_ms=NA`
- `candidate_vs_nncl_ratio=NA`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`
- `independent_candidate=false`

Updated preflight 10 行全部通过：

- A/B 10 shape 均 `candidate_shape_supported=true`
- A/B 10 shape 均 `runner_ready=false`
- A/B 10 shape 均 `nncl_paired_ready=false`
- reason 均包含 `same_run_NNCL_baseline_missing`
- B 族 reason 已更新为 `family_B_down_proj_K512_N2048_has_R0H_M5_synthetic_structural_runner`

旧 M4 回归通过：

- `M=64,K=2048,N=512,projection=gate_proj`
- `precision_pass=true`
- `runner_ready=true`
- `nncl_ms=NA`

说明：默认 GPU0 当时显存占用高，旧 M4 单独跑会在首次 `cudaMalloc` OOM；指定 `CUDA_VISIBLE_DEVICES=4` 后 M4/M5 synthetic 均通过。这不是 `orin_1` 证据，也不是性能结论。

## Reviewer

Reviewer 子代理结论初始为 `MINOR`：

- 新 mode 已接入 help usage / parse / dispatch。
- 旧 M4 mode 仍可运行。
- M5 synthetic 覆盖 A/B 10 shape。
- host/kernel 已使用运行时 `K/N`，避免 B 族 `down_proj K=512,N=2048` 越界。
- M5 CSV fail-closed 字段符合要求。
- M5 candidate 实现文件没有 include/call/wrap NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 `cutlass_extensions` 作为 candidate。
- 未发现把 synthetic runner 误标成 M5 full probe / SOP / tier / formal / Orin 性能结论的实质风险。

MINOR 修复：

- M5 preflight/synthetic 详细 help 文本原本位于 `R0eFormalModesEnabled()==false` 的 `else` 分支内。已移出该分支。
- 修复后 rebuild PASS，help 检查 PASS，M5 synthetic maincheck PASS。

## Remaining Work

真正 M5 full probe 仍未就绪。当前已关闭 `K/N/projection parameterization missing` 和 family B synthetic structural gap，但仍缺：

1. 真实 Q35-028 bundle routing/input 接入。
2. 真实 HF GPTQ weights 接入。
3. same-run NNCL `MoeGroupGemm` paired baseline。
4. 同 row 输出 `candidate_ms/nncl_ms/ratio`。
5. reviewer candidate identity/audit 后，才能准备 R4 `orin_1` command/time/output/stop package。

下一次冷启动恢复点更新为：

```text
in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 NNCL paired runner pending / orin_1_only / spike_only / not_formal
```
