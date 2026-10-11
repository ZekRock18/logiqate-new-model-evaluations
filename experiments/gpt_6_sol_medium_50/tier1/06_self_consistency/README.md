# Self-consistency

Three blinded answer paths are combined by majority vote; a three-way disagreement is counted as no consensus. This is a Tier-1 method in the GPT-6 Sol (medium) 50-question study.

On the applicable obfuscated questions it answered 160/250 (64.0%) correctly. Method sample sizes differ, so compare it with the matched zero-shot cells in the [analysis tables](../Analysis/improvement_over_control.csv), not with another method's raw percentage.

- Input prompts: [path 1](../Dataset/self_consistency_path_1.csv), [path 2](../Dataset/self_consistency_path_2.csv), [path 3](../Dataset/self_consistency_path_3.csv)
- Recorded responses: [path 1](../Result/self_consistency_path_1.csv), [path 2](../Result/self_consistency_path_2.csv), [path 3](../Result/self_consistency_path_3.csv)
- [Voting and agreement table](../Analysis/self_consistency_aggregates.csv)
- [Executed notebook](../notebooks/06_self_consistency.ipynb)
- [Full Tier-1 report](../Analysis/REPORT.md)
- [Protocol and limitations](../README.md)

The files live in the runnable Tier-1 package one level up; these links avoid duplicating data. Public files omit gold answers and row-level correctness labels.
