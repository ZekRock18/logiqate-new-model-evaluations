# Self-verification / CoVe

The model produces an initial answer, then a separate verification pass examines it and supplies a final answer. This is a Tier-1 method in the GPT-5.6 Sol (high) 50-question study.

On the applicable obfuscated questions it answered 163/250 (65.2%) correctly. Method sample sizes differ, so compare it with the matched zero-shot cells in the [analysis tables](../Analysis/improvement_over_control.csv), not with another method's raw percentage.

- Input prompts: [initial](../Dataset/self_verification_cove_initial.csv), [verification](../Dataset/self_verification_cove_verification.csv)
- Recorded responses: [initial](../Result/self_verification_cove_initial.csv), [verification](../Result/self_verification_cove_verification.csv)
- [Combined answers and changes](../Analysis/cove_aggregates.csv)
- [Executed notebook](../notebooks/07_self_verification_cove.ipynb)
- [Full Tier-1 report](../Analysis/REPORT.md)
- [Protocol and limitations](../README.md)

The files live in the runnable Tier-1 package one level up; these links avoid duplicating data. Public files omit gold answers and row-level correctness labels.
