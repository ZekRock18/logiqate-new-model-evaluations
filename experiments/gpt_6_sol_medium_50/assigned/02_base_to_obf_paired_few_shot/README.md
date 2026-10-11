# Base-to-obfuscated paired few-shot

Two examples pair a clean question with its obfuscated form before the test question. This is one of three assigned mitigation experiments on the same 250 obfuscated targets for GPT-6 Sol (medium).

The model answered 154/250 (61.6%) correctly; its fresh matched zero-shot control answered 160/250 (64.0%). Treat this as a descriptive comparison, not an independently replicated effect.

- [Public input prompts](../Dataset/base_to_obf_paired_few_shot.csv)
- [Recorded responses](../Result/base_to_obf_paired_few_shot.csv)
- [Executed notebook](../notebooks/03_base_to_obf_paired_few_shot.ipynb)
- [Combined results and scoring notes](../Analysis/REPORT.md)
- [Run protocol and limitations](../README.md)

The prompts and response files are shared with the runnable package one level up; they are linked here instead of duplicated. Gold answers and row-level correctness labels are not public.
