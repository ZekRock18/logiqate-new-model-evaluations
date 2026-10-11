# Normalize then solve

The prompt asks the model to restate the obfuscated question in a cleaner form before solving it. This is a Tier-1 method in the GPT-6 Sol (medium) 50-question study.

On the applicable obfuscated questions it answered 98/150 (65.3%) correctly. Method sample sizes differ, so compare it with the matched zero-shot cells in the [analysis tables](../Analysis/improvement_over_control.csv), not with another method's raw percentage.

- [Input prompts](../Dataset/normalize_then_solve.csv)
- [Recorded responses](../Result/normalize_then_solve.csv)
- [Executed notebook](../notebooks/01_normalize_then_solve.ipynb)
- [Full Tier-1 report](../Analysis/REPORT.md)
- [Protocol and limitations](../README.md)

The files live in the runnable Tier-1 package one level up; these links avoid duplicating data. Public files omit gold answers and row-level correctness labels.
