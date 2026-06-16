# AUTO-20260608-112 M3 Orin Runner

## 结论

`orin_1` 上完成 M3 grouped dense probe 构建、M64 smoke、两轮 10 shape same-run NNCL paired micro。构建与 micro 均成功，未进入 NCU。

## 远端执行范围

目标设备：

- `orin_1`
- Docker container：`liyang_lape`
- repo：`/workspace/liyang/workspace/lape`
- build dir：`/workspace/liyang/workspace/lape/build_cutedsl_r0f_align1`

本地 evidence 目录：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m3_grouped_dense_orin_1_20260608_165352/`

## 同步与构建

旧默认全量 build 被终止，原因是它由同步脚本附带启动，且启动于 M3 input fix 之前。随后只同步最新 spike/CMake 范围并显式构建 spike target。

关键文件：

- `sync_default_build.rc`：`terminated_for_latest_m3_spike_only_build`
- `sync_m3_latest.rc`：`sync_m3_latest_rc=0`
- `build_grouped_dense_probe.rc`：`build_rc=0`
- `build_grouped_dense_probe.log`

构建命令口径：

```text
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87 -DLAPE_BUILD_SPIKE_CUTE_DSL=ON -DLAPE_CUTE_DSL_ENABLE_R0E_FORMAL_MODES=OFF
cmake --build . --target qwen3_5_cute_dsl_spike -j 4
```

## Micro Evidence

M64 gate smoke：

- `r0f_m3_grouped_dense_m64_gate.log`
- `r0f_m3_grouped_dense_m64_gate.rc`
- `micro_gate_m64_rc=0`

10 shape first run：

- `r0f_m3_grouped_dense_all.log`
- `r0f_m3_grouped_dense_all.csv`
- `r0f_m3_grouped_dense_all.rc`
- `micro_all_rc=0`

10 shape repeat：

- `r0f_m3_grouped_dense_all_repeat.log`
- `r0f_m3_grouped_dense_all_repeat.csv`
- `r0f_m3_grouped_dense_all_repeat.rc`
- `micro_all_repeat_rc=0`

## Field Checks

两轮 10 shape 均满足：

- rows=10
- `precision_pass=true`
- `timing_contaminated=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `grouped_launches_per_iter=1`
- `serial_launches_per_iter=active_experts`

## NCU

未启动 NCU。原因是 grouped candidate 相对 same-run NNCL baseline 两轮 geomean ratio 仍明显 `>1.50x`，按停止条件 fail-closed，不进入 candidate NCU isolation。
