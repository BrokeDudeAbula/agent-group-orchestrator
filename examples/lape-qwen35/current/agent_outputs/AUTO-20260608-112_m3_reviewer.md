# AUTO-20260608-112 M3 Reviewer

## 结论

M3 evidence 可审计，且应 fail-closed：不进入 NCU isolation，不进入 M4 grouped/batched formalization，不进入 M5 W4A16 feasibility promotion。

## 复核结果

通过项：

- `orin_1` Release/sm87 spike 构建成功，`build_rc=0`。
- M64 gate smoke 成功，`micro_gate_m64_rc=0`。
- 两轮 10 shape micro 均成功，`micro_all_rc=0`、`micro_all_repeat_rc=0`。
- 两轮均 rows=10、`precision_pass=true`、`timing_contaminated=false`。
- 所有行均 `valid_for_sop_a=false`、`valid_for_sop_c=false`、`tier_eligible=false`。
- family B `down_proj` 输入已修正为计时区外预构造的 `precomputed_silu_gate_mul_up_routed_prefix`，不是错误使用 hidden `[M,2048]`。
- CSV 明确 `single_projection_only`、`not_w4a16`、`not_fused_decode`。

阻断项：

- 两轮 family A/B grouped_vs_nncl geomean ratio 均明显 `>1.50x`：
  - 第一轮：A `4.442753x`，B `4.092893x`
  - 第二轮：A `4.412637x`，B `4.208391x`
- small `M64` 和 hot `M898` 仍明显慢于 NNCL。
- 结果只证明 grouped dense fp16 launch 相比 serial 有收益，不能证明 W4A16 fused MoE candidate 可行。

## Evidence 边界

这些数据可以说明：

- CUTLASS grouped dense fp16 candidate 可以运行，输出非零且与 serial/NNCL 同输入结果一致。
- grouped launch 数量从 `active_experts` 降到 1。
- grouped launch 减少了 serial per-expert launch overhead。

这些数据不能说明：

- candidate NCU isolation 通过。
- full routed grouped W4A16 MoE 可行。
- SOP-A/SOP-C PASS。
- tier eligible。
- production path 可改。

## Reviewer 判定

状态应写为：

`blocked / M3 grouped_dense_ratio_gt_1p50 / probe-only / not production`

后续若继续，需要新建更接近 NNCL 的 W4A16/fused decode 结构性任务，或转向 NNCL grouped targeted profile。不得把 M3 dense fp16 grouped probe 当作 formal candidate evidence。
