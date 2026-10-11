# Structured decomposition

The prompt asks the model to extract the relevant facts and constraints into a structure before answering. This is a Tier-1 method in the GPT-5.6 Sol (high) 50-question study.

On the applicable obfuscated questions it answered 84/150 (56.0%) correctly. Method sample sizes differ, so compare it with the matched zero-shot cells in the [analysis tables](../Analysis/improvement_over_control.csv), not with another method's raw percentage.

- [Input prompts](../Dataset/structured_decomposition.csv)
- [Recorded responses](../Result/structured_decomposition.csv)
- [Executed notebook](../notebooks/02_structured_decomposition.ipynb)
- [Full Tier-1 report](../Analysis/REPORT.md)
- [Protocol and limitations](../README.md)

The files live in the runnable Tier-1 package one level up; these links avoid duplicating data. Public files omit gold answers and row-level correctness labels.
