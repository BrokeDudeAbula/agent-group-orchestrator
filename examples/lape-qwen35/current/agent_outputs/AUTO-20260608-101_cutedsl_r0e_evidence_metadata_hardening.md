# AUTO-20260608-101 CuTe/CUTLASS R0E evidence metadata hardening

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：本地 R0E evidence metadata / sha hardening；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 根据 reviewer 子代理关于 metadata/sha 绑定的建议，补强 R0E formal 回传证据的可审计性。
- `cutedsl_r0e_guard.py` 的 `r0_verdict.json` 新增 `input_metadata`，记录 `sop_a_precision.csv`、`sop_b_ncu_summary.csv`、`sop_c_routed_grouped.csv` 的 path、exists、size_bytes 和 sha256。
- `cutedsl_r0e_make_runner.py` 生成的 R4 runner 新增：
  - `r0e_run_manifest.csv`
  - `binary.sha256`
  - `help.sha256`
  - `ncu/r0e_sop_b_ncu_summary.rc`
  - `r0e_evidence.sha256`
- `cutedsl_r0e_synthetic_check.py` 验证 passing synthetic evidence 的 verdict metadata 非空，并检查 runner 包含 manifest/sha token。
- R0E 仍为 `blocked / gated`；metadata 只用于 reviewer 追溯，不替代 formal CSV、guard verdict 或 Orin evidence。

## 修改范围

- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_guard.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
- `samples/micro_bench/spike/cute_dsl/README.md`

## 已执行本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py --output /tmp/q35_cutedsl_r0e_runner_check.sh --timestamp CHECK` PASS。
- runner token 检查 PASS：包含 `r0e_run_manifest.csv`、`binary.sha256`、`help.sha256`、`ncu/r0e_sop_b_ncu_summary.rc`、`r0e_evidence.sha256`。

## 非 SOP 边界

- 本轮不运行 `orin_1`、不运行 NCU、不生成 formal evidence。
- sha/manifest metadata 只帮助 reviewer 发现证据替换或混用，不能让 R0E 从 `blocked / gated` 变为 done。
