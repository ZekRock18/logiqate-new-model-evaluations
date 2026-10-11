# Public Experiment Logs

This directory preserves the public audit trail for the prompt-mitigation run.

- [`execution-summary.md`](execution-summary.md) records the final inference totals and retained failures.
- [`run-ledger.csv`](run-ledger.csv) records all 48 run-metadata events in execution order, with private timestamps and run identifiers removed.
- [`validation.md`](validation.md) records notebook, test, publication-audit and continuous-integration checks.
- [`publication_audit_snapshot.json`](publication_audit_snapshot.json) preserves the original release-time scan; its file count predates this model-based folder reorganization.

Raw provider transcripts are intentionally not published because they contain
row-level model outputs and private scoring material. Credentials are never
part of the log archive.
