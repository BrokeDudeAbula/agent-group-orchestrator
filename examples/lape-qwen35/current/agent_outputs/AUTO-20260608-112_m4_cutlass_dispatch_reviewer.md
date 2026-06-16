# AUTO-20260608-112 M4 CUTLASS Dispatch Reviewer

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 审查结论

未发现 P0/P1。

P2 / residual risk：

- 该 mode 名称含 `cutlass_dispatch`，容易被误读为 independent CuTe/CUTLASS candidate；报告、README、CSV/log 已用硬字段缓解：`control_probe_only=true`、`independent_candidate=false`、SOP/tier 三项 false。
- 该 probe 绕过 NNCL public op 和 `MoeGroupGemmRunner`，但仍直接使用 NNCL 模板和 `MoeFCGemm` kernel 类型；任何 formal promotion 都必须另建 independent candidate task 并重新走 SOP-A/B/C。

## Evidence 边界

可接受：

- 用于判断 NNCL public wrapper / runner overhead 是否显著。
- 用于解释 M3 dense fp16 grouped probe 与 NNCL baseline 差距不是 public wrapper 层造成。

不可接受：

- 不可作为 SOP-A/SOP-C PASS。
- 不可作为 tier eligible。
- 不可作为 R1/R3/production 授权依据。
- 不可替代 independent fused GPTQ W4A16 MoeFC grouped candidate。

## 字段复核

`moefc_cutlass_dispatch_m64_smoke.csv`、`moefc_cutlass_dispatch_full_run1.csv`、`moefc_cutlass_dispatch_full_run2.csv` 均已由本轮解析脚本 fail-closed 校验：

- `precision_pass=true`
- `control_probe_only=true`
- `independent_candidate=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## 当前状态建议

保持：

```text
in_progress / M4 CUTLASS dispatch wrapper-isolation done / probe-only / not production / continue_probe
```

下一步只能是新建 independent fused W4A16 MoeFC grouped candidate task，或转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`。
