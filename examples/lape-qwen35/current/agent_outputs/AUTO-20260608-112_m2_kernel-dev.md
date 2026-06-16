# AUTO-20260608-112 M2 Kernel Dev

## 结论

M2 Timing hygiene 的 spike-local 代码修改已完成第一版，并已在 `orin_1` Release/sm87 构建通过。修改范围仍限于 `samples/micro_bench/spike/cute_dsl/` 与必要 CMake 接入，不修改 production Qwen3.5 推理路径。

本阶段只清理 `routed_grouped_micro_nncl_paired` 的 candidate timed loop；旧 `routed_grouped_micro` / reference diagnostic path 仍保留原污染标记，不作为 M2 paired timing evidence。

## 代码修改点

- `spike_common.h`
  - 新增 `kRoutedM2CleanTimingNotes`：
    - `m2_candidate_and_nncl_timed_loop_preallocated_no_torch_empty_no_contiguous_no_host_device_roundtrip_no_inner_sync`
    - `serial_per_expert_launch_remains`
    - `grouped_probe_not_done`
- `cutlass_routed_grouped_micro.cu`
  - 抽出可复用 TensorOp GEMM launch helper，candidate path 固定为 `cutlass_tensorop_dense_fp16`。
  - 新增 `CandidateProjectionPlan` / `CandidateProjectionSegment`，在 timed loop 前预分配 per-expert input view、output view、weight handle 和 TensorOp variant。
  - `TimeCandidateProjection` / family B `TimeCandidate` 的 timed loop 不再调用旧 `ComputeCandidate*`，只循环 launch 已准备好的 CUTLASS GEMM plan。
  - 新增 `SiluMulHalfKernel`，family B gate/up activation 不再在 timed loop 内走 torch expression。
  - `WriteNnclPairedRow` 固定输出：
    - `timing_contaminated=false`
    - `timing_contamination_notes=<kRoutedM2CleanTimingNotes>`
    - `op_class=TensorOp`
    - `arch=Sm80/Sm87-compatible`
    - `candidate_path=cutlass_tensorop_dense_fp16`
    - `valid_for_sop_a=false`
    - `valid_for_sop_c=false`
    - `tier_eligible=false`

## Timed Loop 边界

已移出 paired candidate timed loop：

- `torch::empty`
- `.contiguous()`
- layout copy / `copy_`
- host/device roundtrip
- loop 内 `cudaStreamSynchronize`
- loop 内 `ComputeCandidate*` helper

仍存在但不计入 timed section或属于本阶段未覆盖：

- warmup 前后同步与 CUDA event 同步，用于计时边界。
- per-expert serial CUTLASS launch 仍保留，这是 M4 grouped/batched probe 的对象。
- NNCL baseline 内部实现不展开改动，只作为 same-run baseline。
- 旧 R0d diagnostic path 仍标记 `timing_contaminated=true`。

## 构建证据

- target：`orin_1`
- container：`liyang_lape`
- repo：`/workspace/liyang/workspace/lape`
- build dir：`/workspace/liyang/workspace/lape/build_cutedsl_r0f_align1`
- binary：`/workspace/liyang/workspace/lape/build_cutedsl_r0f_align1/samples/micro_bench/spike/cute_dsl/qwen3_5_cute_dsl_spike`
- build log：`analysis/Qwen35_cutedsl_r0f_r1_probe_orin_1_20260608_154038/build_m2_timing_hygiene_final.log`
- result：`build_rc=0`

## 边界

M2 代码只证明 paired timing loop 的 hygiene 改进。它不证明 grouped launch、W4A16 fused decode、SOP-C PASS 或 tier eligibility。
