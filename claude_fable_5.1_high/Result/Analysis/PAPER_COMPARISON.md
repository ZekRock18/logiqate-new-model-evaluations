# Claude Fable 5.1 High compared with the paper

## Result

Claude Fable 5.1 High has the **4th-smallest mean degradation of 11 models**
when added to the ten models reported by Borah et al. Across zero-shot,
few-shot, and chain-of-thought prompting, its mean relative accuracy change is
**-27.49%**.

Lower-magnitude negative values are better: they indicate that more of the
model's base accuracy survived logical obfuscation.

| Rank | Model | Zero-shot | Few-shot | CoT | Mean across settings | Source |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | GPT-5 | -27.0% | -20.2% | -18.7% | -22.0% | Paper |
| 2 | o4-mini | -21.4% | -22.7% | -22.0% | -22.0% | Paper |
| 3 | Qwen QwQ-32B | -27.5% | -23.3% | -26.1% | -25.6% | Paper |
| **4** | **Claude Fable 5.1 High** | **-28.46%** | **-24.84%** | **-29.18%** | **-27.49%** | **This run** |
| 5 | Llama-4-Maverick-17B | -24.8% | -42.6% | -39.1% | -35.5% | Paper |
| 6 | Claude 4.5 Haiku | -48.2% | -43.3% | -34.8% | -42.1% | Paper |
| 7 | Gemma-3-27B-IT | -39.3% | -44.9% | -43.5% | -42.6% | Paper |
| 8 | Gemini 2.5 Pro | -42.9% | -46.3% | -40.5% | -43.2% | Paper |
| 9 | Claude 3.7 Sonnet | -47.5% | -41.6% | -48.7% | -45.9% | Paper |
| 10 | GPT-4o | -47.6% | -47.2% | -49.4% | -48.1% | Paper |
| 11 | GPT-4o-mini | -51.3% | -48.9% | -50.6% | -50.3% | Paper |

Fable ranks **5th/11 in zero-shot**, **4th/11 in few-shot**, and **4th/11 in
CoT**. Its degradation is close to QwQ-32B in all three settings (0.96, 1.54,
and 3.08 percentage points worse, respectively). Its mean is 1.86 points worse
than QwQ, but 8.01 points better than Llama-4-Maverick.

## Accuracy context for this run

| Setting | Base and obfuscated rows | Correct | Micro accuracy | Mean degradation |
| --- | ---: | ---: | ---: | ---: |
| Zero-shot | 450 | 269 | 59.78% | -28.46% |
| Few-shot | 450 | 264 | 58.67% | -24.84% |
| CoT | 450 | 270 | 60.00% | -29.18% |

The aggregate result is **803/1,350 (59.48%)**. Fable's strongest robustness is
on first-order logic; its largest consistent losses are on obfuscated number
series and blood relations. CoT produced the highest overall accuracy, but it
did not improve robustness: its degradation was slightly larger than in the
other two settings.

## Comparability limits

This is a useful extension, not a strict like-for-like replication:

- The paper uses 1,108 underlying questions; this run uses a deterministic
  sample of 50 underlying questions from each of four tasks.
- The paper's published models and Fable were not evaluated on identical sample
  sizes. Relative degradation is more comparable than absolute accuracy, but
  sampling uncertainty remains.
- Fable was evaluated through a persistent coding-agent session that processed
  rows sequentially, not isolated API calls with a fresh context per row.
- The displayed mean is an additional descriptive average across the three
  prompting settings; the paper reports each setting separately.
- Negative degradation means accuracy fell after obfuscation. Ranking uses the
  value closest to zero as the more robust result; it does not rank raw task
  accuracy or cost.

Paper figures are transcribed from the tables reported by Borah et al. Fable
figures come from `summary.json` and the row-level evidence in
`scored_responses.csv`.
