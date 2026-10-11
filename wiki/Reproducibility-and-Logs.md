# Reproducibility and Logs

The public package preserves the deterministic sample manifest, frozen prompt
templates, executed notebooks, implementation source, tests, aggregate outputs
and a sanitized ledger of every run-metadata event.

- [Execution summary](../experiments/deepseek_v4_1_flash_15/provenance/execution-summary.md)
- [Complete public run ledger](../experiments/deepseek_v4_1_flash_15/provenance/run-ledger.csv)
- [Validation record](../experiments/deepseek_v4_1_flash_15/provenance/validation.md)
- [Publication audit](../experiments/PUBLICATION_AUDIT.json)
- [Shared implementation and tests](../experiments/deepseek_v4_1_flash_15/shared/README.md)

The ledger omits private timestamps and opaque run identifiers but preserves
event order, condition, prompt version, worker count, limits, planned/pending
units, resume counts and new status totals. Raw provider transcripts remain
private because they expose row-level outputs and scoring material.
