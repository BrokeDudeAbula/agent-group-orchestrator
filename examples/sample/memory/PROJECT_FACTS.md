# Project Facts

## Repository Layout

- `service/` contains sample request handling code.
- `config/` contains sample runtime configuration.
- `reports/latency/` contains comparable latency summaries.

## Important Entrypoints

- API request routing starts at `service/router`.
- Runtime timeouts are configured under `config/runtime`.

## Validation Commands

- Read-only analysis does not require running the service.
- Any live validation should be treated as R4 if it uses remote or long-running infrastructure.

## Uncertain Facts

- Whether cache changes or timeout changes are the primary driver remains unconfirmed until a scoped patch and validation are approved.

