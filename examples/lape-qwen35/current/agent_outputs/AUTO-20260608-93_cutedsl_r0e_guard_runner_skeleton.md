# AUTO-20260608-93 CuTe/CUTLASS R0E guard/runner skeleton

日期：2026-06-08
任务：`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
范围：R0E formal 前置工具；不启动远端 R4，不生成 SOP/tier evidence

## 结论

- 已新增 CuTe/CUTLASS R0E fail-closed guard/runner skeleton。
- 该 skeleton 只固定 formal evidence 的文件、字段和 gate 口径，不会解除 R0E `blocked / gated`。
- `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 仍保持 `blocked / gated`，因为仍缺用户 R4 确认和 `qwen3_5_cute_dsl_spike` formal SOP-A/B/C binary modes。

## 新增/更新文件

- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_guard.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_make_runner.py`
- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py`
- `samples/micro_bench/spike/cute_dsl/README.md`

## Sub-agent 复核

- reviewer sub-agent：`019ea690-6c67-7bb2-adad-21b3e6a19dca`
- 结论：
  - 当前不存在 `cute_dsl` formal SOP-A/B/C runner 或专用 guard。
  - 可以先新增本地 fail-closed guard/runner skeleton 推进目标，但不能声明 SOP-A/B/C PASS，也不能解除 R0E blocked。
  - Marlin R4 guard/runner 只能作为模板，不能直接复用到 CuTe/CUTLASS。
  - 仍必须等用户 R4 后执行远端 sync/build/help preflight、真实 SOP-A/B/C workload、NCU、guard、reviewer 复核和 tier 判定。

## Skeleton 行为

- `cutedsl_r0e_make_runner.py` 只生成 shell runner；生成器不连接远端、不编译、不运行 CUDA/NCU。
- 生成的 runner 必须设置 `CUTEDSL_R0E_R4_CONFIRMED=1` 才会继续。
- runner 会先检查 `qwen3_5_cute_dsl_spike --help` 是否包含：
  - `r0e_sop_a_precision`
  - `r0e_sop_b_occupancy`
  - `r0e_sop_c_routed_grouped`
- 若 formal mode 缺失，runner fail-closed 并保持 R0E blocked。
- `cutedsl_r0e_guard.py` 只解析已回传本地文件，要求：
  - `sop_a_precision.csv`
  - `sop_b_ncu_summary.csv`
  - `sop_c_routed_grouped.csv`
  - 输出 `r0_guard_report.md`
  - 输出 `r0_verdict.json`
- guard 显式拒绝 diagnostic modes：`manifest/toolchain_smoke/shape_bench/projection_correctness/routed_grouped_micro/routed_grouped_micro_nncl_paired`。

## 本地验证

已执行：

```bash
python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py
python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_r0e_synthetic_check.py
git diff --check -- samples/micro_bench/spike/cute_dsl
```

结果：

- `py_compile` PASS。
- synthetic PASS：formal synthetic evidence 可通过；用 R0D1 diagnostic mode 冒充 SOP-C 会被 guard 拒绝。
- `git diff --check` PASS。

## 仍缺内容

1. 用户 R4 formal 确认：target、container、remote repo、命令、预计耗时、输出目录、停止条件。
2. `qwen3_5_cute_dsl_spike` formal binary modes：
   - `r0e_sop_a_precision`
   - `r0e_sop_b_occupancy`
   - `r0e_sop_c_routed_grouped`
3. 远端 `orin_1` R4 执行与回传正式文件。
4. guard 正式执行、reviewer 二次复核、tier 判定。

## 非 SOP 边界

- R0c/R0d/R0D1 仍不是 SOP-A、SOP-C 或 tier evidence。
- R0D1 `cutedsl_ms/nncl_ms/ratio` 不得作为 SOP-C 或 tier evidence。
- 本轮 skeleton 不是 execution evidence。
- 缺用户 R4 formal 确认时，不得启动 R0E。
