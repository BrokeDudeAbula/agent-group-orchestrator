# AUTO-20260608-112 M3 Perf Analyst

## 结论

M3 grouped dense probe 证明 grouped launch 能显著减少 serial per-expert launch 成本，但没有接近 same-run NNCL baseline。两轮 10 shape 的 family A/B geomean `grouped_vs_nncl_ratio` 均明显 `>1.50x`，因此不进入 NCU，不进入 M4/M5。

目标 gate 仍是 family A/B geomean ratio 均 `<=1.20x`，且 hot `M898`、small `M64` 不能灾难性退化。M3 未达标。

## 第一轮 Ratio

| family | M | projection | grouped ms | serial ms | NNCL ms | grouped/NNCL | grouped/serial |
|---|---:|---|---:|---:|---:|---:|---:|
| A | 64 | gate_proj | 1.089158 | 2.590520 | 0.219068 | 4.971793 | 0.420440 |
| A | 128 | gate_proj | 1.031219 | 3.389644 | 0.209450 | 4.923454 | 0.304226 |
| A | 256 | gate_proj | 1.266913 | 4.867807 | 0.258886 | 4.893716 | 0.260264 |
| A | 512 | gate_proj | 1.252800 | 6.116554 | 0.329798 | 3.798692 | 0.204821 |
| A | 898 | gate_proj | 1.460171 | 7.362432 | 0.383883 | 3.803689 | 0.198327 |
| B | 64 | down_proj | 0.827660 | 0.972682 | 0.202909 | 4.078963 | 0.850905 |
| B | 128 | down_proj | 1.241348 | 1.393894 | 0.227313 | 5.460971 | 0.890561 |
| B | 256 | down_proj | 1.419160 | 1.879301 | 0.364115 | 3.897565 | 0.755153 |
| B | 512 | down_proj | 1.711011 | 2.295283 | 0.439585 | 3.892329 | 0.745446 |
| B | 898 | down_proj | 1.724509 | 2.744843 | 0.507383 | 3.398831 | 0.628273 |

Summary：

- family A grouped/NNCL geomean：`4.442753x`
- family B grouped/NNCL geomean：`4.092893x`
- family A serial/NNCL geomean：`16.650903x`
- family B serial/NNCL geomean：`5.326005x`
- family A grouped/serial geomean：`0.266817x`
- family B grouped/serial geomean：`0.768473x`

## 第二轮 Ratio

Summary：

- family A grouped/NNCL geomean：`4.412637x`
- family B grouped/NNCL geomean：`4.208391x`
- family A serial/NNCL geomean：`16.657091x`
- family B serial/NNCL geomean：`5.585010x`
- family A grouped/serial geomean：`0.264910x`
- family B grouped/serial geomean：`0.753515x`

small/hot：

- M64：A `5.460091x`，B `3.447001x`
- M898：A `3.798590x`，B `3.878818x`

## 归因

M3 将 launch overhead 从主要疑点中进一步收窄：

- family A grouped dense 相对 serial 提升明显，geomean 约 `0.26x`。
- family B grouped dense 相对 serial 也有收益，但只有约 `0.75x`。
- 即便如此，grouped dense fp16 仍比 NNCL grouped W4A16 慢约 `4x`。

因此当前差距不只是 serial launch overhead，还包括：

- fp16 dense B 矩阵读带宽/容量远高于 W4A16 packed weight；
- 未 fused GPTQ W4A16 decode+matmul；
- grouped dense probe 使用 CUTLASS generic grouped TensorOp，不是 MoE small-M/W4A16 专用 kernel；
- family B down_proj 的输入已正确预构造，但其计时只覆盖 single projection，不包含完整 MoE fused pipeline。

## 判定

M3 structural grouped launch probe 数值通过，但性能 gate 失败：

- 未达到 `<=1.20x`。
- 连续两轮明显 `>1.50x`。
- small `M64` 与 hot `M898` 仍明显退化。

推荐状态：

`blocked / M3 grouped_dense_ratio_gt_1p50 / probe-only / not production`
