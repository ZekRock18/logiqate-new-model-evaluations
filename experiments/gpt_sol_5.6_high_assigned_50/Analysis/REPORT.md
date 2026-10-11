# GPT Sol 5.6 High Assigned-Mitigation Results

All three assigned conditions use 50 underlying items per task and 250 obfuscated targets.
The matched zero-shot row is the fresh control on the same 250 obfuscated forms.

| Condition | Correct | Accuracy | Change from control |
| --- | ---: | ---: | ---: |
| zero_shot_control | 161/250 | 64.40% | +0.00 pp |
| obf_to_obf_few_shot | 150/250 | 60.00% | -4.40 pp |
| base_to_obf_paired_few_shot | 153/250 | 61.20% | -3.20 pp |
| analogical_prompting | 150/250 | 60.00% | -4.40 pp |

Cell-level accuracy, improvement and paired-retention tables are generated from private scoring evidence.
Row-level gold answers and correctness labels are intentionally not published.
