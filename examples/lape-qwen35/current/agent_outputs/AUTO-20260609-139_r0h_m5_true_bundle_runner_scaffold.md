# AUTO-20260609-139 R0H M5 True Bundle Runner Scaffold

日期：2026-06-09

## 结论

R0H 已新增 true-bundle runner scaffold mode：

```text
routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_true_bundle_runner_scaffold
```

该 mode 读取 Q35-028 `moe_block` bundle、CPU top-k、expert-grouped routed rows、`cu_row_prefix` / `padded_cu_row_prefix` / NNCL-style end-prefix，以及 active experts 的 HF GPTQ raw guard。它只完成 true-bundle timed runner 的本地数据面铺设，不启动 R0H candidate kernel，不调用 NNCL baseline，不生成 `candidate_ms/nncl_ms/ratio`，不是 `orin_1` 性能证据，不是 SOP/tier/formal evidence。

当前恢复点更新为：

```text
in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / M5 true bundle runner scaffold done / local NNCL sm120 blocked / true-bundle timed paired runner pending / orin_1 synthetic paired R4 pending / orin_1_only / spike_only / not_formal
```

## Sub-agent 编排

- `repo-explorer` / Ramanujan：只读分析 true-bundle runner 最小接入面。
- `repo-explorer` / Gibbs：只读核对 mode 注册、CMake 显式源列表、匿名 namespace helper 不可跨 TU 复用、`layer_idx/top_k` CLI 解析缺口。
- `main-orchestrator`：新增独立 runner scaffold TU，接入 mode/help/parse/dispatch/CMake，并补 `--layer_idx/--top_k` 解析。
- `reviewer` / Harvey：审查结论 `MINOR`，指出 B 族 `true_bundle_ready=true` 可能被误读为可 timed run。
- `main-orchestrator`：已修复 reviewer MINOR，新增 `bundle_hf_guard_ready`，并让 B 族在 down input 未物化前保持 `true_bundle_ready=false`。

## 实现边界

修改范围保持在 spike 内：

- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_m5_true_bundle_runner.cu`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`

未修改 production Qwen3.5 推理路径。

当前语义：

- A 族 `gate_proj K=2048,N=512`：`bundle_hf_guard_ready=true`、`projection_input_materialized=true`、`true_bundle_ready=true`。
- B 族 `down_proj K=512,N=2048`：`bundle_hf_guard_ready=true`、`projection_input_plan_ready=true`，但 `projection_input_materialized=false`、`true_bundle_ready=false`，因为 `silu(gate)*up` 尚未实际物化。

固定 fail-closed 字段：

- `runner_ready=false`
- `candidate_timed=false`
- `nncl_paired_ready=false`
- `nncl_weight_pack_ready=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`
- `independent_candidate=false`

新 runner TU 未 include/call/wrap NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 NNCL CUTLASS extension fastpath。

## Verification

Build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

True-bundle runner scaffold PASS：

```text
analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_true_bundle_runner_scaffold_all_local_after_reviewfix.csv
```

字段校验：

- 10 行，覆盖 A/B family `M=64/128/256/512/898`。
- 所有行 `bundle_hf_guard_ready=true`、`projection_input_plan_ready=true`。
- A 族 5 行 `true_bundle_ready=true`、`projection_input_materialized=true`。
- B 族 5 行 `true_bundle_ready=false`、`projection_input_materialized=false`，reason 含 `down_proj_input_not_materialized_in_scaffold`。
- 所有行 `runner_ready=false`、`candidate_timed=false`、`nncl_paired_ready=false`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。

Regression：

- true-bundle preflight `r0h_m5_true_bundle_preflight_local_after_runner_scaffold_reviewfix.csv` 10 行 guard PASS 且 fail-closed。
- M5 synthetic A/B `r0h_m5_synthetic_ab_local_after_runner_scaffold_reviewfix.csv` 10 行 `precision_pass=true` 且 fail-closed。

## Remaining Work

真正 M5 full probe 仍未就绪。下一步仍需要：

1. 继续等待用户确认后，在 `orin_1` 执行 AUTO-138 synthetic paired scaffold R4 package。
2. 为 true-bundle runner 物化 B 族 `silu(gate_proj(grouped_hidden)) * up_proj(grouped_hidden)` 输入。
3. 将 true-bundle grouped input 与 HF raw `qweight/scales` 接入 `R0HFusedW4A16GroupedVisitorWmmaKernel` timed path。
4. 接入 same-run public NNCL `MoeGroupGemm` baseline，输出 `candidate_ms/nncl_ms/candidate_vs_nncl_ratio/max_abs_vs_nncl/rmse_vs_nncl`。
5. 进入任何 `orin_1` build/run/NCU 前必须再次满足 R4 门禁：明确 command、预计时间、输出目录、停止条件，并取得用户确认。
