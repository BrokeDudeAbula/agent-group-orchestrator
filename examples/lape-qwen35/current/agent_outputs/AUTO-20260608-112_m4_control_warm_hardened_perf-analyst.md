# AUTO-20260608-112 M4-Control Warm Hardened Perf-Analyst

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 口径

本轮只分析 NNCL internal control probe：

- direct：NNCL internal `MoeGroupGemmRunner<half, cutlass::uint4b_t>`
- baseline：same-run public NNCL grouped `MoeGroupGemm`
- `direct_ms/nncl_ms`：prewarm 后 `direct -> NNCL -> NNCL -> direct` 的 first/second 均值
- `direct_prewarm_ms/nncl_prewarm_ms`：只解释 cold/warm 状态，不进入 candidate gate

主数据：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/r0f_m4_moefc_direct_warm_hardened_all.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/r0f_m4_moefc_direct_warm_hardened_all_repeat.csv`

## Ratio

| file | family | direct geomean | M64 | M898 | prewarm geomean | first geomean | second geomean |
|---|---|---:|---:|---:|---:|---:|---:|
| first | A | 1.001604 | 1.004026 | 0.999987 | 1.385105 | 1.002919 | 0.999951 |
| first | B | 1.022957 | 0.998408 | 1.002118 | 1.428485 | 1.044495 | 0.999794 |
| repeat | A | 0.997920 | 0.988749 | 1.000424 | 1.465250 | 1.002094 | 0.992794 |
| repeat | B | 1.008013 | 0.998928 | 1.001723 | 1.370184 | 1.021779 | 0.993805 |

Shape-mean over repeats：

| family | direct geomean | M64 | M898 | second-pass geomean | second M64 | second M898 |
|---|---:|---:|---:|---:|---:|---:|
| A | 0.999769 | 0.996388 | 1.000205 | 0.996385 | 0.986872 | 0.999880 |
| B | 1.015588 | 0.998668 | 1.001921 | 0.996818 | 0.998328 | 1.000389 |

## Flags

Hardened smoke/full/repeat 共 21 行：

- `precision_pass=true`
- `control_probe_only=true`
- `independent_candidate=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

`bad_count=0`。

## 判定

Hardened warm-state control 证明 NNCL internal MoeFC runner 与 public NNCL baseline
在 post-prewarm paired 口径下同量级。

但 direct path 不是 independent CuTe/CUTLASS candidate。该结果不能作为 SOP-C/tier
或 formal promotion 依据。
