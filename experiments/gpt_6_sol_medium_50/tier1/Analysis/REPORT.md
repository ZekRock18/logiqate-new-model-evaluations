# GPT-6 Sol Medium: Full-50 Tier-1 Results

All seven Tier-1 methods use the parent's fixed 50-item sample and fresh matched zero-shot control.

| Condition | Correct | Accuracy |
| --- | ---: | ---: |
| normalize_then_solve | 98/150 | 65.33% |
| structured_decomposition | 92/150 | 61.33% |
| explicit_task_instructions | 69/100 | 69.00% |
| chain_of_thought | 161/250 | 64.40% |
| rereading_s2a | 60/100 | 60.00% |
| self_consistency | 160/250 | 64.00% |
| self_verification_cove | 139/250 | 55.60% |

Methods cover different task matrices, so these micro-accuracies are not directly comparable across methods. Matched cell-level changes versus the zero-shot control are the primary comparison.

## Special multi-pass metrics

- Self-Consistency agreement rate: 94.22%.
- CoVe changed 51/450 answers, corrected 3 and harmed 25.

Cell accuracy, matched-control improvement, base/obfuscated gaps and paired-retention tables are public aggregates.
Row-level gold answers and correctness labels are intentionally excluded.
