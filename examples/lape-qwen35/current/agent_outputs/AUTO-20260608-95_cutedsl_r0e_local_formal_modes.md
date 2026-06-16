# AUTO-20260608-95 CuTe/CUTLASS R0E local formal-output modes

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：本地 R0E formal-output mode 实现与验证；不启动远端 R4，不生成 Orin formal SOP/tier evidence

## 结论

- 已把 AUTO-94 记录的 R0E source-level WIP 推进为可编译的本地 formal-output candidate modes。
- `qwen3_5_cute_dsl_spike` 现在包含并可链接：
  - `r0e_sop_a_precision`
  - `r0e_sop_b_occupancy`
  - `r0e_sop_c_routed_grouped`
- `cutedsl_r0e_guard.py` 已支持分层 verdict：schema/结构错误为 `schema_fail`；formal evidence 结构正确但 SOP gate 未过为 `gate_fail`。
- `cutedsl_r0e_make_runner.py` 已允许 formal mode 返回 `rc=2` 后继续回传 CSV 并运行 guard；`rc=1` 仍视为运行错误并停止。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍保持 `blocked / gated`：本轮没有用户 R4 formal 确认，没有 `orin_1` formal execution，没有 NCU SOP-B evidence，也没有 reviewer 对 remote evidence 的最终复核。

## 代码范围

- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
  - 新增 `RunR0eSopAPrecision`：使用 NNCL `SoftmaxTopk<half>`，对全部 routed rows 执行 gate/up/down dense-dequant CUTLASS candidate，并做 weighted reduce，对齐 `moe_output_before_combine.pt`。
  - 新增 `RunR0eSopBOccupancy`：无 NCU evidence 时 fail-closed，输出 `valid_for_sop_b=false`。
  - 新增 `RunR0eSopCRoutedGrouped`：复用 R0D1 same-run NNCL paired 计算路径，输出新的 `cutedsl_r0e_sop_c_v1` formal schema，并按 full 10 shape ratio gate 决定 `valid_for_sop_c/tier_eligible`。
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_guard.py`
  - `CheckResult` 新增 `gate_failures` 与 `schema_pass`。
  - verdict 新增 `schema_pass`、`gate_pass`，`status` 可为 `pass/gate_fail/schema_fail`。
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py`
  - 新增 `run_formal_mode` wrapper，允许 `rc=0/2` 继续 guard，阻止 `rc=1` 这类真实运行错误。
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
  - 新增 formal gate-fail synthetic，要求 `schema_pass=true/status=gate_fail`。
  - 保留 diagnostic mode 冒充 SOP-C 的 schema-fail 反例。
- `samples/micro_bench/spike/cute_dsl/README.md`
  - 更新 R0E formal-output candidate modes 与 guard 分层语义。

## Sub-agent 复核来源

本轮复用既有 sub-agent 只读结果：

- `019ea69a-10d7-7e62-b223-bd1c751b62cf`：建议新增 `r0e_sop_a_precision` / `r0e_sop_b_occupancy` / `r0e_sop_c_routed_grouped` 作为 formal schema producer / fail-closed runner；SOP-A 必须 full token reduce；SOP-B 无 NCU 必须 fail-closed；SOP-C 可复用 R0D1 same-run NNCL paired 路径，但必须新写 formal schema。
- `019ea658-208d-7942-87fe-13a2d585c4bb`：确认 NNCL `SoftmaxTopk`、`MoeGroupGemm`、`QuantInfo`、workspace 和 source-row 语义。
- `019ea647-77f6-77e1-bc8a-eb54a41660c9`：确认 NNCL pack/layout 只允许 HF raw -> NNCL layout，不得引入 Marlin packed path。

## 本地验证

已执行：

```bash
python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py
python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py
cmake -S . -B build_cute_dsl_spike_local -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87 -DLAPE_BUILD_SPIKE_CUTE_DSL=ON
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4
./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --help
./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=r0e_sop_b_occupancy --output_csv=/tmp/q35_cutedsl_r0e_sop_b_fail_closed.csv
CUDA_VISIBLE_DEVICES=0 ./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike --mode=r0e_sop_a_precision --warmup=0 --iters=1 --output_csv=/tmp/q35_cutedsl_r0e_sop_a_smoke.csv
python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_guard.py --evidence_dir /tmp/q35_cutedsl_r0e_guard_failclosed_smoke
git diff --check -- CMakeLists.txt samples/micro_bench/spike/cute_dsl .codex/agent_group
```

结果：

- `py_compile` PASS。
- synthetic PASS：formal pass、formal gate fail、diagnostic mode 冒充均按预期分类。
- CMake configure PASS。
- build `qwen3_5_cute_dsl_spike` PASS。
- `--help` 显示 R0E modes。
- SOP-B fail-closed smoke PASS：返回 `rc=2`，CSV 写 `valid_for_sop_b=false/ncu_available=false/fail_closed_reason=no_ncu_evidence`。
- SOP-A local smoke PASS：`max_abs=6.661564e-05`、`rmse=2.843369e-06`、NaN/Inf=0、`reference_nonzero_ok=true`、`valid_for_sop_a=true`。
- guard fail-closed composite smoke PASS：`schema_pass=true`、`overall_pass=false`、`status=gate_fail`。
- 本地 `r0e_sop_c_routed_grouped --m_filter=64` smoke 在当前非 Orin NNCL runtime 上返回 `Arch unsupported for MoE GEMM`，未生成 CSV；这不改变 R0D1 Orin evidence，也说明 SOP-C formal 仍需 `orin_1/sm_87` R4 execution。

## 当前 R0E 状态

`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍为 `blocked / gated`，原因：

1. 仍缺用户 R4 formal 确认 target、container、remote repo、命令、预计耗时、输出目录和停止条件。
2. 仍缺 `orin_1` R4 正式执行。
3. 仍缺真实 SOP-B NCU summary；当前 `r0e_sop_b_occupancy` 只能 fail-closed。
4. 仍缺 full 10 shape `sop_c_routed_grouped.csv` formal evidence。
5. 仍缺 `r0_guard_report.md` / `r0_verdict.json` 的 remote formal guard 结果。
6. 仍缺 reviewer 对 remote formal evidence 的 P0/P1 复核。

## 非 SOP 边界

- 本地 SOP-A smoke 不是 Orin R4 formal SOP-A evidence。
- 本地 SOP-B fail-closed CSV 不是 SOP-B PASS。
- 本地 SOP-C 非 Orin runtime unsupported 不是 formal SOP-C evidence。
- R0c/R0d/R0D1 仍不是 SOP-A、SOP-C 或 tier evidence。
- 不得用 R0D1 `ratio/cutedsl_ms/nncl_ms` 直接声明 SOP-C 或 tier。
- 缺用户 R4 formal 确认时，不得启动 `orin_1` R0E formal execution。
