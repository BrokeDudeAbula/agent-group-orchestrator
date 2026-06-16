# AUTO-20260608-122 R0G WMMA N-Warps Probe

日期：2026-06-08

## Scope

本轮延续 R0G hybrid small-row probe，只在 spike 范围内增加和验证 `wmma_n_warps` 参数：

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `samples/micro_bench/spike/cute_dsl/README.md`

不修改 production Qwen3.5 推理路径。

## Implementation

- 新增 CLI：`--wmma_n_warps=4|8|16`
- 默认值保持 `4`
- hybrid WMMA launcher 根据 `wmma_n_warps` dispatch 到 `RawGptqW4A16GroupedWmmaKernelT<4/8/16>`
- CSV/log notes 增加 `wmma_n_warps`
- hybrid timing notes 增加 `wmma_n_warps_is_probe_parameter`

## Build

- 本地构建通过：`cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`
- `orin_1` 容器 `liyang_lape` 构建通过：`cmake --build . --target qwen3_5_cute_dsl_spike -j 4`

## Remote Probe

输出目录：

- `analysis/Qwen35_cutedsl_r0g_wmma_nwarps_probe_20260608_122/`

执行矩阵：

- mode：`routed_grouped_independent_w4a16_hybrid_smallrow_smoke`
- projection：`gate_proj`
- M：`64`、`898`
- threshold：`2`、`4`
- `wmma_n_warps`：`8`、`16`
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

| threshold | wmma_n_warps | M | candidate_ms | nncl_ms | ratio |
|---:|---:|---:|---:|---:|---:|
| 2 | 8 | 64 | 1.431132 | 0.482228 | 2.967751 |
| 2 | 8 | 898 | 3.535998 | 1.122246 | 3.150822 |
| 2 | 16 | 64 | 1.456659 | 0.482032 | 3.021913 |
| 2 | 16 | 898 | 3.589336 | 0.995590 | 3.605233 |
| 4 | 8 | 64 | 1.647284 | 0.481790 | 3.419090 |
| 4 | 8 | 898 | 3.710034 | 0.931565 | 3.982580 |
| 4 | 16 | 64 | 1.875096 | 0.481864 | 3.891337 |
| 4 | 16 | 898 | 3.758381 | 0.842812 | 4.459334 |

| threshold | wmma_n_warps | geomean_ratio_M64_M898 | gate |
|---:|---:|---:|---|
| 2 | 8 | 3.057917 | FAIL |
| 2 | 16 | 3.300712 | FAIL |
| 4 | 8 | 3.690095 | FAIL |
| 4 | 16 | 4.165666 | FAIL |

## Verdict

`wmma_n_warps=8/16` 没有把 hybrid small-row path 拉近到 NNCL baseline。最佳 common geomean 为 `3.057917x`，仍明显 `>1.50x` 且远离 `<=1.20x`。

判定：

- `done / probe-only / reject_or_hold`
- `not formal`
- `not tier`
- 不 promoted

下一步若继续 CuTe/CUTLASS，不应继续只调当前 raw CUDA/WMMA attribution kernel；需要 true CUTLASS-style fused GPTQ W4A16 grouped mainloop，或转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。
