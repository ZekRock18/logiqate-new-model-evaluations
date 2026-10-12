# Zero-Shot Results: All Models

Obfuscated variants only. All runs scored with task-specific exact-match
normalizers. Missing methods are not zero scores -- they were simply not run.

## Per-task breakdown

| Model | Sample | FOL | Blood Rel | Num Series | Dir Sense |
| --- | ---: | ---: | ---: | ---: | ---: |
| Claude Fable 5.1 High | 50/task | 82.0% | 46.0% (L1 48%, L2 44%) | 40.0% | 40.0% |
| GPT-5.6 Sol High | 50/task | 60.0% | 58.7% (L1 64%, L2 66%) | 84.0% | 36.0% |
| GPT-6 Sol Medium | 50/task | 60.0% | 57.3% (L1 63%, L2 53%) | 84.0% | 36.0% |
| DeepSeek-V4.1-Flash | 15/task | 33.3% | 46.7% (L1 53%, L2 40%) | 13.3% | 26.7% |
| Qwen (main release) | 50/task | 80.0% | 46.0% (L1 50%, L2 40%) | 18.0% | 6.0% |
|  (obf-250 release) | 50/task | 70.0% | 41.0% (L1 46%, L2 38%) | 20.0% | 6.0% |
| Llama 3.1 (Ollama) | 50/task | 58.0% | 13.5% (L1 14%, L2 12%) | 0.0% | 2.0% |
| Phi-4 (Ollama) | 50/task | 78.0% | 23.0% (L1 30%, L2 22%) | 0.0% | 4.0% |

## Overall obfuscated accuracy

| Model | Zero-shot acc | N |
| --- | ---: | ---: |
| GPT-5.6 Sol High | 65.20% | 250 |
| GPT-6 Sol Medium | 64.00% | 250 |
| Claude Fable 5.1 High | 59.78% | 450 |
| DeepSeek-V4.1-Flash | 40.00% | 105 |
|  (main release) | 37.60% | 250 |
|  (obf-250 release) | 33.60% | 250 |
| Phi-4 (Ollama) | 26.80% | 250 |
| Llama 3.1 (Ollama) | 18.80% | 250 |

## Notes

- **Claude Fable 5.1 High**: 450 items (50 per task, paired base + obfuscated forms).
  Source: [claude_fable_5.1_high/Result/Analysis/REPORT.md](../claude_fable_5.1_high/Result/Analysis/REPORT.md)
- **GPT-5.6 Sol High**: 250 obfuscated items (50 per task). Run via Codex aliases.
  Source: [gpt_5_6_sol_high_50/assigned/Analysis/REPORT.md](gpt_5_6_sol_high_50/assigned/Analysis/REPORT.md)
- **GPT-6 Sol Medium**: same 250-item sample, fresh responses.
  Source: [gpt_6_sol_medium_50/assigned/Analysis/REPORT.md](gpt_6_sol_medium_50/assigned/Analysis/REPORT.md)
- **DeepSeek-V4.1-Flash**: 15-item-per-task pilot (75 obfuscated cells).
  Source: [deepseek_v4_1_flash_15/shared/results/REPORT.md](deepseek_v4_1_flash_15/shared/results/REPORT.md)
- ** (main release)**: 50 items per task, obfuscated only, 4 methods. Run by Sayanil.
  Source: [/01_normalize_then_solve/](..//01_normalize_then_solve/)
- ** (obf-250 release)**: separate release, same 50-item obfuscated sample. Run by Sayanil.
  Source: [qwen_obfuscated_250/01_normalize_then_solve/](../qwen_obfuscated_250/01_normalize_then_solve/)
- **Llama 3.1 (Ollama)**: 50 items per task, obfuscated only, 4 methods. Run by Sayanil.
  Source: [llama/01_normalize_then_solve/](../llama/01_normalize_then_solve/)
- **Phi-4 (Ollama)**: 50 items per task, obfuscated only, 4 methods. Run by Sayanil.
  Source: [phi/01_normalize_then_solve/](../phi/01_normalize_then_solve/)

Small-N cells (DeepSeek pilot, 15/task) are not directly comparable to 50-item runs.
Report raw counts with percentages.
