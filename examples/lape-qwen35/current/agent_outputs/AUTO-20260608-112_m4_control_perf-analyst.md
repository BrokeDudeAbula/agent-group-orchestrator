# AUTO-20260608-112 M4-Control Perf-Analyst

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 口径

本轮不是独立 candidate benchmark，而是 NNCL internal control probe。

主数据：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/r0f_m4_moefc_direct_all_balanced.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/r0f_m4_moefc_direct_all_balanced_repeat.csv`

`direct_ms/nncl_ms` 是 balanced order 两次测量均值。`direct_second_ms/nncl_second_ms`
作为 steady-state second-pass 辅助指标。

## Balanced Mean Ratio

| file | family A geomean | A M64 | A M898 | family B geomean | B M64 | B M898 |
|---|---:|---:|---:|---:|---:|---:|
| first | 1.120673 | 1.798023 | 1.132173 | 1.244213 | 1.095809 | 1.292828 |
| repeat | 1.082902 | 1.615987 | 1.140007 | 1.316820 | 1.205527 | 1.300068 |
| shape-mean | 1.102040 | 1.707005 | 1.136090 | 1.280831 | 1.150668 | 1.296448 |

Balanced mean：family B 不满足 `<=1.20x`，不能作为 candidate pass。

## Steady-State Second-Pass Ratio

| file | family A geomean | A M64 | A M898 | family B geomean | B M64 | B M898 |
|---|---:|---:|---:|---:|---:|---:|
| first | 0.865832 | 1.000156 | 0.999542 | 0.943321 | 0.999770 | 0.997525 |
| repeat | 0.872462 | 0.993411 | 1.000230 | 0.941539 | 1.000767 | 0.997276 |
| shape-mean | 0.869187 | 0.996784 | 0.999886 | 0.942515 | 1.000268 | 0.997401 |

Steady-state second-pass 说明 direct internal runner 和 public NNCL kernel path 基本同量级。
M128/M256 小于 1 是 wrapper/timing/order 噪声，不可解释为独立 candidate 优势。

## 判定

M4-control 结论：`continue_probe`。

原因：

- control probe 支持结构性判断：要接近 NNCL，必须走 W4A16 MoeFC grouped 结构，而不是 dense fp16 grouped。
- balanced mean 仍有 first-pass 噪声，family B 超过 `<=1.20x`。
- direct path 调用 NNCL internal runner，不是独立 CuTe/CUTLASS candidate，不可 promotion。
