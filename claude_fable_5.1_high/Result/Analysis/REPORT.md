# Claude Fable 5.1 High — LogiQAte Evaluation Report

## Executive summary

The run scored **803/1350 correct (59.48%)** across all tasks, variants, and prompting settings.

All **1350** expected response IDs were returned. There were **0 missing**, **0 extra**, and **0 duplicate** IDs. Exact prompt comparison found **0 modified prompts**.

The output contains **0 literal `UNKNOWN` responses (0.00%)**. They are retained in the denominator and scored as wrong.

It also contains **0 explicit error responses** and **0 blank responses**; these are likewise scored as wrong.

Every response was substantive, so substantive-answer accuracy is identical to the official score.

## Accuracy by prompting setting

| Setting | Correct | Total | Micro accuracy | UNKNOWN | Mean relative obfuscation change |
| --- | --- | --- | --- | --- | --- |
| Zero-shot | 269 | 450 | 59.78% | 0 (0.00%) | -28.46% |
| Few-shot | 264 | 450 | 58.67% | 0 (0.00%) | -24.84% |
| CoT | 270 | 450 | 60.00% | 0 (0.00%) | -29.18% |

A negative relative change means performance fell under obfuscation; a positive value means it improved. The relative-change aggregate omits any task whose base accuracy is zero.

## Accuracy by task and variant

| Task | Variant | Zero-shot | Few-shot | CoT |
| --- | --- | --- | --- | --- |
| Obfus FOL | Base | 44/50 (88.00%) | 45/50 (90.00%) | 45/50 (90.00%) |
| Obfus FOL | Obfuscation | 41/50 (82.00%) | 43/50 (86.00%) | 40/50 (80.00%) |
| Obfus Blood Relation | Base | 35/50 (70.00%) | 34/50 (68.00%) | 31/50 (62.00%) |
| Obfus Blood Relation | Obfuscation L1 | 24/50 (48.00%) | 26/50 (52.00%) | 28/50 (56.00%) |
| Obfus Blood Relation | Obfuscation L2 | 22/50 (44.00%) | 20/50 (40.00%) | 22/50 (44.00%) |
| Obfus Number Series | Base | 33/50 (66.00%) | 29/50 (58.00%) | 31/50 (62.00%) |
| Obfus Number Series | Obfuscation | 20/50 (40.00%) | 15/50 (30.00%) | 14/50 (28.00%) |
| Obfus Direction Sense | Base | 30/50 (60.00%) | 28/50 (56.00%) | 35/50 (70.00%) |
| Obfus Direction Sense | Obfuscation | 20/50 (40.00%) | 24/50 (48.00%) | 24/50 (48.00%) |

## Paired robustness

Each base question is paired with its corresponding obfuscated version. `Base-only correct` is the clearest robustness failure; `obfuscated-only correct` is a reversal in the other direction.

| Task | Obfuscated variant | Setting | Both correct | Base only | Obfuscated only | Both wrong | Retention |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Obfus FOL | Obfuscation | Zero-shot | 38 | 6 | 3 | 3 | 86.36% |
| Obfus FOL | Obfuscation | Few-shot | 42 | 3 | 1 | 4 | 93.33% |
| Obfus FOL | Obfuscation | CoT | 40 | 5 | 0 | 5 | 88.89% |
| Obfus Blood Relation | Obfuscation L1 | Zero-shot | 21 | 14 | 3 | 12 | 60.00% |
| Obfus Blood Relation | Obfuscation L2 | Zero-shot | 19 | 16 | 3 | 12 | 54.29% |
| Obfus Blood Relation | Obfuscation L1 | Few-shot | 22 | 12 | 4 | 12 | 64.71% |
| Obfus Blood Relation | Obfuscation L2 | Few-shot | 18 | 16 | 2 | 14 | 52.94% |
| Obfus Blood Relation | Obfuscation L1 | CoT | 23 | 8 | 5 | 14 | 74.19% |
| Obfus Blood Relation | Obfuscation L2 | CoT | 19 | 12 | 3 | 16 | 61.29% |
| Obfus Number Series | Obfuscation | Zero-shot | 18 | 15 | 2 | 15 | 54.55% |
| Obfus Number Series | Obfuscation | Few-shot | 13 | 16 | 2 | 19 | 44.83% |
| Obfus Number Series | Obfuscation | CoT | 14 | 17 | 0 | 19 | 45.16% |
| Obfus Direction Sense | Obfuscation | Zero-shot | 18 | 12 | 2 | 18 | 60.00% |
| Obfus Direction Sense | Obfuscation | Few-shot | 20 | 8 | 4 | 18 | 71.43% |
| Obfus Direction Sense | Obfuscation | CoT | 23 | 12 | 1 | 14 | 65.71% |

## Interpretation

- **CoT was strongest overall** at 60.00%; Zero-shot scored 59.78%, Few-shot scored 58.67%.
- **Non-answer audit:** 0 `UNKNOWN`, 0 explicit errors, and 0 blank responses. 0 task/variant/setting cells contain only `UNKNOWN` responses.
- **Obfuscation did not have a uniform effect.** Across the 15 paired cell comparisons, accuracy improved in 0, declined in 15, and was unchanged in 0.
- **The strongest cell** was Obfus FOL / Base / Few-shot at 90.00%. The weakest non-zero cell was Obfus Number Series / Obfuscation / CoT at 28.00%.
- These scores describe this returned batch exactly. Because a persistent coding-agent session processed multiple rows, this should be labelled an agent-driven batch evaluation rather than a strictly isolated row-level API experiment.

## Method

Responses were joined to the private answer key by `response_id` and scored
with task-specific exact-match normalizers. Errors, blanks, and `UNKNOWN`
responses remain in the denominator. The sample contains 50 underlying
questions per task, with paired base and obfuscated forms (plus Blood Relations
Level 1 and Level 2), under three prompting settings. Number Series sampling is
balanced across its three obfuscation types (17/17/16) and excludes known
non-equivalent transformations.

Row-level evidence is in `scored_responses.csv`; all failures are in `incorrect_responses.csv`; machine-readable aggregates are in `summary.json`.

The cross-model interpretation is saved in `PAPER_COMPARISON.md`, with its
underlying table in `paper_comparison.csv`.
