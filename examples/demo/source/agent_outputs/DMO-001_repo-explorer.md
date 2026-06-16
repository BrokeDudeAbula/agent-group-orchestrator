# DMO-001 repo-explorer 摘要

## 1. Micro Bench 总说明路径

- `samples/micro_bench/README.md`
- 补充说明：`samples/micro_bench/qwen3_5_micro_replay.md`

## 2. Attention / GDN / MoE Replay 入口

### Attention Replay

- target：`qwen3_5_full_attention_micro_replay`
- 源码：`samples/micro_bench/qwen3_5_full_attention_micro_replay.cc`
- 典型 bundle case：
  - `full_attention_prefill_len1000`
  - `full_attention_prefill_len2000`
  - `full_attention_prefill_len3000`
  - `full_attention_decode_len1000`
  - `full_attention_decode_len2000`
  - `full_attention_decode_len3000`

### GDN Replay

- target：`qwen3_5_gdn_micro_replay`
- 源码：`samples/micro_bench/qwen3_5_gdn_micro_replay.cc`
- backend 环境变量：`LAPE_QWEN35_GDN_BACKEND=lape/fla`
- 典型 bundle case：
  - `gdn_prefill_len1000`
  - `gdn_prefill_len2000`
  - `gdn_prefill_len3000`
  - `gdn_decode_len1000`
  - `gdn_decode_len2000`
  - `gdn_decode_len3000`

### MoE Replay

- target：`qwen3_5_moe_block_micro_replay`
- 源码：`samples/micro_bench/qwen3_5_moe_block_micro_replay.cc`
- bundle 模式：`moe_block_layer_*`

- target：`qwen3_5_routed_moe_micro_replay`
- 源码：`samples/micro_bench/qwen3_5_routed_moe_micro_replay.cc`
- bundle 模式：`routed_moe_layer_*`

### 统一 Runner / 解析脚本

- runner：`samples/micro_bench/scripts/run_qwen35_bench_suite.sh`
- 报告解析：`samples/micro_bench/scripts/parse_bench_results.py`
- 结果对比：`samples/micro_bench/scripts/compare_bench_results.py`
- 35B MoE attention/GDN bundle 抓取：`samples/micro_bench/scripts/capture_qwen35_moe_attention_replay.sh`
- HTML 报告渲染：`scripts/render_micro_replay_report.py`

## 3. Orin 验证脚本路径及用途

- `scripts/run_orin1_qwen35_micro_replay.sh`
  - 用途：同步/编译到 `orin_1` 或 `orin_cv`，执行 Qwen3.5 attention/GDN micro replay 固定 case，并生成本地 markdown 报告。
  - 默认目标：`orin_1`
  - 默认远端 repo：`/workspace/liyang/workspace/lape`
  - 默认模型：`/workspace/models/Qwen3.5/Qwen3.5-4B-GPTQ-Int4`
  - 默认 bundle：`/workspace/liyang/workspace/qwen35_attention_replay`

- `tools/run_orin1_qwen35_gdn_prefill_validation.sh`
  - 用途：在 `orin_1` 验证 GDN prefill replay，覆盖 `gdn_prefill_len1000/2000/3000`，可选 `--run-nsys` 采集 `gdn_prefill_len2000` 的 nsys。
  - 默认 backend：`fla`
  - 默认输出：`analysis/Qwen35_gdn_prefill_validate_<date>_<backend>`

## 4. Baseline / 报告路径

- micro bench baseline 报告：`analysis/qwen35_stage1_attribution/micro_bench/bench_report.md`
- micro bench baseline TSV：`analysis/qwen35_stage1_attribution/micro_bench/bench_results.tsv`
- stage2 冻结 baseline TSV：`analysis/qwen35_stage2_prefill_optimization/baseline/micro_bench_results.tsv`
- 现有完整 micro bench 报告：`analysis/Qwen35_micro_bench_20260525/bench_report.md`
- 现有完整 micro bench HTML：`analysis/Qwen35_micro_bench_20260525/report.html`
- e2e baseline 报告：`analysis/qwen35_stage1_attribution/e2e/report.md`
- stage2 命令口径：`analysis/qwen35_stage2_prefill_optimization/commands.md`

## 5. 本地可做与必须 Orin 做的边界

### 本地可做

- 只读梳理入口、target、脚本、报告路径。
- 查看 `samples/micro_bench/README.md` 和 `samples/micro_bench/qwen3_5_micro_replay.md` 明确用法。
- 查看已有 `analysis/*/bench_report.md`、`bench_results.tsv`、`commands.md` 做 baseline 索引。
- 如本地已有 CUDA/Torch/TensorRT、模型目录和 bundle，可本地构建并运行 replay；否则只能做代码/脚本级检查。

### 必须在 Orin 上做

- 使用默认 Orin 模型和 bundle 的真实 replay 验证。
- `scripts/run_orin1_qwen35_micro_replay.sh` 触发的同步、远端构建、远端 replay。
- `tools/run_orin1_qwen35_gdn_prefill_validation.sh` 的远端 GDN prefill 验证。
- `--run-nsys` 相关 Nsight Systems 采集。
- 依赖 `/workspace/models/...`、`/workspace/liyang/workspace/qwen35_attention_replay`、Orin Docker 容器 `liyang_lape` 的性能口径复现。

## 6. 实际检查过的文件路径

- `samples/micro_bench/README.md`
- `samples/micro_bench/qwen3_5_micro_replay.md`
- `samples/micro_bench/scripts/run_qwen35_bench_suite.sh`
- `samples/micro_bench/scripts/capture_qwen35_moe_attention_replay.sh`
- `samples/micro_bench/qwen3_5_full_attention_micro_replay.cc`
- `samples/micro_bench/qwen3_5_gdn_micro_replay.cc`
- `samples/micro_bench/qwen3_5_moe_block_micro_replay.cc`
- `samples/micro_bench/qwen3_5_routed_moe_micro_replay.cc`
- `samples/micro_bench/qwen3_5_micro_replay_common.h`
- `scripts/run_orin1_qwen35_micro_replay.sh`
- `scripts/render_micro_replay_report.py`
- `tools/run_orin1_qwen35_gdn_prefill_validation.sh`
- `CMakeLists.txt`
- `analysis/Qwen35_micro_bench_20260525/bench_report.md`
- `analysis/qwen35_stage1_attribution/micro_bench/bench_report.md`
- `analysis/qwen35_stage1_attribution/micro_bench/bench_results.tsv`
- `analysis/qwen35_stage1_attribution/e2e/report.md`
- `analysis/qwen35_stage2_prefill_optimization/commands.md`
- `analysis/qwen35_stage2_prefill_optimization/baseline/micro_bench_results.tsv`
