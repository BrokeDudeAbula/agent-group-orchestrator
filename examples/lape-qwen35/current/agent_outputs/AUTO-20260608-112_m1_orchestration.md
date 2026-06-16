# AUTO-20260608-112 M1 Orchestration

## 结论

M1 Tensor Core sanity 通过。`qwen3_5_cute_dsl_spike` 已在 `orin_1` Release/sm87 构建成功，small `M64` 与 hot `M898` 的 family A/B dense fp16 TensorOp shape bench 均可运行、非零、有限。

当前任务状态更新为：

- `in_progress / M1 Tensor Core sanity pass / entering M2 timing hygiene / probe-only`

## 通过条件复核

| 条件 | 结果 |
|---|---|
| 构建通过 | PASS：`build_rc=0` |
| TensorOp path 可区分 | PASS：`op_class=TensorOp`, `arch=Sm80/Sm87-compatible`, `candidate_path=cutlass_tensorop_dense_fp16` |
| hot `M898` 可运行 | PASS：family A/B 均 `status=pass` |
| small `M64` 可运行 | PASS：family A/B 均 `status=pass` |
| 输出非零有限 | PASS：`nan_count=0`, `inf_count=0`, `nonzero>0` |
| probe-only 标记 | PASS：所有 CSV/log 固定 `valid_for_sop_a=false`, `valid_for_sop_c=false`, `tier_eligible=false` |
| R0E 默认关闭 | PASS：`--mode=r0e_sop_a_precision` 返回 invalid mode |

## 关键证据

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m1_epilogue_scalar.log`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m1_shape_bench_m64.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m1_shape_bench_m898.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/r0f_m1_r0e_disabled_check.log`

## 不变边界

M1 只证明 dense fp16 Tensor Core sanity：

- 不证明 W4A16 fused decode。
- 不证明 routed grouped MoE。
- 不证明 grouped launch。
- 不证明 SOP-C ratio。
- 不允许声明 tier eligible。

## 下一步

进入 M2 Timing Hygiene：

1. 清理 `routed_grouped_micro_nncl_paired` candidate timed loop 内的临时分配、`.contiguous()`、segment copy、host/device roundtrip 和 `cudaStreamSynchronize`。
2. 若未完全清理，CSV/log 必须保留 `timing_contaminated=true`。
3. 在 `orin_1` 上跑 `M={64,128,256,512,898}` family A/B same-run NNCL paired micro，并记录 warmup/iters。
