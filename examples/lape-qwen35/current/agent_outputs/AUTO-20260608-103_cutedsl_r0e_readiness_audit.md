# AUTO-20260608-103 CuTe/CUTLASS R0E readiness audit

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：本地 readiness 审计；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- R0 design/update report 已存在：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d_design_20260608/design_update.md`。
- R0D routed grouped micro 已有 `orin_1` 10 shape diagnostic evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d_orin_1_20260608_074156/routed_grouped_micro.csv`。
- R0D1 same-run NNCL paired diagnostic 已有 `orin_1` full 10 shape evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d1_nncl_paired_orin_1_20260608_083804/r0d1_full.csv`。
- R0D/R0D1 CSV 均固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`，不能作为 R0E formal SOP/tier evidence。
- R0E 本地 readiness 通过：scripts py_compile、synthetic guard、runner generation/token 检查、local build 均 PASS。
- R0E 仍为 `blocked / gated`：缺用户 R4 formal 确认、`orin_1` formal execution、真实 SOP-B NCU、full 10 shape SOP-C formal CSV、remote guard/verdict 和 reviewer remote evidence 复核。

## 本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py --output /tmp/q35_cutedsl_r0e_runner_check.sh --timestamp CHECK` PASS。
- Runner token 检查 PASS：
  - `CUTEDSL_R0E_R4_CONFIRMED`
  - `r0e_sop_a_precision`
  - `r0e_sop_b_occupancy`
  - `r0e_sop_c_routed_grouped`
  - `ncu --target-processes`
  - `cutedsl_r0e_ncu_summary.py`
  - `r0e_run_manifest.csv`
  - `binary.sha256`
  - `help.sha256`
  - `r0e_evidence.sha256`
  - `r0e_sop_b_ncu_summary.rc`
- `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4` PASS。

## Evidence boundary

- R0D CSV：`mode=routed_grouped_micro`、`schema_version=routed_grouped_micro_v1`、`topk_policy=torch_softmax_topk_r0d_diagnostic`、`baseline_source=formal_sopc_csv_join_not_paired`。
- R0D1 CSV：`mode=routed_grouped_micro_nncl_paired`、`schema_version=routed_grouped_micro_nncl_paired_v1`、`topk_policy=nncl_softmax_topk`、`baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`。
- R0D/R0D1 都是 diagnostic-only；R0D1 只关闭 same-run NNCL top-k/paired baseline diagnostic blocker。
- R0E formal 仍必须生成新的 `sop_a_precision.csv`、`sop_b_ncu_summary.csv`、`sop_c_routed_grouped.csv`、`r0_guard_report.md`、`r0_verdict.json`。
- 缺用户 R4 formal 确认时不得启动 `orin_1` R0E formal execution。
