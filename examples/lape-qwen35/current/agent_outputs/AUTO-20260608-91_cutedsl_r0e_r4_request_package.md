# AUTO-20260608-91 CuTe/CUTLASS R0E R4 Request Package

> Superseded notice（2026-06-08）：本报告记录的是 AUTO-91 当时的 R4 request package 状态，其中“只有 diagnostic modes、没有 formal SOP-A/B/C mode 或专用 guard”等表述已被后续 AUTO-95/AUTO-97/AUTO-100/AUTO-101/AUTO-104 覆盖。当前 R4 request package 以 `analysis/Qwen35_cutedsl_w4a16_grouped_r0e_r4_request_20260608/r4_request_package.md` 和 AUTO-106 为准：R0E formal-output candidate modes、guard、runner、NCU summary 路径和 SOP-B/SOP-C hardening 已存在并通过本地验证；R0E 仍 `blocked / gated`，必须等待用户 R4 确认和 remote formal evidence。

## 结论

- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍保持 `blocked / gated`。
- 本轮完成 R0E R4 formal request package，不启动远端 R4 任务，不生成 SOP/tier evidence。
- reviewer sub-agent 复核确认：R0E 不能在无用户 R4 确认时启动。
- 当前 `qwen3_5_cute_dsl_spike` 只有 diagnostic modes，没有 formal SOP-A/B/C mode；因此不能把 R0D1 diagnostic 命令包装成 R0E formal evidence。

## 产物

- request package：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_r4_request_20260608/r4_request_package.md`
- agent output：`.codex/agent_group/current/agent_outputs/AUTO-20260608-91_cutedsl_r0e_r4_request_package.md`

## Reviewer 只读复核

- sub-agent：`019ea672-0d9b-7213-b54f-745841804df6`
- 复核结论：
  - R0E 无用户 R4 确认时不能启动。
  - R4 包必须包含 target、container、remote repo、formal SOP-A/B/C 命令、guard/verdict 命令、预计耗时、输出目录和停止条件。
  - 必须写明 R0c/R0d/R0D1 非 SOP/tier，R0D1 `cutedsl_ms/nncl_ms/ratio` 不能作为 SOP-C 或 tier。

## R4 包核心内容

建议 target：

- target：`orin_1`
- container：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`
- local output：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_<TS>/`

R0E formal package 必须生成：

- `sop_a_precision.csv`
- `sop_b_ncu_summary.csv`
- `sop_c_routed_grouped.csv`
- `r0_guard_report.md`
- `r0_verdict.json`

当前 preflight 事实：

- `cute_dsl` binary modes：`manifest/toolchain_smoke/shape_bench/projection_correctness/routed_grouped_micro/routed_grouped_micro_nncl_paired/help`
- 所有现有 `cute_dsl` modes 都是 diagnostic 或 path/smoke。
- 当前仓库尚未发现 `cute_dsl` formal SOP-A/B/C mode 或专用 `cutedsl_r0e_guard`。

## 状态边界

- R0D1 已 `done / diagnostic-only`，关闭 NNCL top-k 与 same-run NNCL paired baseline diagnostic blocker。
- R0D1 不是 SOP-A/SOP-C/tier evidence。
- R0E 仍需用户 R4 确认。
- R4 确认后也必须先确认 formal runner/guard 存在；若不存在，应停止并保持 R0E blocked。
- 不得用 R0d/R0D1 diagnostic `ratio/cutedsl_ms/nncl_ms` 直接声明 SOP-C 或 tier。

## Stop Conditions

- 用户未确认 R4。
- sync/build/help preflight 失败。
- 没有 formal SOP-A/B/C runner 或 reviewer 接受的等价 formal runner。
- formal package 缺任一必需文件。
- schema/guard 失败。
- NaN/Inf 非 0 或输出全零。
- SOP-A/B/C 任一 gate 不达标。
- reviewer 提出 P0/P1 blocker。

## 当前待办

1. 等待用户 R4 确认是否按 request package 推进。
2. 若确认，先执行 remote sync/build/help preflight。
3. 若 preflight 显示仍无 formal runner/guard，则停止并保持 R0E blocked。
4. 若 formal runner/guard 已存在或被实现，再执行 SOP-A/B/C formal evidence。
5. 运行 guard 与 reviewer 复核后，才允许 tier 判定。
