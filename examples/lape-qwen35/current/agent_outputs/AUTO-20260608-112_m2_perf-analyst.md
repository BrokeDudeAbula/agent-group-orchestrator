# AUTO-20260608-112 M2 Perf Analyst

## 结论

M2 Timing hygiene 的字段与数值 sanity 通过，但性能 gate 明确失败。same-run NNCL paired ratio 连续两轮明显 `>1.50x`，因此按停止条件不进入 M3 NCU isolation。

目标 gate 是 family A/B geomean ratio 均 `<=1.20x`。M2 两轮结果：

- 第一轮：family A `13.589240x`，family B `4.937622x`
- 第二轮：family A `13.388290x`，family B `4.723811x`

这说明清理 timed loop 后，当前 serial per-expert dense fp16 CUTLASS candidate 仍远慢于 same-run NNCL grouped W4A16 baseline。主要可见瓶颈不是 M2 原先清理的 torch allocation/contiguous/host roundtrip，而是结构性差异：

- candidate 仍是 per-expert serial dense fp16 launch；
- NNCL baseline 是 grouped W4A16 `MoeGroupGemm`；
- candidate 仍未做 grouped/batched launch；
- candidate 仍未 fused GPTQ W4A16 decode+matmul。

## 第一轮 Ratio

| family | M | candidate ms | NNCL ms | ratio |
|---|---:|---:|---:|---:|
| A | 64 | 2.774824 | 0.482290 | 5.753436 |
| A | 128 | 3.829242 | 0.301618 | 12.695670 |
| A | 256 | 5.258278 | 0.298097 | 17.639507 |
| A | 512 | 6.188237 | 0.331575 | 18.663155 |
| A | 898 | 7.395670 | 0.383757 | 19.271764 |
| B | 64 | 1.104406 | 0.164189 | 6.726412 |
| B | 128 | 1.751135 | 0.311092 | 5.628985 |
| B | 256 | 2.183487 | 0.531302 | 4.109687 |
| B | 512 | 2.772971 | 0.668250 | 4.149600 |
| B | 898 | 3.717246 | 0.817826 | 4.545278 |

Summary：

- family A geomean：`13.589240x`
- family A hot M898：`19.271764x`
- family A small M64：`5.753436x`
- family B geomean：`4.937622x`
- family B hot M898：`4.545278x`
- family B small M64：`6.726412x`
- all geomean：`8.191369x`

## 第二轮 Ratio

| family | M | candidate ms | NNCL ms | ratio |
|---|---:|---:|---:|---:|
| A | 64 | 2.791951 | 0.481947 | 5.793069 |
| A | 128 | 3.812255 | 0.301146 | 12.659147 |
| A | 256 | 5.027813 | 0.305848 | 16.438945 |
| A | 512 | 6.179174 | 0.334084 | 18.495878 |
| A | 898 | 7.353755 | 0.381194 | 19.291392 |
| B | 64 | 1.163154 | 0.162369 | 7.163632 |
| B | 128 | 1.757232 | 0.313454 | 5.606027 |
| B | 256 | 2.221709 | 0.651662 | 3.409297 |
| B | 512 | 2.829963 | 0.672245 | 4.209720 |
| B | 898 | 3.330187 | 0.816042 | 4.080901 |

Summary：

- family A geomean：`13.388290x`
- family A hot M898：`19.291392x`
- family A small M64：`5.793069x`
- family B geomean：`4.723811x`
- family B hot M898：`4.080901x`
- family B small M64：`7.163632x`
- all geomean：`7.952594x`

## Field Checks

两轮 CSV 均满足：

- `rows=10`
- `missing_columns=[]`
- `precision_pass=true`
- `nan_count=0`
- `inf_count=0`
- `nonzero>0`
- `timing_contaminated=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

## 判据

M2 hygiene 本身可记录为 pass，但 R0F/R1-probe 的性能推进 gate fail：

- 未达到 `<=1.20x`。
- 连续两轮明显 `>1.50x`。
- small `M64` 与 hot `M898` 都出现灾难性退化。

推荐状态：`blocked / M2 stop_condition_ratio_gt_1p50 / probe-only`。除非新建更强结构性设计，否则当前 serial dense fp16 candidate 不应继续进入 M3/M4。
