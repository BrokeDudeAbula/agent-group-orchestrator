# AUTO-20260608-112 M4-Control Orin-Runner

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 设备与目录

- target：`orin_1`
- container：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`
- build dir：`build_cutedsl_r0f_align1`
- local evidence：`analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_orin_1_20260608_173920/`

## 构建

构建参数：

```text
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87 \
  -DLAPE_BUILD_SPIKE_CUTE_DSL=ON \
  -DLAPE_CUTE_DSL_ENABLE_R0E_FORMAL_MODES=OFF
cmake --build . --target qwen3_5_cute_dsl_spike -j 4
```

构建结果：

- `build_moefc_direct_probe.log`：PASS
- `build_moefc_direct_probe_fix.log`：PASS
- `build_moefc_direct_probe_balanced.log`：PASS

## Smoke

balanced smoke：

```text
--mode=routed_grouped_moefc_direct_probe
--projection=gate_proj
--m_filter=64
--warmup=5
--iters=50
```

结果：

- `precision_pass=true`
- `direct_vs_nncl_ratio=1.197989`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## Full 10 Shape Runs

执行两轮 full 10 shape：

- `r0f_m4_moefc_direct_all_balanced.csv`
- `r0f_m4_moefc_direct_all_balanced_repeat.csv`

两轮均：

- rows=10
- `precision_pass=true` for all rows
- `nan_count_vs_nncl=0`
- `inf_count_vs_nncl=0`
- `nonzero_vs_nncl>0`
- probe-only 三项 false

旧 CSV `r0f_m4_moefc_direct_all.csv` 因 timed-loop launch check 污染，不作为 ratio evidence。
