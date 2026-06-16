# AUTO-20260608-113 R0G Independent W4A16 Gap Audit

任务：`Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-GAP-AUDIT`

父任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## Scope

本轮只做 source-level gap audit，不修改 production path，不创建 formal candidate，不把 M4 dispatch promoted。

输出：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_gap_audit_20260608_192510/report.md`

## Findings

- R0F/R1-probe 已在 M5 收口为 `reject_or_hold`。
- M4 dispatch 达到 NNCL 同量级，但直接调用 `dispatch_moe_gemm_to_cutlass<half, cutlass::uint4b_t, Sm80, EpilogueOpNoBias>`，且 include NNCL `moe_cutlass_group_gemm_template.h`。
- NNCL grouped W4A16 性能来自 `DefaultGemmGrouped -> MoeFCGemm -> DqMmaMultistage finegrained scale cp.async` 这条扩展链，不是标准 CUTLASS grouped dense path。
- 当前没有 independent candidate kernel，因此不能启动 Candidate NCU Isolation 或 formal promotion。

## Next Gate

若继续 CuTe/CUTLASS independent 路线，必须新建：

```text
Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE
```

R0G-M0 必须禁止把以下路径作为 candidate：

- `MoeGroupGemmRunner`
- `dispatch_moe_gemm_to_cutlass`
- NNCL `MoeFCGemm`
- 直接复用 NNCL `DqMmaMultistage` / `IteratorScale` / `GemmMoeProblemVisitor` 而声明 independent

## Flags

```text
valid_for_sop_a=false
valid_for_sop_c=false
tier_eligible=false
production_path_changed=false
formal_candidate_created=false
independent_candidate=false
```
