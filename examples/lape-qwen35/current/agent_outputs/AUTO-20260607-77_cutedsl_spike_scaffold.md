# AUTO-20260607-77 CuTeDSL R0a Spike Scaffold

## 结论

已按 Marlin spike 的隔离方式新增 CuTeDSL 第一阶段 spike 工程：

- `samples/micro_bench/spike/cute_dsl/CMakeLists.txt`
- `samples/micro_bench/spike/cute_dsl/README.md`
- `samples/micro_bench/spike/cute_dsl/main.cc`
- `samples/micro_bench/spike/cute_dsl/spike_common.h`

顶层 `CMakeLists.txt` 已新增：

```cmake
add_subdirectory(samples/micro_bench/spike/cute_dsl EXCLUDE_FROM_ALL)
```

target：

- `qwen3_5_cute_dsl_spike`
- option：`LAPE_BUILD_SPIKE_CUTE_DSL=OFF` 默认关闭
- 边界：不链 `liblape.so`，不修改 `src/`、`include/`、`third_party/nncl/` 或 production 推理路径

## 与 Marlin SOP-C 对齐

R0a manifest 固定复用 Marlin SOP-C 输入集合：

- bundle：`analysis/Qwen35_q35_028_moe_bundle_orin_1_20260602_194858/bundles_l15/moe_block_layer_15_prefill_0/`
- model：`/workspace/liyang/model/Qwen3.5/Qwen3.5-35B-A3B-GPTQ-Int4-lmhead`
- layer：`15`
- top_k：`8`
- family A：`K=2048,N=512,M={64,128,256,512,898}`，projection=`gate_proj/up_proj`
- family B：`K=512,N=2048,M={64,128,256,512,898}`，projection=`down_proj`

CSV schema：

```text
family,M,K,N,projection,input_source,bundle_dir,model_path,top_k,layer_idx,evidence_scope,cu_row_source,valid_for_sop_a,valid_for_sop_c,tier_eligible,cutlass_repo,cutedsl_python_dir,cutedsl_examples_dir,notes
```

所有 R0a 输出固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## 本地验证

执行：

```bash
cmake -S . -B build_cute_dsl_spike_local \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CUDA_ARCHITECTURES=87 \
  -DLAPE_BUILD_SPIKE_CUTE_DSL=ON

cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4

./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=manifest \
  --output_csv=/tmp/q35_cutedsl_manifest.csv

./build_cute_dsl_spike_local/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=toolchain_smoke \
  --output_csv=/tmp/q35_cutedsl_toolchain_manifest.csv

git diff --check
```

结果：

- CMake configure PASS
- build target PASS
- `--help` PASS
- `--mode=manifest` PASS，CSV 10 行
- `--mode=toolchain_smoke` PASS，CUTLASS repo / CuTeDSL python / CuTeDSL examples / bundle / model 路径均存在
- Python CSV check PASS：两份 CSV 的 `(family,M,K,N,projection)` 与 Marlin SOP-C manifest 对齐
- `git diff --check` PASS

## 非目标

本轮没有实现 CuTeDSL GEMM kernel，没有运行 Orin/NCU/nsys，也没有产生任何 SOP-A/SOP-C 或 tier 证据。

R0b/R0c 后续建议：

1. R0b：CuTeDSL import/compile smoke，验证 Orin `sm_87` 工具链。
2. R0c：single expert / single projection / small rows W4A16 correctness，对齐 dense-dequant 与 manual int4 oracle。
3. R0d：full routed grouped paired runner，与 Marlin SOP-C 10 shape 统一报告。
