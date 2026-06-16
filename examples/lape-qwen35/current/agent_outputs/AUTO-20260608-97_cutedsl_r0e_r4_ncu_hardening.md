# AUTO-20260608-97 CuTe/CUTLASS R0E R4 NCU hardening

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：本地 R4 runner/guard hardening；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 发现并修复一个 R0E formal 前置缺口：AUTO-95 后 `r0e_sop_b_occupancy` 仍只能写 fail-closed CSV，原 generated runner 即使在用户 R4 后也不能自动产出真实 SOP-B NCU PASS evidence。
- 新增 `cutedsl_r0e_ncu_summary.py`：只解析已回传的 NCU CSV/log 和 workload CSV，生成 `sop_b_ncu_summary.csv`；缺 NCU evidence 时 fail-closed。
- 更新 `cutedsl_r0e_make_runner.py`：R4 脚本会用 `ncu` 包住 `r0e_sop_a_precision` workload，回传 `ncu/r0e_sop_b_cutlass.{csv,log}`，再生成 SOP-B summary；如果 `ncu` 不存在，则显式调用 `r0e_sop_b_occupancy` 生成 fail-closed CSV。
- 更新 `cutedsl_r0e_guard.py`：SOP-B 必须有 `ncu_available=true`、`valid_for_sop_b=true`、`best_occupancy>=30.0`，并通过 target workload / nonzero output checks；手写数字或 fail-closed CSV 不能通过 SOP-B。
- 更新 R4 request package：当前本地已有 R0E formal-output modes，但仍缺用户 R4、`orin_1` formal execution、真实 NCU、full SOP-C、remote guard/verdict 和 reviewer 复核。

## 修改范围

- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_ncu_summary.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_guard.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
- `samples/micro_bench/spike/cute_dsl/README.md`
- `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_r4_request_20260608/r4_request_package.md`

## 已执行本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py` PASS。
- `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py --output /tmp/q35_cutedsl_r0e_runner_check.sh --timestamp CHECK` PASS。
- 生成 runner 已包含 `ncu --target-processes`、`cutedsl_r0e_ncu_summary.py`、`r0e_sop_a_precision` 和 `sop_b_ncu_summary` token。
- `git diff --check -- CMakeLists.txt samples/micro_bench/spike/cute_dsl .codex/agent_group analysis/Qwen35_cutedsl_w4a16_grouped_r0e_r4_request_20260608` PASS。

## 非 SOP 边界

- 本轮不运行 `orin_1`、不运行 NCU、不生成 formal evidence。
- `cutedsl_r0e_ncu_summary.py` 解析 synthetic NCU CSV 通过，只证明 parser/guard 行为，不是 SOP-B PASS。
- R0E 仍为 `blocked / gated`。
- R0c/R0d/R0D1 仍不是 SOP-A/SOP-C/tier evidence。
