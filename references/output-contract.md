# Output Contract

Every worker output should include:

- task id
- worker name
- execution backend, for example `claude-code-cli` or `codex`
- sub-agent reference, if the backend provides one
- scope
- inputs read
- commands run, if any
- conclusion
- produced artifacts
- risks or blockers
- recommended next step

The main orchestrator final report should include:

- whether the user goal is complete
- workers selected and skipped
- sub-agent backends and references for dispatched workers
- files written
- key findings
- validation performed
- evidence spot checks performed by the main orchestrator
- remaining blockers or risks
- next step

Use concise evidence. Link files and reports rather than copying long logs.

The main orchestrator must not write a worker output for a non-main worker unless it is recording a sub-agent failure or blocked dispatch. Worker-scoped conclusions should come from the selected sub-agent output.
