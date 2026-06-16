# AUTO-20260608-112 M2 Orin Runner

## 结论

`orin_1` 上 M2 same-run NNCL paired micro 已执行两轮。两轮程序本身均 `micro_rc=0`，CSV 均已回传本地，所有行保持 probe-only 三项 false。

第一轮最初使用 `scp orin_1:/tmp/...csv` 拉取失败，因为 CSV 写在 Docker 容器内 `/tmp` 而不是主机 `/tmp`。随后改用 `ssh orin_1 "docker exec liyang_lape cat /tmp/..."` 回传成功；该拉取问题不影响 micro 程序结果。

## 执行环境

- target：`orin_1`
- container：`liyang_lape`
- repo：`/workspace/liyang/workspace/lape`
- binary：`/workspace/liyang/workspace/lape/build_cutedsl_r0f_align1/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike`
- bundle：
  - `/workspace/liyang/workspace/lape/analysis/Qwen35_q35_028_moe_bundle_orin_1_20260602_194858/bundles_l15/moe_block_layer_15_prefill_0`
- command mode：`--mode=routed_grouped_micro_nncl_paired`
- warmup / iters：`5 / 50`
- shapes：family A/B, `M={64,128,256,512,898}`

## Evidence

构建与同步：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/sync_m2_timing_hygiene_final.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m2_timing_hygiene_final.log`

第一轮：

- log：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle.log`
- rc：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle.rc`
- CSV：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle.csv`
- final CSV pull rc：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_csv_pull.rc`

第二轮：

- log：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_repeat.log`
- rc：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_repeat.rc`
- CSV：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m2_nncl_paired_all_abs_bundle_repeat.csv`

## Sanity

两轮均满足：

- rows：`10`
- `precision_pass=true`
- `nan_count=0`
- `inf_count=0`
- `nonzero>0`
- `timing_contaminated=false`
- `baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`
- `op_class=TensorOp`
- `candidate_path=cutlass_tensorop_dense_fp16`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Stop Gate

两轮 ratio 均明显大于 `1.50x`，触发 M0/M2 既定停止条件。未启动 M3 NCU，未启动 M4 grouped/batched probe。
