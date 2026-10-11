# Project state and handoff

Last reviewed: 2026-10-11. This is a public, Git-tracked handoff note for future contributors; it is **not** an answer key or a ChatGPT personal-memory entry. For a first-time reader, start with the [repository README](README.md) and [model experiment index](experiments/README.md).

## Canonical layout

- `claude_fable_5.1_high/` is the separate Claude evaluation package.
- `experiments/deepseek_v4_1_flash_15/` holds the 15-question-per-task pilot: `assigned/`, `tier1/`, `shared/`, and `provenance/`.
- `experiments/gpt_5_6_sol_high_50/` and `experiments/gpt_6_sol_medium_50/` each have `assigned/` and `tier1/` packages. Their method subfolders are reading guides; the canonical CSVs, notebooks, code, journals, and audits remain in the runnable package one level up, without duplicate data copies.
- `experiments/llama/`, `phi/`, `qwen/`, and `qwen_obfuscated_250/` hold only the methods actually supplied for those runs. Do not infer results for absent methods.
- `wiki/` is the version-controlled documentation source in this repository. The [wiki home](wiki/Home.md) links to study background and logs.

## Completed work and key counts

| Run | Public scope | Result location |
| --- | --- | --- |
| DeepSeek pilot | 15 questions per task; three assigned prompts and seven Tier-1 methods | [aggregate report](experiments/deepseek_v4_1_flash_15/shared/results/REPORT.md) |
| GPT-5.6 Sol high | 1,200 assigned/control responses plus 3,600 Tier-1 responses; 3,450 scored units | [assigned report](experiments/gpt_5_6_sol_high_50/assigned/Analysis/REPORT.md), [Tier-1 report](experiments/gpt_5_6_sol_high_50/tier1/Analysis/REPORT.md) |
| GPT-6 Sol medium | 1,200 assigned/control responses plus 3,600 Tier-1 responses; 3,450 scored units | [assigned report](experiments/gpt_6_sol_medium_50/assigned/Analysis/REPORT.md), [Tier-1 report](experiments/gpt_6_sol_medium_50/tier1/Analysis/REPORT.md) |
| Llama, Phi, Qwen | Selected methods only, not complete ten-method studies | [model index](experiments/README.md) |

For the GPT-6 run's 250 common obfuscated targets, zero-shot control was 160/250, obfuscated few-shot 161/250, paired few-shot 154/250, and analogical prompting 121/250. The +1-question few-shot difference is descriptive, not a robust improvement claim. Tier-1 methods have different task matrices; use matched cell-level tables, not an overall ranking across unequal denominators.

## Where the logs and validation live

- DeepSeek's sanitized event ledger and historical release audit are in [provenance](experiments/deepseek_v4_1_flash_15/provenance/). The audit's file count predates the folder reorganization.
- Each GPT `assigned/` and `tier1/` package contains `run_provenance.json`, `Result/_answer_journal_*.jsonl`, `PUBLICATION_AUDIT.json`, tests, and executed notebooks. Tier-1 self-consistency keeps three path files; CoVe keeps initial and verifier files.
- The [validation workflow](.github/workflows/validation.yml) runs the package tests and GPT publication audits. The four GPT audits were passing when this note was updated.

## Reproducing checks

From the repository root, run `python -m pytest --import-mode=importlib experiments/deepseek_v4_1_flash_15/shared/tests experiments/gpt_5_6_sol_high_50/assigned/tests experiments/gpt_5_6_sol_high_50/tier1/tests experiments/gpt_6_sol_medium_50/assigned/tests experiments/gpt_6_sol_medium_50/tier1/tests -q`. The separate audit scripts are `src/publication_audit.py` inside each GPT package. Use `run_queue.py status --strict` from a GPT package directory to check response completeness.

## Boundaries and cautions

Do not commit `manual_eval/private_do_not_upload/`, credentials, gold answers, or private row-level scored evidence. Public response journals are intentionally included. GPT runs used Codex model aliases and do not expose dated model snapshots, sampling settings, provider request IDs, or token telemetry. The GPT-6 run also has CLI batch-context and limited self-consistency path-1 carryover caveats described in its package READMEs. The inherited Direction Sense normalizer can inflate some scores. No scoring data was changed during the model-based folder reorganization; the only removed tracked file was a stale Qwen spreadsheet lock, recoverable from Git history.
