# AUTO-20260608-112 M5 Feasibility Qwen-Architect

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 决策

```text
reject_or_hold
```

当前 R0F/R1-probe 不应 promoted 为 formal candidate。

## 依据

- M2 timing hygiene 后 dense fp16 serial path 两轮 family A/B geomean `13.589240/4.937622` 与 `13.388290/4.723811`，不接近 NNCL。
- M3 grouped dense structural probe 证明 grouped launch 有收益，但 grouped-vs-NNCL 两轮仍为 `4.442753/4.092893` 与 `4.412637/4.208391`。
- M4 direct control 与 dispatch wrapper-isolation 接近 NNCL，但都复用 NNCL internal runner/template/header/kernel，不是 independent candidate。
- 当前没有可做 Candidate NCU Isolation 的 independent kernel。

## 下一步选项

1. 新建 `Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE`，实现真正 independent fused GPTQ W4A16 MoE grouped path，并重新走 SOP-A/B/C。
2. 转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`，围绕已有 NNCL grouped path 做 targeted profile 和 production 周边优化。

## 边界

本决策不是 SOP evidence，不是 tier，不进入 R1/R3/production。

固定：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
