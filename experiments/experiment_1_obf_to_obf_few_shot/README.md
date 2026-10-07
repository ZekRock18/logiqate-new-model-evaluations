# Experiment 1 — Obfuscated-to-Obfuscated Few-Shot

## Method

Two solved obfuscated examples are shown before a new obfuscated target. Clean forms are never shown in the demonstrations.

## Research question

Tests whether exposure to the obfuscated input distribution alone improves robustness.

## Implementation in this run

Two fixed, solved obfuscated demonstrations per task; the same underlying demonstration IDs used by Experiment 2; demonstrations and tests are disjoint; evaluated on FOL, Blood Relation L1/L2, Number Series and Direction Sense.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **26/75 (34.67%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blood Relation | obfuscation_l1 | 5/15 | 33.33% | 53.33% | -20.00 pp | 0 |
| Blood Relation | obfuscation_l2 | 5/15 | 33.33% | 40.00% | -6.67 pp | 0 |
| Direction Sense | obfuscation | 5/15 | 33.33% | 26.67% | +6.67 pp | 0 |
| FOL | obfuscation | 10/15 | 66.67% | 33.33% | +33.33 pp | 0 |
| Number Series | obfuscation | 1/15 | 6.67% | 13.33% | -6.67 pp | 0 |

## Included files

- `02_obf_to_obf_few_shot.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../common`](../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
