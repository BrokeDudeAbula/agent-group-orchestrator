# DMO-002 perf-analyst 只读摘要

## 1. Baseline E2E 报告路径与关键指标

主路径：`analysis/Qwen35_e2e_orin_1_20260526/report.md`  
同目录：`report.html`、`tables/moe.md`、`tables/moe.html`  
设备：`orin_1`  
模型标识：`model_list.txt` 显示 `moe`；远端命令为 `./qwen3_5_vl_perf <selected_model_path> --test_data_dir ...`

可见关键指标：

| Case | InLen | OutLen | E2E ms | TTFT ms | p-ntokens/s | ntokens/s | ViT ms | VTokenNum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 纯文本 500 | 504 | 128 | 2569.78 | 214.96 | 2344.62 | 54.2 | 0.00 | 0 |
| 纯文本1000 | 1004 | 128 | 2758.22 | 393.15 | 2553.75 | 54.1 | 0.00 | 0 |
| 纯文本2000 | 2004 | 128 | 3142.81 | 748.94 | 2675.78 | 53.8 | 0.00 | 0 |
| 纯文本3000 | 3004 | 128 | 3492.20 | 1078.09 | 2786.42 | 53.7 | 0.00 | 0 |
| 1张图片 | 231 | 128 | 2573.05 | 155.74 | 1483.28 | 54.7 | 48.93 | 196 |
| 8张图片 | 1617 | 128 | 3634.14 | 648.71 | 2492.65 | 54.1 | 537.75 | 1568 |

补充：`analysis/Qwen35_e2e_orin_1_20260525/report.md` 也存在，stage1 派生分析使用该轮作为旧 baseline；其中纯文本 3000 为 `E2E=3706.92 ms`、`TTFT=1260.75 ms`、`p-ntokens/s=2382.70`。

## 2. Baseline Micro Bench 报告路径与关键指标

主路径：`analysis/Qwen35_micro_bench_20260525/bench_report.md`  
明细表：`analysis/Qwen35_micro_bench_20260525/bench_results.tsv`  
HTML：`analysis/Qwen35_micro_bench_20260525/report.html`  
设备：`orin_1`  
远端输出目录：`/workspace/liyang/workspace/lape/analysis/Qwen35_micro_bench_20260525_110510`  
命令口径：`warmup=10`、`iters=50`、`gdn_backend=fla`，dense 模型为 `Qwen3.5-4B-GPTQ-Int4`，MoE 模型为 `Qwen3.5-35B-A3B-GPTQ-Int4-lmhead`。

结果汇总：`Total cases=68`，`Passed=68`，`Crashed=0`，`Incomplete=0`，`NaN detected=0`。

代表性 latency：

| 模块/Case | 口径 | Latency ms |
|---|---|---:|
| full_attention_prefill_len3000 | num_tokens=3000, hidden_size=2560 | 27.516 |
| gdn_prefill_len3000 | num_tokens=3000, hidden_size=2560, backend=fla | 31.201 |
| prefill_len3000__moe_block_layer_0_prefill_0 | num_tokens=3004, hidden_size=2048 | 16.236 |
| prefill_len3000__routed_moe_layer_0_prefill_0 | num_tokens=3004, hidden_size=2048 | 14.654 |
| decoder_full_attention_prefill_3000 | num_tokens=3000, hidden_size=2560 | 56.293 |
| decoder_gdn_fla_prefill_3000 | num_tokens=3000, hidden_size=2560 | 66.573 |
| expert_block_prefill_3000 | num_tokens=3000, hidden_size=2048 | 16.871 |
| attn_qkv_prefill_3000 | M=3000, K=2560, N=10240 | 4.673 |
| gdn_in_proj_qkv_prefill_3000 | M=3000, K=2560, N=8192 | 3.738 |
| mlp_gate_up_prefill_3000 | M=3000, K=2560, N=18432 | 8.380 |

注意：`layer_count_summary.md` 明确指出，micro bench 中 attention replay、decoder layer、dense MLP 默认使用 dense 4B 模型路径，不能直接代表 35B MoE 的 attention/GDN 层耗时；MoE replay 使用目标 MoE 模型，hidden size 为 2048。

## 3. 其他重要 Qwen3.5 Baseline / MoE / GDN / Attention Analysis 路径

- `analysis/Qwen35_moe_attention_replay_20260525/bench_suite_20260525_042637/bench_report.md`  
  35B MoE true-shape attention/GDN replay：full_attention layer3 prefill len3004 `11.972 ms`；GDN layer0 prefill len3004 `14.579 ms`；2/2 通过。

- `analysis/qwen35_stage1_attribution/layer_count_summary.md`  
  35B MoE 配置摘要：`40` 层；`10` 个 full attention；`30` 个 GDN/linear attention；`40` 个 MoE MLP；无独立 dense MLP；`num_experts=256`，`num_experts_per_tok=8`。

- `analysis/qwen35_stage1_attribution/e2e_text_slope.md`  
  基于 20260525 E2E：1000 到 3000 token 平均斜率 `0.3976 ms/token`，增量吞吐约 `2515.4 tokens/s`。

- `analysis/qwen35_stage1_attribution/stage1_attribution_closure.tsv`  
  以 20260525 纯文本 3000 TTFT 为闭包：full_attention `119.720 ms / 9.50%`，GDN `437.370 ms / 34.69%`，MoE MLP `649.440 ms / 51.51%`，剩余项 `54.220 ms / 4.30%`。

- `analysis/Qwen35_stage1_nsys_orin1_20260525/report/summary.md`  
  nsys 热点摘要：系统行为中 `futex`、`pthread_cond_wait`、`cudaMemcpyAsync`、`cudaStreamSynchronize` 较显著；GPU kernel 侧可见 Quantized GEMM、Linear/GEMM、GDN/attention 相关热点。

- `analysis/qwen35_stage2_prefill_optimization/baseline/`  
  stage2 冻结 baseline：`e2e_text_baseline.tsv`、`micro_bench_results.tsv`、`nsys_kernel_groups.tsv`、`stage1_attribution_closure.tsv`。

- `analysis/qwen35_stage2_prefill_optimization/moe/profile_run/bench_report.md`  
  MoE T2 profile 单 case：`expert_block_prefill_3000`，`num_tokens=3000`、`hidden_size=2048`、`latency=16.745 ms`、通过。

## 4. 指标口径说明

- E2E 指标来自 `qwen3_5_vl_perf`，主要字段为 `E2E Time`、`Preproc`、`TTFT`、`p-ntokens/s`、`ntokens/s`、`ViT`、`VTokenNum`。
- E2E 纯文本 case 固定 `OutLen=128`；输入长度覆盖约 `500/1000/1500/2000/2500/3000` token。
- Micro bench 指标为单模块 replay/bench latency，字段包括 `Latency (ms)`、`Batch Repeat`、`Exit`；不是完整请求 E2E latency。
- Micro bench 20260525 使用 `warmup=10`、`iters=50`，GDN backend 为 `fla`。
- 35B MoE true-shape attention/GDN 应优先参考 `Qwen35_moe_attention_replay_20260525`，不要直接用 dense 4B surrogate 作为 35B attention/GDN 结论。

## 5. 实际检查过的文件路径

- `.codex/agent_group/demo/tasks.csv`
- `analysis/Qwen35_e2e_orin_1_20260526/report.md`
- `analysis/Qwen35_e2e_orin_1_20260526/tables/moe.md`
- `analysis/Qwen35_e2e_orin_1_20260526/target.txt`
- `analysis/Qwen35_e2e_orin_1_20260526/model_list.txt`
- `analysis/Qwen35_e2e_orin_1_20260526/run_qwen35_e2e.remote_cmd.txt`
- `analysis/Qwen35_e2e_orin_1_20260526/remote_output_dir.txt`
- `analysis/Qwen35_e2e_orin_1_20260525/report.md`
- `analysis/Qwen35_micro_bench_20260525/bench_report.md`
- `analysis/Qwen35_micro_bench_20260525/bench_results.tsv`
- `analysis/Qwen35_micro_bench_20260525/target.txt`
- `analysis/Qwen35_micro_bench_20260525/remote_output_dir.txt`
- `analysis/Qwen35_micro_bench_20260525/run_qwen35_micro_bench.remote_cmd.txt`
- `analysis/Qwen35_moe_attention_replay_20260525/bench_suite_20260525_042637/bench_report.md`
- `analysis/qwen35_stage1_attribution/e2e_text_slope.md`
- `analysis/qwen35_stage1_attribution/layer_count_summary.md`
- `analysis/qwen35_stage1_attribution/stage1_attribution_closure.tsv`
- `analysis/Qwen35_stage1_nsys_orin1_20260525/report/summary.md`
- `analysis/qwen35_stage2_prefill_optimization/commands.md`
- `analysis/qwen35_stage2_prefill_optimization/baseline/e2e_text_baseline.tsv`
- `analysis/qwen35_stage2_prefill_optimization/baseline/micro_bench_results.tsv`
- `analysis/qwen35_stage2_prefill_optimization/moe/profile_run/bench_report.md`
