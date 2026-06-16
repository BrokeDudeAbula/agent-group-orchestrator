# AUTO-20260608-92 CuTe/CUTLASS R0 当前记忆同步

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
范围：仅同步 agent_group 记忆

## 结论

- 本轮按用户要求同步当前 CuTe/CUTLASS R0 进度，并列出 R0 阶段剩余待办。
- 本轮不新增实验结果，不启动 `orin_1` 远端任务，不改变任务状态。
- `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 保持 `in_progress / P0-next`。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 保持 `blocked / gated`。

## 当前状态

| 阶段 | 状态 | 说明 |
|---|---|---|
| R0a scaffold | `done / scaffold-only` | 独立 `samples/micro_bench/spike/cute_dsl/` target、manifest/toolchain path check 已完成。 |
| R0b Python CuTeDSL toolchain | `blocked` | `orin_1` import gate 缺 `cutlass._mlir`，当前 pip index 找不到 Jetson aarch64 compatible `nvidia-cutlass-dsl==4.5.0.dev0`。 |
| CuTe/CUTLASS C++ fallback smoke | `done / fallback validation` | 本地与 `orin_1` CuTe C++ tutorial smoke PASS，不依赖 Python CuTeDSL wheel。 |
| aligned shape bench | `done / diagnostic-only` | 覆盖 Marlin SOP-C 10 shape，但为 synthetic fp16 dense diagnostic，非 W4A16 routed grouped MoE evidence。 |
| R0c projection correctness | `done / diagnostic-only` | `gate_proj/up_proj/down_proj x M=64/128/898` 9 case PASS，raw HF GPTQ dense-dequant fp16 B 对齐 torch CUDA reference。 |
| R0d routed grouped micro | `done / diagnostic-only` | `orin_1` 10 shape diagnostic PASS；仍使用 diagnostic top-k / CSV join baseline 口径，不能作为 SOP/tier evidence。 |
| R0D1 same-run NNCL paired diagnostic | `done / diagnostic-only` | `orin_1` full 10 shape PASS，`topk_policy=nncl_softmax_topk`，same-run NNCL grouped baseline，reviewer 无 P0/P1；只关闭 diagnostic blocker。 |
| R0E formal SOP-A/B/C | `blocked / gated` | AUTO-91 R4 request package 已准备；仍缺用户 R4 formal 确认，且当前未证明存在 `cute_dsl` formal SOP-A/B/C runner/guard。 |

## 当前 R0 剩余待办

1. 等待用户 R4 确认 `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 的 formal 执行口径：target、container、remote repo、formal SOP-A/B/C 命令、guard/verdict 命令、预计耗时、本地输出目录和停止条件。
2. 用户 R4 确认后，先执行 remote sync/build/help preflight，确认 `qwen3_5_cute_dsl_spike` 是否存在 formal SOP-A/B/C runner 或 reviewer 接受的等价 runner/guard。
3. 若 preflight 后仍无 formal runner/guard，必须停止并保持 R0E `blocked / gated`；不得用 `routed_grouped_micro_nncl_paired` 或其他 diagnostic mode 冒充 formal evidence。
4. 若 formal runner/guard 已存在或后续经用户确认实现，执行 R0E formal SOP-A/B/C，并回传 `sop_a_precision.csv`、`sop_b_ncu_summary.csv`、`sop_c_routed_grouped.csv`、`r0_guard_report.md`、`r0_verdict.json`。
5. 对 R0E formal evidence 运行 guard 和 reviewer 复核；只有 SOP-A/B/C 全部有效且达标、reviewer 无 P0/P1，才允许 tier 判定。
6. 若 SOP-C ratio gate 失败，则 CuTe/CUTLASS R0 只能归档为未达标路线，不进入 production。
7. Python CuTeDSL route 仍是可选 blocked 分支；只有用户要求回到 Python route 并提供 Jetson CUDA 12.6 / Python 3.10 / aarch64 compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel 后，才重跑 R0b。

## 非 SOP 边界

- R0a/R0b/R0c/R0d/R0D1 均不是 SOP-A、SOP-C 或 tier evidence。
- R0D1 的 `cutedsl_ms`、`nncl_ms`、`ratio` 只能作为 same-run diagnostic timing，不得进入 SOP-C 或 tier 判定。
- 不使用 `B_marlin`、`RepackQweightToMarlin()` 或 `perm64` scales layout。
- 不直接链接 `samples/micro_bench/spike/marlin_moe/main.cc` 到 `cute_dsl` target。
- 不修改 production path。
- 缺用户 R4 formal 确认时，不得启动 R0E。

## 同步文件

- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/memory/TASK_LEDGER.md`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/memory/ROADMAP.md`
- `.codex/agent_group/memory/PROGRESS_LEDGER.md`
- `.codex/agent_group/current/acceptance.md`
