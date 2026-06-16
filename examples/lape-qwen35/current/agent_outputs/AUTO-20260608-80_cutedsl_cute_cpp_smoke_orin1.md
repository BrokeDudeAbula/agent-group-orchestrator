# AUTO-20260608-80 CuTe C++ smoke on orin_1

## 任务

用户要求在 `orin_1` 上跑与本地相同的 CuTe C++ smoke，验证 repo 内 `third_party/nncl/third_party/cutlass` 的 C++ CuTe 路径是否在 Jetson Orin `sm_87` 上可编译运行。

## 执行范围

- 同步本地 repo 到 `orin_1:/workspace/liyang/workspace/lape`。
- 不安装公开版 `nvidia-cutlass-dsl`。
- 不引入新依赖。
- 不改 production path。
- 只构建 CUTLASS CuTe C++ tutorial targets：
  - `cute_tutorial_tiled_copy`
  - `cute_tutorial_sgemm_1`

## 命令

```bash
bash /home/titan/.codex/skills/sync-orin-lape-build/scripts/sync_orin_lape_build.sh \
  --target orin_1 \
  --source /workspace/liyang/lape_a6d6bfb9 \
  --sync-only
```

```bash
cd /workspace/liyang/workspace/lape
cmake -S third_party/nncl/third_party/cutlass \
  -B /tmp/lape_cute_cpp_smoke_sm87_20260608_021956 \
  -DCUTLASS_ENABLE_LIBRARY=OFF \
  -DCUTLASS_ENABLE_TOOLS=ON \
  -DCUTLASS_ENABLE_TESTS=OFF \
  -DCUTLASS_ENABLE_EXAMPLES=ON \
  -DCUTLASS_NVCC_ARCHS=87 \
  -DCUTLASS_ENABLE_HEADERS_ONLY=OFF \
  -DCUTLASS_TEST_LEVEL=0 \
  -DCMAKE_BUILD_TYPE=Release

cmake --build /tmp/lape_cute_cpp_smoke_sm87_20260608_021956 \
  --target cute_tutorial_tiled_copy cute_tutorial_sgemm_1 -j4

/tmp/lape_cute_cpp_smoke_sm87_20260608_021956/examples/cute/tutorial/cute_tutorial_tiled_copy
/tmp/lape_cute_cpp_smoke_sm87_20260608_021956/examples/cute/tutorial/cute_tutorial_sgemm_1 256 256 128
```

## 结果

- sync：PASS。
- configure：PASS；CUDA `12.6.68`，CMake `3.30.4`，CUTLASS `4.3.4`，`CUTLASS_NVCC_ARCHS=87`。
- build：PASS。
- `cute_tutorial_tiled_copy`：PASS，输出 `Success.`。
- `cute_tutorial_sgemm_1 256 256 128`：PASS，设备为 `Orin (SM87, 16 SMs)`，输出 `122.1 GFLOP/s / 0.1374 ms`。

本地证据目录：

- `analysis/Qwen35_cutedsl_cute_cpp_smoke_orin_1_20260608_021956/`
- `report.md`
- `summary.csv`
- `summary.json`
- `sync.log`
- `configure.log`
- `build.log`
- `run.log`

## 结论边界

- 这是 CuTe/CUTLASS C++ fallback toolchain smoke 的 Orin 通过证据。
- 这不解除 Python CuTeDSL `cutlass._mlir` 缺失 blocker。
- 这不是 Qwen3.5 MoE W4A16 grouped GEMM kernel correctness。
- 这不是 SOP-A/SOP-C/tier evidence。

