# AUTO-20260608-114 R0G Independent W4A16 Smoke

任务：`Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-SMOKE`

父任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## Scope

本轮只补 spike-only smoke mode，不修改 production Qwen3.5 推理路径，不创建 formal candidate，不把 R0F/R1 M4 dispatch/control promoted。

写入范围：

- `samples/micro_bench/spike/cute_dsl/`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/`
- `.codex/agent_group/current/agent_outputs/`
- `.codex/agent_group/current/STATE.md`
- `.codex/agent_group/current/tasks.csv`
- `.codex/agent_group/memory/{TASK_LEDGER.md,PROGRESS_LEDGER.md,ROADMAP.md,RISKS.md}`

说明：本轮尝试启动 sidecar reviewer/perf-analyst agent，但命中 `agent thread limit reached`，因此由 main-orchestrator 本地完成实现、审查和验证。

## Implementation

- 新增 mode：`routed_grouped_independent_w4a16_smoke`
- candidate path：`lape_raw_gptq_w4a16_grouped_smoke`
- candidate 使用 spike-local raw HF GPTQ `qweight/scales` CUDA scalar kernel。
- candidate 不调用 NNCL `MoeFCGemm`、`MoeGroupGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass`。
- same-run NNCL `MoeGroupGemm` 只作为 baseline/diff 对照，因此 CSV 明确：
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
- `timing_contaminated=true`，因为该 smoke 仍是 per-active-expert launch，且不是 optimized grouped/TensorCore W4A16 mainloop。

## Verification

本地 build：

```text
cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j 4
```

结果：PASS。

本地 smoke：

- RTX 5090 本地运行失败于 NNCL baseline：`[Error][MoE][GEMM Dispatch] Arch unsupported for MoE GEMM`
- 该失败是本地非 Orin 架构限制；candidate banner 和 audit flags 正常输出。

`orin_1` build：

```text
cmake -S . -B build_cute_dsl_spike_orin1_probe -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87 -DLAPE_BUILD_SPIKE_CUTE_DSL=ON
cmake --build build_cute_dsl_spike_orin1_probe --target qwen3_5_cute_dsl_spike -j 4
```

结果：PASS。

`orin_1` smoke：

```text
--mode=routed_grouped_independent_w4a16_smoke --projection=gate_proj --m_filter=64 --warmup=0 --iters=1
```

结果：

| family | M | K | N | projection | active_experts | candidate_ms | nncl_ms | ratio | precision_pass |
|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| A | 64 | 2048 | 512 | gate_proj | 37 | 32.292320 | 4.967424 | 6.500818 | true |

Evidence：

- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/report.md`
- `analysis/Qwen35_cutedsl_r0g_independent_w4a16_smoke_20260608_114/independent_w4a16_smoke_m64_orin1.csv`

CSV guard：

- 58 fields
- 1 data row
- no extra columns
- required audit fields present

## Decision

`continue_probe / smoke-only / not formal / not tier`

该 smoke 只证明 raw GPTQ decode + matmul correctness 起点可行；ratio `6.500818x` 远高于 `<=1.20x` 目标，不证明性能接近 NNCL。若继续 R0G，必须实现独立 grouped/TensorCore W4A16 mainloop，并新建 formal candidate task 后重新走 SOP-A/B/C。
