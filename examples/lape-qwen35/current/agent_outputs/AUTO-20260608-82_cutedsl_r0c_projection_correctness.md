# AUTO-20260608-82 CuTe/CUTLASS R0c Projection Correctness

task_id: `Q35-MOE-CUTEDSL-R0C-SINGLE-PROJECTION-CORRECTNESS`
status: `done / diagnostic-only`
target: `orin_1`

## 结论

R0c 已按 CuTe/CUTLASS C++ route 完成，不依赖 Python CuTeDSL `_mlir` wheel。

`orin_1` 正式覆盖 `gate_proj/up_proj/down_proj x M=64/128/898` 共 9 case，全部满足 gate：

- `max_abs < 5e-3`
- `rmse < 1e-3`
- NaN/Inf 为 0
- 输出非全零
- `qzeros_sym_ok=true`
- `g_idx_default_ok=true`

所有输出固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

本结果只解锁 R0d routed grouped micro；不能作为 SOP-A/SOP-C/tier evidence，也不解除 Python CuTeDSL R0b `cutlass._mlir` blocker。

## Sub-Agent 结论

- `019ea5ed-6cd8-7051-9140-62fc59b5bae1` / repo-explorer：确认 HF GPTQ raw key、shape、bundle `.pt` InputArchive 协议、router_logits top-k 重建，以及 B 布局风险。重点结论是 dense-dequant 后必须显式生成 CUTLASS 期望的 `K x N` column-major buffer。
- `019ea5ed-7df3-7d81-8235-e6785638163e` / reviewer：确认 R0c 可走 CuTe/CUTLASS C++ fallback，但必须固定非 SOP/tier；只有 9 case 全过才可标记 done；Python CuTeDSL R0b 仍 blocked。

## 代码范围

- `samples/micro_bench/spike/cute_dsl/cutlass_projection_correctness.cu`
- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`
- `samples/micro_bench/spike/cute_dsl/README.md`

未修改 production path；spike target 仍由 `LAPE_BUILD_SPIKE_CUTE_DSL=OFF` 默认关闭；只额外把 `src/models/safetensor_loader.cc` 编入 spike target，不链接 production `liblape.so`。

## 本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py` PASS。
- `cmake -S . -B build_cute_dsl_spike_local -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=87 -DLAPE_BUILD_SPIKE_CUTE_DSL=ON` PASS。
- `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4` PASS。
- `--mode=manifest` PASS。
- `--mode=shape_bench --warmup=1 --iters=1` PASS，10/10 rows。
- `--mode=projection_correctness --projection=all --m_filter=64 --warmup=1 --iters=5` PASS，3/3 rows。
- `git diff --check -- CMakeLists.txt samples/micro_bench/spike/cute_dsl` PASS。

本地模型路径默认回退到 `/workspace/liyang/model/Qwen3.5/Qwen3.5-35B-A3B-GPTQ-Int4-lmhead`；`orin_1` 正式运行使用 `/workspace/models/Qwen3.5/Qwen3.5-35B-A3B-GPTQ-Int4-lmhead`。

## Orin 输出

本地回传目录：

```text
analysis/Qwen35_cutedsl_r0c_projection_correctness_orin_1_20260608_065517/
```

文件：

- `projection_correctness.csv`
- `projection_correctness.log`

远端命令核心参数：

```text
--mode=projection_correctness
--projection=all
--m_filter=0
--warmup=5
--iters=50
--layer_idx=15
--top_k=8
```

CSV schema 严格为：

```text
schema_version,mode,backend,projection,expert_idx,M,K,N,input_source,bundle_dir,model_path,layer_idx,top_k,quant_method,weight_source_layout,candidate_ms,reference_ms,max_abs,rmse,nan_count,inf_count,nonzero,qzeros_sym_ok,g_idx_default_ok,marlin_packed_layout_used,valid_for_sop_a,valid_for_sop_c,tier_eligible
```

CSV gate 校验：9 rows，0 failures。

## 9 Case 摘要

| projection | M | max_abs | rmse | candidate_ms | reference_ms |
|---|---:|---:|---:|---:|---:|
| gate_proj | 64 | 0.000000e+00 | 0.000000e+00 | 0.904828 | 0.274029 |
| gate_proj | 128 | 7.629395e-06 | 3.371748e-07 | 0.998917 | 0.194787 |
| gate_proj | 898 | 6.103516e-05 | 2.697398e-06 | 1.804721 | 0.963493 |
| up_proj | 64 | 5.960464e-08 | 2.634178e-09 | 0.365234 | 0.073316 |
| up_proj | 128 | 2.384186e-07 | 1.490116e-08 | 0.366414 | 0.228762 |
| up_proj | 898 | 2.384186e-07 | 1.053671e-08 | 1.007520 | 0.721012 |
| down_proj | 64 | 1.220703e-04 | 1.508775e-06 | 0.154057 | 0.117148 |
| down_proj | 128 | 2.441406e-04 | 2.812259e-06 | 0.154707 | 0.170007 |
| down_proj | 898 | 1.525879e-05 | 1.739954e-07 | 1.341615 | 0.740475 |

## 非 SOP 边界

- R0c projection_correctness 是 single expert / single projection correctness diagnostic，不是 routed grouped MoE。
- `candidate_ms` 是 CUTLASS dense fp16 GEMM 诊断计时，`reference_ms` 是 torch CUDA dense reference 计时，二者不能作为 SOP-C ratio。
- 本轮不使用 `B_marlin`、`RepackQweightToMarlin()` 或 `perm64` scales layout。
- 即使 9/9 case PASS，也只能解锁 R0d routed grouped micro；不能进入 R0e/SOP-A/B/C，也不能生成 tier。
- Python CuTeDSL R0b 仍因 `cutlass._mlir` 缺失 blocked；CuTe/CUTLASS C++ fallback PASS 不等于 Python CuTeDSL works on Orin。
