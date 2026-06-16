# AUTO-20260608-112 M5 Feasibility Perf-Analyst

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## Ratio 证据

R0E formal：

- family A/B geomean：`152.031603/65.925507`
- status：`gate_fail`

M2 timing hygiene：

- family A/B：`13.589240/4.937622`
- repeat：`13.388290/4.723811`

M3 grouped dense：

- grouped_vs_nncl：`4.442753/4.092893`
- repeat：`4.412637/4.208391`
- grouped_vs_serial 有收益，但无法弥合 W4A16 NNCL 差距。

M4 controls：

- direct control：`0.999769/1.015588`
- dispatch wrapper-isolation run1：`1.001874/1.032655`
- dispatch wrapper-isolation run2：`0.999701/1.011785`

## 解释

唯一接近 NNCL 的路径都是 NNCL internal/control path。M2/M3 中真正独立于 NNCL MoeFC kernel 的 dense fp16 path 不达标，因此不能声明当前 CuTe/CUTLASS C++ spike 已达到 `<=1.20x` final target。

## 决策

`reject_or_hold` 当前 R0F/R1-probe formal promotion。

若继续，需要新 independent W4A16 grouped candidate，并把 same-run NNCL ratio gate 重新设为 family A/B geomean `<=1.20x`。
