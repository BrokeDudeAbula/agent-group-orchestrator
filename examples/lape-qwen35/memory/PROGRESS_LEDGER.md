# Progress Ledger

### 2026-06-09：R0H AUTO-139 M5 true-bundle runner scaffold done

- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-139_r0h_m5_true_bundle_runner_scaffold.md`
- 新增 mode：`routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_true_bundle_runner_scaffold`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- Help PASS，新 mode 与 `--layer_idx/--top_k` 可见。
- Runner scaffold CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_true_bundle_runner_scaffold_all_local_after_reviewfix.csv`。
- CSV 覆盖 A/B 10 shape；所有行 `bundle_hf_guard_ready=true`、`projection_input_plan_ready=true`。
- A 族 5 行 `true_bundle_ready=true`、`projection_input_materialized=true`。
- B 族 5 行 `true_bundle_ready=false`、`projection_input_materialized=false`，reason 含 `down_proj_input_not_materialized_in_scaffold`，等待 `silu(gate)*up` 输入物化。
- 所有行固定 fail-closed：`runner_ready=false`、`candidate_timed=false`、`nncl_paired_ready=false`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- Static guard：新增 runner TU 无 `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass`、NNCL CUTLASS extension fastpath 或 `#include "nncl"` 匹配。
- Regression：true-bundle preflight 10 行 guard PASS 且 fail-closed；M5 synthetic A/B 10 行 `precision_pass=true` 且 fail-closed。
- reviewer / Harvey 初审 MINOR：B 族 `true_bundle_ready=true` 易误读；已修复为 B 族 `true_bundle_ready=false`，新增 `bundle_hf_guard_ready=true` 标识 guard 层 ready。
- 未执行任何 `orin_1` sync/build/run/NCU；AUTO-138 synthetic paired R4 package 仍待用户确认。

### 2026-06-09：CuTeDSL R0H orin_1 synthetic paired R4 package prepared，awaiting confirmation

- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 状态保持 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal`。
- 新增 R4 前置执行包：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-138_r0h_orin1_synthetic_nncl_paired_r4_package.md`
- 使用 sub-agent / Russell 只读核对 binary、mode、CLI flags、spike CMake、`orin_1` runbook、输出目录和停止条件。
- R4 包固定 target 为 `orin_1`，container 为 `liyang_lape`，remote repo 为 `/workspace/liyang/workspace/lape`，mode 为 `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired`。
- 待确认命令覆盖：`sync-orin-lape-build --sync-only`、远端 spike target configure/build、M64 smoke、A/B 10 shape synthetic paired 主验证和结果回传。
- 预计总时间约 10-30 分钟；本地输出目录计划为 `analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546/`。
- 本包仍不是执行结果，不含 `orin_1` 数值 evidence；当前未执行 `orin_1` sync/build/run/回传，未产生有效 paired NNCL baseline。
- 成功后也只能证明 synthetic paired scaffold 在 sm87 上闭合 public NNCL `MoeGroupGemm` baseline；仍不能视作 true-bundle M5 full probe、M6 NCU、SOP/tier/formal 或 production evidence。
- 下一步：等待用户确认 R4 命令后，先运行 M64 smoke；只有 smoke 通过才运行 A/B 10 shape synthetic paired 主验证。

### 2026-06-09：CuTeDSL R0H M5 true bundle/HF GPTQ preflight done，orin_1 paired runner still pending

- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 状态更新为 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal`。
- 新增 orchestration 输出：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-137_r0h_m5_true_bundle_preflight.md`
- 新增 mode：`routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_true_bundle_preflight`。
- 该 mode 读取 Q35-028 `moe_block` bundle metadata、`hidden_states.pt`、`router_logits.pt`，用 torch CPU top-k 构造 family A/B 10 shape grouped routing surface，并读取 active experts 对应 HF GPTQ raw `qweight/qzeros/scales/g_idx` 做 shape 和 guard 检查。
- 该 mode 不启动 R0H candidate kernel，不调用 NNCL `MoeGroupGemm` / `MoeFCGemm` / `dispatch_moe_gemm_to_cutlass`，不生成 `nncl_ms` 或 `candidate_vs_nncl_ratio`，不是 SOP/tier/formal evidence。
- 本地 build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

- Help PASS，新 mode 可见。
- True bundle/HF GPTQ preflight CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_true_bundle_preflight_local_after_reviewfix.csv`。
- True bundle/HF GPTQ preflight 10 行均 `true_bundle_ready=true`、`hf_qweight_shape_ok=true`、`hf_scales_shape_ok=true`、`hf_g_idx_default_ok=true`、`hf_qzeros_sym_ok=true`，且 `runner_ready=false`、`nncl_paired_ready=false`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- Reviewer / Fermat 初审 `ISSUES`：`true_bundle_ready` 未纳入 bundle `hidden_size/moe_intermediate_size/num_experts` 和 family A/B shape 对 bundle metadata 的一致性检查；已修复为 `bundle_dims_ok && shape_matches_bundle` 并 rebuild/rerun PASS。
- 旧 M5 synthetic A/B 10 shape 回归 PASS，CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_after_true_bundle_preflight_reviewfix.csv`；10 行均 `precision_pass=true` 且 `runner_ready=false/nncl_paired_ready=false`。
- 本轮未执行 `orin_1` sync/build、NCU 或有效 paired NNCL baseline。
- 下一步：先准备 R4 command/time/output/stop package，在 `orin_1` 验证 synthetic paired scaffold；随后把 true bundle grouped hidden / HF raw weights 接入 R0H candidate timed path，并补 true bundle same-run NNCL paired runner。

### 2026-06-09：CuTeDSL R0H M5 synthetic NNCL paired scaffold implemented，true bundle+orin_1 paired runner pending

- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 状态更新为 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal`。
- 新增 orchestration 输出：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-136_r0h_m5_synthetic_nncl_paired_scaffold.md`
- 新增 mode：`routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired`。
- paired scaffold 将 synthetic raw qweight `[experts,K/8,N] int32` pack 为 NNCL `[experts,N/4,K*2] uint8`，scales 仍为 `[experts,K/128,N] half`，并把 R0H `cu_row_prefix` 转为 NNCL int64 end-prefix，不含起始 0。
- NNCL 只作为 public `MoeGroupGemm<half, half, QuantMethod::kGPTQFp16Int4Groupwise>` same-run baseline/reference；candidate 仍为 `R0HFusedW4A16GroupedVisitorWmmaKernel`，不得把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 包装为 candidate。
- 本地 build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

- help PASS，新增 mode 可见，并明确该 scaffold 不是 full M5 ready，`runner_ready` 必须保持 `false`。
- 旧 M5 synthetic A/B 10 shape 回归 PASS，CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_after_nncl_pair_majorfix.csv`。
- 回归 CSV 10 行均 `precision_pass=true`、`runner_ready=false`、`nncl_paired_ready=false`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`independent_candidate=false`。
- Reviewer 初审 `MAJOR`：paired synthetic mode 原先会误导为 full M5 ready；已修复为 `RunOneShape(..., false, true, true, ...)`，日志保持 `runner_ready=false`，复审 PASS。
- 本地 paired mode 在 sm120 上因 NNCL baseline 报 `[Error][MoE][GEMM Dispatch] Arch unsupported for MoE GEMM`，只生成 header-only CSV：`r0h_m5_synthetic_nncl_paired_local*.csv`；这些文件不是数值 evidence，不得用于 SOP/tier/formal 或性能结论。
- 本轮未执行 `orin_1` sync/build、NCU 或有效 paired NNCL baseline。
- 下一步：先在 `orin_1` 验证 synthetic paired scaffold，再补真实 Q35-028 bundle routing/input、真实 HF GPTQ weights 和 same-run NNCL `MoeGroupGemm` paired runner；真正 R4 前必须给出 command、预计时间、输出目录和停止条件。

### 2026-06-09：CuTeDSL R0H M5 synthetic A/B runner done，paired scaffold still pending at this checkpoint

- 本条为 AUTO-135 checkpoint，已被上方 AUTO-136 supersede；当前恢复点以顶部 AUTO-136 条目为准。
- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 当时状态更新为 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 paired scaffold pending / orin_1_only / spike_only / not_formal`。
- 新增 orchestration 输出：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-135_r0h_m5_synthetic_ab_runner.md`
- 新增 mode：`routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic`。
- R0H grouped visitor kernel/host path 已从固定 `K=2048,N=512,gate_proj` 参数化到 `problem.k/problem.n/problem.projection`；host buffer、pointer stride、grid.x、K loop、A/qweight/scales/D stride 均使用运行时 K/N。
- M5 synthetic 覆盖 A/B 10 shape：A 为 `M=64/128/256/512/898,K=2048,N=512,gate_proj`；B 为 `M=64/128/256/512/898,K=512,N=2048,down_proj`。
- 本地 build PASS；help MINOR 修复后 rebuild PASS。
- M5 synthetic CSV：
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local.csv`
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_maincheck.csv`
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_maincheck_after_helpfix.csv`
- M4 post-change regression CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_post_m5synthetic.csv`。
- Updated preflight CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local_after_m5synthetic.csv`。
- M5 synthetic 10 行均 `precision_pass=true`、`runner_ready=false`、`candidate_shape_supported=true`、`nncl_paired_ready=false`、`nncl_ms=NA`、`candidate_vs_nncl_ratio=NA`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- Updated preflight 10 行均 `candidate_shape_supported=true`、`runner_ready=false`、`nncl_paired_ready=false`，reason 均包含 `same_run_NNCL_baseline_missing`；B 族 reason 已更新为 `family_B_down_proj_K512_N2048_has_R0H_M5_synthetic_structural_runner`。
- Reviewer 初审 `MINOR`：M5 preflight/synthetic 详细 help 文本在 R0E formal enabled build 下可能不打印；已修复并 rebuild/help/maincheck PASS。
- 本轮未执行 `orin_1` sync/build、NCU 或 same-run NNCL paired baseline；M5 synthetic 仍不是 full M5，不是 SOP/tier/formal evidence，也不是性能结论。
- 下一步：补真实 Q35-028 bundle routing/input、真实 HF GPTQ weights 和 same-run NNCL `MoeGroupGemm` paired baseline；之后才允许准备 R4 `orin_1` command/time/output/stop package。

### 2026-06-09：CuTeDSL R0H M5 preflight done，runner work pending

- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 状态更新为 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 runner work pending / orin_1_only / spike_only / not_formal`。
- 新增 orchestration 输出：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-134_r0h_m5_preflight.md`
- 新增 M5 preflight 文件与接入：
  - `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_m5_preflight.cc`
  - `samples/micro_bench/spike/cute_dsl/main.cc`
  - `samples/micro_bench/spike/cute_dsl/spike_common.h`
  - `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- 新增 mode：`routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_preflight`。
- 该 mode 只枚举 family A/B 10 shape 并 fail-closed 写出 runner 缺口；不启动 candidate kernel，不调用 NNCL candidate，不生成 NNCL ratio，也不声明 M5 pass。
- 本地 build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

- Worker CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local.csv`。
- Main-orchestrator 复跑 CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local_maincheck.csv`。
- CSV 覆盖 10 行：family A 为 `M=64/128/256/512/898,K=2048,N=512,gate_proj`；family B 为 `M=64/128/256/512/898,K=512,N=2048,down_proj`。
- A 族均 `candidate_shape_supported=true`，但 reason 明确 `same_run_NNCL_baseline_missing`。
- B 族均 `candidate_shape_supported=false`，reason 明确 `K_N_projection_parameterization_missing`。
- 所有行均 `runner_ready=false`、`nncl_paired_ready=false`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- reviewer 审查结论 PASS：mode 已接入 help/parse/dispatch/CMake；preflight 文件没有 include/call/wrap NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 `cutlass_extensions` 作为 candidate；没有误标 M5 pass、SOP/tier/formal 或性能结论。
- 本轮未执行 `orin_1` sync/build、NCU 或 same-run NNCL paired baseline。
- 下一步：补 M5 runner 的 `K,N,projection` 参数化、family B `down_proj K=512,N=2048` packed weight/scale 路径，以及 same-run NNCL paired baseline；完成后才允许准备 R4 `orin_1` command/time/output/stop package。

### 2026-06-09：CuTeDSL R0H M4 grouped visitor local structural smoke done

- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 状态更新为 `in_progress / M0-M4 local structural smoke done / M5 pending R4 / orin_1_only / spike_only / not_formal`。
- 新增 orchestration / checklist 输出：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-132_r0h_m4_gate_checklist.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-133_r0h_m4_grouped_visitor_smoke.md`
- 新增 M4 文件与接入：
  - `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_grouped_visitor_smoke.cu`
  - `samples/micro_bench/spike/cute_dsl/main.cc`
  - `samples/micro_bench/spike/cute_dsl/spike_common.h`
  - `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- M4 新增 mode：`routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke`。
- M4 candidate kernel：`R0HFusedW4A16GroupedVisitorWmmaKernel`。
- M4 范围：synthetic grouped `gate_proj`、`K=2048`、`N=512`、`group_size=128`、synthetic HF raw GPTQ input；使用 `cu_row_prefix` / `padded_cu_row_prefix` 将 padded tile row 映射到 expert slot/local row，并用 compact `cu_row_prefix` 写回 routed grouped output；不是 single expert flatten。
- 本地 build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

- Worker 本地 smoke PASS，CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local.csv`。
- Worker CSV 关键结果：`active_experts=4`、`expert_row_counts=7|13|19|25`、`cu_row_prefix=0|7|20|39|64`、`padded_cu_row_prefix=0|16|32|64|96`、`candidate_ms=0.236384`、`reference_ms=0.060224`、`max_abs_vs_reference=3.05548310e-05`、`rmse_vs_reference=8.04463902e-06`、`precision_pass=true`、`candidate_launches_per_iter=1`、`grouped_problem_visitor=true`、`cu_row_prefix_visitor=true`、`nncl_ms=NA`。
- Main-orchestrator 本地复跑 PASS，CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_maincheck.csv`；关键结果 `candidate_ms=0.430688`、`reference_ms=0.060992`、`max_abs=3.055483e-05`、`rmse=8.044639e-06`、`precision_pass=true`。
- Local M sweep check：`M=64/128/256/512/898` 均 PASS，CSV 为 `r0h_m4_grouped_visitor_smoke_local{,_m128,_m256,_m512,_m898}.csv`；所有行均 `precision_pass=true`、`candidate_launches_per_iter=1`、`nncl_ms=NA`。这些仍是 synthetic `gate_proj K=2048,N=512` structural smoke，不是 M5 family A/B full probe。
- reviewer 审查结论 PASS：新 mode 已接入 help/parse/dispatch/CMake；candidate 文件未 include/call/wrap NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 `cutlass_extensions` fastpath；grouped visitor 逻辑不是 single expert flatten。
- explorer 审查 M5 结论：`needs_local_runner_work`。当前 M4 固定 `gate_proj K=2048,N=512`，不支持 family B `down_proj K=512,N=2048`，也没有 same-run NNCL baseline，因此不能直接启动 `orin_1` M5 full shape probe。
- CSV/notes 保持 `b_tile_shared=true`、`scale_tile_shared=true`、`full_b_predecode=false`、`scale_iterator_group128=true`、`packed_b_iterator=true`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- 本轮未执行 `orin_1` sync/build、NCU 或 same-run NNCL paired baseline；M4 仍是本地 structural smoke，不是 SOP/tier evidence，也不是性能结论。
- 下一步 M5：先补本地 M5 runner/preflight；真正 `orin_1` family A/B full probe 执行前必须补齐 family B + same-run NNCL runner，并满足 R4 command/time/output/stop 条件。

### 2026-06-09：CuTeDSL R0H M3 local structural smoke done

- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`；本条记录的是 M3 完成时的历史状态，已被上方 M4 条目 supersede。
- 新增 orchestration / checklist 输出：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-130_r0h_m3_gate_checklist.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-131_r0h_m3_packed_scale_pipeline_smoke.md`
- 新增 M3 文件与接入：
  - `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_packed_scale_pipeline_smoke.cu`
  - `samples/micro_bench/spike/cute_dsl/main.cc`
  - `samples/micro_bench/spike/cute_dsl/spike_common.h`
  - `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- M3 新增 mode：`routed_grouped_r0h_fused_w4a16_packed_scale_pipeline_smoke`。
- M3 candidate kernel：`R0HFusedW4A16PackedScalePipelineWmmaKernel`。
- M3 范围：single expert、`gate_proj`、`K=2048`、`N=512`、`group_size=128`、synthetic HF raw GPTQ input；qweight tile 与 scale tile staged 到 shared buffer，dequant 在 WMMA tile/mainloop 内完成；无 full `dense_B_fp16` predecode；`candidate_launches_per_iter=1`。
- 本地 build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

- 本地 synthetic smoke PASS，latest CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local.csv`。
- 关键结果：`candidate_ms=0.213408`、`reference_ms=0.059072`、`max_abs=3.05548310e-05`、`rmse=7.99963300e-06`、`finite=true`、`nonzero=32768`、`precision_pass=true`、`nncl_ms=NA`。
- rerun CSV：`analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local_rerun.csv`，同样 PASS。
- reviewer 初审结论为 `MINOR`：缺少精确 token `paired_nncl_baseline_pending`；已在 notes 中补齐并 rebuild/rerun PASS。
- CSV/notes 保持 `b_tile_shared=true`、`scale_tile_shared=true`、`full_b_predecode=false`、`scale_iterator_group128=true`、`packed_b_iterator=true`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- 本轮未执行 `orin_1` sync/build、NCU 或 same-run NNCL paired baseline；M3 仍是本地 structural smoke，不是 SOP/tier evidence，也不是性能结论。
- 当时待办是 M4 MoE grouped problem visitor；该待办已在上方 M4 条目完成。实际 `orin_1` build/smoke/NCU 仍需先满足 R4 command/time/output/stop 条件。

### 2026-06-09：CuTeDSL R0H M0-M2 smoke done

- hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 已在 `/goal` 模式启动；本条记录的是 M0-M2 完成时的历史状态，已被上方 M3 条目 supersede。
- 新增 orchestration 输出：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-128_r0h_m0_m1_orchestration.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-129_r0h_m2_single_expert_smoke.md`
- 新增 R0H analysis 输出：
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/m0_goal_baseline_lock.md`
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/nncl_fastpath_spec.md`
  - `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m2_single_expert_smoke_local.csv`
- 子代理编排：`repo-explorer` 梳理 spike 入口和复用函数；`perf-analyst` 锁定 same-run NNCL baseline 与 CSV 字段；`oss-scout` 完成 CUTLASS/NNCL 只读对照；`qwen-architect` 锁定 HF GPTQ raw 语义和 M2/M3/M4 边界；`kernel-dev` 实现 M2；`reviewer` 审查 M2，结论 PASS。
- M2 新增 mode：`routed_grouped_r0h_fused_w4a16_single_expert_smoke`。
- M2 范围：single expert、`gate_proj`、`K=2048`、`N=512`、`group_size=128`；candidate kernel 在 WMMA K-tile loop 内从 HF raw GPTQ `qweight/scales` 解 int4 并应用 scale；timed candidate 内不做 full `dense_B_fp16` predecode。
- 本地 build PASS：

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

- 本地 synthetic smoke PASS，关键结果：`candidate_ms=0.486240`、`reference_ms=0.098176`、`max_abs=3.503263e-05`、`rmse=8.392764e-06`、`finite=true`、`nonzero=32768`、`precision_pass=true`、`nncl_ms=NA`。
- reviewer 审查确认：M2 candidate 文件未调用/包装 `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 NNCL `cutlass_extensions` fastpath；probe flags 顺序与含义符合 R0H 边界。
- 本轮未执行 `orin_1` sync/build、NCU 或 long-running R4 实验；`nncl_ms=NA`，same-run NNCL paired baseline pending。
- 结论：M2 是本地 synthetic smoke/probe-only skeleton，不是 SOP/tier evidence，也不是 Orin 性能结论；当时待办是实现 packed B iterator + scale iterator + shared-memory pipeline，该待办已在上方 M3 条目完成。

### 2026-06-09：CuTeDSL R0H fused W4A16 mainloop plan synced

- 新增 hot task：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`。
- 新增计划输出：`.codex/agent_group/current/agent_outputs/AUTO-20260609-127_r0h_fused_w4a16_plan_sync.md`。
- 已将下一次 agent_group cold start 入口切到 R0H，要求使用 `/goal` 模式启动：

```text
/goal Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP: make current repo CuteDSL/CUTLASS spike performance align with same-run NNCL MoeGroupGemm on orin_1 by building an independent fused W4A16 int4-dequant + scale-iterator + grouped-mainloop pipeline
```

- 固定执行要求：基于 agent_group 规则组织 sub-agent；目标设备只允许 `orin_1`；baseline 为 same-run NNCL `MoeGroupGemm`；初级 gate family A/B geomean `<=1.50x`，最终 gate `<=1.20x`。
- 固定写入范围：`samples/micro_bench/spike/cute_dsl/`、`samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/`、`analysis/Qwen35_cutedsl_r0h_fused_w4a16_<TS>/`、`.codex/agent_group/`、必要 spike CMake 接入。
- 禁止：修改 production Qwen3.5 推理路径；把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 包装为 candidate；在非 `orin_1` 平台生成性能结论。
- R0H 计划 milestones：M0 goal/baseline，M1 NNCL 快路径规格化，M2 单 expert fused smoke，M3 packed B + scale iterator + shared pipeline，M4 MoE grouped problem visitor，M5 `orin_1` full 10 shape probe，M6 NCU isolation，M7 formal 决策。
- 结论：R0F/R1 和 R0G raw CUDA/WMMA 局部参数线已收口/停止；下一步必须从 true independent fused GPTQ W4A16 grouped mainloop 开始。

最后更新：2026-06-09

## 当前摘要

- 当前 repo：`/workspace/liyang/lape_a6d6bfb9`
- 当前分支：`qwen35_moe_perf`
- 当前 production anchor：`aaf6747 / TTFT=1071.21 ms / p-ntokens/s=2804.31`
- 当前 hot epic：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`
- 当前冷启动方向：恢复到 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal`。先读取 `AUTO-127` 到 `AUTO-137`、`STATE.md`、`tasks.csv`、`ROADMAP.md` 和 `TASK_LEDGER.md`；不要重复 M0/M1/M2/M3/M4，也不要把 M5 preflight、M5 synthetic runner、true-bundle preflight 或本地 header-only paired CSV 当成正式 M5。下一步是先准备 R4 command/time/output/stop package，在 `orin_1` 验证 synthetic paired scaffold；随后把 true bundle grouped hidden / HF raw weights 接入 R0H candidate timed path，并补 true bundle same-run NNCL `MoeGroupGemm` paired runner。继续禁止将 NNCL `MoeFCGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 包装为 candidate。
- 历史边界：R0F/R1-probe 已关闭为 `done / reject_or_hold / probe-only / not production`；R0G raw CUDA/WMMA 局部参数线在 AUTO-126 后停止。AUTO-114 到 AUTO-126 只作为为什么不继续调 `threshold/warps/cols` 的依据，不是当前冷启动主线。
- 当前禁止事项：不回到 Marlin R0，不重跑 CuTe/CUTLASS R0E formal，不把 R0c/R0d/R0D1 diagnostic 当 hot task，不把 R0F/R1-probe 当 R1/R3/production 授权，不把 M2 hygiene pass、M3 grouped/serial speedup 或 M4 NNCL-internal control 扩大为 independent candidate pass。

完整压缩前历史已归档到：

- `.codex/agent_group/archive/20260608_marlin_holding_compaction/memory.before/PROGRESS_LEDGER.before.md`

## 近期关键进展

### 2026-06-09：CuTeDSL AUTO-126 R0G small-row cols probe done

- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-126_r0g_smallrow_cols_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_smallrow_cols_probe_20260609_126/`
- 报告：`analysis/Qwen35_cutedsl_r0g_smallrow_cols_probe_20260609_126/report.md`
- 新增参数：`--small_row_cols_per_warp=4|8|16`，默认 `4` 保持旧 small-row vec4 行为。
- 执行矩阵：`cols=4/8/16`，threshold=1，`wmma_n_warps=16`，`wmma_packed_loader=1`，`hybrid_single_kernel=1`，M64/M898，gate_proj。
- 本地 build PASS；`orin_1` sync PASS；`orin_1` spike target build PASS。
- 6 条 CSV guard 全通过：`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`precision_pass=true`、`candidate_launches_per_iter=1`。
- 最佳 common `cols=8`：M64 ratio `2.112438x`，M898 ratio `2.273437x`，geomean `2.191459x`。
- Same-build `cols=4` control geomean `2.209285x`，因此 `cols=8` 只改善约 `0.8%`，且 M64 退化；`cols=16` geomean `2.684973x` 明显退化。
- 结论：`done / probe-only / not formal / reject_or_hold`。small-row SIMT 每 warp 列数不是主导瓶颈；当前 raw CUDA/WMMA attribution line 不应继续做类似局部参数 sweep。

### 2026-06-09：CuTeDSL AUTO-125 R0G hybrid single-kernel threshold/warps sweep done

- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-125_r0g_hybrid_single_kernel_sweep_perf-analyst.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_sweep_20260609_125/`
- 报告：`analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_sweep_20260609_125/report.md`
- 复用 AUTO-124 已验证的 `--hybrid_single_kernel=1` 与 `--wmma_packed_loader=1`。
- 执行矩阵：threshold `1/2/4/8/12/15`，`wmma_n_warps=8/16`，M64/M898，gate_proj，warmup/iters `5/50`。
- 24 条 CSV guard 全通过：`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`precision_pass=true`、`candidate_launches_per_iter=1`。
- 最佳 common 组合 threshold=1、warps=16：M64 ratio `2.548206x`，M898 ratio `1.866342x`，geomean `2.180785x`。
- Per-shape best：M64 threshold=2、warps=8、ratio `2.212469x`；M898 threshold=1、warps=16、ratio `1.866342x`。
- 高 threshold 会让 M898 small-row 数显著增加并恶化到 `5x-7x` ratio。
- 结论：`done / probe-only / not formal / reject_or_hold`。参数微调比 AUTO-124 有改善，但仍明显 `>1.50x` 且不达 `<=1.20x`；建议停止泛参数微调当前 raw CUDA/WMMA hybrid kernel。

### 2026-06-09：CuTeDSL AUTO-124 R0G hybrid single-kernel probe done

- 新增参数：`--hybrid_single_kernel=0|1`，默认保持 `0`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-124_r0g_hybrid_single_kernel_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_probe_20260609_124/`
- 报告：`analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_probe_20260609_124/report.md`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync PASS；spike target build PASS。
- 执行矩阵：threshold `2`，`wmma_n_warps=8`，`wmma_packed_loader=1`，`hybrid_single_kernel=0/1`，M64/M898，gate_proj，warmup/iters `5/50`。
- 4 条 CSV guard 全通过：`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`precision_pass=true`。
- 同 build dual-kernel control：M64/M898 ratio `2.941212x/3.117430x`，geomean `3.028039x`。
- single-kernel probe：M64/M898 ratio `2.297688x/2.704718x`，geomean `2.492910x`，candidate launch 数从 2 降到 1。
- 单 kernel 相对同 build dual-kernel control speedup：M64 `1.278698x`，M898 `1.146003x`。
- 结论：`done / probe-only / not formal / reject_or_hold`。launch fusion 有真实收益，但 AUTO-124 最佳 geomean 与 AUTO-123 `2.490867x` 基本持平，仍明显 `>1.50x` 且不达 `<=1.20x`，不可 promoted。

### 2026-06-09：CuTeDSL AUTO-123 R0G WMMA packed loader probe done

- 新增参数：`--wmma_packed_loader=0|1`，默认保持 `0`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260609-123_r0g_wmma_packed_loader_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_wmma_packed_loader_probe_20260609_123/`
- 报告：`analysis/Qwen35_cutedsl_r0g_wmma_packed_loader_probe_20260609_123/report.md`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync PASS；spike target build PASS。
- 执行矩阵：threshold `2/4`，`wmma_n_warps=8/16`，`wmma_packed_loader=1`，M64/M898，gate_proj，warmup/iters `5/50`。
- 8 条 CSV guard 全通过：`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`precision_pass=true`。
- 最佳组合 threshold=2、`wmma_n_warps=8`、packed=1：M64 ratio `2.665852x`，M898 ratio `2.327368x`，geomean `2.490867x`。
- 相对 AUTO-122 最佳 geomean `3.057917x` 改善约 `18.7%`，但仍明显 `>1.50x` 且不达 `<=1.20x`。
- 结论：`done / probe-only / not formal / reject_or_hold`。packed loader 证明 B-tile raw GPTQ decode/load 放大是真实瓶颈之一，但当前 raw CUDA/WMMA attribution kernel 仍不可 promoted。

### 2026-06-08：CuTeDSL AUTO-122 R0G WMMA N-warps probe done

- 新增参数：`--wmma_n_warps=4|8|16`，默认保持 `4`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-122_r0g_wmma_nwarps_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_wmma_nwarps_probe_20260608_122/`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync PASS；spike target build PASS。
- 执行矩阵：threshold `2/4`，`wmma_n_warps=8/16`，M64/M898，gate_proj，warmup/iters `5/50`。
- 8 条 CSV guard 全通过：`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`precision_pass=true`。
- 最佳组合 threshold=2、`wmma_n_warps=8`：M64 ratio `2.967751x`，M898 ratio `3.150822x`，geomean `3.057917x`。
- 结论：`done / probe-only / not formal / reject_or_hold`。增加 WMMA N-tile warps 没有接近 `<=1.20x`；当前 raw CUDA/WMMA attribution line 建议 hold。

### 2026-06-08：CuTeDSL AUTO-121 R0G hybrid threshold sweep done

- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-121_r0g_hybrid_threshold_sweep_perf-analyst.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_hybrid_threshold_sweep_20260608_121/`
- 报告：`analysis/Qwen35_cutedsl_r0g_hybrid_threshold_sweep_20260608_121/report.md`
- 扫描 threshold：`1/2/4/8/12/15`，M64/M898，gate_proj。
- 12 条 CSV guard 全通过。
- 最佳 common threshold=2，geomean `3.309147x`。
- 最佳 M64 threshold=12，ratio `2.565185x`。
- 最佳 M898 threshold=4，ratio `3.281669x`。
- 结论：`done / probe-only / not formal`。threshold tuning 无法达到 `<=1.20x`。

### 2026-06-08：CuTeDSL AUTO-120 R0G hybrid small-row probe done

- 新增 mode：`routed_grouped_independent_w4a16_hybrid_smallrow_smoke`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-120_r0g_hybrid_smallrow_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync PASS；spike target build PASS with Release/sm87。
- Hybrid threshold=4 M64/gate_proj：`candidate_ms=1.880016`，`nncl_ms=0.481731`，ratio `3.902625`，`candidate_launches_per_iter=2`，`hybrid_tile_m_count=2`，`hybrid_small_row_count=54`，`precision_pass=true`。
- Hybrid threshold=4 M898/gate_proj：`candidate_ms=3.816718`，`nncl_ms=1.107985`，ratio `3.444739`，`candidate_launches_per_iter=2`，`hybrid_tile_m_count=68`，`hybrid_small_row_count=139`，`precision_pass=true`。
- 两 shape geomean ratio：`3.666541x`。对比 AUTO-119 shared-A WMMA `4.372321x / 4.353763x` 有改善，说明 small-row padding 是真实瓶颈之一。
- 但 M64/M898 均明显 `>1.50x` 且不达 `<=1.20x`，因此不扩展为 formal，不进入 SOP/tier/production。
- CSV/report 固定 `independent_candidate=false/candidate_audit_pending=true/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- 结论：`done / probe-only / not formal / continue_probe_or_hold`。后续不应只微调当前 attribution kernel；若继续 CuTe/CUTLASS，应做 true CUTLASS-style fused GPTQ W4A16 grouped mainloop，或转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。

### 2026-06-08：CuTeDSL AUTO-119 R0G WMMA shared-A probe done

- 优化 mode：`routed_grouped_independent_w4a16_wmma_smoke`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-119_r0g_wmma_shared_a_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_wmma_shared_a_probe_20260608_119/`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync PASS；spike target build PASS with `LAPE_BUILD_SPIKE_CUTE_DSL=ON`、Release、sm87。
- Shared-A WMMA M64/gate_proj：`candidate_ms=2.107414`，`nncl_ms=0.481990`，ratio `4.372321`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- Shared-A WMMA M898/gate_proj：`candidate_ms=4.136431`，`nncl_ms=0.950082`，ratio `4.353763`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- 对比 AUTO-117 4-warp WMMA：M898 candidate 从 `5.281041 ms` 降到 `4.136431 ms`；shared A tile reuse 有明确收益，但仍明显 `>1.50x`。
- CSV/report 固定 `independent_candidate=false/candidate_audit_pending=true/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- 结论：`done / probe-only / not formal / continue_probe`。下一步应处理 small expert padding / tile scheduling、B tile decode/layout，或转向真正 CUTLASS-style fused grouped mainloop。

### 2026-06-08：CuTeDSL AUTO-118 R0G predecode WMMA probe done

- 新增 mode：`routed_grouped_independent_w4a16_predecode_wmma_smoke`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-118_r0g_predecode_wmma_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_predecode_wmma_probe_20260608_118/`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync PASS；spike target build PASS with `LAPE_BUILD_SPIKE_CUTE_DSL=ON`、Release、sm87。
- Predecode row-major WMMA M64/gate_proj：`candidate_ms=2.420152`，`nncl_ms=0.321988`，ratio `7.516270`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- Predecode row-major WMMA M898/gate_proj：`candidate_ms=5.940392`，`nncl_ms=0.487489`，ratio `12.185688`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- CSV/report 固定 `independent_candidate=false/candidate_audit_pending=true/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- 结论：`done / probe-only / not formal / continue_probe`。把 raw decode 移出 timed loop 没有改善数量级，当前差距主要来自 naive WMMA tile/mainloop、小 expert 16-row padding 与 grouped 调度效率，而不是 decode-only。

### 2026-06-08：CuTeDSL AUTO-117 R0G independent W4A16 WMMA probe done

- 新增 mode：`routed_grouped_independent_w4a16_wmma_smoke`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-117_r0g_independent_w4a16_wmma_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_independent_w4a16_wmma_probe_20260608_117/`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync/default build PASS；spike target build PASS with `LAPE_BUILD_SPIKE_CUTE_DSL=ON`、Release、sm87。
- single-warp WMMA M64/gate_proj：`candidate_ms=2.436837`，`nncl_ms=0.482528`，ratio `5.050145`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- single-warp WMMA M898/gate_proj：`candidate_ms=7.694731`，`nncl_ms=0.978774`，ratio `7.861604`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- 4-warp WMMA M64/gate_proj：`candidate_ms=2.224506`，`nncl_ms=0.135846`，ratio `16.375158`，`precision_pass=true`；M64 same-run NNCL baseline 明显偏低，按前序 `~0.48 ms` baseline 估算仍约 `4.6x`。
- 4-warp WMMA M898/gate_proj：`candidate_ms=5.281041`，`nncl_ms=0.918199`，ratio `5.751521`，`precision_pass=true`。
- 对比 AUTO-116 single-launch：M898 candidate 从 `14.064703 ms` 改为 `5.281041 ms`；Tensor Core 化有收益，但仍明显 `>1.50x`。
- NCU candidate isolation PASS：filter `RawGptqW4A16GroupedWmmaKernel`，captured kernel 为 `unnamed>::RawGptqW4A16GroupedWmmaKernel(...)`，duration `1.45/1.55 ms`，achieved occupancy `76.97/76.15%`，未看到 `MoeFCGemm/MoeGroupGemm`。
- NCU workload CSV 的 `candidate_ms=161.037857` 是 profiler replay 污染，不用于 ratio。
- CSV/report 固定 `independent_candidate=false/candidate_audit_pending=true/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- 结论：`done / probe-only / not formal / continue_probe_or_reject_or_hold`。Naive WMMA 证明 Tensor Core 化方向有效但仍远离 `<=1.20x`；后续若继续应新建 true CUTLASS-style fused GPTQ W4A16 grouped formal task，不应把该 smoke promoted。

### 2026-06-08：CuTeDSL AUTO-116 R0G independent W4A16 single-launch probe done

- 新增 mode：`routed_grouped_independent_w4a16_single_launch_smoke`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-116_r0g_independent_w4a16_single_launch_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- `orin_1` sync/default build PASS；spike target build PASS with `LAPE_BUILD_SPIKE_CUTE_DSL=ON`、Release、sm87。
- M64/gate_proj single-launch smoke PASS：`candidate_ms=2.766093`，`nncl_ms=0.487725`，ratio `5.671422`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- M898/gate_proj single-launch smoke PASS：`candidate_ms=14.064703`，`nncl_ms=1.411296`，ratio `9.965807`，`candidate_launches_per_iter=1`，`precision_pass=true`。
- 对比 AUTO-115 warp-reduce：M64 从 `7.073074x` 改为 `5.671422x`，M898 从 `15.284829x` 改为 `9.965807x`；launch overhead 有收益，但仍明显 `>1.50x`。
- NCU candidate isolation PASS：filter `RawGptqW4A16GroupedSingleLaunchKernel`，captured kernel 为 `unnamed>::RawGptqW4A16GroupedSingleLaunchKernel(...)`，duration `716864/712704 ns`，achieved occupancy `97.82/97.80%`，未看到 `MoeFCGemm`。
- NCU workload CSV 的 `candidate_ms=143.722336` 是 profiler replay 污染，不用于 ratio。
- CSV/report 固定 `independent_candidate=false/candidate_audit_pending=true/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- 结论：`done / probe-only / not formal / reject_or_hold_or_continue_probe`。Single-launch 去掉 per-active-expert launch overhead 后仍远离 `<=1.20x`，后续若继续需要 true independent TensorCore/int4 W4A16 grouped mainloop。

### 2026-06-08：CuTeDSL AUTO-115 R0G independent W4A16 warp probe done

- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-115_r0g_independent_w4a16_warp_probe_kernel-dev.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/`
- 当前 raw CUDA kernel 为 single-output warp-reduce，不调用 NNCL `MoeFCGemm`、`MoeGroupGemm`、`dispatch_moe_gemm_to_cutlass` 或 NNCL CUTLASS extension headers 作为 candidate。
- `orin_1` M64/gate_proj：`candidate_ms=3.442426`，`nncl_ms=0.486694`，ratio `7.073074`，`candidate_launches_per_iter=37`，`precision_pass=true`。
- `orin_1` M898/gate_proj：`candidate_ms=21.543930`，`nncl_ms=1.409498`，ratio `15.284829`，`candidate_launches_per_iter=117`，`precision_pass=true`。
- tile8 warp kernel 试验更差，M64 ratio 约 `12.493918x`，M898 ratio 约 `15.895572x`，已回退到 single-output warp-reduce。
- CSV/report 固定 `independent_candidate=false/candidate_audit_pending=true/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- 结论：`done / probe-only / not formal / continue_probe`。当前最佳 raw independent smoke 仍远离 `<=1.20x`；下一步应实现 single-launch grouped raw W4A16 kernel，以分离 launch overhead 与 raw SIMT decode/matmul 算力差距。

### 2026-06-08：CuTeDSL AUTO-114 R0G independent W4A16 smoke pass

- 新增 spike-only mode：`routed_grouped_independent_w4a16_smoke`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-114_r0g_independent_w4a16_smoke_kernel-dev.md`
- Evidence：
  - `analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/report.md`
  - `analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/independent_w4a16_smoke_m64_orin1.csv`
- 本地 build PASS：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`。
- 本地 RTX 5090 smoke 被 NNCL baseline 拦截：`[Error][MoE][GEMM Dispatch] Arch unsupported for MoE GEMM`，因此不作为本地功能失败。
- `orin_1` sm87 Release build PASS：`build_cute_dsl_spike_orin1_probe` target `qwen3_5_cute_dsl_spike`。
- `orin_1` M64/gate_proj smoke PASS：`candidate_ms=32.292320`，`nncl_ms=4.967424`，`candidate_vs_nncl_ratio=6.500818`，`precision_pass=true`，`active_experts=37`。
- CSV guard：58 fields，1 data row，无 extra columns，关键审计字段存在。
- 审计字段固定：`candidate_uses_nncl_moefc=false`、`candidate_uses_nncl_moegroupgemm=false`、`candidate_uses_dispatch_moe_gemm_to_cutlass=false`、`candidate_uses_nncl_cutlass_extension_headers=false`、`baseline_uses_nncl_moegroupgemm=true`、`control_probe_only=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- 结论：`done / smoke-only / continue_probe / not formal / not tier`。该 raw CUDA scalar W4A16 kernel 只证明 HF GPTQ `qweight/scales` 解码与 matmul correctness 起点可行；ratio `6.500818x` 远未达到 `<=1.20x`，不能 promoted。若继续 R0G，必须实现 independent grouped/TensorCore W4A16 mainloop，并新建 formal candidate task 重走 SOP-A/B/C。

### 2026-06-08：CuTeDSL AUTO-113 R0G independent W4A16 gap audit done

- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-113_r0g_independent_w4a16_gap_audit.md`
- Evidence：
  - `analysis/Qwen35_cutedsl_r0g_independent_w4a16_gap_audit_20260608_192510/report.md`
- 结论：
  - 当前没有 independent CuTe/CUTLASS W4A16 MoeFC grouped candidate。
  - M4 dispatch 接近 NNCL baseline，但仍直接调用 `dispatch_moe_gemm_to_cutlass` 并复用 NNCL `MoeFCGemm` / CUTLASS extension path，只能作为 wrapper-isolation control。
  - R0G formal candidate 必须新建 task，并替换 candidate kernel 类型、dispatch 模板、fine-grained W4A16 scale mainloop 和 MoE grouped problem visitor；否则仍要标 `independent_candidate=false`。
- 本审计固定 `valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`，没有创建 formal candidate，没有修改 production path。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M5 feasibility reject_or_hold

- 新增 agent outputs：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_qwen-architect.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_perf-analyst.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_reviewer.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_orchestration.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/`
- M5 report：`analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/report.md`
- 决策：`reject_or_hold`。
- 依据：
  - M2 true independent dense fp16 serial path 两轮 family A/B ratio 为 `13.589240/4.937622` 与 `13.388290/4.723811`。
  - M3 grouped dense fp16 path 两轮 family A/B grouped_vs_nncl ratio 为 `4.442753/4.092893` 与 `4.412637/4.208391`。
  - M4 direct/dispatch 与 NNCL 同量级，但都复用 NNCL internal runner/template/header/kernel；dispatch 只证明 public wrapper/runner 开销不是主因。
- 当前没有 independent candidate kernel，不启动 Candidate NCU Isolation，不进入 formal/tier/R1/R3/production。
- 若继续 CuTe/CUTLASS，必须新建 `Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE` 并重新走 SOP-A/B/C；另一方向是 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M4 CUTLASS dispatch wrapper-isolation done

- 新增 agent outputs：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_cutlass_dispatch_kernel-dev.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_cutlass_dispatch_orin-runner.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_cutlass_dispatch_perf-analyst.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_cutlass_dispatch_reviewer.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_cutlass_dispatch_orchestration.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/`
- 新增 `routed_grouped_moefc_cutlass_dispatch_probe`：绕过 NNCL public `MoeGroupGemm` 和 `MoeGroupGemmRunner`，直接调用 NNCL 模板 `dispatch_moe_gemm_to_cutlass<half, cutlass::uint4b_t, Sm80, EpilogueOpNoBias>`。
- 本地 build PASS；`orin_1` sync PASS；`orin_1` Release/sm87 spike build PASS。
- M64 smoke PASS：2/2 rows `precision_pass=true`。
- full run1 PASS：10/10 rows `precision_pass=true`；family A/B dispatch-vs-NNCL geomean `1.001874/1.032655`。
- full run2 PASS：10/10 rows `precision_pass=true`；family A/B dispatch-vs-NNCL geomean `0.999701/1.011785`。
- 全部 dispatch CSV 行均 `precision_pass=true/control_probe_only=true/independent_candidate=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- 当时选择仍是 `continue_probe`。dispatch path 绕过 NNCL public op 和 runner，但仍复用 NNCL CUTLASS extension headers 与 `MoeFCGemm`，不是 independent candidate，不作为 SOP/tier/R1/R3/production evidence。该选择已被 M5 `reject_or_hold` 收口取代。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M4-control warm-state hardened done

- 新增 agent outputs：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_warm_hardened_kernel-dev.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_warm_hardened_orin-runner.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_warm_hardened_perf-analyst.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_warm_hardened_reviewer.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_warm_hardened_orchestration.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/`
- 根据 reviewer P2 审计，`routed_grouped_moefc_direct_probe` CSV 新增硬字段 `control_probe_only`、`independent_candidate`，row log 逐行新增 `independent_candidate=false`。
- 本地 build PASS；`orin_1` build PASS：`build_hardened_warm_probe.log`。
- Hardened smoke/full/repeat 均 PASS，共 21 条 CSV 数据行，全部 `precision_pass=true/control_probe_only=true/independent_candidate=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。
- Hardened warm-state shape-mean family A/B direct-vs-NNCL geomean：`0.999769/1.015588`。
- Hardened warm-state shape-mean family A/B second-pass geomean：`0.996385/0.996818`。
- 当时选择仍是 `continue_probe`。direct path 是 NNCL internal control，不是 independent candidate，不作为 SOP/tier/R1/R3/production evidence。该选择已被 M5 `reject_or_hold` 收口取代。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M4-control direct MoeFC proof done

- 新增 agent outputs：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_kernel-dev.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_orin-runner.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_perf-analyst.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_reviewer.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_orchestration.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/`
- 新增 `routed_grouped_moefc_direct_probe`：直接调用 NNCL internal `MoeGroupGemmRunner<half, cutlass::uint4b_t>`，使用 same packed W4A16 weights、same input、same `cu_row`、same default NNCL config。
- Orin build PASS：`build_moefc_direct_probe_balanced.log`，`build_rc=0`。
- balanced smoke `M64 gate_proj` PASS：`precision_pass=true`，`direct_vs_nncl_ratio=1.197989`，probe-only 三项 false。
- 两轮 10 shape balanced micro 均 rows=10、`precision_pass=true`、`nan_count_vs_nncl=0`、`inf_count_vs_nncl=0`、probe-only 三项 false。
- Balanced mean shape-mean family A/B ratio：`1.102040/1.280831`；family B 仍 `>1.20`，不能 candidate pass。
- Steady-state second-pass shape-mean family A/B ratio：`0.869187/0.942515`；证明 W4A16 MoeFC grouped runner 与 public NNCL kernel path 基本同量级。
- 旧 `r0f_m4_moefc_direct_all.csv` 因 timed-loop launch check 污染被排除。
- 当时选择：`continue_probe`。direct path 是 NNCL internal control，不是 independent candidate，不作为 SOP/tier/R1/R3/production evidence。该选择已被 M5 `reject_or_hold` 收口取代。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M3 grouped dense structural probe done, ratio stop

- 新增 agent outputs：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_kernel-dev.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_orin-runner.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_perf-analyst.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_reviewer.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_orchestration.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/`
- M3 构建 PASS：`build_grouped_dense_probe.log`，`build_rc=0`。
- 新增/修正 `routed_grouped_dense_probe`：CUTLASS `GemmGrouped` dense fp16 single-projection；family B `down_proj` 输入在计时区外预构造为 `silu(gate_proj(hidden))*up_proj(hidden)`。
- M64 gate smoke PASS：`micro_gate_m64_rc=0`，`precision_pass=true`，三项 false。
- 两轮 10 shape `orin_1` same-run NNCL paired micro 均 `micro_rc=0`、rows=10、`precision_pass=true`、`timing_contaminated=false`、probe-only 三项 false。
- grouped 相比 serial 有收益：
  - 第一轮 family A/B grouped_vs_serial geomean：`0.266817/0.768473`
  - 第二轮 family A/B grouped_vs_serial geomean：`0.264910/0.753515`
- 但 grouped 相对 same-run NNCL baseline 仍明显不达标：
  - 第一轮 family A/B grouped_vs_nncl geomean：`4.442753/4.092893`
  - 第二轮 family A/B grouped_vs_nncl geomean：`4.412637/4.208391`
- 已触发停止条件：ratio 连续两轮明显 `>1.50x`。不启动 Candidate NCU Isolation，不进入 M4/M5，不作为 SOP/tier/R1/R3/production evidence。
- 当前任务状态更新为 `blocked / M3 grouped_dense_ratio_gt_1p50 / probe-only / not production`。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M2 Timing hygiene done, ratio stop

- 新增 agent outputs：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_kernel-dev.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_orin-runner.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_perf-analyst.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_reviewer.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_orchestration.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/`
- M2 构建 PASS：`build_m2_timing_hygiene_final.log`，`build_rc=0`。
- paired timed loop hygiene：CSV/log 标记 `timing_contaminated=false`，notes 为 `m2_candidate_and_nncl_timed_loop_preallocated_no_torch_empty_no_contiguous_no_host_device_roundtrip_no_inner_sync;serial_per_expert_launch_remains;grouped_probe_not_done`。
- 两轮 `orin_1` same-run NNCL paired micro 均 `micro_rc=0`、rows=10、`precision_pass=true`、`nan_count=0`、`inf_count=0`、`nonzero>0`、probe-only 三项 false。
- 第一轮 family A/B geomean ratio：`13.589240/4.937622`；第二轮：`13.388290/4.723811`。
- 当时已触发停止条件：ratio 连续两轮明显 `>1.50x`。M2 后不直接进入 NCU/M4；后续 M3 是作为新的结构性 grouped dense probe 恢复验证，见上方 M3 record。
- 当时任务状态更新为 `blocked / M2 stop_condition_ratio_gt_1p50 / probe-only / not production`；该状态先被 M3 grouped dense probe 取代，最终已由 M5 收口为 `done / reject_or_hold / probe-only / not production`。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M1 Tensor Core sanity pass

- 新增 agent outputs：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m1_kernel-dev.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m1_orin-runner.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m1_reviewer.md`
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m1_orchestration.md`
- Evidence 目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/`
- `orin_1` Release/sm87 build PASS：`build_m1_epilogue_scalar.log`，`build_rc=0`。
- CMake cache：`LAPE_BUILD_SPIKE_CUTE_DSL=ON`，`LAPE_CUTE_DSL_ENABLE_R0E_FORMAL_MODES=OFF`，`CMAKE_CUDA_ARCHITECTURES=87`。
- `shape_bench` small/hot sanity PASS：`M64` 与 `M898` 的 family A/B 共 4 行均 `status=pass`、`op_class=TensorOp`、`candidate_path=cutlass_tensorop_dense_fp16`、`nan_count=0`、`inf_count=0`、`nonzero>0`。
- 默认 R0E modes 关闭：`--mode=r0e_sop_a_precision` 返回 `rc=1 / invalid --mode=r0e_sop_a_precision`。
- reviewer 无 P0/P1；P2 仅提醒 `status=pass` 字段可能被粗糙脚本误读，但 CSV/log 已有 `diagnostic_only/not_w4a16/not_routed_grouped_moe` 与三项 false 防护。
- 当前任务进入 `in_progress / M1 Tensor Core sanity pass / entering M2 timing hygiene / probe-only`。

### 2026-06-08：CuTeDSL AUTO-112 R0F/R1-probe M0 locked

- `/goal` 已启动：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`。
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m0_orchestration.md`
- 已写入一次性授权范围：`samples/micro_bench/spike/cute_dsl/`、必要 `CMakeLists.txt` spike 接入、`.codex/agent_group/`、`analysis/Qwen35_cutedsl_r0f_r1_probe_<TS>/`。
- 已写入 R4 停止条件：构建失败、精度非有限/全零、NCU 抓不到 candidate kernel、或 ratio 连续两轮明显 `>1.50x`。
- baseline 口径固定为 same-run NNCL grouped `MoeGroupGemm`，ratio=`candidate_ms/nncl_ms`，主 gate family A/B geomean `<=1.20x`。
- 任务状态从 `todo` 更新为 `in_progress / M0 baseline locked / probe-only`。

### 2026-06-08：Marlin holding memory compaction

- 按用户要求压缩 agent_group 记忆，并将 Marlin 方案标注为 `holding / tier D / archived / not production`。
- 新归档目录：
  - `.codex/agent_group/archive/20260608_marlin_holding_compaction/`
- 已归档内容：
  - `current.before/STATE.before.md`
  - `current.before/epic.before.md`
  - `current.before/acceptance.before.md`
  - `current.before/tasks.before.csv`
  - `memory.before/ROADMAP.before.md`
  - `memory.before/TASK_LEDGER.before.md`
  - `memory.before/RISKS.before.md`
  - `memory.before/PROGRESS_LEDGER.before.md`
  - `memory.before/DECISIONS.before.md`
  - `agent_outputs/`：64 个 Marlin 相关 worker 输出
  - `tools/`：15 个 `q35_m4_*` Marlin guard/analyzer/runner 工具
  - `tasks.archived.csv`
- 已重写 hot 文档：
  - `.codex/agent_group/current/STATE.md`
  - `.codex/agent_group/current/epic.md`
  - `.codex/agent_group/current/acceptance.md`
  - `.codex/agent_group/current/tasks.csv`
- 已压缩长期记忆：
  - `.codex/agent_group/memory/ROADMAP.md`
  - `.codex/agent_group/memory/TASK_LEDGER.md`
  - `.codex/agent_group/memory/RISKS.md`
  - `.codex/agent_group/memory/PROGRESS_LEDGER.md`
  - `.codex/agent_group/memory/DECISIONS.md`
- 冷启动结果：当前 hot task 只剩 `Q35-MOE-CUTEDSL-R0F-R1-PROBE`；第一步固定为 Tensor Core sanity。

### 2026-06-08：CuTeDSL AUTO-111 R0F cold-start memory sync

- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-111_cutedsl_r0f_cold_start_sync.md`
- 将冷启动入口切到 `Q35-MOE-CUTEDSL-R0F-R1-PROBE`。
- 固定顺序：Tensor Core sanity -> timing hygiene -> candidate NCU isolation -> grouped launch probe -> W4A16 feasibility -> formal gate。
- 所有 R0F/R1-probe 输出必须 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。

### 2026-06-08：CuTeDSL AUTO-110 R0F/R1-probe plan sync

- 新增任务：
  - `Q35-MOE-CUTEDSL-R0F-R1-PROBE`：当时为 `todo / probe-only`，现已在 M5 收口为 `done / reject_or_hold / probe-only / not production`
- 新增 agent output：
  - `.codex/agent_group/current/agent_outputs/AUTO-20260608-110_cutedsl_r0f_r1_probe_plan.md`
- 该任务只做 post-R0E performance attribution 和上限验证，不改变 R0E `done / formal FAIL / gate_fail` 结论。

### 2026-06-08：CuTe/CUTLASS R0E formal gate fail

- 用户已确认 R4，并在 `orin_1` 容器 `liyang_lape` 执行 formal SOP-A/B/C。
- Evidence 目录：
  - `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`
- Guard verdict：
  - `schema_pass=true`
  - `status=gate_fail`
  - `overall_pass=false`
  - `tier_eligible=false`
- SOP-A PASS：`max_abs=6.661564e-05`，`rmse=2.843369e-06`。
- SOP-B PASS：真实 NCU best occupancy `31.060000`。
- SOP-C FAIL：family A/B geomean `152.031603/65.925507`。
- 结论：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 为 `done / tier D / not production`，不进入 R1/R3/production。

### 2026-06-06：Marlin formal R0 tier D

- `Q35-022 M-4 Marlin-MoE Spike R0` 已完成正式 R0 判定。
- SOP-A PASS：`max_abs=0.000120982528`，`rmse=4.56000724e-06`。
- SOP-B PASS：fresh Orin NCU best occupancy `33.24% > 30%`。
- SOP-C FAIL：family A/B geomean `1.155492/1.287823`，hot M898 `1.246268/1.367099`，small M64 `1.112405/1.239476`。
- 结论：tier D；压缩后状态为 `holding / tier D / archived / not production`。
