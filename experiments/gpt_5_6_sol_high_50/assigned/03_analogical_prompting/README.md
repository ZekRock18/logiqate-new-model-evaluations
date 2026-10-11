# Analogical prompting

The prompt asks the model to form an analogy before answering the obfuscated question. This is one of three assigned mitigation experiments on the same 250 obfuscated targets for GPT-5.6 Sol (high).

The model answered 150/250 (60.0%) correctly; its fresh matched zero-shot control answered 163/250 (65.2%). Treat this as a descriptive comparison, not an independently replicated effect.

- [Public input prompts](../Dataset/analogical_prompting.csv)
- [Recorded responses](../Result/analogical_prompting.csv)
- [Executed notebook](../notebooks/04_analogical_prompting.ipynb)
- [Combined results and scoring notes](../Analysis/REPORT.md)
- [Run protocol and limitations](../README.md)

The prompts and response files are shared with the runnable package one level up; they are linked here instead of duplicated. Gold answers and row-level correctness labels are not public.
