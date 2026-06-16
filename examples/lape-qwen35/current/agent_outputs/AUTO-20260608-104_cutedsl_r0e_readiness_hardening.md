# AUTO-20260608-104 CuTe/CUTLASS R0E readiness hardening

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：本地 readiness/guard hardening；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 根据 reviewer 子代理只读复核，修复 R0E 本地 readiness 的 P1/P2 缺口。
- SOP-B NCU runner workload 从 `r0e_sop_a_precision` 改为绑定 `r0e_sop_c_routed_grouped --m_filter=64`，使 SOP-B NCU 更贴近 SOP-C formal workload。
- SOP-C formal CSV 现在显式输出 `qzeros_sym_ok`、`g_idx_default_ok`、`marlin_packed_layout_used`。
- `cutedsl_r0e_guard.py` 对 SOP-C 加严校验：
  - `input_source=bundle_hidden_states_routed_prefix`
  - `quant_method=dense_dequant_fp16_vs_nncl_gptq_w4a16_baseline`
  - `weight_source_layout=hf_gptq_raw`
  - `qzeros_sym_ok=true`
  - `g_idx_default_ok=true`
  - `marlin_packed_layout_used=false`
  - 非空 `bundle_dir/model_path`（字段存在时）
- R0E 仍为 `blocked / gated`；本轮只加固本地前置工具，不替代用户 R4 formal 确认或 remote evidence。

## 修改范围

- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_guard.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
- `samples/micro_bench/spike/cute_dsl/README.md`

## 本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py --output /tmp/q35_cutedsl_r0e_runner_check.sh --timestamp CHECK` PASS。
- Runner token 检查 PASS：
  - `CUTEDSL_R0E_R4_CONFIRMED`
  - `r0e_sop_a_precision`
  - `r0e_sop_b_occupancy`
  - `r0e_sop_c_routed_grouped`
  - `--m_filter=64`
  - `sop_b_workload_sop_c_m64.csv`
  - `cutlass_r0e_sop_c_routed_grouped_m64`
  - `ncu --target-processes all`
  - `cutedsl_r0e_ncu_summary.py`
  - `r0e_run_manifest.csv`
  - `binary.sha256`
  - `help.sha256`
  - `r0e_evidence.sha256`
  - `r0e_sop_b_ncu_summary.rc`
- `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4` PASS。
- 本地 `r0e_sop_b_occupancy` fail-closed smoke PASS：返回 `rc=2`，输出 `valid_for_sop_b=false`、`ncu_available=false`、`fail_closed_reason=no_ncu_evidence`。
- `git diff --check -- CMakeLists.txt samples/micro_bench/spike/cute_dsl .codex/agent_group analysis/Qwen35_cutedsl_w4a16_grouped_r0e_r4_request_20260608` PASS。

## 非 SOP 边界

- AUTO-104 是 readiness hardening，不是 execution evidence。
- SOP-B workload 绑定到 SOP-C M64 只加严 R4 runner，不构成 SOP-B PASS。
- SOP-C CSV/guard schema 加严只提升可审计性，不构成 SOP-C PASS。
- 缺用户 R4 formal 确认、`orin_1` formal execution、真实 SOP-B NCU、full 10 shape SOP-C formal CSV、remote guard/verdict 和 reviewer remote evidence 复核时，R0E 必须继续 `blocked / gated`。
