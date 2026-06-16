# AUTO-20260608-83 CuTeDSL R0 Current Todo Sync

task_id: `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
status: `in_progress`
date: `2026-06-08`

## 当前进度同步

CuTe/CUTLASS C++ route 已成为当前可推进路线；Python CuTeDSL route 仍被 `cutlass._mlir` packaging blocker 卡住。

已完成：

- R0a scaffold：`samples/micro_bench/spike/cute_dsl/` 独立 spike target 已落盘，默认 `LAPE_BUILD_SPIKE_CUTE_DSL=OFF`。
- R0b Python toolchain smoke：`orin_1` sync/build PASS，但 import gate FAIL：`No module named cutlass._mlir`；该子路线保持 `blocked`。
- CuTe/CUTLASS C++ fallback smoke：本地与 `orin_1` tutorial compile/run PASS。
- Aligned shape bench：`--mode=shape_bench` 覆盖 Marlin SOP-C 10 shape，`orin_1` 10/10 PASS；仍是 `fp16_dense` diagnostic only。
- R0c projection correctness：`--mode=projection_correctness` 在 `orin_1` 覆盖 `gate_proj/up_proj/down_proj x M=64/128/898` 共 9 case，全部 PASS。

R0c 正式证据目录：

```text
analysis/Qwen35_cutedsl_r0c_projection_correctness_orin_1_20260608_065517/
```

R0c 边界：

- single expert / single projection correctness diagnostic，不是 routed grouped MoE。
- `candidate_ms/reference_ms` 不是 SOP-C ratio。
- 所有行固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- 不使用 `B_marlin`、`RepackQweightToMarlin()` 或 `perm64` scales layout。
- R0c 只解锁 R0d，不能直接进入 R0e/SOP-A/B/C 或 tier。

## R0 当前待办

1. `Q35-MOE-CUTEDSL-R0D-ROUTED-GROUPED-MICRO`
   - 状态：`todo / next`
   - 依赖：R0c 9 case PASS，已满足。
   - 目标：构造 routed rows、expert remap、`cu_row`、padding、source row，覆盖 Marlin SOP-C 10 shape。
   - 输出：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d_<target>_<ts>/routed_grouped_micro.csv`。
   - 至少记录：`family,M,K,N,projection,active_experts,padded_rows,cutedsl_ms,nncl_ms,ratio,max_abs,rmse,nan_count,inf_count,nonzero,valid_for_sop_a,valid_for_sop_c,tier_eligible`。
   - 边界：仍是 diagnostic-only，不能替代 SOP-A/B/C。

2. `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
   - 状态：`todo / gated`
   - 依赖：R0d 10 shape precision/timing 完整，reviewer 无 P0/P1 blocker，用户 R4 确认。
   - 目标：复用 Q35-022 SOP-A/B/C gate，生成 formal R0 verdict 与 tier 判定。
   - 输出：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_<target>_<ts>/`。
   - 边界：不得用 R0a/R0b/R0c/R0d diagnostic 直接声明 tier。

3. Python CuTeDSL route blocker closure
   - 状态：`blocked / optional unless user chooses Python route`
   - 阻塞：Jetson CUDA 12.6 / Python 3.10 / aarch64 compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel 当前不可得，导致 `cutlass._mlir` 缺失。
   - 解锁动作：提供可用 wheel 后重跑 R0b import、elementwise、tensorop smoke。
   - 边界：当前 C++ fallback PASS 不等于 Python CuTeDSL works on Orin。

4. R0 design/update report
   - 状态：`todo / documentation`
   - 目标：在推进 R0d 前补一份当前 chosen route 的 design/update 文档，说明 C++ fallback 的 kernel launch 形态、数据流、与 Python route 的分叉风险。
   - 建议输出：`analysis/Qwen35_cutedsl_w4a16_grouped_<TS>/design.md` 或 R0d 输出目录内 `design_update.md`。

## 当前推荐下一步

优先启动 R0d routed grouped micro。R0e/SOP-A/B/C 和 tier 判定必须等待 R0d 完整通过后再由用户 R4 确认。
