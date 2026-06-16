# AUTO-20260608-120 R0G Hybrid Small-Row Probe

## Scope

- Goal: continue `Q35-MOE-CUTEDSL-R0F-R1-PROBE` with a probe-only small-row-aware R0G experiment after AUTO-119 shared-A WMMA.
- Write scope used: `samples/micro_bench/spike/cute_dsl/`, `.codex/agent_group/`, `analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/`.
- Production path changes: none.
- Formal/SOP/tier status: none; all evidence remains probe-only.

## Code Changes

- Added mode `routed_grouped_independent_w4a16_hybrid_smallrow_smoke`.
- Added `--hybrid_small_row_threshold=<1..15>`, default `4`.
- Added spike-local `RawGptqW4A16GroupedSmallRowsVec4Kernel` for small row fragments.
- Added hybrid plan that routes full 16-row tiles to existing shared-A WMMA and small fragments to vec4 SIMT.
- Kept same independent W4A16 smoke CSV schema; hybrid partition data is in `notes`:
  - `hybrid_small_row_threshold`
  - `hybrid_tile_m_count`
  - `hybrid_small_row_count`

## Verification

- Local build PASS:
  - `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4`
- `orin_1` sync PASS:
  - `sync_orin_lape_build.sh --target orin_1 --sync-only --no-clean`
- `orin_1` target build PASS:
  - `cmake --build . --target qwen3_5_cute_dsl_spike -j 4`
- `orin_1` smoke PASS, threshold=4:
  - M64/gate_proj: `candidate_ms=1.880016`, `nncl_ms=0.481731`, ratio `3.902625`, `precision_pass=true`, `hybrid_tile_m_count=2`, `hybrid_small_row_count=54`, launches `2`.
  - M898/gate_proj: `candidate_ms=3.816718`, `nncl_ms=1.107985`, ratio `3.444739`, `precision_pass=true`, `hybrid_tile_m_count=68`, `hybrid_small_row_count=139`, launches `2`.
  - two-shape geomean ratio: `3.666541x`.

## Evidence

- `analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/report.md`
- `analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/hybrid_smallrow_thr4_M64.csv`
- `analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/hybrid_smallrow_thr4_M898.csv`
- `analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/hybrid_smallrow_thr4_M64.log`
- `analysis/Qwen35_cutedsl_r0g_hybrid_smallrow_probe_20260608_120/hybrid_smallrow_thr4_M898.log`

## Audit Boundary

- CSV guard PASS for both rows:
  - `valid_for_sop_a=false`
  - `valid_for_sop_c=false`
  - `tier_eligible=false`
  - `independent_candidate=false`
  - `candidate_audit_pending=true`
  - `candidate_uses_nncl_moefc=false`
  - `candidate_uses_nncl_moegroupgemm=false`
  - `candidate_uses_dispatch_moe_gemm_to_cutlass=false`
  - `candidate_uses_nncl_cutlass_extension_headers=false`
  - `baseline_uses_nncl_moegroupgemm=true`
- Candidate does not call NNCL MoeFC/dispatch path; same-run NNCL remains baseline/diff only.
- Translation unit still includes NNCL headers for baseline/control, so CSV keeps `translation_unit_includes_nncl_headers=true`.
- `timing_contaminated=true` remains intentional for this attribution smoke.

## Conclusion

`done / probe-only / not formal / continue_probe_or_hold`.

Hybrid small-row improves over AUTO-119 shared-A WMMA (`4.372321x/4.353763x` -> `3.902625x/3.444739x`), so per-expert 16-row padding is a real bottleneck. It still fails the `<=1.20x` goal and remains clearly `>1.50x`, so this result must not be promoted to SOP/tier/production. Further CuTe/CUTLASS work should not be more minor tuning of this raw CUDA/WMMA attribution kernel; it needs a true CUTLASS-style fused GPTQ W4A16 grouped mainloop, or the project should pivot to `Q35-MOE-NNCL-GROUPED-TARGETED-R0`.
