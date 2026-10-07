# Tier 1.5 — Re-reading / System 2 Attention

## Method

The model reads twice, isolates only logically relevant facts and solves from the reduced representation.

## Research question

Tests whether removing distracting presentation helps attention focus on the underlying logic.

## Implementation in this run

Applied to FOL base/obfuscation and Blood Relation base/L2, the initially specified complex condition.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **37/60 (61.67%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | base | 11/15 | 73.33% | — | — | 0 |
| Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 40.00% | +0.00 pp | 0 |
| FOL | base | 13/15 | 86.67% | — | — | 0 |
| FOL | obfuscation | 7/15 | 46.67% | 33.33% | +13.33 pp | 0 |

## Included files

- `09_rereading_s2a.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../../common`](../../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
