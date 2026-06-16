# AUTO-20260608-112 M1 Reviewer

## P0 Findings

无。

M1 dense fp16 `shape_bench` 未被升级为 SOP-C、tier 或 W4A16 grouped PASS。证据行均显式写出：

- `valid_for_sop_a=false`
- `valid_for_sop_c=false`
- `tier_eligible=false`

默认 binary 对 `r0e_sop_a_precision` 返回：

- `rc=1`
- `invalid --mode=r0e_sop_a_precision`

## P1 Findings

无。

`shape_bench` 的 `status=pass` 只表示 CUTLASS TensorOp dense fp16 形状 sanity 通过，不是 formal PASS。CSV 同时标明：

- `mode=shape_bench`
- `candidate_path=cutlass_tensorop_dense_fp16`
- `quant_method=fp16_dense`
- `weight_source=synthetic_fp16_dense`
- `notes=diagnostic_only;...;not_w4a16;not_routed_grouped_moe`

## P2 Findings

存在轻微口径风险：CSV 字段 `baseline_status=pass` 和 log 中 `status=pass` 若被粗糙脚本单独抓取，可能被误读。

当前防护充足：

- CSV/log 有 probe-only 三项 false。
- notes 含 `diagnostic_only`、`not_w4a16`、`not_routed_grouped_moe`。
- `main.cc` 默认不接受 `r0e_sop_*`。
- `CMakeLists.txt` 默认 `LAPE_CUTE_DSL_ENABLE_R0E_FORMAL_MODES=OFF`。

## 结论

M1 Tensor Core sanity 可进入 orchestration summary。后续只能进入 M2 timing hygiene，不能进入 formal/tier，也不能表述为 SOP-C、tier eligible 或 W4A16 grouped PASS。
