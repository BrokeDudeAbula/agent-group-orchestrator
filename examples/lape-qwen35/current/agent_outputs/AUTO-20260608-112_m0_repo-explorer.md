# AUTO-20260608-112 M0 Repo Explorer

## 结论

只读检查完成。当前 spike 入口为 `qwen3_5_cute_dsl_spike`，`samples/micro_bench/spike/cute_dsl/CMakeLists.txt` 中默认 `LAPE_BUILD_SPIKE_CUTE_DSL=OFF`，顶层 CMake 仅做 isolated spike 接入，不影响 production path。

## 关键事实

- mode 分发在 `samples/micro_bench/spike/cute_dsl/main.cc`，当前包含 `manifest/toolchain_smoke/shape_bench/projection_correctness/routed_grouped_micro/routed_grouped_micro_nncl_paired/r0e_sop_a_precision/r0e_sop_b_occupancy/r0e_sop_c_routed_grouped/help`。
- 10 个 SOP-C shape 定义在 `samples/micro_bench/spike/cute_dsl/spike_common.h`。
- `cutlass_routed_grouped_micro.cu` 原 dense helper 仍有 `OpClassSimt + Sm70`。
- timed loop 污染点包括 `RunCutlassDense` 内分配 `C`、launch 后 `cudaStreamSynchronize`、column-major 到 row-major `.contiguous()`，以及 `TimeCandidate` / `TimeCandidateProjection` 反复调用完整 candidate 构造。

## 历史 Evidence

- R0D1 diagnostic evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d1_nncl_paired_orin_1_20260608_083804/`，10/10 diagnostic PASS，但明确 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- R0E formal evidence：`analysis/Qwen35_cutedsl_w4a16_grouped_r0e_sop_abc_orin_1_20260608_113730/`，SOP-A/B PASS，SOP-C gate fail，`overall_pass=false`，`tier_eligible=false`。

## M0 结论

当前只能作为 R0D1 diagnostic PASS 与 R0E formal FAIL 的事实来源，不能作为 R1/tier/production 证据。M1 必须先建立可审计 TensorOp dense probe path，M2 前所有 routed timing 均应标记为 contaminated diagnostic。
