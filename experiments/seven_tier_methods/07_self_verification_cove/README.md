# Tier 1.7 — Self-Verification / CoVe

## Method

An initial solution is followed by an independent verification pass that can retain or revise the answer.

## Research question

Tests whether a separate audit catches mistakes made by the initial solution.

## Implementation in this run

Applied to base and all obfuscated forms for every task; initial answer, verification response, final answer and answer-change flag were recorded.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **73/135 (54.07%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | base | 11/15 | 73.33% | — | — | 0 |
| Blood Relation | obfuscation_l1 | 7/15 | 46.67% | 53.33% | -6.67 pp | 0 |
| Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 40.00% | +0.00 pp | 0 |
| Direction Sense | base | 8/15 | 53.33% | — | — | 0 |
| Direction Sense | obfuscation | 8/15 | 53.33% | 26.67% | +26.67 pp | 0 |
| FOL | base | 13/15 | 86.67% | — | — | 0 |
| FOL | obfuscation | 7/15 | 46.67% | 33.33% | +13.33 pp | 0 |
| Number Series | base | 12/15 | 80.00% | — | — | 0 |
| Number Series | obfuscation | 1/15 | 6.67% | 13.33% | -6.67 pp | 0 |

CoVe changed 18/135 answers, corrected 1 initially wrong answer and changed 11 initially correct answers to incorrect.

## Included files

- `11_self_verification_cove.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../../common`](../../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
