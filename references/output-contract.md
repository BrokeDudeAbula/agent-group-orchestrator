# Output Contract

Every worker output stays within 120 lines and 6000 characters. Link files and reports instead of copying logs. Strict and non-strict validation both reject outputs over that cap.

Include these headings:

```text
## Task ID
## Worker Name
## Execution Backend
## Sub-Agent Reference
## Scope
## Inputs Read
## Commands Run
## Conclusion
## Artifacts
## Risks or Blockers
## Recommended Next Step
```

A sub-agent prompt does not contain this file or the upstream outputs. It contains a short summary and the output path. The worker reads what it needs.

The main orchestrator report names goal status, workers used, workers skipped and why, sub-agent references, files written, blockers, and the next step. It does not paste worker logs.

Cheap read-only R0/R1 lookups done in the main session are not written up as another worker's output.
