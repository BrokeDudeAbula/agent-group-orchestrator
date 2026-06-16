# AUTO-20260608-94 CuTe/CUTLASS R0 当前进度与 WIP 同步

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
范围：agent_group 记忆同步与 R0 待办清单；不启动远端 R4，不生成 SOP/tier evidence

## 结论

- 当前 CuTe/CUTLASS R0 权威状态不变：`Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 仍为 `in_progress / P0-next`。
- 已完成项仍为 R0a scaffold、CuTe/CUTLASS C++ fallback smoke、aligned shape bench、R0c projection correctness、R0d routed grouped micro、R0D1 same-run NNCL paired diagnostic。
- R0b Python CuTeDSL route 仍 `blocked`，阻塞点是 Jetson aarch64 环境缺 `cutlass._mlir` / compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel。
- R0E formal SOP-A/B/C 仍 `blocked / gated`。当前不能把 R0c/R0d/R0D1、AUTO-91 R4 request package、AUTO-93 guard/runner skeleton 或本地 R0E source WIP 当作 SOP/tier evidence。

## 当前本地 WIP

本轮复核发现，实际工作树已经超过 AUTO-93 的记录，但仍是未完成、未验证的本地 WIP：

- `samples/micro_bench/spike/cute_dsl/main.cc` 已出现 `r0e_sop_a_precision`、`r0e_sop_b_occupancy`、`r0e_sop_c_routed_grouped` 的 help、mode 校验和 dispatch。
- `samples/micro_bench/spike/cute_dsl/spike_common.h` 已声明：
  - `RunR0eSopAPrecision`
  - `RunR0eSopBOccupancy`
  - `RunR0eSopCRoutedGrouped`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu` 已出现部分 R0E helper，例如 `WeightedReduceGroupedRows`、`SopCRatioGate`、`WriteR0eSop*`。
- `rg` 复核未找到三个 entry function 的定义；当前尚未执行 C++ configure/build 验证。

因此，本地 source-level mode 名称和 helper 不能视为 formal binary modes 已完成。R0E 仍缺完整实现、编译验证、本地 smoke、用户 R4 确认、远端 formal execution、guard/reviewer 复核和 tier 判定。

本轮尝试启动新的只读 sub-agent 复核，但当前 sub-agent thread limit 已满，未能新增 sub-agent 结论；本次同步只记录本地复核事实。

## R0 待办清单

1. 完成 `qwen3_5_cute_dsl_spike` 的 R0E formal entry functions，至少包括：
   - `RunR0eSopAPrecision`
   - `RunR0eSopBOccupancy`
   - `RunR0eSopCRoutedGrouped`
2. 补齐 SOP-A formal：使用 NNCL `SoftmaxTopk<half>` 路由、gate/up/down dense-dequant/CUTLASS candidate、weighted reduce，对齐 `moe_output_before_combine.pt`，输出 `sop_a_precision.csv`。
3. 补齐 SOP-B formal：若没有 NCU formal summary，必须 fail-closed 输出 `valid_for_sop_b=false`；不得用本地 CUDA occupancy API 替代 NCU。
4. 补齐 SOP-C formal：复用 R0D1 same-run NNCL paired 计算路径，但必须输出新的 formal schema；按 SOP-C ratio gate 决定 `valid_for_sop_c/tier_eligible`，不得直接复用 R0D1 diagnostic CSV。
5. 调整 `cutedsl_r0e_guard.py`：区分 schema/结构错误与 ratio gate failure；允许 formal failure evidence 生成 `overall_pass=false`，不要把 gate fail 混成 schema error。
6. 调整 `cutedsl_r0e_make_runner.py`：formal mode 返回 fail-closed rc 时仍应回传 CSV 并继续 guard；构建失败、缺文件、schema 错误仍应停止。
7. 更新 `cutedsl_r0e_synthetic_check.py`，覆盖 formal pass、formal gate fail、diagnostic mode 冒充、缺字段/错 schema 等反例。
8. 完成本地验证：
   - `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py`
   - `python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
   - `cmake -S . -B build_cute_dsl_spike_local -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87 -DLAPE_BUILD_SPIKE_CUTE_DSL=ON`
   - `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4`
   - `git diff --check -- CMakeLists.txt samples/micro_bench/spike/cute_dsl .codex/agent_group`
9. 等待用户 R4 formal 确认 target、container、remote repo、命令、预计耗时、输出目录和停止条件。
10. 用户 R4 确认后，执行 `orin_1` remote sync/build/help preflight；若 formal binary modes 或 reviewer 接受的等价 runner 不存在，停止并保持 R0E `blocked / gated`。
11. formal modes 存在且本地验证通过后，在 `orin_1` 执行 R0E formal SOP-A/B/C，回传：
    - `sop_a_precision.csv`
    - `sop_b_ncu_summary.csv`
    - `sop_c_routed_grouped.csv`
    - `r0_guard_report.md`
    - `r0_verdict.json`
12. 对 formal evidence 跑 guard 与 reviewer 复核；只有 SOP-A/B/C 全部有效且达标、reviewer 无 P0/P1，才允许 tier 判定。
13. Python CuTeDSL route blocker closure 仍为可选待办；只有用户要求回到 Python route 并提供 compatible wheel 后，才重跑 R0b import/elementwise/tensorop smoke。

## 非 SOP 边界

- R0a/R0b/R0c/R0d/R0D1 均不是 SOP-A、SOP-C 或 tier evidence。
- R0D1 `cutedsl_ms/nncl_ms/ratio` 不得用于 SOP-C 或 tier。
- AUTO-91 R4 request package、AUTO-93 guard/runner skeleton、AUTO-94 记忆同步都不是 execution evidence。
- 本地 R0E source-level WIP 不是 formal binary modes 完成证明。
- 不使用 `B_marlin`、`RepackQweightToMarlin()` 或 `perm64` scales layout 作为 CuTe/CUTLASS correctness/formal 证据。
- 不直接链接 `samples/micro_bench/spike/marlin_moe/main.cc` 到 `cute_dsl` target。
- 不修改 production path。
- 缺用户 R4 formal 确认时，不得启动 R0E 远端 formal execution。
