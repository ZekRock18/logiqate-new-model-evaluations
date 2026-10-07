# Tier 1.2 — Structured Decomposition

## Method

The model extracts atomic kinship links or movements, records intermediate state and composes the steps in order.

## Research question

Tests whether an explicit intermediate representation makes multi-step reasoning more robust.

## Implementation in this run

Applied to clean and obfuscated Blood Relation and Direction Sense inputs; kinship uses directed relations, while navigation tracks coordinates and facing separately.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **41/75 (54.67%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | base | 10/15 | 66.67% | — | — | 0 |
| Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 53.33% | +6.67 pp | 0 |
| Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 40.00% | +0.00 pp | 0 |
| Direction Sense | base | 8/15 | 53.33% | — | — | 0 |
| Direction Sense | obfuscation | 8/15 | 53.33% | 26.67% | +26.67 pp | 0 |

## Included files

- `06_structured_decomposition.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../../common`](../../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
