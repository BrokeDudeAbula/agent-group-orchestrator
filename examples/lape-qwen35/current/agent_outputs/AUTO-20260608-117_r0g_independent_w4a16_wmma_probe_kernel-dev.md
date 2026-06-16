# AUTO-20260608-117 R0G independent W4A16 WMMA probe

日期：2026-06-08

## Scope

实现并验证 spike-local `routed_grouped_independent_w4a16_wmma_smoke`：

- 不修改 production Qwen3.5 推理路径。
- 不调用 NNCL `MoeFCGemm`、`MoeGroupGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 作为 candidate。
- same-run NNCL `MoeGroupGemm` 只作为 baseline/diff。
- 所有输出保持 probe-only。

## Code Changes

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`

核心实现：

- 新增 mode：`routed_grouped_independent_w4a16_wmma_smoke`。
- 新增 `RawGptqW4A16GroupedWmmaKernel`。
- raw HF GPTQ `qweight/scales` 在 kernel 内解码到 shared-memory B tile。
- 使用 CUDA WMMA `m16n16k16` Tensor Core fragments 做 fp16 MMA。
- 4-warp 版本每个 block 覆盖同一 M tile 下 4 个 N tile。
- timed loop 外预构造 `tile_row_begin/tile_rows/tile_expert` 与 raw `qweight/scales` device pointer arrays。
- 每 iteration 只 launch 一个 grouped WMMA kernel。
- CSV `candidate_launches_per_iter=1`。

## Verification

本地构建 PASS：

```text
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

`orin_1` 同步与构建 PASS：

```text
bash sync_orin_lape_build.sh --target orin_1 --source /workspace/liyang/lape_a6d6bfb9
cmake .. -DLAPE_BUILD_SPIKE_CUTE_DSL=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87
cmake --build . --target qwen3_5_cute_dsl_spike -j 4
```

Smoke results：

| candidate | shape | candidate_ms | nncl_ms | ratio | launches/iter | precision_pass |
|---|---|---:|---:|---:|---:|---|
| single-warp WMMA | A/M64/gate_proj | 2.436837 | 0.482528 | 5.050145 | 1 | true |
| single-warp WMMA | A/M898/gate_proj | 7.694731 | 0.978774 | 7.861604 | 1 | true |
| 4-warp WMMA | A/M64/gate_proj | 2.224506 | 0.135846 | 16.375158 | 1 | true |
| 4-warp WMMA | A/M898/gate_proj | 5.281041 | 0.918199 | 5.751521 | 1 | true |

4-warp M64 的 same-run NNCL baseline 明显偏低；即按前序 `~0.48 ms` baseline 估算，candidate 仍约 `4.6x`，不影响 fail 结论。

NCU candidate isolation：

- filter：`regex:RawGptqW4A16GroupedWmmaKernel`
- captured kernel：`unnamed>::RawGptqW4A16GroupedWmmaKernel(...)`
- duration：`1.45 ms / 1.55 ms`
- achieved occupancy：`76.97% / 76.15%`
- no `MoeFCGemm` or `MoeGroupGemm` in NCU output

Evidence：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_wmma_probe_20260608_117/report.md`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_wmma_probe_20260608_117/wmma_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_wmma_probe_20260608_117/wmma_m898_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_wmma_probe_20260608_117/wmma4_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_wmma_probe_20260608_117/wmma4_m898_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_wmma_probe_20260608_117/wmma4_ncu_m64.csv`

## Boundary

CSV/log fields remain:

- `independent_candidate=false`
- `candidate_audit_pending=true`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Decision

Do not promote. WMMA Tensor Core path improves raw SIMT, but 4-warp WMMA still remains `5x+` from same-run NNCL on hot M898 and does not approach `<=1.20x`.

Further useful work requires a true independent CUTLASS-style fused GPTQ W4A16 MoeFC grouped mainloop or a new formal task. Naive WMMA smoke should remain probe-only and not tier eligible.
