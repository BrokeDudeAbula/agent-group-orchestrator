# AUTO-20260609-136 R0H M5 Synthetic NNCL Paired Scaffold

日期：2026-06-09

## 结论

R0H 已新增 spike-only synthetic same-run NNCL paired scaffold：

```text
routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired
```

该 mode 只用于把 R0H synthetic A/B 10 shape candidate 与 public NNCL `MoeGroupGemm` baseline 放到同一进程路径中，验证 qweight pack、scale、`cu_row` 语义和 CSV 字段闭环。它不是 full M5 ready，不是 `orin_1` 性能证据，不是 SOP/tier/formal evidence。

当前恢复点应更新为：

```text
in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal
```

## Worker 编排

- `repo-explorer` / Banach：只读确认 public NNCL baseline 最小依赖链，建议先做 synthetic paired scaffold，不直接抽真实 bundle/HF helper。
- `kernel-dev` / Hilbert：实现新增 mode、qweight pack、NNCL end-prefix、CSV 字段和 help/dispatch 接入。
- `reviewer` / Hegel：初审 `MAJOR`，指出 paired synthetic mode 不能写 `runner_ready=true`。
- `kernel-dev` / Hilbert：按 reviewer 做最小修复，paired mode 改为 `runner_ready=false`、`nncl_paired_ready=true`。
- `reviewer` / Carver：复审 PASS，确认 MAJOR 关闭，可进行记忆同步。

## 实现边界

修改范围保持在 spike 内：

- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_grouped_visitor_smoke.cu`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`

未修改 production Qwen3.5 推理路径。

NNCL 只作为 baseline/reference：

- include：public `nncl.h`
- call：`GetMoeGroupGemmWorkspaceSize`、`QuantInfo`、public `MoeGroupGemm<half, half, QuantMethod::kGPTQFp16Int4Groupwise>`
- 不 include/call/wrap `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 `cutlass_extensions` fastpath 作为 candidate

candidate 仍为：

```text
R0HFusedW4A16GroupedVisitorWmmaKernel
```

## 数据语义

- raw synthetic qweight：`[experts,K/8,N] int32`
- NNCL packed qweight：`[experts,N/4,K*2] uint8`
- scales：`[experts,K/128,N] half`
- R0H `cu_row_prefix`：含起始 0 的 int prefix
- NNCL `cu_row`：int64 end-prefix，不含起始 0，长度为 `active_experts`，最后值等于 `routed_rows`
- candidate timing 与 NNCL baseline timing 分开计时，`candidate_ms` 不包含 NNCL baseline

## Verification

Build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

Help PASS：

```bash
./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=help | rg "m5_synthetic_nncl_paired|runner_ready remains false|not full M5 ready"
```

旧 M5 synthetic A/B 10 shape 回归 PASS：

```text
analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_after_nncl_pair_majorfix.csv
```

该 CSV 10 行均：

- `precision_pass=true`
- `runner_ready=false`
- `nncl_paired_ready=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `independent_candidate=false`
- candidate NNCL flags 均为 `false`

本地 paired mode 只做 expected-fail smoke；本机 sm_120 NNCL baseline 报：

```text
[Error][MoE][GEMM Dispatch] Arch unsupported for MoE GEMM
```

相关 header-only CSV 不作为数值 evidence：

- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_nncl_paired_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_nncl_paired_local_gpu0_m64_probe.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_nncl_paired_local_maincheck_gpu0_m64_expected_fail.csv`

## Remaining Work

真正 M5 full probe 仍未就绪。下一步仍需要：

1. 在 `orin_1` 或 NNCL 支持的架构上运行新增 synthetic paired mode，确认 pack layout、NNCL end-prefix 和 `max_abs_vs_nncl/rmse_vs_nncl`。
2. 接入真实 Q35-028 bundle routing/input。
3. 接入真实 HF GPTQ weights。
4. 对 family B `down_proj K=512,N=2048` 构造真实 `silu(gate) * up` 输入。
5. 产出同一 CSV 行内 `candidate_ms/nncl_ms/candidate_vs_nncl_ratio`。
6. R4 执行前必须明确 command、预计时间、输出目录和停止条件。

