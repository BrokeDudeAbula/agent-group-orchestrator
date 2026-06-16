# AUTO-20260608-112 M4 CUTLASS Dispatch Perf-Analyst

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## Baseline

same-run public NNCL grouped `MoeGroupGemm`。

ratio：

```text
dispatch_vs_nncl_ratio = dispatch_ms / nncl_ms
```

## Ratio 汇总

| run | family | rows | geomean | min | max | M64 | M898 |
|---|---:|---:|---:|---:|---:|---:|---:|
| m64_smoke | A | 1 | 0.970332 | 0.970332 | 0.970332 | 0.970332 | NA |
| m64_smoke | B | 1 | 1.001961 | 1.001961 | 1.001961 | 1.001961 | NA |
| full_run1 | A | 5 | 1.001874 | 0.999670 | 1.005646 | 1.005646 | 1.000288 |
| full_run1 | B | 5 | 1.032655 | 0.996715 | 1.111202 | 1.111202 | 0.996715 |
| full_run2 | A | 5 | 0.999701 | 0.999315 | 1.000248 | 0.999315 | 0.999838 |
| full_run2 | B | 5 | 1.011785 | 0.999465 | 1.045302 | 0.999547 | 0.999465 |

## 字段审计

CSV 行数：

- M64 smoke：2 rows
- full run1：10 rows
- full run2：10 rows

全部 rows：

- `precision_pass=true`
- `control_probe_only=true`
- `independent_candidate=false`
- `bypasses_nncl_public_op=true`
- `bypasses_nncl_runner=true`
- `uses_nncl_cutlass_extension_headers=true`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `nan_count_vs_nncl=0`
- `inf_count_vs_nncl=0`
- `nonzero_vs_nncl>0`

## 解释

full run1/run2 的 family A/B geomean 都低于 `1.20x`，但该 probe 仍复用 NNCL CUTLASS extension headers 和 `MoeFCGemm`，不是 independent candidate。结论只能是：NNCL public op / `MoeGroupGemmRunner` wrapper 开销不是 R0E/M3 性能差距主因。

当前选择仍是 `continue_probe`，不能 promoted。
