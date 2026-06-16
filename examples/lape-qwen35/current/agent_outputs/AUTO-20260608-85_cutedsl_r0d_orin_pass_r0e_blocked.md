# AUTO-20260608-85 CuTeDSL R0d Orin Pass R0e Blocked

task_id: `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0`
subtask_done: `Q35-MOE-CUTEDSL-R0D-ROUTED-GROUPED-MICRO`
subtask_blocked: `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
date: `2026-06-08`

## 结论

R0d routed grouped micro 已完成并可标为 `done / diagnostic-only`。

R0e formal SOP-A/B/C 当前不能启动，必须保持 blocked/gated。原因：

- R0d top-k policy 是 `torch_softmax_topk_r0d_diagnostic`，不是 NNCL `SoftmaxTopk<half>`。
- R0d `nncl_ms/ratio` 来自 formal SOP-C CSV join，`baseline_source=formal_sopc_csv_join_not_paired`，不是同 run paired NNCL baseline。
- 尚缺用户 R4 确认 formal 命令、预计耗时、输出目录和停止条件。

## Sub-Agent 结论

- repo-explorer / `019ea62b-566c-7942-b2f7-b12bbd3a2336`：静态 10 shape、bundle/model/layer/top_k、HF raw GPTQ loader/dequant、禁用 Marlin packed 路径均符合 R0d diagnostic 目标；P1 风险是 torch top-k、NNCL CSV join not paired、source/routed row 只输出 policy 和 `cu_row`。
- reviewer / `019ea62b-7568-7523-82a5-1e5aa0b2684f`：R0d 继续验证合规，R0e 当前不得启动。
- final reviewer / `019ea635-975f-7de0-9ed4-3d6140b6e903`：R0d 可标 `done / diagnostic-only`；R0e blocked，需记录 top-k、paired baseline 和 R4 gate 阻塞。

## Evidence

目录：

```text
analysis/Qwen35_cutedsl_w4a16_grouped_r0d_orin_1_20260608_074156/
```

关键文件：

- `report.md`
- `configure.log`
- `build.log`
- `manifest.csv`
- `routed_grouped_micro_m64_smoke.csv`
- `routed_grouped_micro_m64_smoke.log`
- `routed_grouped_micro.csv`
- `routed_grouped_micro.log`
- `r0d_gate_check.txt`
- `remote_build_dir.txt`

远端信息：

- target: `orin_1`
- container: `liyang_lape`
- remote repo: `/workspace/liyang/workspace/lape`
- remote build dir: `/tmp/lape_cutedsl_r0d_20260608_074156`

## 本地验证

- `python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/*.py`: PASS
- CMake configure: PASS
- `cmake --build build_cute_dsl_spike_local --target qwen3_5_cute_dsl_spike -j4`: PASS
- `--mode=manifest`: PASS, 10 rows
- `--mode=shape_bench --warmup=1 --iters=1`: PASS, 10/10 rows after selecting GPU2
- `--mode=projection_correctness --projection=all --m_filter=64 --warmup=1 --iters=5`: PASS, 3/3 rows
- `--mode=routed_grouped_micro --m_filter=64 --warmup=1 --iters=5`: PASS, 2/2 rows
- `git diff --check -- CMakeLists.txt samples/micro_bench/spike/cute_dsl`: PASS

Note: the first local `shape_bench` attempt on default GPU0 failed at `cudaStreamCreate` with OOM because local GPUs were heavily occupied. Retrying on GPU2 passed.

## Orin R0d 结果

Command:

```bash
/tmp/lape_cutedsl_r0d_20260608_074156/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=routed_grouped_micro \
  --m_filter=0 \
  --warmup=5 \
  --iters=50 \
  --output_csv=/tmp/lape_cutedsl_r0d_20260608_074156_routed_grouped_micro.csv
```

Gate check:

- rows: `10`
- shape set: Marlin SOP-C 10 shapes
- required fields: present
- `gate_pass=True`
- `active_experts>1`: all rows
- `cu_row_last_matches_routed_rows=true`: all rows
- `max_abs<5e-3`: all rows
- `rmse<1e-3`: all rows
- NaN/Inf: `0/0` all rows
- `nonzero>0`: all rows
- `valid_for_sop_a=false`, `valid_for_sop_c=false`, `tier_eligible=false`: all rows

## 非 SOP 边界

R0d 是 routed grouped diagnostic，不是 formal SOP-A/B/C 或 tier evidence。

- Candidate is per-expert dense-dequant fp16 CUTLASS GEMM, not fused W4A16 grouped MoE.
- Reference is torch dense grouped rows without final token reduce, not `moe_output_before_combine.pt`.
- `nncl_ms/ratio` are diagnostic metadata, not same-run paired SOP-C ratio.
- Production path is untouched.

## R0e 状态

`Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC` 标记为 `blocked / gated`。

解除条件：

1. top-k policy 对齐 NNCL `SoftmaxTopk<half>` 或 reviewer 明确接受等价证据。
2. NNCL baseline 变为同 run paired baseline，不能只使用 formal SOP-C CSV join。
3. 用户 R4 明确确认 formal 命令、预计耗时、输出目录和停止条件。
4. R0e 继续复用 Q35-022 SOP-A/B/C gate，不得用 R0d diagnostic 直接声明 tier。
