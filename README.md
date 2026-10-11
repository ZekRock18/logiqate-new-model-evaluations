# LogiQAte: evaluations on new models

This repository studies whether prompting can help language models answer questions whose logical structure has been obscured. It extends the work in *Don't Judge a Book by its Cover: Testing LLMs' Robustness Under Logical Obfuscation* (Borah et al., EACL 2026). The repository contains several **different runs**, so do not assume every model used the same sample size or method set.

**Start with the [model experiment index](experiments/README.md).** Choose a model, then a prompting method. Each guide points to the public inputs, recorded answers, analysis, notebook, and limitations. The [project wiki](wiki/Home.md) explains the pilot protocol and lists public artifacts. The [project-state note](PROJECT_MEMORY.md) records the current layout, checks, and handoff cautions.

## What is here?

| Study | Scope | Guide |
| --- | --- | --- |
| Claude Fable 5.1 High | 50 questions per task; zero-shot, few-shot, and chain-of-thought evaluation | [Claude report](claude_fable_5.1_high/Result/Analysis/REPORT.md) |
| DeepSeek-V4.1-Flash | 15-question-per-task prompt-mitigation pilot; three assigned prompts and seven Tier-1 methods | [DeepSeek pilot](experiments/deepseek_v4_1_flash_15/) |
| GPT-5.6 Sol (high) | 50-question-per-task mitigation study; fresh control, three assigned prompts, seven Tier-1 methods | [GPT-5.6 study](experiments/gpt_5_6_sol_high_50/) |
| GPT-6 Sol (medium) | Same fixed 50-question sample and method set, with fresh model responses | [GPT-6 study](experiments/gpt_6_sol_medium_50/) |
| Llama, Phi, Qwen | Supplied runs for selected methods; not all ten methods are present | [Available runs](experiments/README.md) |

On the common 250 obfuscated targets, GPT-6 Sol's fresh zero-shot control scored 160/250 (64.0%). Obfuscated few-shot scored 161/250 (64.4%), paired few-shot 154/250 (61.6%), and analogical prompting 121/250 (48.4%). GPT-5.6 Sol's corresponding control scored 163/250 (65.2%). Its strongest full-matrix Tier-1 result was Chain of Thought at 176/250 (70.4%). These are descriptive results from this repository's scoring rules, **not** claims that a small difference will generalize.

## How to read a method folder

- **Dataset/input:** the question and prompt given to the model. Public GPT queues have no gold answers.
- **Result:** the recorded model response. Multi-pass methods retain their separate paths or stages.
- **Analysis:** aggregate accuracy and matched-control comparisons. Check the denominator and task variants before comparing methods.
- **Notebook and source:** the procedure used to prepare, run, or inspect the experiment. The GPT packages also contain validation tests and publication audits.

Shared controls, manifests, reusable code, and audits sit at the model/package level so large CSVs do not appear twice. Method READMEs link to the exact files. The DeepSeek pilot uses 15 questions per task; the GPT studies use 50. Some Llama, Phi, and Qwen folders contain only three or four methods. Missing methods are not zero scores.

## Reproducibility and release boundary

The two GPT studies used Codex model aliases, not dated snapshot-pinned API calls. The runtime did not expose all sampling settings or request IDs; see each run's provenance and context limitations before making cross-model claims. The Claude study has its own [row-by-row runner](claude_fable_5.1_high/run_row_by_row.py) and [report](claude_fable_5.1_high/Result/Analysis/REPORT.md).

Public packages intentionally omit API credentials, private answer keys, private scoring manifests, and row-level gold correctness labels. The GPT packages publish prompts, submitted responses, aggregate scores, executed notebooks, and publication audits. These studies extend the paper; they are not a strict reproduction of its full 1,108-question evaluation.
