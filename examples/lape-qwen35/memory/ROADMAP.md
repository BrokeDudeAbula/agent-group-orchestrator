# LAPE Qwen3.5 MoE 推理优化 Roadmap

最后更新：2026-06-09

## 核心目标

在 `orin_1` 上，让 Qwen3.5 MoE 模型 `inputLen=2500` 纯文本 prefill 吞吐达到 `3000 tok/s`，同时保持正确语义、replay 精度、e2e token 稳定和 production 可回滚。

当前 production anchor：

| 项 | 当前值 |
|---|---|
| anchor commit | `aaf6747 perf(qwen35-gdn): inline fast_expf via ex2.approx.f32 + bf16 rtne` |
| anchor 数据 | MoE 3004 5 轮 cross-confirm median：`TTFT=1071.21 ms / p-ntokens/s=2804.31` |
| 目标缺口 | 距 `3000 tok/s` 约 `64 ms TTFT` |
| 当前 hot epic | `Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP` 已在 `/goal` 模式启动，M0-M4 local structural smoke done，M5 preflight done，M5 synthetic A/B runner done；M5 synthetic NNCL paired scaffold 已实现但本地 sm120 NNCL baseline blocked；M5 true bundle/HF GPTQ preflight 已完成；下一步先在 `orin_1` 验证 synthetic paired scaffold，并补 true bundle same-run NNCL paired runner；正式 family A/B probe 仍需满足 R4 门禁 |
| 当前 R1 状态 | 不允许进入 R1；Marlin 为 `holding / tier D / archived / not production`，CuTe/CUTLASS R0E 为 `done / formal FAIL / gate_fail`，R0F/R1-probe 已完成 M5 feasibility，决策为 `reject_or_hold / probe-only / not production`；AUTO-126 small-row cols probe 最佳 `cols=8` geomean `2.191459x`，仍明显 `>1.50x` 且不达 `<=1.20x`，raw CUDA/WMMA 局部参数线停止。当前 hot 为 `Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`：M0/M1 已锁定 baseline 和 NNCL fastpath spec，M2 single expert fused W4A16 WMMA smoke 本地 build/synthetic smoke/reviewer PASS；M3 packed B iterator + scale iterator + shared-memory pipeline structural smoke 本地 build/smoke/rerun PASS；M4 grouped problem visitor structural smoke 本地 build/smoke/maincheck/reviewer PASS；M5 preflight fail-closed PASS；M5 synthetic A/B runner 覆盖 A `gate_proj K=2048,N=512` 与 B `down_proj K=512,N=2048` 10 shape 且 precision PASS，已关闭 K/N/projection 参数化缺口；已新增 synthetic NNCL paired scaffold，但本地 sm120 NNCL baseline 因 arch unsupported 无法产出 paired 数值；已新增 true bundle/HF GPTQ preflight 且 10 shape guard PASS；仍缺 `orin_1` same-run NNCL paired baseline 和 true bundle candidate timed path；`nncl_ms=NA`，未执行 `orin_1`/NCU/有效 paired NNCL baseline，不是 SOP/tier evidence。 |

文档边界：

- 本文件是真实位置 `.codex/agent_group/memory/ROADMAP.md`，兼容软链为 `.codex/agent_group/ROADMAP.md`。
- 当前执行状态以 `current/STATE.md` 和 `current/tasks.csv` 为准。
- 跨阶段任务台账以 `memory/TASK_LEDGER.md` 为准。
- 历史细节与压缩前全文在 `.codex/agent_group/archive/20260608_marlin_holding_compaction/`。

## 冷启动恢复

下次 agent_group 冷启动后，必须继续 `Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`，恢复点为 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal`。R0H 已在 `/goal` 模式启动，目标仍为：

```text
/goal Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP: make current repo CuteDSL/CUTLASS spike performance align with same-run NNCL MoeGroupGemm on orin_1 by building an independent fused W4A16 int4-dequant + scale-iterator + grouped-mainloop pipeline
```

R0H 固定要求：

- 基于 agent_group 规则组织 sub-agent 执行。
- 测试目标设备固定为 `orin_1`，不得切换平台生成性能结论。
- baseline 固定为 same-run NNCL `MoeGroupGemm`。
- 初级目标 family A/B geomean ratio `<=1.50x`，最终目标 `<=1.20x`，同时检查 `M64/M898`。
- 不修改 production Qwen3.5 推理路径。
- 不得把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 包装成 candidate。

R0F/R1 M5 与 AUTO-126 仍作为历史边界读取：当前 raw CUDA/WMMA 局部参数 probe 已停止，下一步必须实现 true independent fused GPTQ W4A16 grouped mainloop，而不是继续调 `threshold/warps/cols`。

必须读取：

- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/current/epic.md`
- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/current/acceptance.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-127_r0h_fused_w4a16_plan_sync.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-128_r0h_m0_m1_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-129_r0h_m2_single_expert_smoke.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-130_r0h_m3_gate_checklist.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-131_r0h_m3_packed_scale_pipeline_smoke.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-132_r0h_m4_gate_checklist.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-133_r0h_m4_grouped_visitor_smoke.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-134_r0h_m5_preflight.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-135_r0h_m5_synthetic_ab_runner.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-136_r0h_m5_synthetic_nncl_paired_scaffold.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-137_r0h_m5_true_bundle_preflight.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-138_r0h_orin1_synthetic_nncl_paired_r4_package.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-110_cutedsl_r0f_r1_probe_plan.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-111_cutedsl_r0f_cold_start_sync.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_orchestration.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/report.md`

R0F/R0G 历史边界如下，仅用于避免回退到旧线；当前恢复点不是 M5 feasibility，而是 R0H M5 synthetic A/B runner done / synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / true bundle+orin_1 paired runner pending：

- M1 Tensor Core sanity 已通过。
- M2 Timing hygiene 已完成，paired timed loop 标记 `timing_contaminated=false`。
- M3 grouped dense fp16 single-projection structural probe 已完成，grouped 相比 serial 有收益，但两轮 same-run NNCL paired ratio 仍约 `4x`。
- M4-control direct NNCL internal MoeFC runner probe 已完成 warm-state schema hardening，hardened shape-mean family A/B direct-vs-NNCL geomean 为 `0.999769/1.015588`，证明 W4A16 MoeFC grouped runner 与 public NNCL 同量级；但 direct path 是 NNCL internal control，不是 independent candidate。
- M4 CUTLASS dispatch wrapper-isolation 已完成，绕过 NNCL public op 和 `MoeGroupGemmRunner` 后，full run1 family A/B geomean 为 `1.001874/1.032655`，run2 为 `0.999701/1.011785`；但该 path 仍复用 NNCL CUTLASS extension headers 和 `MoeFCGemm`，不是 independent candidate。
- M5 feasibility 已完成，决策为 `reject_or_hold`。不要 direct 或 dispatch formal promotion；若继续必须新建 independent fused W4A16 MoeFC grouped candidate task，或转向 NNCL targeted R0。
- R0G independent W4A16 gap audit 已完成，只确认下一 formal task 的替换面和禁止复用边界；没有创建 formal candidate。
- R0G independent W4A16 raw/WMMA probes 已完成：`routed_grouped_independent_w4a16_smoke` 证明 correctness 起点，warp-reduce M64/M898 为 `7.073074x / 15.284829x`；`routed_grouped_independent_w4a16_single_launch_smoke` 将 launch 数降到 1 后 M64/M898 仍为 `5.671422x / 9.965807x`；`routed_grouped_independent_w4a16_wmma_smoke` 用 WMMA Tensor Core 后，4-warp M64/M898 为 `16.375158x / 5.751521x`（M64 same-run NNCL baseline 明显偏低，按前序 baseline 估算仍约 `4.6x`），M898 candidate 从 `14.064703 ms` 降到 `5.281041 ms`；`routed_grouped_independent_w4a16_predecode_wmma_smoke` 将 raw decode 移出 timed loop 后 M64/M898 ratio 仍为 `7.516270x / 12.185688x`；shared-A WMMA 将 M64/M898 ratio 改为 `4.372321x / 4.353763x`；hybrid small-row threshold=4 将 M64/M898 ratio 改为 `3.902625x / 3.444739x`，两 shape geomean `3.666541x`；threshold sweep 最佳 common geomean `3.309147x`；`wmma_n_warps=8/16` 最佳 common geomean `3.057917x`；packed loader 最佳 common geomean `2.490867x`；hybrid single-kernel 将 launch 数从 2 降到 1，M64/M898 ratio `2.297688x / 2.704718x`，geomean `2.492910x`；single-kernel threshold/warps sweep 最佳 common threshold=1、warps=16，M64/M898 ratio `2.548206x / 1.866342x`，geomean `2.180785x`；small-row cols probe 最佳 `cols=8`，M64/M898 ratio `2.112438x / 2.273437x`，geomean `2.191459x`，相比 same-build `cols=4` 只改善约 `0.8%` 且 M64 退化。这些 probe 精度通过但仍明显 `>1.50x`。NCU 已抓到 `RawGptqW4A16GroupedSingleLaunchKernel` 与 `RawGptqW4A16GroupedWmmaKernel`，而不是 NNCL `MoeFCGemm`。这些 probe 只证明 raw HF GPTQ `qweight/scales` decode+matmul correctness、launch overhead、naive Tensor Core 化、decode-only 归因、shared-A reuse、小行阈值、N-warps 调参、packed-loader 读放大、single-kernel launch fusion 和 small-row SIMT 列粒度上限，不是 optimized grouped/CUTLASS W4A16 candidate，不可 promoted。当前线不应继续局部参数微调。

不得从以下旧状态恢复主线：

- Marlin R0 或 Marlin SOP-C v12/v13/v14/v16 参数线。
- CuTe/CUTLASS R0E formal 重跑。
- R0c/R0d/R0D1 diagnostic 重跑。
- Python CuTeDSL `_mlir` blocker closure。

## 当前 Hot Epic

### Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP

状态：`in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / local NNCL sm120 blocked / true bundle+orin_1 paired runner pending / orin_1_only / spike_only / not_formal`

目标：让当前 repo 的 CuteDSL/CUTLASS spike 方案尽可能与 same-run NNCL `MoeGroupGemm` 性能对齐。实现路径必须从 true independent fused W4A16 mainloop 开始，包含 packed int4 B iterator、groupwise scale iterator、cp.async multistage pipeline、fused dequant MMA 和 MoE grouped problem visitor。

当前输出：

- `.codex/agent_group/current/agent_outputs/AUTO-20260609-127_r0h_fused_w4a16_plan_sync.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-128_r0h_m0_m1_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-129_r0h_m2_single_expert_smoke.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-130_r0h_m3_gate_checklist.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-131_r0h_m3_packed_scale_pipeline_smoke.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-132_r0h_m4_gate_checklist.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-133_r0h_m4_grouped_visitor_smoke.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-134_r0h_m5_preflight.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-135_r0h_m5_synthetic_ab_runner.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-136_r0h_m5_synthetic_nncl_paired_scaffold.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-137_r0h_m5_true_bundle_preflight.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-138_r0h_orin1_synthetic_nncl_paired_r4_package.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/m0_goal_baseline_lock.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/nncl_fastpath_spec.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m2_single_expert_smoke_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local_rerun.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_maincheck.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_m128.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local_maincheck.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_maincheck.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_synthetic_ab_local_maincheck_after_helpfix.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_post_m5synthetic.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m5_preflight_local_after_m5synthetic.csv`
- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_single_expert_smoke.cu`
- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_packed_scale_pipeline_smoke.cu`
- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_grouped_visitor_smoke.cu`
- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/r0h_m5_preflight.cc`

最新 checkpoint：

- M0 `/goal` 初始化、worker 编排、same-run NNCL `MoeGroupGemm` baseline 口径、R3/R4 边界和停止条件已锁定。
- M1 NNCL W4A16 MoE grouped fastpath 已反向规格化为 R0H candidate 约束。
- M2 single expert `gate_proj` `K=2048,N=512,group_size=128` fused W4A16 WMMA smoke 已完成；本地 build PASS，本地 synthetic smoke PASS，reviewer PASS。
- M2 CSV 固定 `nncl_ms=NA`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- M3 packed B iterator + scale iterator + shared-memory pipeline structural smoke 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_packed_scale_pipeline_smoke`，candidate kernel 为 `R0HFusedW4A16PackedScalePipelineWmmaKernel`。
- M3 本地 build/smoke/rerun PASS；最新 CSV `candidate_ms=0.213408`、`reference_ms=0.059072`、`max_abs=3.05548310e-05`、`rmse=7.99963300e-06`、`finite=true`、`nonzero=32768`、`precision_pass=true`、`nncl_ms=NA`。
- M3 notes/CSV 固定 `b_tile_shared=true`、`scale_tile_shared=true`、`full_b_predecode=false`、`scale_iterator_group128=true`、`packed_b_iterator=true`、`candidate_launches_per_iter=1`、`paired_nncl_baseline_pending`。
- M4 MoE grouped problem visitor structural smoke 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke`，candidate kernel 为 `R0HFusedW4A16GroupedVisitorWmmaKernel`。
- M4 使用 `cu_row_prefix` / `padded_cu_row_prefix` 将 padded tile row 映射到 expert slot/local row，并用 compact `cu_row_prefix` 写回 routed grouped output；不是 single expert flatten。
- M4 主 CSV `active_experts=4`、`expert_row_counts=7|13|19|25`、`cu_row_prefix=0|7|20|39|64`、`padded_cu_row_prefix=0|16|32|64|96`、`candidate_launches_per_iter=1`、`grouped_problem_visitor=true`、`cu_row_prefix_visitor=true`、`precision_pass=true`、`nncl_ms=NA`。
- M4 local M sweep 补充：`M=64/128/256/512/898` 均为 synthetic `gate_proj K=2048,N=512` structural smoke PASS，均 `precision_pass=true`、`candidate_launches_per_iter=1`、`nncl_ms=NA`；CSV 为 `r0h_m4_grouped_visitor_smoke_local{,_m128,_m256,_m512,_m898}.csv`。
- M4 reviewer PASS；main-orchestrator 本地 build 和 smoke maincheck PASS。
- M5 gap audit：当前 M4 固定 `gate_proj K=2048,N=512`，不支持 family B `down_proj K=512,N=2048`，也没有 same-run NNCL baseline；M5 状态是 `needs_local_runner_work`，不能直接 R4 到 `orin_1` full shape probe。
- M5 preflight/scaffold 已完成；mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_preflight` 枚举 A/B 10 shape 并 fail-closed 输出 runner 缺口。
- M5 synthetic A/B structural runner 已完成；mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic` 覆盖 A/B 10 shape，A 族 `gate_proj K=2048,N=512` 与 B 族 `down_proj K=512,N=2048` 均 precision PASS。
- R0H grouped visitor kernel/host path 已从固定 `K=2048,N=512,gate_proj` 参数化到 `problem.k/problem.n/problem.projection`；host buffer、pointer stride、grid.x、K loop、A/qweight/scales/D stride 均使用运行时 K/N。
- M5 synthetic CSV 所有行均 `precision_pass=true`、`runner_ready=false`、`candidate_shape_supported=true`、`nncl_paired_ready=false`、`nncl_ms=NA`、`candidate_vs_nncl_ratio=NA`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- Updated preflight CSV 中 A/B 族均为 `candidate_shape_supported=true` 但 `same_run_NNCL_baseline_missing`；B 族 reason 已更新为 `family_B_down_proj_K512_N2048_has_R0H_M5_synthetic_structural_runner`。
- M5 preflight 本地 build/maincheck/reviewer PASS；它不是 M5 pass、没有 ratio、没有 SOP/tier/formal 结论。
- M5 synthetic reviewer 初审 MINOR：help 详细说明在 R0E formal enabled build 下可能不打印；已修复并 rebuild/help/maincheck PASS。
- M5 synthetic NNCL paired scaffold 已完成；mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired` 会将 synthetic raw qweight `[experts,K/8,N] int32` pack 为 NNCL `[experts,N/4,K*2] uint8`，scales 仍为 `[experts,K/128,N] half`，并把 R0H `cu_row_prefix` 转为 NNCL int64 end-prefix。
- NNCL 在该 scaffold 中只作为 public `MoeGroupGemm` baseline/reference，candidate 仍为 `R0HFusedW4A16GroupedVisitorWmmaKernel`；candidate timing 不包含 NNCL timing。
- reviewer 初审 MAJOR：paired synthetic mode 不得写 `runner_ready=true`；已修复为 `runner_ready=false`、`candidate_shape_supported=true`、`run_nncl_paired=true`，复审 PASS。
- 本地 build/help PASS；旧 M5 synthetic A/B 10 shape 回归 CSV `r0h_m5_synthetic_ab_local_after_nncl_pair_majorfix.csv` 10 行均 `precision_pass=true` 且 `runner_ready=false/nncl_paired_ready=false`。
- 本地 paired mode 在 sm120 上因 NNCL baseline 报 `[Error][MoE][GEMM Dispatch] Arch unsupported for MoE GEMM`，只生成 header-only CSV；这些文件不是数值 evidence。
- M5 true bundle/HF GPTQ preflight 已完成；mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_true_bundle_preflight` 读取 Q35-028 `moe_block` bundle、CPU top-k grouped routing surface 和 HF GPTQ raw `qweight/qzeros/scales/g_idx` guard，不启动 candidate，不调用 NNCL，不生成 ratio。
- True bundle preflight CSV `r0h_m5_true_bundle_preflight_local_after_reviewfix.csv` 10 行均 `true_bundle_ready=true`、`hf_qweight_shape_ok=true`、`hf_scales_shape_ok=true`、`hf_g_idx_default_ok=true`、`hf_qzeros_sym_ok=true`，且 `runner_ready=false/nncl_paired_ready=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false/independent_candidate=false`。
- R4 前置包已准备：`.codex/agent_group/current/agent_outputs/AUTO-20260609-138_r0h_orin1_synthetic_nncl_paired_r4_package.md`；它只覆盖 `orin_1` synthetic paired scaffold 验证命令、预计时间、输出目录和停止条件，尚未获得用户确认，未执行 `orin_1` sync/build/run/回传。
- 本轮未执行 `orin_1` sync/build、NCU 或有效 paired NNCL baseline；M2/M3/M4/M5 synthetic/scaffold 均不可作为 SOP/tier evidence 或性能结论。

执行要求：

- 必须使用 `/goal` 模式启动。
- 必须基于 agent_group 规则组织 sub-agent 执行。
- 测试目标设备固定为 `orin_1`。
- baseline 固定为 same-run NNCL `MoeGroupGemm`。
- 初级 gate：family A/B geomean ratio `<=1.50x`。
- 目标 gate：family A/B geomean ratio `<=1.20x`，同时检查 `M64/M898`。
- 不修改 production path。
- 不得把 NNCL internal `MoeFCGemm` / `MoeGroupGemmRunner` / `dispatch_moe_gemm_to_cutlass` 包装成 candidate。

Worker 编排：

- `repo-explorer`：梳理当前 spike、AUTO-114 到 AUTO-126 evidence、NNCL `MoeFCGemm` / `dq_mma_multistage_finegrained` 快路径。
- `qwen-architect`：定义 Qwen3.5 MoE W4A16 grouped GEMM 数据流和 formal 边界。
- `oss-scout`：只读对照 CUTLASS grouped GEMM、mixed-input GEMM、MoE 示例，不引入 production 依赖。
- `kernel-dev`：在 spike-only 路径实现 independent fused W4A16 mainloop。
- `orin-runner`：只在 `orin_1` 构建、运行 micro、抓 NCU，并回传日志。
- `perf-analyst`：固定 NNCL baseline 口径，解析 ratio、geomean、M64/M898、launch count、NCU 指标。
- `reviewer`：审查是否误用 NNCL kernel、是否越界为 SOP/tier、是否污染 timing。
- `main-orchestrator`：每个 milestone 后写 orchestration summary，并同步 current/memory。

Milestones：

1. M0 `/goal` 初始化与 same-run NNCL baseline 锁定。已完成。
2. M1 NNCL 快路径反向规格化，输出 `nncl_fastpath_spec.md`。已完成。
3. M2 单 expert fused W4A16 mainloop smoke。已完成，本地 synthetic smoke only。
4. M3 加入 packed B iterator + scale iterator + shared-memory pipeline，禁止全量 predecode。已完成，本地 structural smoke only。
5. M4 加入 MoE grouped problem visitor，支持 active experts 变化，candidate launch count 目标为 1。已完成，本地 structural smoke only。
6. M5 `orin_1` family A/B 10 shape full probe。preflight、synthetic A/B runner、synthetic paired scaffold 和 true bundle/HF GPTQ preflight 已完成但 runner 仍未就绪；synthetic paired scaffold 的 `orin_1` R4 package 已准备但未执行，需用户确认后先验证 synthetic paired scaffold，再补 true bundle same-run NNCL paired runner。
7. M6 NCU isolation，必须抓到 independent fused candidate kernel，不是 `MoeFCGemm`。
8. M7 formal 决策，只允许 `promote_to_formal_sop`、`continue_probe`、`reject_or_hold`。

输出守卫：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`

停止条件：

- `orin_1` 构建失败。
- candidate 输出 NaN/Inf/全零。
- NCU 抓不到 independent candidate kernel。
- NCU 只抓到 `MoeFCGemm` / `MoeGroupGemm`。
- ratio 连续两轮 `>1.50x` 且没有明确结构性改进证据。
- 需要修改 production path 才能继续。

## 已收口 Hot Epic

### Q35-MOE-CUTEDSL-R0F-R1-PROBE

状态：`done / reject_or_hold / probe-only / not production`

目标：解释 R0E formal gate fail 后的性能异常，并判断是否存在值得新建正式候选的 Tensor Core / grouped launch / W4A16 上限。

固定顺序：

1. Tensor Core sanity：M1 已在 `orin_1` sm87 通过 dense fp16 TensorOp small/hot sanity。
2. Timing hygiene：M2 已完成，但 serial dense fp16 ratio 连续两轮明显 `>1.50x`。
3. Grouped dense structural probe：M3 已完成，grouped launch 相比 serial 有收益，但相对 NNCL 仍连续明显 `>1.50x`。
4. M4-control direct MoeFC probe：已完成 warm-state hardened 验证；shape-mean family A/B direct-vs-NNCL `0.999769/1.015588`，second-pass `0.996385/0.996818`，但 direct path 是 NNCL internal control，不是 independent candidate。
5. M4 CUTLASS dispatch wrapper-isolation：已完成；绕过 NNCL public op / runner 后 full run1 family A/B `1.001874/1.032655`，run2 `0.999701/1.011785`，但仍复用 NNCL CUTLASS extension headers / `MoeFCGemm`，不是 independent candidate。
6. Candidate NCU isolation：未启动；当前没有 independent candidate kernel，不能用 NNCL internal/control path 伪造 candidate NCU evidence。
7. W4A16 feasibility/formal gate decision：M5 已完成，决策为 `reject_or_hold`；必须另起 formal candidate task 才能继续。

M2 evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m2_timing_hygiene_final.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_repeat.csv`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_orchestration.md`

M2 ratio：

- 第一轮 family A/B geomean：`13.589240x / 4.937622x`
- 第二轮 family A/B geomean：`13.388290x / 4.723811x`

M3 evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/build_grouped_dense_probe.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/r0f_m3_grouped_dense_all.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/r0f_m3_grouped_dense_all_repeat.csv`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_orchestration.md`

M3 ratio：

- 第一轮 family A/B grouped_vs_nncl geomean：`4.442753x / 4.092893x`
- 第二轮 family A/B grouped_vs_nncl geomean：`4.412637x / 4.208391x`
- 第一轮 family A/B grouped_vs_serial geomean：`0.266817x / 0.768473x`
- 第二轮 family A/B grouped_vs_serial geomean：`0.264910x / 0.753515x`

M4-control evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/report.md`
- `r0f_m4_moefc_direct_warm_hardened_all.csv`
- `r0f_m4_moefc_direct_warm_hardened_all_repeat.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/report.md`
- `dispatch_probe_summary.csv`
- `moefc_cutlass_dispatch_full_run1.csv`
- `moefc_cutlass_dispatch_full_run2.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/report.md`
- `r0f_m4_moefc_direct_all_balanced.csv`
- `r0f_m4_moefc_direct_all_balanced_repeat.csv`

M4-control ratio：

- hardened warm-state shape-mean family A/B direct-vs-NNCL geomean：`0.999769x / 1.015588x`
- hardened warm-state shape-mean family A/B second-pass geomean：`0.996385x / 0.996818x`
- hardened smoke/full/repeat 共 21 行均 `precision_pass=true/control_probe_only=true/independent_candidate=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`
- CUTLASS dispatch wrapper-isolation full run1 family A/B dispatch-vs-NNCL geomean：`1.001874x / 1.032655x`
- CUTLASS dispatch wrapper-isolation full run2 family A/B dispatch-vs-NNCL geomean：`0.999701x / 1.011785x`
- dispatch smoke/full/repeat 共 22 行均 `precision_pass=true/control_probe_only=true/independent_candidate=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`
- direct 和 dispatch probes 均是 NNCL internal/control，不可 promoted。

M5 feasibility evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/report.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_qwen-architect.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_perf-analyst.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_reviewer.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_orchestration.md`

M5 decision：

- `reject_or_hold`
- M2/M3 真正独立于 NNCL MoeFC kernel 的 dense fp16 serial/grouped paths 不达标。
- M4 direct/dispatch 接近 NNCL baseline，但都使用 NNCL internal runner/template/header/kernel，只能作为 control evidence。
- 当前没有 independent candidate kernel，因此不启动 Candidate NCU Isolation，不进入 formal/tier/R1/R3/production。
- 若继续 CuTe/CUTLASS，必须新建 `Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE` 并重新走 SOP-A/B/C；另一可选方向是 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。

R0G gap audit evidence：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_gap_audit_20260608_192510/report.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-113_r0g_independent_w4a16_gap_audit.md`
- 结论：当前没有 independent W4A16 MoeFC grouped candidate；R0G formal task 必须替换 NNCL `MoeFCGemm`、`dispatch_moe_gemm_to_cutlass`、fine-grained scale mainloop/control path 的 candidate 复用，不能只改 wrapper。

R0G smoke evidence：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/report.md`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/independent_w4a16_smoke_m64_orin1.csv`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-114_r0g_independent_w4a16_smoke_kernel-dev.md`
- 结论：`done / smoke-only / continue_probe / not formal / not tier`。CSV 固定 `candidate_uses_nncl_moefc=false`、`candidate_uses_nncl_moegroupgemm=false`、`candidate_uses_dispatch_moe_gemm_to_cutlass=false`、`candidate_uses_nncl_cutlass_extension_headers=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。ratio `6.500818x`，不能作为性能通过证据。

R0G warp probe evidence：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/report.md`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/warp_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/warp_m898_orin1.csv`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-115_r0g_independent_w4a16_warp_probe_kernel-dev.md`
- 结论：`done / probe-only / continue_probe / not formal / not tier`。warp-reduce M64 ratio `7.073074x`、M898 ratio `15.284829x`，tile8 更差已回退；当前最佳 raw independent smoke 仍远离 `<=1.20x`。下一步应做 single-launch grouped raw W4A16 kernel，仍不得 promoted。

R0G single-launch probe evidence：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/report.md`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/single_launch_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/single_launch_m898_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/single_launch_ncu_m64.csv`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-116_r0g_independent_w4a16_single_launch_probe_kernel-dev.md`
- 结论：`done / probe-only / reject_or_hold_or_continue_probe / not formal / not tier`。M64 ratio `5.671422x`，M898 ratio `9.965807x`，launches/iter 均为 `1`。NCU 抓到 `RawGptqW4A16GroupedSingleLaunchKernel`，无 `MoeFCGemm`。Single-launch 去掉 launch overhead 后仍远离 `<=1.20x`，后续需要 true independent TensorCore/int4 W4A16 grouped mainloop。

边界：

- 所有 probe 输出固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- R0F/R1-probe 不是 SOP evidence，不是 tier，不是 R1/R3/production 授权。
- 若要升级为正式候选，必须新建 formal task 并重新走 SOP-A/B/C。

参考：

- `.codex/agent_group/current/agent_outputs/AUTO-20260608-110_cutedsl_r0f_r1_probe_plan.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-111_cutedsl_r0f_cold_start_sync.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m1_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_orchestration.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/`
- `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`

## Holding / Archived Routes

### Q35-022 M-4 Marlin-MoE Spike R0

状态：`holding / tier D / archived / not production`

归档目录：

- `.codex/agent_group/archive/20260608_marlin_holding_compaction/`

完整旧热状态、任务表、Roadmap、风险和输出：

- `current.before/`
- `memory.before/`
- `agent_outputs/`
- `tools/`
- `tasks.archived.csv`

最终结论：

- SOP-A PASS：`max_abs=0.000120982528`，`rmse=4.56000724e-06`。
- SOP-B PASS：fresh Orin NCU best occupancy `33.24% > 30%`。
- SOP-C FAIL：family A/B geomean `1.155492/1.287823`，hot M898 `1.246268/1.367099`，small M64 `1.112405/1.239476`。
- reviewer 无 P0/P1 evidence blocker；qwen-architect 判定 tier D。
- 不进入 R1/R3/production；不请求 production 写入授权。

Holding 恢复条件：

- 用户明确要求重开 Marlin；或
- 旧 formal evidence 被 reviewer 判为无效；或
- 新结构性 Marlin 方案以新 task id 立项。

恢复要求：

- 不得复用 archived diagnostic 直接声明 PASS。
- 必须重新写当前任务、验收、R4 evidence 计划。
- 必须重新走 SOP-A/B/C。

### Q35-MOE-CUTEDSL-W4A16-GROUPED-R0

状态：`done / tier D / not production`

R0E formal evidence：

- `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`

结论：

- Guard：`schema_pass=true`，`status=gate_fail`，`overall_pass=false`，`tier_eligible=false`。
- SOP-A PASS，SOP-B PASS，SOP-C ratio gate FAIL。
- 不声明 SOP-C PASS、tier eligible，不进入 R1/R3/production。

Python CuTeDSL route：

- 状态：`blocked optional`
- 阻塞点：Jetson aarch64 环境缺 `cutlass._mlir` / compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
- 只有用户提供 compatible wheel 并明确要求回到 Python route 时才重跑 R0b。

## Backlog

| 优先级 | 工作项 | 状态 | 说明 |
|---|---|---|---|
| P0-closed | `Q35-MOE-CUTEDSL-R0F-R1-PROBE` | done / reject_or_hold | M5 已收口；direct/dispatch controls 说明 NNCL wrapper/runner 开销不是主因，但没有 independent candidate，不能 promoted |
| P0-option | `Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE` | todo / needs_new_formal_task / raw_simt_probe_failed | 只有用户选择继续 CuTe/CUTLASS 且接受新 formal 任务时启动；R0G gap audit 已明确禁止把 NNCL `MoeFCGemm`/`dispatch_moe_gemm_to_cutlass` 当 candidate，AUTO-116 single-launch raw SIMT 仍 `5.67x/9.97x`，必须独立实现 TensorCore/int4 W4A16 MoeFC grouped candidate，并重新走 SOP-A/B/C |
| P0-option | `Q35-MOE-NNCL-GROUPED-TARGETED-R0` | todo | NNCL grouped targeted profile + 周边优化 spike；适合在确认 NNCL internal MoeFC 已是可用上限后转向 production-adjacent 优化 |
| P4 | `Q35-MOE-BACKUP-CUTLASS-GROUPED` | todo | 泛化 CUTLASS/NNCL grouped GEMM 备线 |
| P4 | `Q35-MOE-DISPATCH-METADATA-BUILDER` | todo | 评估 align-block-size / sentinel sorted token ids |
| P4 | `Q35-MOE-FUSED-TOPK-RENORM-RECHECK` | todo | 复核历史 fastpath 是否已覆盖全融合 |
| P5 | `Q35-ATTN-FUSED-QKNORM-ROPE-KVWRITE` | todo | 评估 Q/K RMSNorm+RoPE+KV write 单 kernel |
| P5 | `Q35-GDN-DECODE-PACKED-BATCHED-FUSED` | todo | 评估 packed + batched GDN decode mega-kernel |
| P5 | `Q35-GDN-PREFILL-KKT-SOLVE-SMEM-RECHECK` | todo | 重新评估 GDN prefill chunk pipeline 结构性候选 |
| P5 | `Q35-GDN-SSM-STATE-POOL-SPEC-DECODE` | todo | serving 架构备线 |

## 已吸收基础设施

| 工作项 | 状态 | 结论 |
|---|---|---|
| `AG-INFRA` | done | agent_group 共享记忆、worker registry、routing policy、Orin runbook 已建立 |
| `Q35-ANCHOR` | done | 当前 production anchor 固定为 `aaf6747` |
| `Q35-028` | done | MoE bundle export 已合入，支持后续 replay/spike |
| `Q35-026` | done | GDN hygiene：`ex2.approx.f32` + bf16 rtne 已成为 anchor |
