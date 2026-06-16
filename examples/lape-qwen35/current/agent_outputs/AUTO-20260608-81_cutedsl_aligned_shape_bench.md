---
ag_schema: v1
doc_id: AUTO-20260608-81
category: current
doc_type: agent_output
authority: evidence_summary
lifecycle: hot
owner: main-orchestrator
task_id: Q35-MOE-CUTEDSL-ALIGNED-SHAPE-BENCH
status: done
updated_at: 2026-06-08
---

# AUTO-81 CuTe/CUTLASS aligned shape_bench

## 结论

已按 agent_group 规则组织 sub-agent，并完成 `cute_dsl` spike 的 shape-level 对齐诊断：

- Marlin/NNCL 仍引用正式 `perf_routed_grouped` SOP-C evidence。
- CuTe/CUTLASS 新增 `shape_bench`，覆盖同 10 个 `(family,M,K,N,projection)`。
- `orin_1` 上 `shape_bench` 10/10 rows PASS。
- 三方报告已生成，但 CuTe 行是 `fp16_dense` synthetic dense fallback，固定 `formal_sop_c_comparable=false`。

本轮不是 CuTe W4A16 routed grouped MoE SOP-C evidence，不改变 Marlin tier D。

## Sub-agent 结论

- `019ea557-dc1b-7490-ad16-175a3247b4b5` / Linnaeus / perf-reviewer：Marlin 与 NNCL 可放入正式 W4A16 MoE SOP-C 对比；CuTe/CUTLASS C++ fallback 当前只能是 toolchain/fp16 dense diagnostic。
- `019ea557-ac25-7912-a7a0-4deb9dbe9d46` / Dirac / repo-explorer：正式 Marlin SOP-C 使用 `perf_routed_grouped`、Q35-028 layer15 bundle、10 shape；family A projection 应为 `gate_proj`。
- `019ea557-c4ac-7ad1-a3b5-9d7795d1b99f` / Meitner / kernel-dev：当前最小可落地是新增 CUTLASS C++ `shape_bench`；后续再做 routed grouped / dense-dequant correctness。

## 代码范围

- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/cutlass_shape_bench.cu`
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- `samples/micro_bench/spike/cute_dsl/README.md`
- `samples/micro_bench/spike/cute_dsl/scripts/compare_marlin_cute_nncl.py`

没有修改 production path；没有安装公开版 `nvidia-cutlass-dsl`；没有引入新依赖。

## Orin 证据

输出目录：

- `analysis/Qwen35_cutedsl_aligned_shape_bench_orin_1_20260608_035534/`

关键文件：

- `cutedsl_shape_bench.csv`
- `marlin_cute_nncl_aligned.csv`
- `marlin_cute_nncl_aligned.md`
- `configure.log`
- `build.log`
- `run.log`
- `compare.log`

远端信息：

- target：`orin_1`
- container：`liyang_lape`
- repo：`/workspace/liyang/workspace/lape`
- build dir：`/tmp/lape_cutedsl_aligned_shape_bench_20260608_035534`
- target：`qwen3_5_cute_dsl_spike`

验证结果：

- configure PASS。
- build PASS。
- `shape_bench --warmup=5 --iters=50` PASS。
- CSV rows：10。
- CuTe CSV：`quant_method=fp16_dense`，`valid_for_sop_c=false`，`tier_eligible=false`。
- 对齐报告：`formal_sop_c_comparable=false`，`cute_valid_for_sop_c=false`。

## 性能摘要

报告路径：

- `analysis/Qwen35_cutedsl_aligned_shape_bench_orin_1_20260608_035534/marlin_cute_nncl_aligned.md`

关键边界：

- `marlin_ms` / `nncl_ms` 来自正式 SOP-C `sop_c_routed_grouped.csv`。
- `cute_ms` 来自 CUTLASS C++ synthetic fp16 dense GEMM。
- `cute_vs_nncl_ratio` 和 `cute_vs_marlin_ratio` 只是同 shape 诊断比值，不是 formal SOP-C ratio。

## 下一步

建议沿 CuTe C++ route 做 `Q35-MOE-CUTEDSL-R0C-SINGLE-PROJECTION-CORRECTNESS`：

- 从 HF raw `qweight/qzeros/scales/g_idx` 出发。
- 先 dense-dequant 到 fp16。
- 覆盖 `gate_proj/up_proj/down_proj`。
- 对齐 Marlin dense/manual oracle 和 NNCL correctness 阈值。
- 继续固定非 SOP 证据，直到 R0d/R0e 完整实现同 bundle、同 routed rows、同 NNCL baseline、同 precision gate。
