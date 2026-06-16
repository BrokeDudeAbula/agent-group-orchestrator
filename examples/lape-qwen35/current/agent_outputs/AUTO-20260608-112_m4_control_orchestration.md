# AUTO-20260608-112 M4-Control Orchestration

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 本轮目标

在 M3 grouped dense fp16 相对 NNCL 仍约 4x 后，补做一个 control probe：
直接调用 NNCL internal CUTLASS `MoeGroupGemmRunner<half, cutlass::uint4b_t>`，
判断差距是否来自缺少 W4A16 MoeFC grouped 结构。

## 结果

实现并验证：

- `--mode=routed_grouped_moefc_direct_probe`
- same packed W4A16 weights
- same input
- same `cu_row`
- same default NNCL MoeGroupGemm config
- balanced order：`direct -> NNCL -> NNCL -> direct`

Evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/r0f_m4_moefc_direct_all_balanced.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/r0f_m4_moefc_direct_all_balanced_repeat.csv`

## 性能摘要

Balanced mean shape-mean over repeats：

- family A geomean：`1.102040`
- family B geomean：`1.280831`

Steady-state second-pass shape-mean over repeats：

- family A geomean：`0.869187`
- family B geomean：`0.942515`

解释：

- steady-state control 证明 direct internal MoeFC runner 与 public NNCL 路径基本同量级。
- balanced mean 仍显示 first-pass/状态噪声，且 family B 超过 `<=1.20x`。
- 因 direct path 是 NNCL internal runner control，不是 independent candidate，不能 formal promotion。

## 当前状态

任务状态从 M3 `blocked` 调整为：

```text
in_progress / M4-control direct MoeFC proof done / probe-only / not production / continue_probe
```

下一步建议：

- 不继续 dense fp16 grouped candidate。
- 若继续 CuTe/CUTLASS，需新建 independent fused GPTQ W4A16 MoeFC grouped candidate task。
- 或转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0` 做 NNCL grouped 周边 profile/ROI。

所有 M4-control 输出仍固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
