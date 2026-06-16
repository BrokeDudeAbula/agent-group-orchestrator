# AUTO-20260609-123 R0G WMMA Packed Loader Probe

日期：2026-06-09

## Scope

本轮只修改 spike：

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `samples/micro_bench/spike/cute_dsl/README.md`

不修改 production Qwen3.5 推理路径，不调用 NNCL MoeFC/dispatch 作为 candidate。

## Implementation

- 新增 CLI：`--wmma_packed_loader=0|1`
- 默认值：`0`，保持 AUTO-122 历史可比性
- `wmma_packed_loader=1` 时，WMMA B-tile loader 按 GPTQ packed int32 word 展开：
  - 每个 packed word 覆盖 8 个 K 元素
  - scale 在当前 G128 group 内只读取一次
  - 目标是减少原始逐 half 元素解码路径的 qweight/scale 读取放大
- CSV/log notes 增加 `wmma_packed_loader`
- timing notes 增加 `wmma_packed_loader_is_probe_parameter`

## Build

- 本地构建通过：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`
- `orin_1` 容器 `liyang_lape` 构建通过：`cmake --build . --target qwen3_5_cute_dsl_spike -j 4`

## Remote Probe

输出目录：

- `analysis/Qwen35_cutedsl_r0g_wmma_packed_loader_probe_20260609_123/`

执行矩阵：

- mode：`routed_grouped_independent_w4a16_hybrid_smallrow_smoke`
- projection：`gate_proj`
- M：`64`、`898`
- threshold：`2`、`4`
- `wmma_n_warps`：`8`、`16`
- `wmma_packed_loader`：`1`
- warmup/iters：`5/50`

## Guard

8 条 CSV 均通过：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `independent_candidate=false`
- `candidate_audit_pending=true`
- `precision_pass=true`
- `candidate_uses_nncl_moefc=false`
- `candidate_uses_nncl_moegroupgemm=false`
- `candidate_uses_dispatch_moe_gemm_to_cutlass=false`
- `baseline_uses_nncl_moegroupgemm=true`

## Results

| threshold | warps | packed | M | candidate_ms | nncl_ms | ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 8 | 1 | 64 | 1.286125 | 0.482444 | 2.665852 |
| 2 | 8 | 1 | 898 | 2.408466 | 1.034845 | 2.327368 |
| 2 | 16 | 1 | 64 | 1.201869 | 0.482659 | 2.490100 |
| 2 | 16 | 1 | 898 | 2.556600 | 0.938769 | 2.723355 |
| 4 | 8 | 1 | 64 | 1.429300 | 0.482017 | 2.965250 |
| 4 | 8 | 1 | 898 | 2.712841 | 1.037648 | 2.614413 |
| 4 | 16 | 1 | 64 | 1.486049 | 0.482308 | 3.081118 |
| 4 | 16 | 1 | 898 | 3.050110 | 0.968515 | 3.149266 |

| threshold | warps | packed | geomean_ratio_M64_M898 | gate |
|---:|---:|---:|---:|---|
| 2 | 8 | 1 | 2.490867 | FAIL |
| 2 | 16 | 1 | 2.604117 | FAIL |
| 4 | 8 | 1 | 2.784311 | FAIL |
| 4 | 16 | 1 | 3.115006 | FAIL |

## Verdict

`wmma_packed_loader=1` 有真实收益，最佳 geomean 从 AUTO-122 的 `3.057917x` 改为 `2.490867x`，但仍明显 `>1.50x` 且远离 `<=1.20x`。

判定：

- `done / probe-only / reject_or_hold`
- `not formal`
- `not tier`
- 不 promoted

下一步如果继续 raw CUDA/WMMA line，应优先验证 small-row SIMT 路径和双 launch 成本是否还能继续压缩；若目标是 formal candidate，应改为 true CUTLASS-style fused GPTQ W4A16 grouped mainloop。
