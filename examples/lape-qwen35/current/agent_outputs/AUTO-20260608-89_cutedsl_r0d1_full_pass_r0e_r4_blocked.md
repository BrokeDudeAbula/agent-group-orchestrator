# AUTO-20260608-89 CuTe/CUTLASS R0D1 full PASS, R0E R4 blocked

## 结论

- `Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC` 可标记为 `done / diagnostic-only`。
- R0D1 full 10 shape 在 `orin_1` PASS，且 reviewer full-evidence 复核无 P0/P1。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍保持 `blocked / gated`，当前只缺用户 R4 formal 确认，不能自动启动。
- R0D1 不是 SOP-A/SOP-C/tier evidence；`cutedsl_ms`、`nncl_ms` 和 `ratio` 只能作为 same-run diagnostic timing。

## Evidence

- evidence 目录：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d1_nncl_paired_orin_1_20260608_083804/`
- report：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d1_nncl_paired_orin_1_20260608_083804/report.md`
- full CSV：`r0d1_full.csv`
- full log：`r0d1_full.log`
- gate checker：`r0d1_gate_check.{md,json,txt}`
- M64 smoke：`r0d1_m64_smoke.{csv,log}`
- build evidence：`configure.log`、`build.log`、`manifest.csv`、`manifest.log`

## Full Command

```text
--mode=routed_grouped_micro_nncl_paired --m_filter=0 --warmup=5 --iters=50
```

## Gate Result

- rows：10
- expected rows：10
- required fields：PASS
- shape set：PASS
- all rows：PASS
- gate_pass：true
- shape coverage：
  - family A：`M={64,128,256,512,898}, K=2048, N=512, projection=gate_proj`
  - family B：`M={64,128,256,512,898}, K=512, N=2048, projection=down_proj`
- `topk_policy=nncl_softmax_topk`
- `source_row_policy=token_major_source_row_for_replay`
- `nncl_source_row_mismatch=0`
- `baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`
- `reference_backend=nncl_grouped_moe_group_gemm`
- `reference_source=same_run_nncl_grouped_baseline`
- `max_abs<5e-3`
- `rmse<1e-3`
- NaN/Inf = 0
- nonzero > 0
- `precision_pass=true`
- `qzeros_sym_ok=true`
- `g_idx_default_ok=true`
- `weight_source_layout=hf_gptq_raw`
- `marlin_packed_layout_used=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Reviewer

- sub-agent：`019ea672-0d9b-7213-b54f-745841804df6`
- 结论：R0D1 full 10 shape 满足 `done / diagnostic-only`，未看到 P0/P1 blocker。
- R0E 仍不能直接启动；必须等待用户 R4 确认 formal 命令、预计耗时、输出目录和停止条件。

## R0E Status

R0D1 已关闭 NNCL top-k 与 same-run NNCL paired baseline 的 diagnostic blocker。R0E formal SOP-A/B/C 仍需：

- 用户 R4 确认 formal 命令口径；
- 用户 R4 确认预计耗时；
- 用户 R4 确认输出目录；
- 用户 R4 确认停止条件。

R0E formal package 仍必须复用 Q35-022 SOP-A/B/C gate，并生成 `sop_a_precision.csv`、`sop_b_ncu_summary.csv`、`sop_c_routed_grouped.csv`、`r0_guard_report.md`、`r0_verdict.json`。
