# AUTO-20260609-126 R0G Small-Row Cols Probe - kernel-dev/perf-analyst

## 摘要

在 AUTO-125 的最佳 common 参数基础上，新增并验证 small-row SIMT 列粒度 probe：

- `--small_row_cols_per_warp=4|8|16`
- 固定 `--hybrid_small_row_threshold=1`
- 固定 `--wmma_n_warps=16`
- 固定 `--wmma_packed_loader=1`
- 固定 `--hybrid_single_kernel=1`
- M64/M898，`gate_proj`

本轮只修改 spike-only 路径，不修改 production Qwen3.5 推理路径。`small_row_cols_per_warp=4` 是 same-build control，保持旧 vec4 行为。

## 代码范围

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `samples/micro_bench/spike/cute_dsl/README.md`

主要实现：

- 将 `RawGptqW4A16GroupedSmallRowsVec4Kernel` 改为 `RawGptqW4A16GroupedSmallRowsColsKernel<4|8|16>`。
- 将 `RawGptqW4A16GroupedHybridSingleKernelT` 增加 `kSmallColsPerWarp` 模板参数。
- 新增 CLI 参数 `--small_row_cols_per_warp=4|8|16`，默认 `4`。
- CSV schema 不新增列；审计字段写入 `notes`：`small_row_cols_per_warp=<N>`。

## Evidence

- 本地/远端输出目录：
  `analysis/Qwen35_cutedsl_r0g_smallrow_cols_probe_20260609_126/`
- 报告：
  `analysis/Qwen35_cutedsl_r0g_smallrow_cols_probe_20260609_126/report.md`

## 构建

- 本地构建通过：
  `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`
- `orin_1` 同步通过：
  `sync_orin_lape_build.sh --target orin_1 --source /workspace/liyang/lape_a6d6bfb9 --sync-only --no-clean`
- `orin_1` 容器构建通过：
  `cd /workspace/liyang/workspace/lape/build && cmake --build . --target qwen3_5_cute_dsl_spike -j 4`

## Guard

- CSV 文件：6
- CSV 行：6
- `guard_errors=0`
- 所有行 `precision_pass=true`
- 所有行 `candidate_launches_per_iter=1`
- 所有行固定 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`
- 所有行固定 `independent_candidate=false`、`candidate_audit_pending=true`
- candidate NNCL usage flags 均为 false；baseline NNCL usage flag 为 true

## 结果

| small_row_cols_per_warp | geomean | M64 ratio | M898 ratio |
|---:|---:|---:|---:|
| 4 | 2.209285x | 2.043727x | 2.388255x |
| 8 | 2.191459x | 2.112438x | 2.273437x |
| 16 | 2.684973x | 2.850827x | 2.528768x |

Best common combo：

- `small_row_cols_per_warp=8`
- geomean `2.191459x`
- M64 ratio `2.112438x`
- M898 ratio `2.273437x`

## 结论

`small_row_cols_per_warp=8` 相比 same-build `cols=4` 只改善约 `0.8%` geomean，且 M64 退化；`cols=16` 明显退化。small-row SIMT 每 warp 列数不是当前 raw CUDA/WMMA attribution kernel 的主导瓶颈。

状态：`done / reject_or_hold / probe-only / not formal / not tier / not production`。

AUTO-126 不能作为 SOP-A/SOP-C evidence、tier evidence 或 production 授权。当前 raw CUDA/WMMA attribution line 不应继续做类似局部参数 sweep；后续若要接近 NNCL baseline，应转向 true independent CUTLASS-style fused GPTQ W4A16 grouped mainloop，或切到 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。
