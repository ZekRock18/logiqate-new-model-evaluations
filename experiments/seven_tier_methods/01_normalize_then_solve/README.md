# Tier 1.1 — Normalize Then Solve

## Method

The model rewrites the input into a simpler logically equivalent form, checks that meaning was preserved and solves the normalized problem.

## Research question

Tests whether explicit normalization reduces failures caused by surface-form complexity.

## Implementation in this run

Applied to clean and obfuscated FOL and Blood Relation inputs, including both Blood Relation obfuscation levels.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **41/75 (54.67%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | base | 10/15 | 66.67% | — | — | 0 |
| Blood Relation | obfuscation_l1 | 7/15 | 46.67% | 53.33% | -6.67 pp | 0 |
| Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 40.00% | +0.00 pp | 0 |
| FOL | base | 12/15 | 80.00% | — | — | 0 |
| FOL | obfuscation | 6/15 | 40.00% | 33.33% | +6.67 pp | 0 |

## Included files

- `05_normalize_then_solve.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../../common`](../../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
