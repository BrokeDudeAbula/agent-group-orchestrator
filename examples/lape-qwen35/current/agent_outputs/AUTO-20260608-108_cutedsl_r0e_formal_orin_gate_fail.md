# AUTO-20260608-108 CuTe/CUTLASS R0E formal Orin gate fail

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：用户 R4 确认后的 `orin_1` formal SOP-A/B/C execution、guard、reviewer 复核和 R0 verdict

## 结论

- `orin_1` R0E formal 已执行并回传完整 evidence。
- Evidence 目录：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`
- Guard verdict：`schema_pass=true`、`overall_pass=false`、`status=gate_fail`、`tier_eligible=false`。
- SOP-A：PASS。
- SOP-B：PASS。
- SOP-C：FAIL，ratio gate 大幅失败。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 建议状态：`done / formal FAIL / gate_fail`。
- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 建议归档：`done / tier D / not production`。
- 不允许声明 SOP-C PASS、tier eligible、R1 启动或 production 路径推进。

## 执行口径

- target：`orin_1`
- container：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`
- build dir：`/tmp/lape_cutedsl_r0e_20260608_113730`
- local output：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`
- runner：`r0e_runner.sh`
- R4 confirmed flag：`CUTEDSL_R0E_R4_CONFIRMED=1`

## Evidence 文件

- `sync.log`
- `configure.log`
- `build.log`
- `help.log`
- `formal_run.log`
- `r0e_run_manifest.csv`
- `binary.sha256`
- `help.sha256`
- `r0e_evidence.sha256`
- `sop_a_precision.csv`
- `sop_b_ncu_summary.csv`
- `sop_b_workload_sop_c_m64.csv`
- `sop_c_routed_grouped.csv`
- `r0_guard_report.md`
- `r0_verdict.json`
- `ncu/r0e_sop_b_cutlass.csv`
- `ncu/r0e_sop_b_cutlass.log`
- `ncu/r0e_sop_b_ncu_summary.rc`

## Gate 结果

### SOP-A PASS

- `valid_for_sop_a=true`
- `max_abs=6.661564e-05`
- `rmse=2.843369e-06`
- `nan_count=0`
- `inf_count=0`
- `reference_nonzero_ok=true`
- `qzeros_sym_ok=true`
- `g_idx_default_ok=true`
- `marlin_packed_layout_used=false`

### SOP-B PASS

- `valid_for_sop_b=true`
- `best_occupancy=31.060000`
- `ncu_available=true`
- `has_duration=true`
- `saw_target_workload=true`
- `saw_nonzero_output=true`
- label：`cutlass_r0e_sop_c_routed_grouped_m64`
- workload：`r0e_sop_c_routed_grouped --m_filter=64`

### SOP-C FAIL

- rows：10
- schema：formal SOP-C schema
- `precision_pass=true` for all rows
- `valid_for_sop_c=false` for all rows
- `tier_eligible=false` for all rows
- family A geomean：`152.03160348560172`
- family A hot M898：`170.410573`
- family A small M64：`94.754880`
- family B geomean：`65.92550662294984`
- family B hot M898：`71.708239`
- family B small M64：`69.122485`

SOP-C thresholds remain `family geomean <= 0.90`、`hot M=898 <= 0.85`、`small M=64 <= 1.00`，therefore R0E fails.

## Reviewer 复核

- reviewer 子代理：`019ea69a-10d7-7e62-b223-bd1c751b62cf`
- 结论：evidence schema 完整且可审计；SOP-A/SOP-B PASS；SOP-C FAIL；无 evidence schema/审计完整性 P0/P1。
- 状态建议：R0E 标 `done / FAIL`，主线归档 `tier D / not production`。

## 非 SOP 边界

- 本次 formal evidence 不能声明 SOP-C PASS。
- 本次 formal evidence 不能声明 tier eligible。
- 不允许进入 R1、production 或 R3 写入请求。
- R0c/R0d/R0D1 diagnostic timing/ratio 仍不能作为 SOP/tier evidence。
