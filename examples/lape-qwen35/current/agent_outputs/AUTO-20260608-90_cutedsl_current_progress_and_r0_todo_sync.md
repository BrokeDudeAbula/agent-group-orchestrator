# AUTO-20260608-90 CuTeDSL 当前进度与 R0 待办同步

## 结论

- 本次同步不引入新的实验结果，也不改变任务状态。
- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 仍为 `in_progress / P0-next`。
- R0a scaffold、CuTe/CUTLASS C++ fallback smoke、aligned shape bench、R0c projection correctness、R0d routed grouped micro、R0D1 same-run NNCL paired diagnostic 均已完成。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍为 `blocked / gated`，当前只缺用户 R4 formal 确认。
- Python CuTeDSL route 仍为 `blocked / optional`，阻塞点是 `cutlass._mlir` / Jetson aarch64 `nvidia-cutlass-dsl==4.5.0.dev0` wheel 不可用。

## 当前状态表

| R0 项 | 状态 | 当前结论 |
|---|---|---|
| R0a scaffold | `done` | `samples/micro_bench/spike/cute_dsl/` 独立 target 与 manifest/toolchain path check 已完成；非 SOP/tier |
| R0b Python CuTeDSL toolchain smoke | `blocked` | `orin_1` import gate 失败：`No module named cutlass._mlir`；elementwise/tensorop 未运行 |
| CuTe/CUTLASS C++ fallback smoke | `done` | 本地与 `orin_1` CuTe C++ tutorial 编译运行 PASS；只证明 C++ fallback 可用 |
| aligned shape bench | `done / diagnostic-only` | 同 Marlin SOP-C 10 shape 的 synthetic fp16 dense CUTLASS bench PASS；非 SOP/tier |
| R0c projection correctness | `done / diagnostic-only` | `gate_proj/up_proj/down_proj x M=64/128/898` 共 9 case 在 `orin_1` PASS；非 SOP/tier |
| R0d routed grouped micro | `done / diagnostic-only` | 10 shape diagnostic PASS；历史 NNCL CSV join 与 torch top-k 结果不能作为 formal SOP-C |
| R0D1 same-run NNCL paired diagnostic | `done / diagnostic-only` | 10 shape same-run NNCL paired diagnostic PASS，reviewer 无 P0/P1；只关闭 diagnostic blocker |
| R0e formal SOP-A/B/C | `blocked / gated` | 等待用户 R4 确认 formal 命令、预计耗时、输出目录和停止条件 |

## 当前 R0 待办

1. `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 的 R4 确认包。
   - 明确 target：`orin_1`。
   - 明确 container：`liyang_lape`。
   - 明确 remote repo：`/workspace/liyang/workspace/lape`。
   - 明确本地输出目录建议：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_<TS>/`。
   - 明确预计耗时和停止条件。

2. R0E formal SOP-A/B/C 远端执行。
   - 只有用户完成 R4 确认后才能启动。
   - 必须复用 Q35-022 SOP-A/B/C gate。
   - 预期 formal package 至少包含：
     - `sop_a_precision.csv`
     - `sop_b_ncu_summary.csv`
     - `sop_c_routed_grouped.csv`
     - `r0_guard_report.md`
     - `r0_verdict.json`

3. R0E formal evidence guard 与 reviewer 复核。
   - SOP-A：`max_abs < 1e-2`、`rmse < 1e-3`、NaN/Inf=0，reference 必须是 `moe_output_before_combine.pt`。
   - SOP-B：真实 Orin NCU Marlin/CuTe candidate kernel occupancy 或等价正式口径必须满足 gate。
   - SOP-C：必须是 same-run paired grouped baseline，不能使用 R0d/R0D1 diagnostic ratio。
   - reviewer 无 P0/P1 后才能进入 tier 判定。

4. R0E tier 判定。
   - 只有 formal SOP-A/B/C 全部有效且达标，才允许生成 tier A/B/C 并考虑后续 R1/R3。
   - 若 formal SOP-C ratio gate 失败，则 R0 只能归档为未达标路线，不能进入 production。

5. Python CuTeDSL route blocker closure，当前为可选待办。
   - 若用户要求回到 Python CuTeDSL route，需要提供 Jetson CUDA 12.6 / Python 3.10 / aarch64 compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
   - 补齐 wheel 后重跑 R0b import、Ampere elementwise compile/run、tensorop GEMM smoke。
   - C++ fallback 已通过不等于 Python CuTeDSL `_mlir` route 可用。

## 非 SOP 边界

- R0c/R0d/R0D1 均不是 SOP-A、SOP-C 或 tier evidence。
- R0D1 的 `cutedsl_ms`、`nncl_ms`、`ratio` 只能作为 same-run diagnostic timing，不能进入 SOP-C 或 tier 判定。
- 不使用 `B_marlin`、`RepackQweightToMarlin()` 或 `perm64` scales layout。
- 不直接链接 `samples/micro_bench/spike/marlin_moe/main.cc` 到 `cute_dsl` target。
- 不修改 production path。
- 缺用户 R4 formal 确认时，不得启动 R0E。

## 本次同步文件

- `.codex/agent_group/current/agent_outputs/AUTO-20260608-90_cutedsl_current_progress_and_r0_todo_sync.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
