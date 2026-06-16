# AUTO-20260608-112 M1 Orin Runner

## 结论

`orin_1` M1 smoke 通过。`M64` 与 hot `M898` 的 family A/B 共 4 行均为 `status=pass`，输出有限且非零，CSV/log 均标明 probe-only。

## 远端执行口径

- target：`orin_1`
- container：`liyang_lape`
- repo：`/workspace/liyang/workspace/lape`
- build dir：`build_cutedsl_r0f_align1`
- binary：`build_cutedsl_r0f_align1/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike`
- build：Release, `sm_87`, `LAPE_BUILD_SPIKE_CUTE_DSL=ON`, `LAPE_CUTE_DSL_ENABLE_R0E_FORMAL_MODES=OFF`

## 输出目录

- `analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/`

关键文件：

- `r0f_m1_shape_bench_m64.log`
- `r0f_m1_shape_bench_m64.csv`
- `r0f_m1_shape_bench_m64.rc`
- `r0f_m1_shape_bench_m898.log`
- `r0f_m1_shape_bench_m898.csv`
- `r0f_m1_shape_bench_m898.rc`
- `r0f_m1_r0e_disabled_check.log`

## Shape Bench 结果

| family | M | K | N | projection | ms | GFLOP/s | nonzero | status |
|---|---:|---:|---:|---|---:|---:|---:|---|
| A | 64 | 2048 | 512 | gate_proj | 0.259370 | 517.475 | 32768 | pass |
| B | 64 | 512 | 2048 | down_proj | 0.087469 | 1534.464 | 131072 | pass |
| A | 898 | 2048 | 512 | gate_proj | 0.270158 | 6970.891 | 459776 | pass |
| B | 898 | 512 | 2048 | down_proj | 0.355565 | 5296.482 | 1839104 | pass |

所有行均满足：

- `op_class=TensorOp`
- `arch=Sm80/Sm87-compatible`
- `candidate_path=cutlass_tensorop_dense_fp16`
- `tensorop_variant=tensorop_align8_default`
- `can_implement_status=Success`
- `nan_count=0`
- `inf_count=0`
- `nonzero>0`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## R0E 默认关闭检查

默认 binary 执行 archived R0E mode：

- command：`--mode=r0e_sop_a_precision`
- result：`rc=1`
- log：`invalid --mode=r0e_sop_a_precision`

默认 help 不列出 `r0e_sop_*` modes，并明确当前 probe modes 固定输出 `valid_for_sop_a=false valid_for_sop_c=false tier_eligible=false`。

## 结论边界

M1 evidence 只能说明 CUTLASS TensorOp dense fp16 path 在 Orin `sm_87` 上对 small/hot SOP-C shapes 可构建、可运行、输出非零有限。它不能作为 SOP-C/tier/W4A16 grouped PASS。
