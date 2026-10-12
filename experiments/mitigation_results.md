# Mitigation Technique Results: All Models

Obfuscated variants only. All runs use fresh matched zero-shot controls on the
same obfuscated items. Missing methods are not zero scores -- they were not run.

## Per-model note

- **GPT-5.6 Sol High** and **GPT-6 Sol Medium** have complete ten-method studies
  (3 assigned + 7 Tier-1). Tier-1 methods cover different task matrices; compare
  via matched cell-level tables, not overall accuracy across unequal denominators.
- **DeepSeek-V4.1-Flash** has a 15-item-per-task pilot. Small-N cells are
  descriptive, not stable effects.
- **Llama 3.1, Phi-4, ** only have zero-shot obfuscated results; mitigation
  methods were not run for these models.
- **Claude Fable 5.1 High** has zero-shot, few-shot, and CoT on paired
  base + obfuscated forms (not a ten-method study).

## GPT-5.6 Sol High (50/task, 250 obf total)

### Assigned experiments (matched zero-shot: 65.2%)

| Method | Correct | Accuracy | Delta |
| --- | ---: | ---: | ---: |
| Zero-shot control | 163/250 | 65.2% | +0.0 pp |
| Obf-to-Obf Few-Shot | 150/250 | 60.0% | -5.2 pp |
| Base-to-Obf Paired FS | 153/250 | 61.2% | -4.0 pp |
| Analogical Prompting | 150/250 | 60.0% | -5.2 pp |

### Tier-1 methods (matched zero-shot: 65.2% on obfuscated variants)

| Method | Scope | Correct | Accuracy | Delta vs control |
| --- | ---: | ---: | ---: | ---: |
| Normalize-then-Solve | obf only | 98/150 | 65.3% | +0.1 pp |
| Structured Decomposition | obf only | 84/150 | 56.0% | -9.2 pp |
| Explicit Task Instructions | obf only | 60/100 | 60.0% | -5.2 pp |
| Chain of Thought | obf only | 176/250 | 70.4% | +5.2 pp |
| Re-reading / S2A | obf only | 71/100 | 71.0% | +5.8 pp |
| Self-Consistency | obf only | 162/250 | 64.8% | -0.4 pp |
| Self-Verification / CoVe | obf only | 163/250 | 65.2% | 0.0 pp |

Source: [gpt_5_6_sol_high_50/assigned/Analysis/REPORT.md](gpt_5_6_sol_high_50/assigned/Analysis/REPORT.md),
[gpt_5_6_sol_high_50/tier1/Analysis/REPORT.md](gpt_5_6_sol_high_50/tier1/Analysis/REPORT.md)

## GPT-6 Sol Medium (50/task, 250 obf total)

### Assigned experiments (matched zero-shot: 64.0%)

| Method | Correct | Accuracy | Delta |
| --- | ---: | ---: | ---: |
| Zero-shot control | 160/250 | 64.0% | +0.0 pp |
| Obf-to-Obf Few-Shot | 161/250 | 64.4% | +0.4 pp |
| Base-to-Obf Paired FS | 154/250 | 61.6% | -2.4 pp |
| Analogical Prompting | 121/250 | 48.4% | -15.6 pp |

### Tier-1 methods (matched zero-shot: 64.0% on obfuscated variants)

| Method | Scope | Correct | Accuracy | Delta vs control |
| --- | ---: | ---: | ---: | ---: |
| Normalize-then-Solve | obf only | 98/150 | 65.3% | +1.3 pp |
| Structured Decomposition | obf only | 92/150 | 61.3% | -2.7 pp |
| Explicit Task Instructions | obf only | 69/100 | 69.0% | +5.0 pp |
| Chain of Thought | obf only | 161/250 | 64.4% | +0.4 pp |
| Re-reading / S2A | obf only | 60/100 | 60.0% | -4.0 pp |
| Self-Consistency | obf only | 160/250 | 64.0% | 0.0 pp |
| Self-Verification / CoVe | obf only | 139/250 | 55.6% | -8.4 pp |

Source: [gpt_6_sol_medium_50/assigned/Analysis/REPORT.md](gpt_6_sol_medium_50/assigned/Analysis/REPORT.md),
[gpt_6_sol_medium_50/tier1/Analysis/REPORT.md](gpt_6_sol_medium_50/tier1/Analysis/REPORT.md)

## DeepSeek-V4.1-Flash (15/task pilot, 75 obf total)

### Assigned experiments (matched zero-shot: 40.0%)

| Method | FOL | Blood Rel L1 | Blood Rel L2 | Num Series | Dir Sense | Overall | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zero-shot | 5/15 | 8/15 | 6/15 | 2/15 | 4/15 | 25/75 | +0.0 |
| Obf-to-Obf FS | 10/15 | 5/15 | 5/15 | 1/15 | 5/15 | 26/75 | +1.3 |
| Base-to-Obf Paired FS | 10/15 | 6/15 | 4/15 | 1/15 | 5/15 | 26/75 | +1.3 |
| Analogical Prompting | 6/15 | 9/15 | 6/15 | 3/15 | 6/15 | 30/75 | +6.7 |

### Tier-1 methods

| Method | FOL | Blood Rel L1 | Blood Rel L2 | Num Series | Dir Sense |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normalize-then-Solve | 6/15 | 7/15 | 6/15 | N/A | N/A |
| Structured Decomposition | N/A | 9/15 | 6/15 | N/A | 8/15 |
| Explicit Task Instructions | N/A | N/A | N/A | 5/15 | 9/15 |
| Chain of Thought | 9/15 | 9/15 | 4/15 | 4/15 | 7/15 |
| Re-reading / S2A | 7/15 | N/A | 6/15 | N/A | N/A |
| Self-Consistency | 8/15 | 9/15 | 6/15 | 4/15 | 11/15 |
| Self-Verification / CoVe | 7/15 | 7/15 | 6/15 | 1/15 | 8/15 |

Source: [deepseek_v4_1_flash_15/shared/results/REPORT.md](deepseek_v4_1_flash_15/shared/results/REPORT.md)

## Models without mitigation results

| Model | Available | Zero-shot only |
| --- | --- | --- |
| Claude Fable 5.1 High | Zero-shot, few-shot, CoT | See claude_fable_5.1_high/Result/Analysis/REPORT.md |
| Llama 3.1 (Ollama) | 4 methods, obfuscated only | 18.8% overall zero-shot |
| Phi-4 (Ollama) | 4 methods, obfuscated only | 26.8% overall zero-shot |
|  | 4 methods, obfuscated only | 37.6% overall zero-shot |
|  (obf-250 release) | 4 methods, obfuscated only | 33.6% overall zero-shot |

## Cross-model comparison: zero-shot control on obfuscated items

| Model | Sample size | Overall acc |
| --- | ---: | ---: |
| GPT-5.6 Sol High | 250 | 65.2% |
| GPT-6 Sol Medium | 250 | 64.0% |
| Claude Fable 5.1 High | 450 | 59.8% |
| DeepSeek-V4.1-Flash | 105 | 40.0% |
|  | 250 | 37.6% |
| Phi-4 (Ollama) | 250 | 26.8% |
| Llama 3.1 (Ollama) | 250 | 18.8% |

Caveat: GPT-5.6 and GPT-6 used Codex model aliases; dated snapshots and sampling
parameters were unavailable. Claude Fable 5.1 used a different sample structure
(paired base + obfuscated forms, 450 items). DeepSeek is a 15-item/task pilot.
Report raw counts with percentages. Do not treat small differences as stable effects.
