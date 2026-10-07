# Tier 1.3 — Explicit Task Instructions

## Method

The prompt names the relevant obfuscation mechanism and gives task-specific decoding instructions.

## Research question

Tests whether directly teaching the transformation rules improves decoding and downstream reasoning.

## Implementation in this run

Number Series instructions cover planet digits, lowercase-planet ASCII sums and single-digit MD5 hashes. Direction Sense instructions cover clock directions, cancelled rotations, opposite movements and facing changes.

The model was `deepseek-ai/DeepSeek-V4.1-Flash`, prompt version `v2`, with 15 fixed test IDs per task. Single-path calls used temperature 0 unless noted above. All final answers were scored by task-specific exact-match normalization, and failures remained in the denominator.

## Results

This condition scored **35/60 (58.33%)** across its configured cells. Totals across methods are not always directly comparable because the Tier 1 task mappings differ.

| Task | Variant | Correct | Accuracy | Zero-shot control | Change | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Direction Sense | base | 8/15 | 53.33% | — | — | 0 |
| Direction Sense | obfuscation | 9/15 | 60.00% | 26.67% | +33.33 pp | 0 |
| Number Series | base | 13/15 | 86.67% | — | — | 0 |
| Number Series | obfuscation | 5/15 | 33.33% | 13.33% | +20.00 pp | 3 |

## Included files

- `07_explicit_task_instructions.ipynb` — executed review notebook.
- `results/accuracy_by_cell.csv` — raw counts and percentages for this condition.
- `results/improvement_over_zero_shot.csv` — obfuscated-cell comparison with the matched zero-shot control.
- `results/base_obfuscated_gaps.csv` — base/obfuscation gaps where applicable.
- `results/paired_retention.csv` — paired correctness transitions.

Shared protocol, prompts, public sample IDs, aggregate report and implementation code are under [`../../common`](../../common/).

## Interpretation constraint

This is a 15-item-per-task pilot. Use raw counts with percentages and do not treat small differences as stable effects.
