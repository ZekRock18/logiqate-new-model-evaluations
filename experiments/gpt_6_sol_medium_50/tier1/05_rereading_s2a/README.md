# Re-reading / System 2 Attention

The prompt asks the model to isolate relevant information and re-read the question before answering. This is a Tier-1 method in the GPT-6 Sol (medium) 50-question study.

On the applicable obfuscated questions it answered 60/100 (60.0%) correctly. Method sample sizes differ, so compare it with the matched zero-shot cells in the [analysis tables](../Analysis/improvement_over_control.csv), not with another method's raw percentage.

- [Input prompts](../Dataset/rereading_s2a.csv)
- [Recorded responses](../Result/rereading_s2a.csv)
- [Executed notebook](../notebooks/05_rereading_s2a.ipynb)
- [Full Tier-1 report](../Analysis/REPORT.md)
- [Protocol and limitations](../README.md)

The files live in the runnable Tier-1 package one level up; these links avoid duplicating data. Public files omit gold answers and row-level correctness labels.
