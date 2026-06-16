# AUTO-20260609-124 R0G Hybrid Single-Kernel Probe - kernel-dev/perf-analyst

## 摘要

为 `routed_grouped_independent_w4a16_hybrid_smallrow_smoke` 新增 probe-only 参数：

`--hybrid_single_kernel=0|1`

新路径把原 hybrid WMMA tile kernel 与 small-row vec4 kernel 合并到一次 launch 中，仅用于归因。默认值仍为 `0`，因此不改变 AUTO-123 及此前默认行为。

## 修改文件

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`

## 验证

- 本地构建通过：
  `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`
- 已同步到 `orin_1`。
- 远端构建通过：
  `cd /workspace/liyang/workspace/lape/build && cmake --build . --target qwen3_5_cute_dsl_spike -j 4`
- 远端 probe 输出：
  `analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_probe_20260609_124`
- 本地报告：
  `analysis/Qwen35_cutedsl_r0g_hybrid_single_kernel_probe_20260609_124/report.md`

## 结果

同一 build、同一 `threshold=2`、`wmma_n_warps=8`、`wmma_packed_loader=1`：

| variant | M64 ratio | M898 ratio | geomean | launches |
|---|---:|---:|---:|---:|
| dual-kernel control | 2.941212x | 3.117430x | 3.028039x | 2 |
| single-kernel probe | 2.297688x | 2.704718x | 2.492910x | 1 |

candidate 相对同 build dual-kernel control 的 speedup：

- M64：`1.278698x`
- M898：`1.146003x`

CSV guard：

- 检查 4 行
- `guard_errors=0`
- 所有行 `precision_pass=true`
- 所有行 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`
- 所有行 `independent_candidate=false`、`candidate_audit_pending=true`
- candidate NNCL usage flags 均为 false；baseline NNCL usage flag 为 true

## 决策

`continue_probe_or_hold / not formal / not tier / not production`。

AUTO-124 证明 launch fusion 有收益，但收益不足。最佳 geomean 仍为 `2.492910x`，远高于目标 `<=1.20x`，且与 AUTO-123 最佳 `2.490867x` 基本持平。不得 promoted。正式路线仍需要新建 independent CUTLASS-style fused GPTQ W4A16 grouped mainloop task，并重新走 SOP-A/B/C。
