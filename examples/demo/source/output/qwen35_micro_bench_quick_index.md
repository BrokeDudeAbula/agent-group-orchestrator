# Qwen3.5 Micro Bench / Orin 验证 Quick Index

本文是给新 agent 的快速索引：3 分钟内定位 Qwen3.5 micro bench、Orin 验证入口和 baseline 报告。路径均相对 repo 根目录 `/Users/liyang/Desktop/workspace/lape`。

## 1. 首先看哪里

- Micro bench 总说明：`samples/micro_bench/README.md`
- Qwen3.5 replay 补充说明：`samples/micro_bench/qwen3_5_micro_replay.md`
- 统一 bench suite runner：`samples/micro_bench/scripts/run_qwen35_bench_suite.sh`
- 报告解析：`samples/micro_bench/scripts/parse_bench_results.py`
- 结果对比：`samples/micro_bench/scripts/compare_bench_results.py`
- HTML 报告渲染：`scripts/render_micro_replay_report.py`

## 2. Replay Target / 源码入口

### Attention

- target：`qwen3_5_full_attention_micro_replay`
- 源码：`samples/micro_bench/qwen3_5_full_attention_micro_replay.cc`
- 常见 case：`full_attention_prefill_len1000/2000/3000`、`full_attention_decode_len1000/2000/3000`
- 35B MoE attention/GDN bundle 抓取脚本：`samples/micro_bench/scripts/capture_qwen35_moe_attention_replay.sh`

### GDN

- target：`qwen3_5_gdn_micro_replay`
- 源码：`samples/micro_bench/qwen3_5_gdn_micro_replay.cc`
- backend 环境变量：`LAPE_QWEN35_GDN_BACKEND=lape/fla`
- 常见 case：`gdn_prefill_len1000/2000/3000`、`gdn_decode_len1000/2000/3000`

### MoE

- MoE block target：`qwen3_5_moe_block_micro_replay`
- MoE block 源码：`samples/micro_bench/qwen3_5_moe_block_micro_replay.cc`
- Routed MoE target：`qwen3_5_routed_moe_micro_replay`
- Routed MoE 源码：`samples/micro_bench/qwen3_5_routed_moe_micro_replay.cc`
- 通用 replay 辅助头：`samples/micro_bench/qwen3_5_micro_replay_common.h`

## 3. Orin 验证入口

- `scripts/run_orin1_qwen35_micro_replay.sh`
  - 用途：同步到 `orin_1` 或 `orin_cv`，远端构建并执行 Qwen3.5 attention/GDN micro replay 固定 case。
  - 默认目标：`orin_1`
  - 默认远端 repo：`/workspace/liyang/workspace/lape`
  - 默认模型：`/workspace/models/Qwen3.5/Qwen3.5-4B-GPTQ-Int4`
  - 默认 bundle：`/workspace/liyang/workspace/qwen35_attention_replay`

- `tools/run_orin1_qwen35_gdn_prefill_validation.sh`
  - 用途：在 `orin_1` 验证 GDN prefill replay，覆盖 `gdn_prefill_len1000/2000/3000`。
  - 可选 `--run-nsys`：采集 `gdn_prefill_len2000` 的 Nsight Systems 数据。
  - 默认 backend：`fla`
  - 默认输出：`analysis/Qwen35_gdn_prefill_validate_<date>_<backend>`

## 4. Baseline / 报告路径

### E2E Baseline

- 当前主要 E2E 报告：`analysis/Qwen35_e2e_orin_1_20260526/report.md`
- E2E HTML：`analysis/Qwen35_e2e_orin_1_20260526/report.html`
- E2E MoE 表：`analysis/Qwen35_e2e_orin_1_20260526/tables/moe.md`
- 旧 baseline：`analysis/Qwen35_e2e_orin_1_20260525/report.md`
- stage1 E2E 摘要：`analysis/qwen35_stage1_attribution/e2e/report.md`
- stage2 冻结 E2E baseline：`analysis/qwen35_stage2_prefill_optimization/baseline/e2e_text_baseline.tsv`

### Micro Bench Baseline

- 当前主要 micro bench 报告：`analysis/Qwen35_micro_bench_20260525/bench_report.md`
- 明细 TSV：`analysis/Qwen35_micro_bench_20260525/bench_results.tsv`
- HTML：`analysis/Qwen35_micro_bench_20260525/report.html`
- stage1 micro bench baseline：`analysis/qwen35_stage1_attribution/micro_bench/bench_report.md`
- stage1 micro bench TSV：`analysis/qwen35_stage1_attribution/micro_bench/bench_results.tsv`
- stage2 冻结 micro bench baseline：`analysis/qwen35_stage2_prefill_optimization/baseline/micro_bench_results.tsv`

### 35B MoE True-shape Attention/GDN

- 关键报告：`analysis/Qwen35_moe_attention_replay_20260525/bench_suite_20260525_042637/bench_report.md`
- 用途：查看 35B MoE 真实 shape 下的 attention/GDN replay，而不是 dense 4B surrogate 口径。

### 辅助归因与 Profile

- 层结构摘要：`analysis/qwen35_stage1_attribution/layer_count_summary.md`
- TTFT 闭包归因：`analysis/qwen35_stage1_attribution/stage1_attribution_closure.tsv`
- E2E text slope：`analysis/qwen35_stage1_attribution/e2e_text_slope.md`
- nsys 热点摘要：`analysis/Qwen35_stage1_nsys_orin1_20260525/report/summary.md`
- stage2 命令口径：`analysis/qwen35_stage2_prefill_optimization/commands.md`
- MoE T2 profile 单 case：`analysis/qwen35_stage2_prefill_optimization/moe/profile_run/bench_report.md`

## 5. 指标口径风险

- Micro bench 是单模块 replay/bench latency，不是完整请求 E2E latency；不能把单模块 ms 直接当作用户侧总延迟。
- E2E 指标来自 `qwen3_5_vl_perf`，重点看 `E2E Time`、`TTFT`、`p-ntokens/s`、`ntokens/s`、`ViT`、`VTokenNum`。
- `analysis/Qwen35_micro_bench_20260525` 的口径：`warmup=10`、`iters=50`、`gdn_backend=fla`。
- 20260525 micro bench 中，部分 attention/GDN 和 decoder layer 使用 dense 4B surrogate；不能直接代表 35B MoE 的 attention/GDN 层耗时。
- 35B MoE true-shape attention/GDN 应参考：`analysis/Qwen35_moe_attention_replay_20260525/bench_suite_20260525_042637/bench_report.md`。
- MoE replay 使用目标 MoE 模型，典型 hidden size 为 `2048`；dense surrogate attention/GDN 常见 hidden size 为 `2560`，比较时必须先确认 shape。

## 6. 本地可做 vs 必须在 Orin 上做

### 本地可做

- 只读检查源码、脚本、README 和已有 `analysis` 报告。
- 梳理 target、case、bundle、报告字段和 baseline 路径。
- 在不缺 CUDA/Torch/TensorRT、模型和 bundle 的前提下，可做本地构建或 replay；缺任一依赖时只做代码级检查。
- 用已有 `bench_report.md`、`bench_results.tsv`、`report.md` 做指标索引和归因阅读。

### 必须在 Orin 上做

- 使用 Orin 默认模型和 bundle 复现真实性能口径。
- 执行 `scripts/run_orin1_qwen35_micro_replay.sh` 触发的同步、远端构建、远端 replay。
- 执行 `tools/run_orin1_qwen35_gdn_prefill_validation.sh` 的远端 GDN prefill 验证。
- 任何 `--run-nsys` 或 Nsight Systems 采集。
- 依赖 `/workspace/models/...`、`/workspace/liyang/workspace/qwen35_attention_replay`、Orin Docker 容器 `liyang_lape` 的验证。

## 7. 速查结论

- 找入口：先看 `samples/micro_bench/README.md`。
- 找 target：看 `samples/micro_bench/qwen3_5_*_micro_replay.cc` 和对应 CMake target 名。
- 找 Orin 验证：看 `scripts/run_orin1_qwen35_micro_replay.sh` 与 `tools/run_orin1_qwen35_gdn_prefill_validation.sh`。
- 找 E2E baseline：优先看 `analysis/Qwen35_e2e_orin_1_20260526/report.md`。
- 找 micro baseline：优先看 `analysis/Qwen35_micro_bench_20260525/bench_report.md`。
- 判断 35B MoE attention/GDN：优先看 `analysis/Qwen35_moe_attention_replay_20260525/bench_suite_20260525_042637/bench_report.md`。
