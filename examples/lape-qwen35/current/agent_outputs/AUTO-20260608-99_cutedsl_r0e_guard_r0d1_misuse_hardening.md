# AUTO-20260608-99 CuTe/CUTLASS R0E guard R0D1 misuse hardening

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：本地 guard/synthetic hardening；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 新增 R0E synthetic 反例：把 R0D1 same-run NNCL paired diagnostic 形态的 CSV 改名为 `sop_c_routed_grouped.csv` 放入 R0E evidence dir，`cutedsl_r0e_guard.py` 必须判定 `schema_fail`。
- 该反例覆盖冷启动/人工整理时最危险的误用：R0D1 CSV 虽有 10 shape、NNCL top-k、same-run NNCL baseline 和 ratio 字段，但仍是 `mode=routed_grouped_micro_nncl_paired`、`schema_version=routed_grouped_micro_nncl_paired_v1`、`valid_for_sop_c=false`、`tier_eligible=false`、`notes=diagnostic_only`，不能作为 R0E SOP-C formal evidence。
- README 已补充 synthetic 覆盖范围，明确 parser/guard synthetic 不构成 R4 formal evidence。
- R0E 仍为 `blocked / gated`；本轮不改变任务状态，不请求 production 后续。

## 修改范围

- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
- `samples/micro_bench/spike/cute_dsl/README.md`

## 已执行本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py --output /tmp/q35_cutedsl_r0e_runner_check.sh --timestamp CHECK` PASS。
- `tasks.csv` 状态检查 PASS：23 rows、无重复 ID、主 R0 `in_progress`、R0D1 `done`、R0E `blocked`。

## 非 SOP 边界

- 本轮不运行 `orin_1`、不运行 NCU、不生成 formal evidence。
- R0D1 改名反例 PASS 只证明 guard 能拒绝 diagnostic CSV 冒充，不是 SOP-C PASS。
- R0c/R0d/R0D1、AUTO-95 本地 smoke、AUTO-97 synthetic NCU 和本轮 synthetic 都不能作为 SOP/tier evidence。
