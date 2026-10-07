# Tier 1.4 — Chain of Thought

## Method

The model decodes obfuscation, reasons step by step, performs a sanity check and emits a strict final answer.

## Research question

Tests whether explicit intermediate reasoning improves robustness across task families.

## Implementation in this run

Applied to base and all obfuscated forms for all four tasks at temperature 0.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **74/135 (54.81%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | base | 10/15 | 66.67% | — | — | 0 |
| Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 53.33% | +6.67 pp | 0 |
| Blood Relation | obfuscation_l2 | 4/15 | 26.67% | 40.00% | -13.33 pp | 0 |
| Direction Sense | base | 7/15 | 46.67% | — | — | 0 |
| Direction Sense | obfuscation | 7/15 | 46.67% | 26.67% | +20.00 pp | 0 |
| FOL | base | 12/15 | 80.00% | — | — | 0 |
| FOL | obfuscation | 9/15 | 60.00% | 33.33% | +26.67 pp | 0 |
| Number Series | base | 12/15 | 80.00% | — | — | 1 |
| Number Series | obfuscation | 4/15 | 26.67% | 13.33% | +13.33 pp | 2 |

## Included files

- `08_chain_of_thought.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../../common`](../../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
