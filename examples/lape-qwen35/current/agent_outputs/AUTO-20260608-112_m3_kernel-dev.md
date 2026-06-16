# AUTO-20260608-112 M3 Kernel Dev

## 结论

M3 structural grouped dense probe 已在 spike 范围内实现并修正输入口径。该实现只覆盖 `samples/micro_bench/spike/cute_dsl/` 和必要 CMake 接入，不修改 production Qwen3.5 推理路径。

## 修改范围

- `CMakeLists.txt`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`

## 实现内容

- 新增 mode：`--mode=routed_grouped_dense_probe`。
- 新增 candidate path：`cutlass_grouped_dense_fp16_single_projection`。
- 使用 CUTLASS `GemmGrouped` TensorOp dense fp16，把同一 projection 的多 expert dense GEMM 合成单次 grouped launch。
- 保留 serial per-expert TensorOp dense fp16 path 作为同输入对照。
- same-run baseline 仍使用 NNCL grouped `MoeGroupGemm`。
- CSV 增加 `grouped_ms`、`serial_ms`、`nncl_ms`、`grouped_vs_nncl_ratio`、`serial_vs_nncl_ratio`、`grouped_vs_serial_ratio`、`serial_launches_per_iter`、`grouped_launches_per_iter`。

## 关键修正

`down_proj` family B 不能直接使用 routed hidden `[M,2048]` 作为输入。M3 已改为在计时区外构造：

- `gate = gate_proj(hidden)`
- `up = up_proj(hidden)`
- `act = silu(gate) * up`
- `down_proj` grouped/serial/NNCL 都使用同一 `act` 输入

CSV 中 family A 的 `input_source=bundle_hidden_states_routed_prefix`，family B 的 `input_source=precomputed_silu_gate_mul_up_routed_prefix`。

## 构建

- 本地构建 PASS：`build_cute_dsl_spike_local`，target `qwen3_5_cute_dsl_spike`。
- `orin_1` Release/sm87 构建 PASS：
  - `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/build_grouped_dense_probe.log`
  - `build_rc=0`

## 边界

该 probe 是 dense fp16 single-projection grouped launch 上限验证：

- 不是 W4A16 fused decode。
- 不是完整 MoE fused path。
- 不是 SOP-A/SOP-C/tier evidence。
- 所有输出保持 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
