# AUTO-20260608-112 M4-Control Warm Hardened Orchestration

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 本轮目标

根据 reviewer 对 warm-state control 的 P2 审计，补齐硬字段：

- `control_probe_only=true`
- `independent_candidate=false`

并重新在 `orin_1` 跑 smoke/full/repeat，形成无歧义的 M4-control warm-state evidence。

## 结果

实现：

- `routed_grouped_moefc_direct_probe` CSV 新增 `control_probe_only`、`independent_candidate`
- row log 新增逐行 `independent_candidate=false`
- README 新增 direct MoeFC control schema

验证：

- 本地 build PASS
- `orin_1` build PASS
- hardened smoke PASS
- hardened full 10 shape PASS
- hardened repeat 10 shape PASS

Evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/r0f_m4_moefc_direct_warm_hardened_all.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/r0f_m4_moefc_direct_warm_hardened_all_repeat.csv`

## 性能摘要

Shape-mean over repeats：

- family A direct-vs-NNCL geomean：`0.999769`
- family B direct-vs-NNCL geomean：`1.015588`
- family A second-pass geomean：`0.996385`
- family B second-pass geomean：`0.996818`

所有 21 条 CSV 数据行：

- `precision_pass=true`
- `control_probe_only=true`
- `independent_candidate=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## 当前状态

任务保持：

```text
in_progress / M4-control warm-state hardened done / probe-only / not production / continue_probe
```

解释：

- M4-control warm-state hardened 证明 NNCL internal MoeFC runner 与 public NNCL baseline 同量级。
- dense fp16 serial/grouped independent probe 仍不达标。
- direct path 是 NNCL internal control，不是 independent candidate，不允许 formal promotion。

下一步只能新建 independent fused W4A16 MoeFC grouped candidate formal task，或转向
`Q35-MOE-NNCL-GROUPED-TARGETED-R0`。
