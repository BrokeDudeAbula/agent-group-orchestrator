# AUTO-20260608-112 M1 Kernel Dev

## 结论

M1 Tensor Core sanity 的 spike-local 代码路径已完成并通过 `orin_1` Release 构建。修改范围只在 isolated spike 与必要 CMake 接入内，不修改 production Qwen3.5 推理路径。

## 代码范围

- 顶层 `CMakeLists.txt` 接入 `samples/micro_bench/spike/cute_dsl`，仍为 `EXCLUDE_FROM_ALL`。
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`：
  - `LAPE_BUILD_SPIKE_CUTE_DSL=OFF` 默认保持。
  - 新增 `LAPE_CUTE_DSL_ENABLE_R0E_FORMAL_MODES=OFF` 默认关闭 archived R0E formal modes。
- `spike_common.h`：
  - 固定 `op_class=TensorOp`、`arch=Sm80/Sm87-compatible`、`candidate_path=cutlass_tensorop_dense_fp16`。
  - 保留 `tensorop_align8_default` 与 `tensorop_align8_epilogue_scalar` variant 字段。
- `cutlass_shape_bench.cu`：
  - dense shape bench 使用 `OpClassTensorOp + Sm80`。
  - A/B alignment 保持默认 align8；若默认 epilogue 不可用，再尝试 scalar epilogue，不走 `AlignmentA/B=1`。
  - CSV/log 每行输出 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- `cutlass_routed_grouped_micro.cu`：
  - routed diagnostic dense helper 切到 TensorOp path，保留 SIMT helper 为 unused fallback。
  - 默认宏未开启时，R0E writer fail-closed 写 false。
- `main.cc`：
  - 默认 help/parse/dispatch 不暴露 `r0e_sop_*` modes。

## 构建证据

远端目标：

- target：`orin_1`
- container：`liyang_lape`
- repo：`/workspace/liyang/workspace/lape`
- build dir：`/workspace/liyang/workspace/lape/build_cutedsl_r0f_align1`
- binary：`build_cutedsl_r0f_align1/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike`

CMake cache：

- `CMAKE_BUILD_TYPE=Release`
- `CMAKE_CUDA_ARCHITECTURES=87`
- `LAPE_BUILD_SPIKE_CUTE_DSL=ON`
- `LAPE_CUTE_DSL_ENABLE_R0E_FORMAL_MODES=OFF`

日志：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m1_epilogue_scalar.log`
- `build_rc=0`

历史失败保留：

- `build_m1_align1.log` 记录 `AlignmentA/B=1` 导致 CUTLASS `cp_async_zfill<SizeInBytes=2>` static assert，不作为当前路径。

## 边界

M1 只证明 dense fp16 TensorOp sanity。它不是 W4A16 fused decode、不是 grouped launch、不是 SOP-C，也不是 tier evidence。
