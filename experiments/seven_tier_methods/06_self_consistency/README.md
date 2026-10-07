# Tier 1.6 — Self-Consistency

## Method

Three independent reasoning paths are generated and their normalized answers are majority-voted.

## Research question

Tests whether sampling multiple reasoning paths reduces single-path reasoning errors.

## Implementation in this run

Applied to base and all obfuscated forms for every task; three paths at temperature 0.7; three different normalized answers produce NO_CONSENSUS and count as wrong.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **84/135 (62.22%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | base | 10/15 | 66.67% | — | — | 2 |
| Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 53.33% | +6.67 pp | 3 |
| Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 40.00% | +0.00 pp | 5 |
| Direction Sense | base | 11/15 | 73.33% | — | — | 0 |
| Direction Sense | obfuscation | 11/15 | 73.33% | 26.67% | +46.67 pp | 1 |
| FOL | base | 13/15 | 86.67% | — | — | 0 |
| FOL | obfuscation | 8/15 | 53.33% | 33.33% | +20.00 pp | 0 |
| Number Series | base | 12/15 | 80.00% | — | — | 2 |
| Number Series | obfuscation | 4/15 | 26.67% | 13.33% | +13.33 pp | 7 |

Self-consistency reached a majority or unanimous vote on 115/135 items (85.19%). The remaining 20 were recorded as `NO_CONSENSUS`.

## Included files

- `10_self_consistency.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../../common`](../../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
