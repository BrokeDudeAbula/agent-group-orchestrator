# AUTO-20260608-112 M4-Control Warm Hardened Reviewer

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## Findings

无 P0/P1 evidence blocker。

已处理上一轮 P2：

- 旧 warm CSV 只有 notes/timing notes 写 `control_probe_only` 与 `not_independent_candidate`。
- 新 hardened CSV 已提供硬字段 `control_probe_only=true`、`independent_candidate=false`。
- 新 hardened row log 已逐行打印 `independent_candidate=false`。

## Probe-only 边界

核查范围：

- `r0f_m4_moefc_direct_warm_hardened_smoke.csv`
- `r0f_m4_moefc_direct_warm_hardened_all.csv`
- `r0f_m4_moefc_direct_warm_hardened_all_repeat.csv`
- `smoke_m64_gate_hardened.log`
- `run_warm_hardened_all.log`
- `run_warm_hardened_all_repeat.log`

21 条 CSV 数据行均满足：

- `precision_pass=true`
- `control_probe_only=true`
- `independent_candidate=false`
- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

未修改 production Qwen3.5 推理路径。

## 判定

接受 hardened warm-state control evidence。

该证据仍只能说明 NNCL internal `MoeGroupGemmRunner` 与 public NNCL baseline 的
warm-state timing 对齐，不能作为 independent CuTe/CUTLASS candidate、SOP-A、
SOP-C、tier 或 production evidence。
