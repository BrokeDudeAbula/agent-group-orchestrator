# AUTO-20260609-137 R0H M5 True Bundle/HF GPTQ Preflight

日期：2026-06-09

## 结论

R0H 已新增 true-bundle/HF GPTQ fail-closed preflight mode：

```text
routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_true_bundle_preflight
```

该 mode 读取 Q35-028 `moe_block` bundle 的 metadata、`hidden_states.pt`、`router_logits.pt`，用 torch CPU top-k 构造 family A/B 10 shape 的 grouped routing surface，并读取 active experts 对应的 HF GPTQ raw `qweight/qzeros/scales/g_idx` 做 shape 和 guard 检查。它不启动 R0H candidate kernel，不调用 NNCL `MoeGroupGemm` / `MoeFCGemm` / `dispatch_moe_gemm_to_cutlass`，不生成 ratio，不是 `orin_1` 性能证据，不是 SOP/tier/formal evidence。

当前恢复点应更新为：

```text
in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal
```

## Sub-agent 编排

- `repo-explorer` / Peirce：只读确认最小 scaffold 应复用 `cutlass_routed_grouped_micro.cu` 的 bundle/topk/routing/GPTQ helper 语义；指出现有 helper 在匿名 namespace 内，建议在 R0H TU 做最小复制或抽共享 helper。
- `main-orchestrator`：实现 true-bundle/HF GPTQ preflight mode，并保持 fail-closed CSV 守卫。
- `reviewer` / Fermat：初审 `ISSUES`，指出 `true_bundle_ready` 未纳入 bundle `hidden_size/moe_intermediate_size/num_experts` 和 family A/B shape 对 bundle metadata 的一致性检查。
- `main-orchestrator`：已修复 reviewer issue，将 `bundle_dims_ok` 与 `shape_matches_bundle` 纳入 `true_bundle_ready` 条件，并 rebuild/rerun PASS。

## 实现边界

修改范围保持在 spike 内：

- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_m5_preflight.cc`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`

未修改 production Qwen3.5 推理路径。

新增 preflight 只读检查：

- bundle `module_kind=moe_block`
- bundle `layer_idx/top_k` 与 CLI/config 一致
- `hidden_states` shape 为 `[num_tokens, hidden_size]`
- `router_logits` shape 为 `[num_tokens, num_experts]`
- torch CPU top-k 后按 expert group，生成 selected experts、row counts、NNCL-style int64 end-prefix
- active expert 的 HF GPTQ `qweight` 为 `[K/8,N] int32`
- `scales` 为 `[K/128,N] fp16`
- `qzeros` 为 groupwise symmetric `0x77777777`
- `g_idx[i] == i / 128`

固定 fail-closed 字段：

- `runner_ready=false`
- `nncl_paired_ready=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`
- `independent_candidate=false`

## Verification

Build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

Help PASS，新 mode 可见：

```bash
./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --help | rg "true_bundle_preflight|MoeGroupGemm|runner_ready"
```

True bundle/HF GPTQ preflight PASS：

```text
analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_true_bundle_preflight_local_after_reviewfix.csv
```

该 CSV 10 行均：

- `true_bundle_ready=true`
- `hf_qweight_shape_ok=true`
- `hf_scales_shape_ok=true`
- `hf_g_idx_default_ok=true`
- `hf_qzeros_sym_ok=true`
- `runner_ready=false`
- `nncl_paired_ready=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`
- `independent_candidate=false`

旧 M5 synthetic A/B 10 shape 回归 PASS：

```text
analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_after_true_bundle_preflight_reviewfix.csv
```

该 CSV 10 行均：

- `precision_pass=true`
- `runner_ready=false`
- `nncl_paired_ready=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`
- `independent_candidate=false`

## Remaining Work

真正 M5 full probe 仍未就绪。下一步仍需要：

1. 在 `orin_1` 验证 synthetic paired scaffold，确认 NNCL baseline 可运行且 `max_abs_vs_nncl/rmse_vs_nncl` 合理。
2. 将 true bundle grouped hidden / HF raw weights 接入 R0H candidate timed path。
3. 为 family B `down_proj K=512,N=2048` 构造真实 `silu(gate) * up` 输入。
4. 产出 true bundle same-run NNCL paired runner CSV 行，包含 `candidate_ms/nncl_ms/candidate_vs_nncl_ratio`。
5. R4 执行前必须明确 command、预计时间、输出目录和停止条件。
