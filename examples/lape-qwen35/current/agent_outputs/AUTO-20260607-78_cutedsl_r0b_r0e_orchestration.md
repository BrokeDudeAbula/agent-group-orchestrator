# AUTO-20260607-78 CuTeDSL R0b-R0e Sub-Agent Orchestration

## 结论

已基于 sub-agent 结果把 `Q35-MOE-CUTEDSL-W4A16-GROUPED-R0` 拆成可执行 DAG：

```text
R0b toolchain smoke -> R0c single projection correctness -> R0d routed grouped micro -> R0e formal SOP-A/B/C
```

当前状态是 **R0b 本地准备完成，等待用户 R4 确认后执行 Orin sm_87 import/compile smoke**。R0b 还没有完成，因为本轮没有启动 Orin、CUDA workload、NCU 或 nsys。

## Sub-Agent 结果

| agent | role | 结果 |
|---|---|---|
| `019ea289-566b-7381-abad-3ac9cc948f12` / Locke | repo-explorer | 确认 CuTeDSL R0a scaffold、Q35-028 bundle、HF GPTQ raw tensor 与 Marlin 可迁移资产；建议复用 bundle guard、top-k 重建、raw GPTQ guard、dense/manual oracle，禁止复用 Marlin packed layout 和 `perm64` scales layout。 |
| `019ea289-7b4b-7d53-9395-da6f886c2c48` / Heisenberg | oss-scout | 确认本地 CuTeDSL runtime 有 `sm_87` mapping，Ampere 示例包含 `elementwise_add.py`、`tensorop_gemm.py`、`sgemm.py`；建议 R0c 先做 Python CuTeDSL fp16 dense GEMM correctness，B 由 raw GPTQ 在 Python/torch 侧 dequant 到 fp16。 |
| `019ea289-f527-7d01-880d-e1d9ef3b0893` / Avicenna | qwen-architect | 给出 R0b/R0c/R0d/R0e 阶段 gate、worker DAG、本地与 Orin/R4 边界；确认所有真实 compile/run、NCU、SOP-A/B/C 均需用户 R4 确认。 |
| `019ea28a-1b6b-78d1-8930-f52baab9b3cb` / Pascal | kernel-dev | 新增 R0b 本地脚本 `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_toolchain_smoke.py`，并更新 README；dry-run 只检查路径、PYTHONPATH、Ampere 示例和 sm_87 mapping，不 import CuTeDSL heavy packages，不跑 CUDA。 |

## 已落盘资产

- `samples/micro_bench/spike/cute_dsl/scripts/cutedsl_toolchain_smoke.py`
- `samples/micro_bench/spike/cute_dsl/README.md`
- 本地验证输出：
  - `/tmp/q35_cutedsl_r0b_toolchain_smoke_main_verify/cutedsl_toolchain_smoke_dry_run.csv`
  - `/tmp/q35_cutedsl_r0b_toolchain_smoke_main_verify/cutedsl_toolchain_smoke_dry_run.json`
  - `/tmp/q35_cutedsl_r0b_toolchain_smoke_main_verify/cutedsl_toolchain_smoke_dry_run.md`

R0b dry-run 结果：

- `status=pass`
- `requested_arch=sm_87`
- `arch_mapping_contains_requested=true`
- `elementwise_compile_status=todo_guard_not_run`
- `tensorop_gemm_compile_status=todo_guard_not_run`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## 阶段 Gate

| 阶段 | 状态 | 进入条件 | 完成条件 |
|---|---|---|---|
| R0a scaffold | done | Marlin SOP-C 10 shape 与 Q35-028 bundle 固定 | 独立 target 默认 OFF；manifest/toolchain path check PASS；非 SOP 证据字段固定 false |
| R0b toolchain smoke | in_progress | R0a done；CUTLASS/CuTeDSL repo 可见；R0b dry-run PASS | Orin `sm_87` 上 CuTeDSL import PASS；elementwise compile/run PASS；fp16 tensorop GEMM smoke 有明确 PASS/FAIL；输出仍非 SOP 证据 |
| R0c single projection correctness | todo | R0b Orin smoke PASS | gate/up/down 三类 projection 覆盖；raw GPTQ guard PASS；dense/manual int4 oracle 与 CuTeDSL fp16 dense GEMM 对齐 |
| R0d routed grouped micro | todo | R0c gate/up/down correctness PASS | 构造 routed rows/expert remap/cu_row；覆盖 Marlin SOP-C 10 shape；与 NNCL grouped baseline 统一 CSV |
| R0e formal SOP-A/B/C | todo | R0d 10 shape precision/timing 完整；reviewer 无 P0/P1 | 用户 R4 确认后跑正式 Orin SOP-A/B/C；不得用 R0a/R0b/R0c 证据替代 |

## 关键技术取舍

- R0c 第一条 correctness 主线使用 **Python CuTeDSL fp16 dense GEMM**。权重 B 先由 HF raw `qweight/qzeros/scales/g_idx` 在 Python/torch 侧 dequant 到 fp16。
- fused W4A16 decode+matmul 不作为 R0c 必达项；只能在 dense-dequant correctness 通过后作为 candidate-only 分支。
- Hopper/Blackwell grouped GEMM 示例只可借鉴问题表、group search、per-group pointer/stride 思想，不能直接迁移到 Orin `sm_87`。
- 若 Python CuTeDSL 在 Orin `sm_87` 上 elementwise 或 tensorop GEMM smoke 失败，停止 Python DSL 路线并评估 CuTe/CUTLASS C++ fallback。

## 下一步执行队列

1. `Q35-MOE-CUTEDSL-R0B-TOOLCHAIN-SMOKE`
   - 当前：本地脚本与 dry-run PASS。
   - 下一步：向用户请求 R4，明确 Orin 命令、预计耗时、输出目录和停止条件。
2. `Q35-MOE-CUTEDSL-R0C-SINGLE-PROJECTION-CORRECTNESS`
   - 当前：todo。
   - 本地可先准备 HF raw tensor loader、qzeros/g_idx guard、CPU/torch dense-dequant oracle。
3. `Q35-MOE-CUTEDSL-R0D-ROUTED-GROUPED-MICRO`
   - 当前：todo。
   - 依赖 R0c 三类 projection 通过；不得跳过 R0c 直接做 timing。
4. `Q35-MOE-CUTEDSL-R0E-FORMAL-SOP-ABC`
   - 当前：todo。
   - 只能在 R0d 完整后进入；必须复用 Q35-022 SOP-A/B/C gate。

## 本地验证

```bash
python3 -m py_compile samples/micro_bench/spike/cute_dsl/scripts/cutedsl_toolchain_smoke.py

PYTHONPATH=/home/titan/.codex/skills/cutlass-skill/repos/cutlass/python/CuTeDSL \
python3 samples/micro_bench/spike/cute_dsl/scripts/cutedsl_toolchain_smoke.py \
  --cutlass_repo=/home/titan/.codex/skills/cutlass-skill/repos/cutlass \
  --output_dir=/tmp/q35_cutedsl_r0b_toolchain_smoke_main_verify \
  --arch=sm_87 \
  --dry_run

git diff --check -- CMakeLists.txt samples/micro_bench/spike/cute_dsl
```

结果均 PASS。未启动 Orin、NCU、nsys 或 CUDA workload。
