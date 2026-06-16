# Current State

最后更新：2026-06-09

## 冷启动入口

下次 agent_group 冷启动后，必须继续 **`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`**，当前恢复点是 `in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / M5 true bundle runner scaffold done / local NNCL sm120 blocked / true-bundle timed paired runner pending / orin_1 synthetic paired R4 pending / orin_1_only / spike_only / not_formal`。不要重复 M0/M1/M2/M3/M4，也不要把 M5 preflight、M5 synthetic runner、true-bundle preflight、true-bundle runner scaffold 或本地 header-only paired CSV 误认为正式 M5 full probe；也不要回到 R0F/R1 或 R0G raw CUDA/WMMA 局部参数 probe。R0H 已在 `/goal` 模式下启动，目标仍为：

```text
/goal Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP: make current repo CuteDSL/CUTLASS spike performance align with same-run NNCL MoeGroupGemm on orin_1 by building an independent fused W4A16 int4-dequant + scale-iterator + grouped-mainloop pipeline
```

固定执行边界：

- 基于 agent_group 规则组织 sub-agent 执行，由 main-orchestrator 编排，不直接把计划当单 agent 私改。
- 测试目标设备固定为 `orin_1`，性能结论不得切换到 `orin_cv`、本地 GPU 或其他平台。
- baseline 固定为 same-run NNCL `MoeGroupGemm`，ratio=`candidate_ms/nncl_ms`。
- 初级目标 family A/B geomean ratio `<=1.50x`，最终目标 `<=1.20x`，同时检查 hot `M898` 与 small `M64`。
- 不修改 production Qwen3.5 推理路径；所有实现先限于 spike、analysis 和 agent_group 记忆。
- 不得把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 包装成 candidate。

必须先读：

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
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-139_r0h_m5_true_bundle_runner_scaffold.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/current/epic.md`
- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/TASK_LEDGER.md`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `third_party/nncl/nncl/csrc/cuda/kernel/cutlass_kernels/moe_group_gemm/moe_cutlass_group_gemm_template.h`
- `third_party/nncl/nncl/csrc/cuda/include/cutlass_extensions/gemm/kernel/moe_cutlass_kernel.h`
- `third_party/nncl/nncl/csrc/cuda/include/cutlass_extensions/gemm/threadblock/dq_mma_multistage_finegrained.h`

R0F/R1-probe 已完成 feasibility decision：`reject_or_hold / probe-only / not production`。AUTO-126 后 raw CUDA/WMMA 局部参数 probe 也应停止；下一步不是继续调 `threshold/warps/cols`，而是实现 true independent fused GPTQ W4A16 grouped mainloop。

补充：R0G gap audit 后已新增 raw W4A16 smoke/probe。`routed_grouped_independent_w4a16_smoke` 最初 M64 ratio 为 `6.500818x`；warp-reduce M64/M898 为 `7.073074x / 15.284829x`；`routed_grouped_independent_w4a16_single_launch_smoke` 将 launch 数降到 1 后 M64/M898 仍为 `5.671422x / 9.965807x`；`routed_grouped_independent_w4a16_wmma_smoke` 用 WMMA Tensor Core 后，4-warp M64/M898 为 `16.375158x / 5.751521x`（M64 same-run NNCL baseline 明显偏低，按前序 baseline 估算仍约 `4.6x`），M898 candidate 从 `14.064703 ms` 降到 `5.281041 ms`；`routed_grouped_independent_w4a16_predecode_wmma_smoke` 将 raw decode 移出 timed loop 后 M64/M898 ratio 仍为 `7.516270x / 12.185688x`；shared-A WMMA 将 M64/M898 ratio 改为 `4.372321x / 4.353763x`；AUTO-120 hybrid small-row threshold=4 将 M64/M898 ratio 进一步改为 `3.902625x / 3.444739x`，两 shape geomean `3.666541x`；AUTO-121 threshold sweep 覆盖 threshold `1/2/4/8/12/15`，最佳 common threshold 为 `2`、geomean `3.309147x`，最佳 M64 threshold=12 ratio `2.565185x`，最佳 M898 threshold=4 ratio `3.281669x`；AUTO-122 在 threshold `2/4` 上测试 `wmma_n_warps=8/16`，最佳 common 组合 threshold=2、warps=8，M64/M898 ratio `2.967751x / 3.150822x`、geomean `3.057917x`；AUTO-123 新增 `wmma_packed_loader=1`，最佳 common 组合 threshold=2、warps=8、packed=1，M64/M898 ratio `2.665852x / 2.327368x`、geomean `2.490867x`，相对 AUTO-122 改善约 `18.7%`；AUTO-124 新增 `hybrid_single_kernel=1`，同 build 对照把 launch 数从 2 降到 1，M64/M898 ratio `2.297688x / 2.704718x`、geomean `2.492910x`，相对双 kernel control 有 M64 `1.278698x`、M898 `1.146003x` speedup；AUTO-125 在 single-kernel+packed loader 下扫描 threshold/warps，最佳 common 组合为 threshold=1、warps=16，M64/M898 ratio `2.548206x / 1.866342x`、geomean `2.180785x`；AUTO-126 新增 `small_row_cols_per_warp=4/8/16` 小行 SIMT 列粒度 probe，最佳 `cols=8` 的 M64/M898 ratio 为 `2.112438x / 2.273437x`、geomean `2.191459x`，相比 same-build `cols=4` 仅改善约 `0.8%` 且 M64 退化。这些结果比早期 raw/WMMA probe 有改善但仍远离 `<=1.20x`。NCU 已确认抓到 `RawGptqW4A16GroupedSingleLaunchKernel` 与 `RawGptqW4A16GroupedWmmaKernel`，而不是 NNCL `MoeFCGemm`。这些结果只证明 raw HF GPTQ decode+matmul correctness、launch overhead、naive Tensor Core 化、decode-only 归因、shared-A reuse、小行 hybrid、WMMA N-tile 调参、packed-loader 读放大、hybrid single-kernel launch fusion 和 small-row SIMT 列粒度归因，不是 optimized candidate，不是 formal，不可进入 SOP/tier。AUTO-126 精度和 guard 通过但仍明显 `>1.50x` 且不达 `<=1.20x`。下一步应停止局部参数微调；若要继续，应做真正 fused mainloop 结构验证；若要 formal，应实现 true independent CUTLASS-style fused GPTQ W4A16 grouped mainloop，或转向 NNCL targeted R0。

历史 probe 参考可按需读取：

- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/current/epic.md`
- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-110_cutedsl_r0f_r1_probe_plan.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-111_cutedsl_r0f_cold_start_sync.md`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-114_r0g_independent_w4a16_smoke_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-115_r0g_independent_w4a16_warp_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-116_r0g_independent_w4a16_single_launch_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-117_r0g_independent_w4a16_wmma_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-118_r0g_predecode_wmma_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-119_r0g_wmma_shared_a_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-120_r0g_hybrid_smallrow_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-122_r0g_wmma_nwarps_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-123_r0g_wmma_packed_loader_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-124_r0g_hybrid_single_kernel_probe_kernel-dev.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-125_r0g_hybrid_single_kernel_sweep_perf-analyst.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-126_r0g_smallrow_cols_probe_kernel-dev.md`

可按需读取：

- R0G hybrid small-row evidence：`analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/`
- R0G threshold sweep evidence：`analysis/Qwen35_cutedsl_r0g_hybrid_threshold_sweep_20260608_121/`
- R0G WMMA N-warps evidence：`analysis/Qwen35_cutedsl_r0g_wmma_nwarps_probe_20260608_122/`
- R0G WMMA packed loader evidence：`analysis/Qwen35_cutedsl_r0g_wmma_packed_loader_probe_20260609_123/`
- R0G hybrid single-kernel evidence：`analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_probe_20260609_124/`
- R0G hybrid single-kernel sweep evidence：`analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_sweep_20260609_125/`
- R0G small-row cols evidence：`analysis/Qwen35_cutedsl_r0g_smallrow_cols_probe_20260609_126/`
- R0G smoke evidence：`analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/`
- R0E formal failure evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`
- R0D1 diagnostic evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d1_nncl_paired_orin_1_20260608_083804/`
- CuTe/CUTLASS C++ smoke evidence：`analysis/Qwen35_cutedsl_cute_cpp_smoke_orin_1_20260608_021956/`

不要把以下内容作为冷启动主线：

- `Q35-022 M-4 Marlin-MoE Spike R0`
- Marlin SOP-C v12/v13/v14/v16 candidate-only 参数线
- CuTe/CUTLASS R0E formal 重跑
- R0c/R0d/R0D1 diagnostic 重跑
- Python CuTeDSL `_mlir` blocker closure

## 当前主线

当前 hot epic：**CuTe/CUTLASS R0H fused W4A16 mainloop 已在 `/goal` 模式启动，M0-M4 local structural smoke done，M5 preflight done，M5 synthetic A/B runner done，M5 synthetic NNCL paired scaffold implemented，M5 true bundle/HF GPTQ preflight done，M5 true-bundle runner scaffold done，本地 sm120 NNCL baseline blocked；下一步是在 orin_1 验证 synthetic paired scaffold，并补 true-bundle timed same-run NNCL paired runner 后再进入 R4-gated family probe**

任务编号：`Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`

状态：`in_progress / M0-M4 local structural smoke done / M5 preflight done / M5 synthetic A/B runner done / M5 synthetic NNCL paired scaffold implemented / M5 true bundle HF GPTQ preflight done / M5 true bundle runner scaffold done / local NNCL sm120 blocked / true-bundle timed paired runner pending / orin_1 synthetic paired R4 pending / orin_1_only / spike_only / not_formal`

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
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-139_r0h_m5_true_bundle_runner_scaffold.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/m0_goal_baseline_lock.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/nncl_fastpath_spec.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m2_single_expert_smoke_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local_rerun.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m3_packed_scale_pipeline_smoke_local_notes.md`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_maincheck.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_m128.csv`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_20260609_071108/r0h_m4_grouped_visitor_smoke_local_notes.md`
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

- M0：`/goal` 初始化、worker 编排、same-run NNCL `MoeGroupGemm` baseline 口径、R3/R4 边界和停止条件已锁定。
- M1：NNCL W4A16 MoE grouped fastpath 已反向规格化为 R0H candidate 约束。
- M2：single expert `gate_proj` `K=2048,N=512,group_size=128` fused W4A16 WMMA smoke 已完成；本地 build PASS，本地 synthetic smoke PASS，reviewer PASS。
- M2 CSV 固定 `nncl_ms=NA`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- M3：packed B iterator + scale iterator + shared-memory pipeline structural smoke 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_packed_scale_pipeline_smoke`，candidate kernel 为 `R0HFusedW4A16PackedScalePipelineWmmaKernel`。
- M3 范围仍为 single expert、`gate_proj`、`K=2048,N=512,group_size=128`、synthetic HF raw GPTQ input；qweight tile 与 scale tile 均 staged 到 shared buffer，dequant 在 WMMA tile/mainloop 内完成；无 full `dense_B_fp16` predecode，`candidate_launches_per_iter=1`。
- M3 本地 build PASS，本地 synthetic smoke PASS，rerun PASS；最新 CSV：`candidate_ms=0.213408`、`reference_ms=0.059072`、`max_abs=3.05548310e-05`、`rmse=7.99963300e-06`、`finite=true`、`nonzero=32768`、`precision_pass=true`、`nncl_ms=NA`。
- reviewer 初审 `MINOR`：缺少精确 token `paired_nncl_baseline_pending`；已在 `spike_common.h` notes 中补齐并 rebuild/rerun PASS。
- M4：MoE grouped problem visitor structural smoke 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_smoke`，candidate kernel 为 `R0HFusedW4A16GroupedVisitorWmmaKernel`。
- M4 使用 `cu_row_prefix` / `padded_cu_row_prefix` 将 padded tile row 映射到 expert slot/local row，并用 compact `cu_row_prefix` 写回 routed grouped output；不是 single expert flatten。
- M4 主 CSV：`active_experts=4`、`expert_row_counts=7|13|19|25`、`cu_row_prefix=0|7|20|39|64`、`padded_cu_row_prefix=0|16|32|64|96`、`candidate_launches_per_iter=1`、`grouped_problem_visitor=true`、`cu_row_prefix_visitor=true`、`precision_pass=true`、`nncl_ms=NA`。
- M4 local M sweep 补充：`M=64/128/256/512/898` 均为 synthetic `gate_proj K=2048,N=512` structural smoke PASS，均 `precision_pass=true`、`candidate_launches_per_iter=1`、`nncl_ms=NA`；CSV 为 `r0h_m4_grouped_visitor_smoke_local{,_m128,_m256,_m512,_m898}.csv`。
- M4 main-orchestrator 本地复跑 PASS：`r0h_m4_grouped_visitor_smoke_local_maincheck.csv`，`candidate_ms=0.430688`、`reference_ms=0.060992`、`max_abs=3.055483e-05`、`rmse=8.044639e-06`、`precision_pass=true`。
- reviewer 审查 M4 结论 PASS：新 mode 接入 help/parse/dispatch/CMake；candidate 文件未 include/call/wrap NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 `cutlass_extensions` fastpath。
- explorer 审查 M5 结论为 `needs_local_runner_work`：当前 M4 固定 `gate_proj K=2048,N=512`，不支持 family B `down_proj K=512,N=2048`，且没有 same-run NNCL baseline；不能直接作为 `orin_1` family A/B 10 shape M5 runner。
- M5 preflight/scaffold 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_preflight`，枚举 family A/B 10 shape 并 fail-closed 写出 runner 缺口。
- M5 synthetic A/B structural runner 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic`，覆盖 A/B 10 shape，A 族 `gate_proj K=2048,N=512` 与 B 族 `down_proj K=512,N=2048` 均 precision PASS。
- R0H grouped visitor kernel/host path 已从固定 `K=2048,N=512,gate_proj` 参数化到 `problem.k/problem.n/problem.projection`；host buffer、pointer stride、grid.x、K loop、A/qweight/scales/D stride 均使用运行时 K/N。
- M5 synthetic CSV 所有行均 `precision_pass=true`、`runner_ready=false`、`candidate_shape_supported=true`、`nncl_paired_ready=false`、`nncl_ms=NA`、`candidate_vs_nncl_ratio=NA`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- 更新后的 M5 preflight CSV 覆盖 A/B 10 shape；A/B 族均 `candidate_shape_supported=true` 但 reason 均包含 `same_run_NNCL_baseline_missing`；B 族 reason 已为 `family_B_down_proj_K512_N2048_has_R0H_M5_synthetic_structural_runner`。
- M5 preflight 本地 build PASS、main-orchestrator 复跑 PASS、reviewer PASS；它没有启动 candidate kernel、没有 NNCL ratio、不是 M5 pass、不是 SOP/tier/formal evidence。
- M5 synthetic reviewer 初审 MINOR：help 详细说明在 R0E formal enabled build 下可能不打印；已修复并 rebuild/help/maincheck PASS。
- M5 synthetic NNCL paired scaffold 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired`，将 synthetic raw qweight `[experts,K/8,N] int32` pack 为 NNCL `[experts,N/4,K*2] uint8`，scales 仍为 `[experts,K/128,N] half`，NNCL `cu_row` 转为 int64 end-prefix、不含起始 0。
- 该 paired scaffold 中 NNCL 只作为 public `MoeGroupGemm<half, half, QuantMethod::kGPTQFp16Int4Groupwise>` baseline/reference；candidate 仍是 `R0HFusedW4A16GroupedVisitorWmmaKernel`，candidate timing 不包含 NNCL timing。
- reviewer 初审 MAJOR：paired synthetic mode 不得写 `runner_ready=true`；已修复为 `runner_ready=false`、`candidate_shape_supported=true`、`run_nncl_paired=true`，汇总日志为 `runner_ready=false nncl_paired_ready=true`；复审 PASS。
- 本地 build/help PASS；旧 M5 synthetic A/B 10 shape 回归 CSV `r0h_m5_synthetic_ab_local_after_nncl_pair_majorfix.csv` 10 行均 `precision_pass=true` 且 `runner_ready=false/nncl_paired_ready=false`。
- 本地 paired mode 在 sm120 上因 NNCL baseline 报 `[Error][MoE][GEMM Dispatch] Arch unsupported for MoE GEMM`，只生成 header-only CSV；这些文件不是数值 evidence。
- M5 true bundle/HF GPTQ preflight 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_true_bundle_preflight`，读取 Q35-028 `moe_block` bundle、CPU top-k grouped routing surface 和 HF GPTQ raw `qweight/qzeros/scales/g_idx` guard，不启动 candidate，不调用 NNCL，不生成 ratio。
- True bundle preflight CSV `r0h_m5_true_bundle_preflight_local_after_reviewfix.csv` 10 行均 `true_bundle_ready=true`、`hf_qweight_shape_ok=true`、`hf_scales_shape_ok=true`、`hf_g_idx_default_ok=true`、`hf_qzeros_sym_ok=true`，且 `runner_ready=false/nncl_paired_ready=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false/independent_candidate=false`。
- M5 true-bundle runner scaffold 已完成；新增 mode `routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_true_bundle_runner_scaffold`，展开 true bundle 的 `grouped_source_rows/grouped_routed_rows`、`cu_row_prefix`、`padded_cu_row_prefix`、NNCL-style `cu_row_end_prefix` 和 active experts 的 HF GPTQ raw guard。该 mode 不启动 candidate，不调用 NNCL，不生成 ratio，固定 `runner_ready=false/candidate_timed=false/nncl_paired_ready=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false/independent_candidate=false`。
- Runner scaffold CSV `r0h_m5_true_bundle_runner_scaffold_all_local_after_reviewfix.csv` 覆盖 A/B 10 shape；所有行 `bundle_hf_guard_ready=true`、`projection_input_plan_ready=true`；A 族 5 行 `true_bundle_ready=true/projection_input_materialized=true`；B 族 5 行 `true_bundle_ready=false/projection_input_materialized=false`，明确等待 `silu(gate)*up` 输入物化，避免被误读为可 timed run。
- R4 前置包已准备：`.codex/agent_group/current/agent_outputs/AUTO-20260609-138_r0h_orin1_synthetic_nncl_paired_r4_package.md`；它只覆盖 `orin_1` synthetic paired scaffold 验证命令、预计时间、输出目录和停止条件，尚未获得用户确认，未执行 `orin_1` sync/build/run/回传。
- 本轮未执行 `orin_1` sync/build、NCU 或有效 paired NNCL baseline；M2/M3/M4/M5 synthetic/scaffold 均不可作为 SOP/tier evidence 或性能结论。

建议写入范围：

- `samples/micro_bench/spike/cute_dsl/`
- `samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/`
- `analysis/Qwen35_cutedsl_r0h_fused_w4a16_<TS>/`
- `.codex/agent_group/`
- 必要的 spike `CMakeLists.txt` 接入

禁止：

- 修改 production Qwen3.5 推理路径。
- 把 NNCL `MoeFCGemm` / `MoeGroupGemmRunner` / `dispatch_moe_gemm_to_cutlass` 包装成 candidate。
- 使用非 `orin_1` 平台生成性能结论。

R0H milestones：

1. M0：`/goal` 初始化与 same-run NNCL baseline 锁定。已完成。
2. M1：NNCL 快路径反向规格化，输出 `nncl_fastpath_spec.md`。已完成。
3. M2：单 expert fused W4A16 mainloop smoke。已完成，本地 synthetic smoke only。
4. M3：加入 packed B iterator + scale iterator + shared-memory pipeline，禁止全量 predecode。已完成，本地 structural smoke only。
5. M4：加入 MoE grouped problem visitor，支持 active experts 变化，candidate launch count 目标为 1。已完成，本地 structural smoke only。
6. M5：`orin_1` family A/B 10 shape full probe。preflight、synthetic A/B runner、synthetic NNCL paired scaffold、true bundle/HF GPTQ preflight 与 true-bundle runner scaffold 已完成但仍显示 `runner_ready=false`；synthetic paired scaffold 的 `orin_1` R4 package 已准备但未执行，需用户确认后先验证 paired scaffold，再补齐 true-bundle timed same-run NNCL paired runner。
7. M6：NCU isolation，必须抓到 independent fused candidate kernel，不是 `MoeFCGemm`。
8. M7：formal 决策，只允许 `promote_to_formal_sop`、`continue_probe`、`reject_or_hold`。

R0H 初始 probe 输出默认固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `candidate_audit_pending=true`

R0H 停止条件：

- `orin_1` 构建失败。
- candidate 输出 NaN/Inf/全零。
- NCU 抓不到 independent candidate kernel。
- NCU 只抓到 `MoeFCGemm` / `MoeGroupGemm`。
- ratio 连续两轮 `>1.50x` 且没有明确结构性改进证据。
- 需要修改 production path 才能继续。

## 已收口主线：R0F/R1-probe

任务编号：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

状态：`done / reject_or_hold / probe-only / not production`

本轮 `/goal` 已启动，M0 已锁定一次性授权范围、停止条件和 same-run NNCL baseline 口径。M1 已完成 Tensor Core dense fp16 sanity。M2 Timing hygiene 已完成并构建通过，paired timed loop 已标记 `timing_contaminated=false`，但 serial dense fp16 ratio 连续明显 `>1.50x`。M3 grouped dense fp16 single-projection probe 证明 grouped launch 相比 serial per-expert launch 有明确收益，但相对 same-run NNCL baseline 两轮仍明显 `>1.50x`。M4-control 先证明 NNCL internal MoeFC runner 与 public NNCL 同量级，随后完成 CUTLASS dispatch wrapper-isolation；但 direct/dispatch paths 都复用 NNCL internal runner/template/header/kernel，不是 independent candidate。M5 feasibility 决策为 `reject_or_hold`：当前 R0F/R1-probe 不 promoted，不启动 Candidate NCU Isolation，不进入 formal/tier/production。M0/M1/M2/M3/M4/M5 输出：

- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m0_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m1_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m2_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m3_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_control_warm_hardened_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m4_cutlass_dispatch_orchestration.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260608-112_m5_feasibility_orchestration.md`

M1 关键 evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m1_epilogue_scalar.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m1_shape_bench_m64.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m1_shape_bench_m898.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m1_r0e_disabled_check.log`

M2 关键 evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m2_timing_hygiene_final.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_repeat.csv`

M2 ratio 结论：

- 第一轮 family A/B geomean：`13.589240x / 4.937622x`
- 第二轮 family A/B geomean：`13.388290x / 4.723811x`
- hot `M898`：A `19.271764x / 19.291392x`，B `4.545278x / 4.080901x`
- small `M64`：A `5.753436x / 5.793069x`，B `6.726412x / 7.163632x`

M3 关键 evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/build_grouped_dense_probe.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/r0f_m3_grouped_dense_all.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/r0f_m3_grouped_dense_all_repeat.csv`

M3 ratio 结论：

- 第一轮 family A/B grouped_vs_nncl geomean：`4.442753x / 4.092893x`
- 第二轮 family A/B grouped_vs_nncl geomean：`4.412637x / 4.208391x`
- 第一轮 family A/B grouped_vs_serial geomean：`0.266817x / 0.768473x`
- 第二轮 family A/B grouped_vs_serial geomean：`0.264910x / 0.753515x`
- repeat hot `M898`：A `3.798590x`，B `3.878818x`
- repeat small `M64`：A `5.460091x`，B `3.447001x`


M4-control 关键 evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/r0f_m4_moefc_direct_warm_hardened_all.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/r0f_m4_moefc_direct_warm_hardened_all_repeat.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/dispatch_probe_summary.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/moefc_cutlass_dispatch_full_run1.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/moefc_cutlass_dispatch_full_run2.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/r0f_m4_moefc_direct_all_balanced.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/r0f_m4_moefc_direct_all_balanced_repeat.csv`

M4-control ratio 结论：

- hardened warm-state shape-mean family A/B direct-vs-NNCL geomean：`0.999769x / 1.015588x`
- hardened warm-state shape-mean family A/B second-pass geomean：`0.996385x / 0.996818x`
- hardened smoke/full/repeat 共 21 条 CSV 数据行均 `precision_pass=true`、`control_probe_only=true`、`independent_candidate=false`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`
- CUTLASS dispatch wrapper-isolation full run1 family A/B dispatch-vs-NNCL geomean：`1.001874x / 1.032655x`
- CUTLASS dispatch wrapper-isolation full run2 family A/B dispatch-vs-NNCL geomean：`0.999701x / 1.011785x`
- dispatch smoke/full/repeat 共 22 条 CSV 数据行均 `precision_pass=true`、`control_probe_only=true`、`independent_candidate=false`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`
- direct 与 dispatch paths 均是 NNCL internal/control evidence，不是 independent candidate，因此不能 formal promotion。

M5 feasibility evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/report.md`
- 决策：`reject_or_hold`
- 原因：M2/M3 真正独立于 NNCL MoeFC kernel 的 dense fp16 serial/grouped paths 不达标；M4 direct/dispatch 接近 NNCL 但都是 NNCL internal/control path；当前没有 independent candidate kernel。
- 不启动 Candidate NCU Isolation；不进入 formal/tier/R1/R3/production。

下一步不是继续 dense fp16 grouped candidate，也不是 promoted 当前 dispatch probe。若要继续 CuTe/CUTLASS，必须新建真正 independent fused GPTQ W4A16 MoeFC grouped formal candidate task；或转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。

R0G smoke 补充：

- 新增 mode：`routed_grouped_independent_w4a16_smoke`
- Evidence：`analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/report.md`
- `orin_1` M64/gate_proj：`candidate_ms=32.292320`，`nncl_ms=4.967424`，`candidate_vs_nncl_ratio=6.500818`，`precision_pass=true`
- CSV 字段固定 `candidate_uses_nncl_moefc=false`、`candidate_uses_nncl_moegroupgemm=false`、`candidate_uses_dispatch_moe_gemm_to_cutlass=false`、`candidate_uses_nncl_cutlass_extension_headers=false`、`independent_candidate=false`、`candidate_audit_pending=true`、`valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`
- 结论：`done / smoke-only / continue_probe / not formal / not tier`；不得 promoted。若继续 R0G，必须实现 independent grouped/TensorCore W4A16 mainloop 并新建 formal candidate task。

R0G warp probe 补充：

- Evidence：`analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/report.md`
- `orin_1` M64/gate_proj：`candidate_ms=3.442426`，`nncl_ms=0.486694`，`candidate_vs_nncl_ratio=7.073074`，`candidate_launches_per_iter=37`，`precision_pass=true`
- `orin_1` M898/gate_proj：`candidate_ms=21.543930`，`nncl_ms=1.409498`，`candidate_vs_nncl_ratio=15.284829`，`candidate_launches_per_iter=117`，`precision_pass=true`
- tile8 warp kernel 试验更差，M64 ratio 约 `12.493918x`，M898 ratio 约 `15.895572x`，已回退。
- 结论：`done / probe-only / not formal / continue_probe`；当前最佳 raw independent smoke 仍远离 `<=1.20x`。下一步应做 spike-local single-launch grouped raw W4A16 kernel，把 launch overhead 与 raw SIMT decode/matmul 算力差距分离。

R0G single-launch probe 补充：

- 新增 mode：`routed_grouped_independent_w4a16_single_launch_smoke`
- Evidence：`analysis/Qwen35_cutedsl_r0g_independent_w4a16_single_launch_probe_20260608_116/report.md`
- `orin_1` M64/gate_proj：`candidate_ms=2.766093`，`nncl_ms=0.487725`，ratio `5.671422`，`candidate_launches_per_iter=1`，`precision_pass=true`
- `orin_1` M898/gate_proj：`candidate_ms=14.064703`，`nncl_ms=1.411296`，ratio `9.965807`，`candidate_launches_per_iter=1`，`precision_pass=true`
- NCU candidate isolation：filter `RawGptqW4A16GroupedSingleLaunchKernel`，captured kernel 为 `unnamed>::RawGptqW4A16GroupedSingleLaunchKernel(...)`，duration `716864/712704 ns`，achieved occupancy `97.82/97.80%`，未看到 `MoeFCGemm`。
- 结论：`done / probe-only / not formal / reject_or_hold_or_continue_probe`；single-launch 去除了 per-active-expert launch overhead，但 raw SIMT decode/matmul 仍远离 `<=1.20x`。不能 promoted；后续若继续必须做 true independent TensorCore/int4 W4A16 grouped mainloop。

R0F/R1-probe 固定顺序：

1. Tensor Core sanity。
2. Timing hygiene：移除 timed loop 内同步、临时分配、layout copy 和 host/device roundtrip，预分配 A/B/C/workspace。
3. Grouped dense structural probe：M3 已验证 grouped dense fp16 降低 serial launch overhead，但相对 NNCL 仍不达标。
4. M4-control direct MoeFC probe：已完成 hardened warm-state 验证，用 NNCL internal runner 证明 W4A16 MoeFC grouped 与 public NNCL 同量级；该证据不是 independent candidate。
5. M4 CUTLASS dispatch wrapper-isolation：已完成，绕过 NNCL public op 和 runner 后仍与 NNCL baseline 同量级；该证据仍复用 NNCL CUTLASS extension headers / `MoeFCGemm`，不是 independent candidate。
6. Candidate NCU isolation：当前未启动；若未来恢复，必须证明 NCU 抓到 independent candidate kernel，而不是 NNCL baseline `MoeFCGemm`。
7. W4A16 feasibility：只有另起 independent fused GPTQ W4A16 decode+matmul/grouped candidate 后，才评估 formal。
8. Formal gate：若要升级为正式候选，必须新建 formal 任务并重新走 SOP-A/B/C；不得复用 R0E tier 或 diagnostic probe 数据。

## 已归档或 Holding 路线

`Q35-022 M-4 Marlin-MoE Spike R0` 已压缩并归档到：

- `.codex/agent_group/archive/20260608_marlin_holding_compaction/`

状态：`holding / tier D / archived / not production`

结论：

- SOP-A PASS：`max_abs=0.000120982528`，`rmse=4.56000724e-06`。
- SOP-B PASS：fresh Orin NCU best occupancy `33.24% > 30%`。
- SOP-C FAIL：family A/B geomean `1.155492/1.287823`，hot M898 `1.246268/1.367099`，small M64 `1.112405/1.239476`。
- reviewer 无 P0/P1 evidence blocker，但 qwen-architect 判定 tier D。
- 不允许进入 R1/R3/production；除非用户明确重开 Marlin，否则不得恢复 Marlin 参数线或 candidate-only runner。

`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 已完成 R0E formal 并归档为 `done / tier D / not production`：

- Evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`
- Guard：`schema_pass=true`，`status=gate_fail`，`overall_pass=false`，`tier_eligible=false`。
- SOP-A PASS，SOP-B PASS，SOP-C ratio gate FAIL。
- 不允许声明 SOP-C PASS、tier eligible，不允许进入 R1/R3/production。

Python CuTeDSL route 仍是 optional blocker：

- 阻塞点：`No module named cutlass._mlir`，当前 container pip indexes 找不到 `nvidia-cutlass-dsl==4.5.0.dev0`。
- 只有用户提供 compatible Jetson aarch64 wheel 并明确要求回到 Python route 时，才重跑 R0b。

## 当前边界

- R0F/R1-probe 是 diagnostic/probe-only，不是 SOP evidence。
- 所有 probe CSV/log 默认 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- 修改 CUDA/CUTLASS/CMake 前属于 R3，需明确写入范围。
- 启动 Orin 构建、NCU 或长任务前属于 R4，需用户确认命令、预计耗时、输出目录和停止条件。
- 不得修改 production Qwen3.5 推理路径，除非用户明确授权 R3 production 写入。

## Repo Snapshot

- repo：`/workspace/liyang/lape_a6d6bfb9`
- 分支：`qwen35_moe_perf`
- production anchor：`aaf6747 perf(qwen35-gdn): inline fast_expf via ex2.approx.f32 + bf16 rtne`
- anchor 性能：MoE 3004 5 轮 cross-confirm median `TTFT=1071.21 ms / p-ntokens/s=2804.31`
- 目标：`inputLen=2500` 纯文本 prefill 达 `3000 tok/s`
