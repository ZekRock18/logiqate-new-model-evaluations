# Experiment 3 — Analogical Prompting

## Method

The model constructs or recalls a structurally similar problem, solves the analogy and transfers the structure to the target.

## Research question

Tests whether a self-generated analogy can replace fixed labelled demonstrations.

## Implementation in this run

No labelled demonstrations; concise analogy and transferable structure requested before a machine-parseable final answer; evaluated on every obfuscated task form.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **30/75 (40.00%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 53.33% | +6.67 pp | 0 |
| Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 40.00% | +0.00 pp | 0 |
| Direction Sense | obfuscation | 6/15 | 40.00% | 26.67% | +13.33 pp | 0 |
| FOL | obfuscation | 6/15 | 40.00% | 33.33% | +6.67 pp | 0 |
| Number Series | obfuscation | 3/15 | 20.00% | 13.33% | +6.67 pp | 0 |

## Included files

- `04_analogical_prompting.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../common`](../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
