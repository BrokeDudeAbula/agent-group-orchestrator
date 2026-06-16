# AUTO-20260608-112 M4-Control Reviewer

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## Findings

无 P0/P1 evidence blocker。

P2：`routed_grouped_moefc_direct_probe` 是 NNCL internal control，不是独立 candidate。
后续报告必须持续使用 `control_probe_only=true` 和 `independent_candidate=false`，不得将
steady-state ratio 解释为 CuTe/CUTLASS 自研 candidate 达标。

P2：`r0f_m4_moefc_direct_all.csv` 来自旧 timed-loop launch check 实现，存在 host-side
检查污染。已在 `report.md` 标为排除数据，不应进入 geomean 结论。

## Probe-only 边界

已核查 balanced CSV/log：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`
- `precision_pass=true`
- `nan_count_vs_nncl=0`
- `inf_count_vs_nncl=0`
- `nonzero_vs_nncl>0`

未修改 production Qwen3.5 推理路径。

## 判定

接受 M4-control 作为结构性 evidence：

- 证明 direct internal W4A16 MoeFC runner 与 public NNCL steady-state 基本同量级。
- 不证明独立 candidate 通过。
- 不允许 promoted to formal task，除非另起真正 independent W4A16 MoeFC candidate 并重新走 SOP-A/B/C。
