# AUTO-20260608-106 CuTe/CUTLASS R0E R4 request refresh

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：刷新 R4 request package；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 已刷新 `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_r4_request_20260608/r4_request_package.md`，使其反映 AUTO-95/AUTO-97/AUTO-100/AUTO-101/AUTO-104 后的当前事实。
- 当前 `qwen3_5_cute_dsl_spike` 已有本地可编译/可 smoke 的 R0E formal-output candidate modes 和 guard/runner/NCU summary 工具，但这些仍不是 Orin formal evidence。
- R0E 仍为 `blocked / gated`：缺用户 R4 formal 确认、`orin_1` formal execution、真实 SOP-B NCU、full 10 shape SOP-C formal CSV、remote guard/verdict 和 reviewer remote evidence 复核。

## 刷新内容

- R4 确认项新增：SOP-B NCU workload 绑定 `r0e_sop_c_routed_grouped --m_filter=64`，并回传 `sop_b_workload_sop_c_m64.csv`。
- Formal requirements 新增：
  - SOP-A CSV 必须含 `qzeros_sym_ok/g_idx_default_ok/marlin_packed_layout_used`。
  - SOP-B summary 必须来自真实 Orin NCU，且满足 `ncu_available=true`、`has_duration=true`、`saw_target_workload=true`、`saw_nonzero_output=true`、`valid_for_sop_b=true`、`best_occupancy>=30.0`。
  - SOP-C CSV 必须满足 `input_source=bundle_hidden_states_routed_prefix`、`quant_method=dense_dequant_fp16_vs_nncl_gptq_w4a16_baseline`、`weight_source_layout=hf_gptq_raw`、`qzeros_sym_ok=true`、`g_idx_default_ok=true`、`marlin_packed_layout_used=false`，字段存在时 `bundle_dir/model_path` 非空。
  - verdict/runner sidecar 需包含 input CSV metadata/sha、`r0e_run_manifest.csv`、`binary.sha256`、`help.sha256`、`ncu/r0e_sop_b_ncu_summary.rc`、`r0e_evidence.sha256`。
- Stop conditions 新增：
  - SOP-B workload 不是 `r0e_sop_c_routed_grouped --m_filter=64` 或缺 `sop_b_workload_sop_c_m64.csv` 时停止。
  - SOP-A/SOP-C 缺 layout guard 字段或字段未满足 `true/true/false` 时停止。
  - SOP-C 缺 raw GPTQ/layout/input 字段或字段不满足 formal 口径时停止。

## Sub-agent 复核

- 复用了 reviewer 子代理 `019ea69a-10d7-7e62-b223-bd1c751b62cf` 的只读复核结论：R0 design/update report 和 R0D 可保持 done；R0E 必须保持 `blocked / gated`；AUTO-104 已覆盖它之前指出的 SOP-B workload 绑定、SOP-C schema/layout 字段和 guard 加严缺口。
- 本轮已请求该 reviewer 对刷新后的 R4 package 做只读复核；结果若回传，将继续追加到后续记忆同步。

## 非 SOP 边界

- AUTO-106 是 request package 刷新，不是 execution evidence。
- 未运行 `orin_1`、未运行 NCU、未生成 formal package。
- 不得用 AUTO-106、AUTO-104、本地 smoke、synthetic NCU、runner token、R0D 或 R0D1 声明 SOP/tier。
