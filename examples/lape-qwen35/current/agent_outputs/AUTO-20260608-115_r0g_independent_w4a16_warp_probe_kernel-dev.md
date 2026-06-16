# AUTO-20260608-115 R0G independent W4A16 warp probe

日期：2026-06-08

## Scope

补齐 `routed_grouped_independent_w4a16_smoke` 的 warp-reduce raw CUDA kernel evidence。该输出为 probe-only，不修改 production Qwen3.5 推理路径，不作为 SOP/tier evidence。

## Evidence

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/report.md`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/warp_m64_orin1.csv`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_warp_probe_20260608_115/warp_m898_orin1.csv`

## Result

| shape | candidate_ms | nncl_ms | ratio | launches/iter | precision_pass |
|---|---:|---:|---:|---:|---|
| A/M64/gate_proj | 3.442426 | 0.486694 | 7.073074 | 37 | true |
| A/M898/gate_proj | 21.543930 | 1.409498 | 15.284829 | 117 | true |

tile8 warp kernel 试验更差，M64 ratio 约 `12.493918x`，M898 ratio 约 `15.895572x`，已回退。当前代码保留 single-output warp-reduce 版本。

## Boundary

CSV 中 probe-only / audit 字段保持：

- `candidate_uses_nncl_moefc=false`
- `candidate_uses_nncl_moegroupgemm=false`
- `candidate_uses_dispatch_moe_gemm_to_cutlass=false`
- `candidate_uses_nncl_cutlass_extension_headers=false`
- `baseline_uses_nncl_moegroupgemm=true`
- `translation_unit_includes_nncl_headers=true`
- `control_probe_only=false`
- `independent_candidate=false`
- `candidate_audit_pending=true`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Decision

继续 probe，但不 promoted。下一步应做 spike-local single-launch grouped raw W4A16 kernel，把 `candidate_launches_per_iter` 从 active expert 数降到 1，用于分离 launch overhead 与 raw int4 SIMT decode/matmul 算力差距。即使 single-launch 通过，也仍是 smoke/probe-only，formal promotion 必须新建任务并重走 SOP-A/B/C。
