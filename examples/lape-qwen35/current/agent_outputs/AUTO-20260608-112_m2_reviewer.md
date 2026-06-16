# AUTO-20260608-112 M2 Reviewer

## 结论

M2 evidence 可审计，且结论应 fail-closed：不进入 M3 NCU，不进入 M4 grouped launch，不声明 SOP-C/tier/R1。

## 复核结果

通过项：

- 两轮 Orin micro 都完成，程序 `micro_rc=0`。
- CSV 已回传，均为 10 shape。
- 两轮均 `precision_pass=true`、`nan_count=0`、`inf_count=0`、`nonzero>0`。
- paired CSV/log 均有：
  - `timing_contaminated=false`
  - `op_class=TensorOp`
  - `arch=Sm80/Sm87-compatible`
  - `candidate_path=cutlass_tensorop_dense_fp16`
  - `baseline_source=nncl_grouped_moe_group_gemm_paired_same_run`
  - `valid_for_sop_a=false`
  - `valid_for_sop_c=false`
  - `tier_eligible=false`
- 第一轮 scp 失败已解释为容器 `/tmp` 与主机 `/tmp` 路径差异；CSV 后续通过 `docker exec cat` 成功回传，不影响 micro evidence。

阻断项：

- ratio 连续两轮明显 `>1.50x`：
  - family A geomean：`13.589240x` / `13.388290x`
  - family B geomean：`4.937622x` / `4.723811x`
- hot `M898` 与 small `M64` 都存在明显灾难性退化。

## Evidence 边界

这些数据只能说明：

- M2 paired timed loop 的主要 torch 分配/contiguous/host roundtrip 污染已清理。
- 当前 serial per-expert dense fp16 TensorOp candidate 仍远慢于 same-run NNCL grouped W4A16 baseline。

这些数据不能说明：

- candidate NCU isolation 通过。
- grouped/batched launch 有收益。
- W4A16 fused decode+matmul 可行。
- SOP-C PASS。
- tier eligible。
- production path 可改。

## Reviewer 判定

状态应写为：

`blocked / M2 stop_condition_ratio_gt_1p50 / probe-only / not production`

若继续推进，必须先提出新设计或新任务；不得把当前 M2 evidence 当作进入 formal candidate 的依据。
