# AUTO-20260608-112 M4 CUTLASS Dispatch Orin-Runner

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 目标设备

- target：`orin_1`
- container：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`
- local repo：`/workspace/liyang/lape_a6d6bfb9`
- local evidence：`analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/`

## 执行命令

同步：

```bash
bash ~/.codex/skills/sync-orin-lape-build/scripts/sync_orin_lape_build.sh \
  --target orin_1 \
  --source /workspace/liyang/lape_a6d6bfb9 \
  --sync-only
```

构建：

```bash
cmake -S . -B build_cute_dsl_spike \
  -DCMAKE_BUILD_TYPE=Release \
  -DLAPE_BUILD_SPIKE_CUTE_DSL=ON \
  -DCMAKE_CUDA_ARCHITECTURES=87
cmake --build build_cute_dsl_spike --target qwen3_5_cute_dsl_spike -j 4
```

Smoke：

```bash
./build_cute_dsl_spike/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=routed_grouped_moefc_cutlass_dispatch_probe \
  --projection=all \
  --m_filter=64 \
  --warmup=10 \
  --iters=100
```

Full/repeat：

```bash
./build_cute_dsl_spike/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=routed_grouped_moefc_cutlass_dispatch_probe \
  --projection=all \
  --warmup=10 \
  --iters=100
```

## 结果

- sync PASS
- remote build PASS：`logs/remote_build.log`
- M64 smoke PASS：2/2 rows `precision_pass=true`
- full run1 PASS：10/10 rows `precision_pass=true`
- full run2 PASS：10/10 rows `precision_pass=true`

Evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/moefc_cutlass_dispatch_m64_smoke.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/moefc_cutlass_dispatch_full_run1.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/moefc_cutlass_dispatch_full_run2.csv`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m4_cutlass_dispatch_orin_1_20260608_185114/dispatch_probe_summary.csv`

备注：首次用宿主机 `scp` 拉取容器内文件失败，随后通过 `docker exec cat` 正确回传 CSV/log。

## 边界

所有输出固定 `control_probe_only=true/independent_candidate=false/valid_for_sop_a=false/valid_for_sop_c=false/tier_eligible=false`。该 run 不是 formal SOP evidence。
