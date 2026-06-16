# AUTO-20260608-112 M4 CUTLASS Dispatch Kernel-Dev

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 实现范围

只修改 spike / analysis / agent_group 范围，未修改 production Qwen3.5 推理路径。

代码变更：

- 新增 `samples/micro_bench/spike/cute_dsl/moefc_cutlass_dispatch_probe.cu`
- 更新 `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- 更新 `samples/micro_bench/spike/cute_dsl/spike_common.h`
- 更新 `samples/micro_bench/spike/cute_dsl/main.cc`
- 更新 `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- 更新 `samples/micro_bench/spike/cute_dsl/README.md`

## 新增 Mode

`routed_grouped_moefc_cutlass_dispatch_probe`

语义：

- 绕过 NNCL public `MoeGroupGemm`
- 绕过 `MoeGroupGemmRunner`
- 直接调用 NNCL 模板 `dispatch_moe_gemm_to_cutlass<half, cutlass::uint4b_t, Sm80, EpilogueOpNoBias>`
- 仍复用 NNCL CUTLASS extension headers 和 `MoeFCGemm` kernel 类型

CSV/log 硬字段：

- `bypasses_nncl_public_op=true`
- `bypasses_nncl_runner=true`
- `uses_nncl_cutlass_extension_headers=true`
- `control_probe_only=true`
- `independent_candidate=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## 本地验证

```bash
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

结果：PASS，`qwen3_5_cute_dsl_spike` 链接成功。

## 边界

该 mode 是 wrapper-isolation control，不是 independent CuTe/CUTLASS candidate，不得作为 SOP-A/SOP-C/tier/R1/R3/production evidence。
