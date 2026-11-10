# Decisions

## Summary

Three active decisions: research stays read-only until a gate, benchmark claims need comparable timing, and optimization directions live in `memory/ROADMAP.md`.

## Recent

| Decision ID | Date | Status | Decision | Rationale | Supersedes |
|---|---|---|---|---|---|
| DEC-20260616-ELLM-01 | 2026-06-16 | active | Treat competitor research as read-only until explicit benchmark or implementation gates are approved. | The workflow should not modify source or run remote jobs while gathering evidence. | |
| DEC-20260616-ELLM-02 | 2026-06-16 | active | Benchmark comparability must be established before speed or throughput claims are accepted. | Different repos may count tokenization, warmup, prefill, decode, streaming, and synchronization differently. | |
| DEC-20260616-ELLM-03 | 2026-06-16 | active | Put optimization directions in `memory/ROADMAP.md`. | Roadmap entries must survive context handoff and be reviewable after research completes. | |
