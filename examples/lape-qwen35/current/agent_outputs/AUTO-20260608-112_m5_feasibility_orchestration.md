# AUTO-20260608-112 M5 Feasibility Orchestration

任务：`Q35-MOE-CUTEDSL-R0F-R1-PROBE`

## 本轮目标

在 M1-M4 evidence 基础上完成 W4A16 feasibility decision，避免把 NNCL control path promoted 为 independent CuTe/CUTLASS candidate。

## 结果

决策：

```text
reject_or_hold
```

Evidence：

- `analysis/Qwen35_cutedsl_r0f_r1_probe_m5_feasibility_20260608_191226/report.md`

关键结论：

- M2/M3 真正独立于 NNCL MoeFC kernel 的 dense fp16 serial/grouped paths 不达标。
- M4 direct/dispatch 接近 NNCL，但都是 NNCL internal/control path。
- 当前没有 independent candidate kernel，不启动 Candidate NCU Isolation。
- 当前 R0F/R1-probe 不进入 formal，不进入 tier，不进入 production。

## 后续路线

二选一：

1. 新建 `Q35-MOE-CUTEDSL-R0G-INDEPENDENT-W4A16-FORMAL-CANDIDATE`，实现 independent fused GPTQ W4A16 grouped path，并重新走 SOP-A/B/C。
2. 转向 `Q35-MOE-NNCL-GROUPED-TARGETED-R0`，围绕现有 NNCL grouped path 做 targeted profile 和 production 周边优化。

## 状态

```text
done / reject_or_hold / probe-only / not production
```

注意：这是当前 R0F/R1-probe 的任务状态，不代表 `/goal` objective 已完成；目标中的“优化到接近 NNCL baseline”尚未由 independent candidate 实现。
