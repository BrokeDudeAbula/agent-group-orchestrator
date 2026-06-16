# AUTO-20260608-88 CuTe/CUTLASS R0D1 M64 Smoke Progress Sync

## 结论

- 本轮将 R0D1 same-run NNCL paired diagnostic 的最新进展同步到 agent_group 记忆。
- `Q35-MOE-CUTEDSL-R0D1-SAME-RUN-NNCL-PAIRED-DIAGNOSTIC` 仍为 `in_progress / diagnostic-only`，不能标记 done。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍为 `blocked / gated`，不能启动 formal SOP-A/B/C。

## 当前证据

- evidence 目录：`analysis/Qwen35_cutedsl_w4a16_grouped_r0d1_nncl_paired_orin_1_20260608_083804/`
- 关键文件：
  - `configure.log`
  - `build.log`
  - `manifest.csv`
  - `manifest.log`
  - `r0d1_m64_smoke.csv`
  - `r0d1_m64_smoke.log`
  - `remote_build_dir.txt`
  - `remote_output_dir.txt`

## 已完成进展

- `samples/micro_bench/spike/cute_dsl` 内的 `routed_grouped_micro_nncl_paired` mode 已能在 `orin_1` 编译运行。
- `orin_1` configure/build `qwen3_5_cute_dsl_spike` PASS。
- `--mode=manifest` PASS，输出 10 rows。
- `--mode=routed_grouped_micro_nncl_paired --m_filter=64 --warmup=1 --iters=2` smoke PASS，输出 2 rows：
  - family A：`M=64,K=2048,N=512,projection=gate_proj`
  - family B：`M=64,K=512,N=2048,projection=down_proj`
- M64 smoke 字段检查：
  - `topk_policy=nncl_softmax_topk`
  - `source_row_policy=token_major_source_row_for_replay`
  - `baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`
  - `max_abs<5e-3`
  - `rmse<1e-3`
  - `nan_count=0`
  - `inf_count=0`
  - `nonzero>0`
  - `valid_for_sop_a=false`
  - `valid_for_sop_c=false`
  - `tier_eligible=false`

## 未完成项

- 尚未运行 `--mode=routed_grouped_micro_nncl_paired --m_filter=0 --warmup=5 --iters=50` full 10 shape diagnostic。
- 尚未生成 full diagnostic gate checker 报告。
- 尚未由 reviewer 对 full 10 shape CSV、schema、NNCL top-k、source row、same-run baseline 和非 SOP 边界做 P0/P1 复核。
- 因此 R0D1 不能标记 done，R0e 不能解除 blocked。

## 非 SOP 边界

- R0D1 是 blocker-closure diagnostic，不是 formal SOP-A/SOP-C 或 tier evidence。
- R0D1 timing、ratio、`cutedsl_ms` 和 `nncl_ms` 不得用于声明 SOP-C PASS 或 tier。
- 不修改 production path。
- 不直接链接 `samples/micro_bench/spike/marlin_moe/main.cc` 到 `cute_dsl` target。
- 不使用 `B_marlin`、`RepackQweightToMarlin()` 或 `perm64` scales layout。
