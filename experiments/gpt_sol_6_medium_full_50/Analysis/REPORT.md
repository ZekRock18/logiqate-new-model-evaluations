# GPT-6 Sol Medium Assigned-Mitigation Results

All three assigned conditions use 50 underlying items per task and 250 obfuscated targets.
The matched zero-shot row is the fresh control on the same 250 obfuscated forms.

| Condition | Correct | Accuracy | Change from control |
| --- | ---: | ---: | ---: |
| zero_shot_control | 160/250 | 64.00% | +0.00 pp |
| obf_to_obf_few_shot | 161/250 | 64.40% | +0.40 pp |
| base_to_obf_paired_few_shot | 154/250 | 61.60% | -2.40 pp |
| analogical_prompting | 121/250 | 48.40% | -15.60 pp |

Cell-level accuracy, improvement and paired-retention tables are generated from private scoring evidence.
Row-level gold answers and correctness labels are intentionally not published.
