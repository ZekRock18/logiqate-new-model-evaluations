# Reproducibility and public logs

The studies have different execution protocols. Use the [model index](../experiments/README.md) to choose the run first; do not treat one model's log or sample manifest as another's.

## DeepSeek 15-question pilot

The [sanitized execution ledger](../experiments/deepseek_v4_1_flash_15/provenance/run-ledger.csv) records run-metadata events in order, without private timestamps or opaque request identifiers. The [execution summary](../experiments/deepseek_v4_1_flash_15/provenance/execution-summary.md), [validation record](../experiments/deepseek_v4_1_flash_15/provenance/validation.md), and [historical publication-audit snapshot](../experiments/deepseek_v4_1_flash_15/provenance/publication_audit_snapshot.json) document completion and release checks. That snapshot's file count predates the model-based folder reorganization. The [shared protocol package](../experiments/deepseek_v4_1_flash_15/shared/) holds its sample manifest, prompt templates, notebooks, code, and aggregate tables.

## GPT 50-question studies

Each GPT study has an [assigned](../experiments/gpt_6_sol_medium_50/assigned/) package and a [Tier-1](../experiments/gpt_6_sol_medium_50/tier1/) package. Both contain public prompt CSVs, response CSVs, append-only answer journals under `Result/`, `run_provenance.json`, executed notebooks, aggregate analysis, tests, and `PUBLICATION_AUDIT.json`. The [GPT-5.6](../experiments/gpt_5_6_sol_high_50/) and [GPT-6](../experiments/gpt_6_sol_medium_50/) model guides explain their model-specific settings and limitations.

The GPT Tier-1 packages retain three independent self-consistency paths and both CoVe stages. They use each model run's own fresh zero-shot control. Gold answers and private row-level scored evidence are excluded from Git.

## Continuing or checking the work

The [validation workflow](../.github/workflows/validation.yml) runs public package tests and audits. From a GPT package directory, `python run_queue.py status --strict` checks response completeness; `python src/publication_audit.py` checks the public release. The [project-state note](../PROJECT_MEMORY.md) lists all canonical paths and the combined local test command.

Keep historical logs as evidence. If a new run is added, give it its own model folder, provenance, and matched control rather than appending responses to an existing run.
