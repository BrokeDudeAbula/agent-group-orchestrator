# AUTO-20260608-100 CuTe/CUTLASS R0E local guard hardening

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：本地 R0E guard/schema/synthetic hardening；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 根据 reviewer 子代理只读复核的 P1/P2 建议，继续补强 R0E 本地证据防误用能力。
- `r0e_sop_a_precision` CSV 新增 `qzeros_sym_ok`、`g_idx_default_ok`、`marlin_packed_layout_used` 字段；`cutedsl_r0e_guard.py` 将这些字段列为 SOP-A 必填，并要求 `qzeros_sym_ok=true`、`g_idx_default_ok=true`、`marlin_packed_layout_used=false`。
- `cutedsl_r0e_ncu_summary.py` 修复 log fallback：不再因为日志中出现 `nonzero=0` 字符串就误判非零；只接受 CSV 数值非零、log 中非零 `nonzero=` / `nonzero: `，或 explicit `valid_for_sop_a=true` / `valid_for_sop_c=true`。
- `cutedsl_r0e_make_runner.py` 记录 `cutedsl_r0e_ncu_summary.py` 返回码到 `ncu/r0e_sop_b_ncu_summary.rc`，方便后续 reviewer 区分 parser fail 与 gate fail。
- `cutedsl_r0e_synthetic_check.py` 新增 NCU summary 负例矩阵：低 occupancy、无 target kernel、无 duration、workload 全零、malformed NCU CSV 都必须 fail-closed。
- R0E 仍为 `blocked / gated`；本轮不改变任务状态，不请求 production 后续。

## 修改范围

- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_guard.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_ncu_summary.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
- `samples/micro_bench/spike/cute_dsl/README.md`

## 已执行本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py --output /tmp/q35_cutedsl_r0e_runner_check.sh --timestamp CHECK` PASS。
- runner token 检查 PASS：包含 `ncu --target-processes all`、`sop_b_ncu_summary.csv`、`ncu_summary_rc`、`ncu/r0e_sop_b_ncu_summary.rc`。
- `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4` PASS。

## 非 SOP 边界

- 本轮不运行 `orin_1`、不运行 NCU、不生成 formal evidence。
- 新增字段和 synthetic 只加严本地 guard/schema，不能解除 R0E `blocked / gated`。
- R0c/R0d/R0D1、AUTO-95 本地 smoke、AUTO-97/AUTO-100 synthetic NCU 都不能作为 SOP/tier evidence。
