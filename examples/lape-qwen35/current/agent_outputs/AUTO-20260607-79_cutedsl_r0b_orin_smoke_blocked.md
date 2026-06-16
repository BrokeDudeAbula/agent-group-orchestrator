# AUTO-20260607-79 CuTeDSL R0b orin_1 Smoke Blocked

## 结论

`Q35-MOE-CUTEDSL-R0B-TOOLCHAIN-SMOKE` 已在 `orin_1` 组织执行。同步和远端构建通过，但 Python CuTeDSL import smoke 在 `cutlass._mlir` 缺失处阻塞，后续 `elementwise_add.py`、`tensorop_gemm.py` 和可选 `sgemm.py` 按 stop condition 未执行。

本结果只证明 `orin_1` repo/build 可用，并定位 Python CuTeDSL packaging blocker；不能声明 CuTeDSL kernel compile/run 可用，不能进入 R0c/R0d/SOP，也不能生成 tier。

## 执行范围

- target：`orin_1`
- container：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`
- local output：`analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/`
- command package：`analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/r4_command_package.md`

允许范围：

- 同步当前 repo 到 `orin_1`
- 远端 build sanity
- CuTeDSL import smoke
- 若 import PASS，则跑 Ampere elementwise/tensorop smoke

实际未进入：

- R0c single projection correctness
- R0d routed grouped micro
- R0e SOP-A/B/C
- NCU/nsys
- tier verdict

## 执行结果

| item | result |
|---|---|
| remote sync | PASS |
| remote build | PASS |
| remote artifact | `/workspace/liyang/workspace/lape/build/llm_server` |
| R0b script synced | PASS |
| CUTLASS repo path | PASS after syncing local repo into container |
| static path checks | PASS |
| `sm_87` mapping | PASS |
| CuTeDSL import | FAIL |
| elementwise smoke | NOT RUN |
| tensorop smoke | NOT RUN |
| sgemm fallback | NOT RUN |

Import failure from structured JSON:

```text
import cutlass failed: No module named 'cutlass._mlir'
import cutlass.cute failed: No module named 'cutlass._mlir'
import cutlass.cute.runtime failed: No module named 'cutlass._mlir'
```

官方安装尝试也失败：

```text
bash setup.sh --cu12
ERROR: Could not find a version that satisfies the requirement nvidia-cutlass-dsl==4.5.0.dev0
ERROR: No matching distribution found for nvidia-cutlass-dsl==4.5.0.dev0
```

容器 pip index：

```text
http://jetson.webredirect.org/jp6/cu126
https://pypi.ngc.nvidia.com
```

## 证据文件

- `analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/r0b_smoke_report.md`
- `analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/r0b_smoke_summary.csv`
- `analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/r0b_smoke_summary.json`
- `analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/remote/r0b_orin_smoke_summary.csv`
- `analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/remote/toolchain_script/cutedsl_toolchain_smoke_import_smoke.json`
- `analysis/Qwen35_cutedsl_w4a16_grouped_r0b_orin_1_20260607_smoke/remote/logs/import_smoke.log`

## Evidence Flags

所有 R0b 输出继续固定：

```text
valid_for_sop_a=false
valid_for_sop_c=false
tier_eligible=false
```

## 下一步

1. 优先补齐 Jetson CUDA 12.6 / Python 3.10 / aarch64 可用的 `nvidia-cutlass-dsl==4.5.0.dev0` wheel 及依赖库，再重跑 R0b import、elementwise 和 tensorop smoke。
2. 如果 wheel 短期不可得，将 R0b fallback 改为 CuTe/CUTLASS C++ smoke，并把 Python CuTeDSL route 标记为工具链 blocked。

R0c/R0d/R0e 在 R0b import/compile/run smoke PASS 前保持 `todo`。
