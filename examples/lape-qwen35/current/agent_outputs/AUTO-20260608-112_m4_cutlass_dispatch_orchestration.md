# AUTO-20260608-112 M4 CUTLASS Dispatch Orchestration

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 本轮目标

完成 wrapper-isolation 子探针：

- bypass NNCL public `MoeGroupGemm`
- bypass `MoeGroupGemmRunner`
- direct dispatch CUTLASS `MoeFCGemm` via NNCL template
- 保持 probe-only、control-only、not independent candidate

## 结果

实现：

- 新增 `routed_grouped_moefc_cutlass_dispatch_probe`
- 新增 `moefc_cutlass_dispatch_probe.cu`
- CSV/log 增加并固定：
  - `bypasses_nncl_public_op=true`
  - `bypasses_nncl_runner=true`
  - `uses_nncl_cutlass_extension_headers=true`
  - `control_probe_only=true`
  - `independent_candidate=false`
  - `valid_for_sop_a=false`
  - `valid_for_sop_c=false`
  - `tier_eligible=false`

验证：

- 本地 build PASS
- `orin_1` sync PASS
- `orin_1` Release/sm87 spike build PASS
- M64 smoke PASS
- full 10 shape run1 PASS
- full 10 shape run2 PASS

Evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/dispatch_probe_summary.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/moefc_cutlass_dispatch_full_run1.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/moefc_cutlass_dispatch_full_run2.csv`

## 性能摘要

- full run1 family A/B dispatch-vs-NNCL geomean：`1.001874/1.032655`
- full run2 family A/B dispatch-vs-NNCL geomean：`0.999701/1.011785`
- full run1 hot M898 A/B：`1.000288/0.996715`
- full run2 hot M898 A/B：`0.999838/0.999465`
- small M64 无灾难性退化；run1 family B `M64=1.111202`，run2 family B `M64=0.999547`

## 当前状态

```text
in_progress / M4 CUTLASS dispatch wrapper-isolation done / probe-only / not production / continue_probe
```

解释：

- 该 probe 证明 NNCL public op / `MoeGroupGemmRunner` wrapper 开销不是主要差距来源。
- 它仍复用 NNCL CUTLASS extension headers 和 `MoeFCGemm`，不是 independent candidate。
- 不允许 promoted，不允许作为 SOP/tier/R1/R3/production evidence。
- 若继续 CuTe/CUTLASS，必须新建 independent fused GPTQ W4A16 MoeFC grouped candidate task并重新走 SOP-A/B/C；另一选择是转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。
