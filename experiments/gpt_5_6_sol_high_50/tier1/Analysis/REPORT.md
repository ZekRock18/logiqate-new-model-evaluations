# GPT Sol 5.6 High: Full-50 Tier-1 Results

All seven Tier-1 methods use the parent's fixed 50-item sample and fresh matched zero-shot control.

| Condition | Correct | Accuracy |
| --- | ---: | ---: |
| normalize_then_solve | 98/150 | 65.33% |
| structured_decomposition | 84/150 | 56.00% |
| explicit_task_instructions | 60/100 | 60.00% |
| chain_of_thought | 176/250 | 70.40% |
| rereading_s2a | 71/100 | 71.00% |
| self_consistency | 162/250 | 64.80% |
| self_verification_cove | 163/250 | 65.20% |

Methods cover different task matrices, so these micro-accuracies are not directly comparable across methods. Matched cell-level changes versus the zero-shot control are the primary comparison.

## Special multi-pass metrics

- Self-Consistency agreement rate: 98.44%.
- CoVe changed 6/450 answers, corrected 1 and harmed 5.

Cell accuracy, matched-control improvement, base/obfuscated gaps and paired-retention tables are public aggregates.
Row-level gold answers and correctness labels are intentionally excluded.
