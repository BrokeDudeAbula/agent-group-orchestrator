# Risks

## Summary

Four active research risks: unsupported competitor claims, inconsistent timing windows, server strategies copied onto edge, and license reuse.

## Recent

| Risk ID | Status | Owner | Trigger | Impact | Mitigation | Latest Update |
|---|---|---|---|---|---|---|
| RISK-ELLM-01 | active | oss-scout | Competitor claims are copied from docs or marketing without source or benchmark evidence. | Roadmap may optimize for non-transferable assumptions. | Require source links, hardware config, model config, and timing definition for each claim. | Demo marks competitor findings as placeholders. |
| RISK-ELLM-02 | active | perf-analyst | E2E metrics use inconsistent timing windows. | Current repo and competitor throughput or latency numbers become misleading. | Use the timing semantics checklist before comparing numbers. | Checklist added to perf-analyst output. |
| RISK-ELLM-03 | active | architect | Server-oriented strategies are moved to edge without checking memory, power, or thermal limits. | Optimization may regress deployability. | Add edge suitability and validation method to each roadmap item. | Roadmap includes edge-specific evidence requirements. |
| RISK-ELLM-04 | active | reviewer | External code or kernels are copied without license review. | License or maintenance risk. | Reuse ideas only after license review; do not copy code in research phase. | Reviewer output flags license risk. |
