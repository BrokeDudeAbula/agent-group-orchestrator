# AUTO-20260608-84 CuTeDSL R0d Design And Current Todo

task_id: `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
status: `in_progress`
date: `2026-06-08`

## 当前进度同步

CuTe/CUTLASS C++ route 继续作为当前可推进路线。Python CuTeDSL route 仍被 `cutlass._mlir` packaging blocker 卡住，除非补齐 Jetson CUDA 12.6 / Python 3.10 / aarch64 compatible `nvidia-cutlass-dsl==4.5.0.dev0` wheel，否则不能声明 Python CuTeDSL works on Orin。

已完成：

- R0a scaffold：`samples/micro_bench/spike/cute_dsl/` 独立 spike target 已落盘，默认 `LAPE_BUILD_SPIKE_CUTE_DSL=OFF`。
- R0b Python toolchain smoke：`orin_1` sync/build PASS，但 import gate FAIL：`No module named cutlass._mlir`；该子路线保持 `blocked`。
- CuTe/CUTLASS C++ fallback smoke：本地与 `orin_1` tutorial compile/run PASS。
- Aligned shape bench：`--mode=shape_bench` 覆盖 Marlin SOP-C 10 shape，`orin_1` 10/10 PASS；仍是 `fp16_dense` diagnostic only。
- R0c projection correctness：`--mode=projection_correctness` 在 `orin_1` 覆盖 `gate_proj/up_proj/down_proj x M=64/128/898` 共 9 case，全部 PASS。

本轮新增状态：

- R0 design/update report 已落盘：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d_design_20260608/design_update.md`。
- R0d C++ 最小实现已落地：`samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`。
- R0d 已接入 spike target 与 CLI：`--mode=routed_grouped_micro`、`--nncl_csv=`。
- `Q35-MOE-CUTEDSL-R0D-ROUTED-GROUPED-MICRO` 从 `todo` 更新为 `in_progress / implementation landed, not verified`。

## R0d 当前实现意图

- 读取 Q35-028 layer15 `moe_block` bundle：`hidden_states.pt`、`router_logits.pt`、`meta.json`。
- 用 torch CUDA `softmax/topk` 重建 routed rows，按 expert 分桶，生成 selected experts、active experts、source rows、`cu_row` 和 block16 padding metadata。
- 从 HF raw GPTQ 读取 `qweight/qzeros/scales/g_idx`，强制 `qzeros==0x77777777`、`g_idx[i]==i/128`、`K%128==0`。
- dense-dequant 生成 fp16 B，禁止 `B_marlin`、`RepackQweightToMarlin()`、`perm64` scales layout。
- family A：per-expert `gate_proj` CUTLASS dense GEMM。
- family B：per-expert `gate_proj + up_proj` CUTLASS dense GEMM，torch `silu(gate) * up` 后再执行 `down_proj` CUTLASS dense GEMM。
- reference 使用同一 dense B 的 torch CUDA fp32 matmul 后转 fp16，比较 grouped rows，不做 final token reduce。
- `nncl_ms` 当前只从 formal SOP-C CSV join metadata，`baseline_source=formal_sopc_csv_join_not_paired`，不能当作同-run paired SOP-C evidence。

## 当前未验证项

- 尚未跑 `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py`。
- 尚未完成 CMake configure/build `qwen3_5_cute_dsl_spike`。
- 尚未跑本地 `manifest`、`shape_bench`、`projection_correctness --m_filter=64`、`routed_grouped_micro --m_filter=64` smoke。
- 尚未同步并运行 `orin_1` R0d full 10 shape。
- 尚未经过 reviewer 对 schema、routing/top-k 口径、NNCL baseline join 和非 SOP 边界的 P0/P1 复核。

## R0 阶段所有待办

1. `Q35-MOE-CUTEDSL-R0D-ROUTED-GROUPED-MICRO`
   - 状态：`in_progress / verify next`
   - 立即动作：编译检查并修复 `cutlass_routed_grouped_micro.cu`。
   - 本地验证：`py_compile`、CMake configure/build、`manifest`、`shape_bench`、`projection_correctness --m_filter=64`、`routed_grouped_micro --m_filter=64`。
   - Orin 验证：同步到 `orin_1` 后运行 `--mode=routed_grouped_micro --m_filter=0 --warmup=5 --iters=50`，回传 CSV/日志。
   - Gate：10 shape precision/timing 完整，NaN/Inf=0，nonzero=true，`active_experts>1`，`cu_row_last_matches_routed_rows=true`，固定非 SOP/tier 字段。
   - 边界：diagnostic-only；当前 top-k 是 torch softmax/topk，不是 NNCL `SoftmaxTopk<half>`。

2. `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
   - 状态：`todo / gated`
   - 依赖：R0d 10 shape precision/timing 完整，reviewer 无 P0/P1 blocker。
   - R4 要求：启动前必须由用户确认 formal 命令、预计耗时、输出目录和停止条件。
   - Gate：复用 Q35-022 SOP-A/B/C 阈值，生成 formal R0 verdict 与 tier 判定。
   - 边界：不得用 R0a/R0b/R0c/R0d diagnostic 直接声明 SOP-A/SOP-C PASS 或 tier。

3. Python CuTeDSL route blocker closure
   - 状态：`blocked / optional unless user chooses Python route`
   - 阻塞：`cutlass._mlir` 缺失，当前 container pip indexes 找不到 `nvidia-cutlass-dsl==4.5.0.dev0`。
   - 解锁动作：提供 compatible wheel 后重跑 R0b import、elementwise、tensorop smoke。
   - 边界：当前 C++ fallback PASS 不等于 Python CuTeDSL works on Orin。

## 非 SOP 边界

- R0d 不是 fused W4A16 grouped MoE kernel。
- R0d `ratio` 不是 SOP-C ratio。
- `shape_bench`、R0c、R0d timing 都不能作为 tier evidence。
- R0e 不能在 R0d 前直接启动。
- production path 不修改；所有实现限制在 `samples/micro_bench/spike/cute_dsl/`，记忆和报告限制在 `.codex/agent_group/` 与 `analysis/`。
