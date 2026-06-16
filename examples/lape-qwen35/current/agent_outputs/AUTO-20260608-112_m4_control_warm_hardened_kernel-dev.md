# AUTO-20260608-112 M4-Control Warm Hardened Kernel-Dev

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 修改范围

仅修改 spike 审计 schema 和文档：

- `samples/micro_bench/spike/cute_dsl/cutlass_routed_grouped_micro.cu`
- `samples/micro_bench/spike/cute_dsl/README.md`

未修改 production Qwen3.5 推理路径。

## 变更

`routed_grouped_moefc_direct_probe` 的 CSV schema 新增硬字段：

- `control_probe_only`
- `independent_candidate`

row 输出固定为：

- `control_probe_only=true`
- `independent_candidate=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

row log 同步新增逐行 `independent_candidate=false`，避免只在 summary 或 notes
中表达 control 边界。

README 新增 M4-control direct MoeFC probe CSV schema，明确该 mode 直接调用 NNCL
internal `MoeGroupGemmRunner<half, cutlass::uint4b_t>`，只能作为 control proof，
不是 independent candidate，也不能作为 SOP/tier/production evidence。

## 本地验证

本地 build 通过：

```text
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

静态检查确认：

- direct header 只有一处 `control_probe_only,independent_candidate`
- direct row 只有一处 `false,true,false,false,false,false`
- row log 包含 `independent_candidate=false`

## 判定

schema hardening 接受。该变更不改变性能结论，只降低后续 grep/CSV 审计歧义。
