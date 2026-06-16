# AUTO-20260609-138 R0H orin_1 Synthetic NNCL Paired R4 Package

日期：2026-06-09

## 结论

R0H 下一步 R4 前置执行包已准备，但尚未获得用户确认，未执行任何 `orin_1` 同步、构建、运行或回传命令。

本包只用于在 `orin_1` 验证 synthetic paired scaffold：

```text
routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired
```

验证目标是确认 R0H synthetic A/B shape 的 qweight pack、scale layout、NNCL int64 end-prefix `cu_row` 和 same-run public NNCL `MoeGroupGemm` baseline 在 sm87 上能闭环。它不是 true-bundle runner，不是正式 M5 full shape probe，不是 SOP/tier/formal evidence。

## Sub-agent 编排

- `repo-explorer` / Russell：只读核对 `main.cc`、spike CMake、runbook 和 AUTO-136，确认 binary、mode、CLI flags、远端构建口径、输出目录和停止条件。
- `main-orchestrator`：整合 R4 command/time/output/stop package，并同步 agent_group 记忆。
- `reviewer`：待本包写入后审查是否满足 R4 门禁、是否越界为 formal/SOP/tier、是否误用 NNCL 作为 candidate。

## 固定边界

- target：`orin_1`
- host：`orin_1`
- container：`liyang_lape`
- remote repo：`/workspace/liyang/workspace/lape`
- local repo：`/workspace/liyang/lape_a6d6bfb9`
- local output dir：

```text
/workspace/liyang/lape_a6d6bfb9/analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546
```

- remote output dir：

```text
/workspace/liyang/workspace/lape/analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546
```

- binary：

```text
build_cute_dsl_spike_orin1/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike
```

- mode：

```text
routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired
```

NNCL 仅作为 public baseline/reference：

```text
MoeGroupGemm<half, half, QuantMethod::kGPTQFp16Int4Groupwise>
```

candidate 仍为 R0H independent grouped visitor kernel：

```text
R0HFusedW4A16GroupedVisitorWmmaKernel
```

禁止把 NNCL `MoeFCGemm`、`MoeGroupGemmRunner`、`dispatch_moe_gemm_to_cutlass` 或 NNCL CUTLASS extension fastpath 包装为 candidate。

## 待确认命令

以下所有命令均属于 R4。用户确认前不得执行。

### 1. 同步源码

```bash
SKILL_SCRIPT=~/.codex/skills/sync-orin-lape-build/scripts/sync_orin_lape_build.sh

bash "$SKILL_SCRIPT" \
  --target orin_1 \
  --source /workspace/liyang/lape_a6d6bfb9 \
  --sync-only
```

### 2. 远端配置和构建 spike target

```bash
ssh orin_1 'docker exec liyang_lape bash -lc "
set -euo pipefail
cd /workspace/liyang/workspace/lape
cmake -S . -B build_cute_dsl_spike_orin1 \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CUDA_ARCHITECTURES=87 \
  -DLAPE_BUILD_SPIKE_CUTE_DSL=ON
cmake --build build_cute_dsl_spike_orin1 \
  --target qwen3_5_cute_dsl_spike -j 4
"'
```

### 3. M64 smoke

该命令只跑 A/B family 的 `M=64` 两行，用于快速暴露 NNCL arch/runtime/layout 错误。为缩短风险窗口，`warmup=1,iters=3`。

```bash
ssh orin_1 'docker exec liyang_lape bash -lc "
set -euo pipefail
cd /workspace/liyang/workspace/lape
OUT=analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546
mkdir -p \"\$OUT\"
./build_cute_dsl_spike_orin1/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired \
  --output_csv=\"\$OUT/r0h_m5_synthetic_nncl_paired_m64_smoke.csv\" \
  --m_filter=64 \
  --warmup=1 \
  --iters=3 \
  2>&1 | tee \"\$OUT/r0h_m5_synthetic_nncl_paired_m64_smoke.log\"
"'
```

### 4. A/B 10 shape 主验证

仅当 M64 smoke 通过后执行。该命令覆盖 family A/B 10 shape，使用 `warmup=5,iters=50`。

```bash
ssh orin_1 'docker exec liyang_lape bash -lc "
set -euo pipefail
cd /workspace/liyang/workspace/lape
OUT=analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546
mkdir -p \"\$OUT\"
./build_cute_dsl_spike_orin1/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike \
  --mode=routed_grouped_r0h_fused_w4a16_grouped_visitor_m5_synthetic_nncl_paired \
  --output_csv=\"\$OUT/r0h_m5_synthetic_nncl_paired_all_shapes.csv\" \
  --m_filter=0 \
  --warmup=5 \
  --iters=50 \
  2>&1 | tee \"\$OUT/r0h_m5_synthetic_nncl_paired_all_shapes.log\"
"'
```

### 5. 回传结果

仅当 smoke 或 all-shapes 至少有一个生成远端输出目录时执行。

```bash
mkdir -p /workspace/liyang/lape_a6d6bfb9/analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546
ssh orin_1 'docker exec liyang_lape bash -lc "
cd /workspace/liyang/workspace/lape/analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546
tar -cf - .
"' | tar -xf - -C /workspace/liyang/lape_a6d6bfb9/analysis/Qwen35_cutedsl_r0h_synthetic_nncl_paired_orin_1_20260609_093546
```

## 预计时间

- 同步：约 1-3 分钟。
- CMake configure + spike target build：约 5-15 分钟，取决于远端 build cache。
- M64 smoke：约 1-3 分钟。
- A/B 10 shape 主验证：约 3-8 分钟。
- 回传：约 1 分钟。

预计总时间：约 10-30 分钟。

## 输出文件

远端与本地输出目录都应包含：

```text
r0h_m5_synthetic_nncl_paired_m64_smoke.csv
r0h_m5_synthetic_nncl_paired_m64_smoke.log
r0h_m5_synthetic_nncl_paired_all_shapes.csv
r0h_m5_synthetic_nncl_paired_all_shapes.log
```

如果 M64 smoke 失败，则只要求回传 smoke CSV/log 或失败日志。

## 成功判据

M64 smoke 至少要求：

- 进程返回 0。
- CSV 有 header + 2 行数据。
- 两行均 `precision_pass=true`。
- 两行均有有限 `nncl_ms`、`candidate_vs_nncl_ratio`、`max_abs_vs_nncl`、`rmse_vs_nncl`。
- 两行均 `baseline_uses_nncl_moegroupgemm=true`。
- 两行均 `candidate_uses_nncl_moefc=false`、`candidate_uses_nncl_moegroupgemm=false`、`candidate_uses_dispatch_moe_gemm_to_cutlass=false`、`candidate_uses_nncl_cutlass_extension_headers=false`。
- 两行均 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`、`candidate_audit_pending=true`、`independent_candidate=false`。
- 两行均保持 `runner_ready=false`。该 scaffold 即使在 `orin_1` 上跑通，也不得升级为 full M5 ready。

A/B 10 shape 主验证额外要求：

- CSV 有 header + 10 行数据。
- 覆盖 A family `M=64/128/256/512/898,K=2048,N=512,gate_proj`。
- 覆盖 B family `M=64/128/256/512/898,K=512,N=2048,down_proj`。
- 所有行满足 M64 smoke 的字段要求。

## 停止条件

任一条件触发即停止，不扩大验证：

- sync 失败。
- CMake configure 或 build 失败。
- `qwen3_5_cute_dsl_spike` 未生成。
- M64 smoke 非零退出。
- CSV 无法写入或没有数据行。
- `orin_1` 上仍出现 NNCL arch unsupported。
- 出现 CUDA illegal access、NaN/Inf、进程崩溃或输出全零。
- 任一 shape `precision_pass=false`。
- paired 输出缺少 `nncl_ms`、`candidate_vs_nncl_ratio`、`max_abs_vs_nncl` 或 `rmse_vs_nncl`。
- CSV 或日志出现 `valid_for_sop_a=true`、`valid_for_sop_c=true`、`tier_eligible=true`。
- CSV 或日志把 synthetic scaffold 宣称为 full M5 ready、formal evidence、SOP evidence、tier evidence 或 production evidence。

## 结果边界

即使本包在 `orin_1` 上全部通过，也只能说明 synthetic paired scaffold 可在 sm87 上闭合 same-run NNCL baseline。它不能证明：

- true Q35-028 bundle grouped hidden/input 已接入。
- HF raw GPTQ weights 的 candidate timed path 已接入。
- family B `down_proj` 的真实 `silu(gate) * up` 输入已接入。
- full M5 true-bundle family A/B probe 已完成。
- M6 NCU identity 已完成。
- formal/SOP/tier/production 已通过。

通过后下一步仍是：把 true bundle grouped hidden / HF raw weights 接入 R0H candidate timed path，并补 true bundle same-run NNCL paired runner。
