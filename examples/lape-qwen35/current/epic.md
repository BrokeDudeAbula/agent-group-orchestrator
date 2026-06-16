# Current Epic: Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP

## 目标

使用 `/goal` 模式启动并执行 `Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP`，让当前 repo 的 CuteDSL/CUTLASS spike 方案尽可能与 same-run NNCL `MoeGroupGemm` 性能对齐。

启动命令：

```text
/goal Q35-MOE-CUTEDSL-R0H-FUSED-W4A16-MAINLOOP: make current repo CuteDSL/CUTLASS spike performance align with same-run NNCL MoeGroupGemm on orin_1 by building an independent fused W4A16 int4-dequant + scale-iterator + grouped-mainloop pipeline
```

测试目标设备固定为 `orin_1`。性能结论不得切换到 `orin_cv`、本地 GPU 或其他平台。

## 背景

`Q35-MOE-CUTEDSL-R0F-R1-PROBE` 已完成 M5 feasibility，结论为：

`done / reject_or_hold / probe-only / not production`

AUTO-114 到 AUTO-126 已证明：

- raw HF GPTQ decode+matmul correctness 可行。
- Tensor Core WMMA 能被正确调用，NCU 已抓到 `RawGptqW4A16GroupedWmmaKernel`。
- single-launch、shared-A、hybrid small-row、packed loader、single-kernel、threshold/warps/cols 调参均有局部收益。
- 最新 AUTO-126 最佳 `small_row_cols_per_warp=8` 仍只有 M64/M898 ratio `2.112438x / 2.273437x`，geomean `2.191459x`，明显高于 `<=1.20x`，且仍 `>1.50x`。

因此当前 raw CUDA/WMMA 局部参数 probe 线停止。下一步必须实现 true independent fused GPTQ W4A16 grouped mainloop，而不是继续调 `threshold/warps/cols`。

## 固定边界

- 必须基于 agent_group 规则组织 sub-agent 完成目标。
- main-orchestrator 负责编排、agent output、memory sync 和 stop/go gate。
- baseline 固定为 same-run NNCL `MoeGroupGemm`。
- 初级目标：family A/B geomean ratio `<=1.50x`。
- 最终目标：family A/B geomean ratio `<=1.20x`，同时检查 hot `M898` 与 small `M64`。
- 不修改 production Qwen3.5 推理路径。
- 不得把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner` 或 `dispatch_moe_gemm_to_cutlass` 包装成 candidate。
- 所有 probe 输出默认 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`。

## Worker 编排

| worker | 职责 |
|---|---|
| repo-explorer | 梳理当前 spike、AUTO-114 到 AUTO-126 evidence、NNCL `MoeFCGemm` / `dq_mma_multistage_finegrained` 快路径 |
| qwen-architect | 定义 Qwen3.5 MoE W4A16 grouped GEMM 数据流和 formal 边界 |
| oss-scout | 只读对照 CUTLASS grouped GEMM、mixed-input GEMM、MoE 示例，不引入 production 依赖 |
| kernel-dev | 在 spike-only 路径实现 independent fused W4A16 mainloop |
| orin-runner | 只在 `orin_1` 构建、运行 micro、抓 NCU，并回传日志 |
| perf-analyst | 固定 NNCL baseline 口径，解析 ratio、geomean、M64/M898、launch count、NCU 指标 |
| reviewer | 审查是否误用 NNCL kernel、是否越界为 SOP/tier、是否污染 timing |
| main-orchestrator | 每个 milestone 后写 orchestration summary，并同步 current/memory |

## 写入范围

允许写：

```text
samples/micro_bench/spike/cute_dsl/
samples/micro_bench/spike/cute_dsl/independent_w4a16_fused/
analysis/Qwen35_cutedsl_r0h_fused_w4a16_<TS>/
.codex/agent_group/
必要的 spike CMakeLists.txt 接入
```

禁止写 production path，除非用户另行明确授权。

## Milestones

1. M0 目标初始化与基线锁定：用 `/goal` 启动；确认 `orin_1`；固定 same-run NNCL baseline；写入 R3/R4 边界和停止条件。
2. M1 NNCL 快路径反向规格化：输出 `nncl_fastpath_spec.md`，抽象 packed int4 B iterator、scale iterator、cp.async pipeline、MoE problem visitor。
3. M2 单 expert fused W4A16 mainloop smoke：固定单 expert / `gate_proj` / `K=2048,N=512` / `group_size=128`，证明非零、finite、precision pass 和 NCU candidate identity。
4. M3 加入 scale iterator + packed B pipeline：不允许全量 predecode；scale/B tile 进入 shared memory；dequant 在 mainloop 中完成。
5. M4 MoE grouped problem visitor：使用 `cu_row / total_rows_before_expert`，支持 active experts 变化，candidate launch count 控制在 1。
6. M5 `orin_1` full shape probe：family A/B 10 shape same-run NNCL 对比，主指标 geomean，辅助看 `M64/M898`。
7. M6 NCU isolation：必须抓到 independent fused candidate kernel，不是 `MoeFCGemm`，记录 duration、occupancy、Tensor Core utilization、memory throughput、register/thread、shared memory/block。
8. M7 formal 决策：只允许 `promote_to_formal_sop`、`continue_probe`、`reject_or_hold` 三种输出。若 promoted，必须新建 formal task 并重新走 SOP-A/B/C。

## Stop Conditions

- `orin_1` 构建失败。
- candidate 输出 NaN/Inf/全零。
- NCU 抓不到 independent candidate kernel。
- NCU 只抓到 `MoeFCGemm` / `MoeGroupGemm`。
- ratio 连续两轮 `>1.50x` 且没有明确结构性改进证据。
- 需要修改 production path 才能继续。

## 参考

- `.codex/agent_group/current/agent_outputs/AUTO-20260609-127_r0h_fused_w4a16_plan_sync.md`
- `.codex/agent_group/current/agent_outputs/AUTO-20260609-126_r0g_smallrow_cols_probe_kernel-dev.md`
- `analysis/Qwen35_cutedsl_r0g_smallrow_cols_probe_20260609_126/report.md`
- `analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/report.md`
- `third_party/nncl/nncl/csrc/cuda/kernel/cutlass_kernels/moe_group_gemm/moe_cutlass_group_gemm_template.h`
- `third_party/nncl/nncl/csrc/cuda/include/cutlass_extensions/gemm/kernel/moe_cutlass_kernel.h`
- `third_party/nncl/nncl/csrc/cuda/include/cutlass_extensions/gemm/threadblock/dq_mma_multistage_finegrained.h`
