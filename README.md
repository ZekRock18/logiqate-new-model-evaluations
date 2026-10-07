# LogiQAte evaluations on new models

This repository collects new-model evaluations for *Don't Judge a Book by its
Cover: Testing LLMs' Robustness Under Logical Obfuscation* (Borah et al., EACL
2026). Each model is tested on the same fixed sample and stored in its own
folder with the prompts, raw submitted answers, and scored analysis.

## Completed models

| Model | Responses | Accuracy | ZS degradation | FS degradation | CoT degradation | Report |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Claude Fable 5.1 High | 1,350/1,350 | 59.48% | -28.46% | -24.84% | -29.18% | [Open report](claude_fable_5.1_high/Result/Analysis/REPORT.md) |

## Prompt-mitigation experiments

The [`experiments/`](experiments/) section contains the completed 15-item-per-task
prompt-mitigation study on `deepseek-ai/DeepSeek-V4.1-Flash`. It includes the
three supervisor-assigned experiments, all seven Tier 1 prompting methods, the
matched zero-shot control, executed notebooks, aggregate results, public sample
metadata, versioned prompt templates and validation code.

The public package intentionally excludes credentials, private scoring
manifests, row-level gold-answer files and raw provider transcripts.

Fable has the **4th-smallest mean degradation of 11 models** when placed beside
the ten models reported in the paper. The full ranked table and comparison
limitations are in [PAPER_COMPARISON.md](claude_fable_5.1_high/Result/Analysis/PAPER_COMPARISON.md).

## Evaluation design

Every model receives the same 50 underlying questions from each of four task
families:

- first-order logic: base and obfuscated;
- blood relations: base, level-1 obfuscation, and level-2 obfuscation;
- number series: base and obfuscated; and
- direction sense: base and obfuscated.

Every form is evaluated with zero-shot, few-shot, and chain-of-thought
prompting. This produces **1,350 response rows per model** from 200 underlying
questions.

## Repository structure

~~~text
.
├── README.md
└── <model_name>/
    ├── Dataset/               fixed input CSV files
    ├── Result/                submitted answers
    │   └── Analysis/          report, workbook, aggregates, and row evidence
    ├── START.md               prompt for a coding agent
    └── run_row_by_row.py      UTF-8-safe durable queue
~~~

The result CSVs are the raw model submissions. scored_responses.csv records the
row-level judgment, incorrect_responses.csv isolates failures, summary.json
provides machine-readable aggregates, and ANALYSIS_REPORT.xlsx is the
spreadsheet version.

## Validate a completed model

Python 3.10 or newer is recommended. The queue runner uses only the standard
library, so no package installation or API key is required.

~~~bash
python -X utf8 claude_fable_5.1_high/run_row_by_row.py status --strict
~~~

The command must report 1,350/1,350 resolved rows and exit successfully.

## Add another model

Create a new model-named folder with the same four files under Dataset/, a copy
of run_row_by_row.py, and START.md. Begin with an empty Result/ directory, then
give START.md to the coding agent being evaluated. The runner checkpoints every
answer atomically and maintains a recovery journal, so another session can
safely resume.

Keep these controls consistent across models:

- do not change the sampled rows, prompts, response IDs, or order;
- let the evaluated model reason about each row itself;
- do not use regex solvers, hard-coded maps, external decoders, web search, or
  another model/API;
- do not show the model an answer key or another model's results; and
- publish a model folder only after status --strict succeeds and its results
  have been scored.

## Interpretation warning

The paper evaluates 1,108 underlying questions, while these runs use a fixed
sample of 50 questions per task. In addition, agent runs process rows
sequentially in a persistent session rather than through isolated API calls.
Relative degradation is more useful than raw accuracy for comparison, but these
runs should be described as an extension—not a strict reproduction of the
paper's protocol.

No API keys or credentials are included in this repository.
