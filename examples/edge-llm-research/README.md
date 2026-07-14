# Edge LLM Research Agent Group Demo

This demo shows how to use an agent group for a read-heavy competitor research workflow.

Scenario:

- The current repository is an edge-deployed LLM inference engine.
- The agent group should research `trt-edge-llm`, `vLLM`, and other relevant inference engines.
- The research must compare operator implementation strategies, inference acceleration features, e2e benchmark methodology, module-level benchmark methodology, and timing semantics.
- The output should produce optimization directions for the current repo and place them into a roadmap.

The complete user prompt is in:

```text
current/prompt.md
```

This demo intentionally uses placeholder findings. In a real repository, `oss-scout` should read upstream code, official docs, issues, benchmark scripts, and papers before turning any item into a factual claim.
