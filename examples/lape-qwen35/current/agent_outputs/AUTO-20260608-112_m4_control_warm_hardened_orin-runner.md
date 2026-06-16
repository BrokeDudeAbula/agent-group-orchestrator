# AUTO-20260608-112 M4-Control Warm Hardened Orin-Runner

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 设备与目录

- 设备：`orin_1`
- 容器：`liyang_lape`
- 远端 repo：`/workspace/liyang/workspace/lape`
- build：`/workspace/liyang/workspace/lape/build_cutedsl_r0f_align1`
- 输出目录：`analysis/Qwen35_cutedsl_r0f_r1_probe_m4_moefc_direct_warm_hardened_orin_1_20260608_182900/`

## 执行

同步范围：

- `CMakeLists.txt`
- `samples/micro_bench/spike/cute_dsl/`

远端 build：

```text
cmake --build . --target qwen3_5_cute_dsl_spike -j 4
```

结果：build PASS，日志为 `build_hardened_warm_probe.log`。

执行 micro：

- smoke：`--mode=routed_grouped_moefc_direct_probe --projection=gate_proj --m_filter=64 --warmup=10 --iters=100`
- full：`--projection=all --m_filter=0 --warmup=10 --iters=100`
- repeat：同 full

## Evidence

- `smoke_m64_gate_hardened.log`
- `r0f_m4_moefc_direct_warm_hardened_smoke.csv`
- `run_warm_hardened_all.log`
- `r0f_m4_moefc_direct_warm_hardened_all.csv`
- `run_warm_hardened_all_repeat.log`
- `r0f_m4_moefc_direct_warm_hardened_all_repeat.csv`

## 结果

- smoke rows=1，PASS
- full rows=10，PASS
- repeat rows=10，PASS
- 日志逐行包含 `control_probe_only=true independent_candidate=false`
- summary 包含 `diagnostic_only=true valid_for_sop_a=false valid_for_sop_c=false tier_eligible=false`

## 判定

Orin schema-hardened warm-state control micro 完成。仍为 NNCL internal control proof，
不是 independent candidate。
