# GPT Sol 5.6 High: Full-50 Tier-1 Methods

This extension evaluates the seven Tier-1 prompt-mitigation methods on the
same fixed 50-item-per-task sample and against the same fresh zero-shot control
as the parent assigned-experiment package.

## Evaluation matrix

| Method | Applicable task forms | Evaluation units | Raw generations |
| --- | --- | ---: | ---: |
| Normalize Then Solve | FOL base/obfuscated; Blood Relation base/L1/L2 | 250 | 250 |
| Structured Decomposition | Blood Relation base/L1/L2; Direction base/obfuscated | 250 | 250 |
| Explicit Task Instructions | Number Series base/obfuscated; Direction base/obfuscated | 200 | 200 |
| Chain of Thought | All nine task/variant cells | 450 | 450 |
| Re-reading / S2A | FOL base/obfuscated; Blood Relation base/L2 | 200 | 200 |
| Self-Consistency | All nine cells, three paths per item | 450 | 1,350 |
| Self-Verification / CoVe | All nine cells, initial and verifier passes | 450 | 900 |
| **Total** | **45 cells** | **2,250** | **3,600** |

Self-consistency uses three separately queued worker paths and a normalized
majority vote. Fewer than two matching paths produces `NO_CONSENSUS`, which is
retained as wrong. CoVe retains both the initial solution and the verifier's
response; only the verified answer is scored.

## Runtime boundary

This is a `gpt-5.6-sol` high-reasoning Codex agent run, not a snapshot-pinned
API run. The runtime does not expose temperature, random seeds, provider
request IDs, sampling parameters or token telemetry. The self-consistency
paths therefore use distinct blinded workers but cannot reproduce the earlier
API protocol's temperature-0.7 sampling guarantee. Persistent workers also do
not technically guarantee context isolation between successive queue items.

The fresh matched control was generated before this Tier-1 extension, so
run-order and time effects are not controlled. These are prompt-level
treatments: full concise responses are retained, but adherence to every
requested internal normalization, decomposition, CoT or S2A step is not
independently verified.

Scoring uses the parent package's operational normalizers. FOL takes the last
`TRUE`/`FALSE` token, Number Series takes the last integer, and Blood Relation
uses punctuation-insensitive labels with digit/word count equivalence. The
Direction normalizer collapses `KM`, `M` and `BLOCKS` to the same numeric form;
after directions match, it also accepts a row when either side omits distance.
This inherited behavior can inflate Direction accuracy and affects
self-consistency votes and CoVe transition metrics. A 0.05 numeric tolerance
is used when both direction answers include distances.

Some inherited Blood Relation prompts ask for a count despite the shared task
instruction requesting a relationship label. The retained model responses
usually follow the question itself; the count-aware normalizer handles digit
and word forms consistently.

Because the seven methods cover different task matrices, their overall
micro-accuracies are not directly comparable. The matched task/variant-cell
changes against zero-shot are the primary comparison. This run's CoVe verifier
receives the complete retained initial prompt and response, rather than only a
target and task instruction; responses are serialized on one physical line.
Both are deliberate `gpt56-tier1-v1` agent-runtime adaptations of the earlier
API protocol.

All raw model responses and public prompts are retained. Gold answers and
row-level correctness labels remain in the private workspace and are excluded
from this repository.

## Results

| Method | Obfuscated correct | Obfuscated accuracy |
| --- | ---: | ---: |
| Normalize Then Solve | 98/150 | 65.33% |
| Structured Decomposition | 84/150 | 56.00% |
| Explicit Task Instructions | 60/100 | 60.00% |
| Chain of Thought | 176/250 | 70.40% |
| Re-reading / S2A | 71/100 | 71.00% |
| Self-Consistency | 162/250 | 64.80% |
| Self-Verification / CoVe | 163/250 | 65.20% |

The matched zero-shot control scored 163/250 (65.20%) across all five
obfuscated task forms. Of the three methods evaluated on that complete
250-question matrix, Chain of Thought improved by 13 answers (+5.20 percentage
points), Self-Consistency decreased by one answer (-0.40 points), and CoVe was
unchanged overall. Re-reading / S2A's 71.00% is on a narrower 100-question
FOL/Blood-L2 subset and must not be compared directly with the full-matrix
figures.

Self-Consistency produced 382 unanimous votes, 61 two-of-three majorities and
7 `NO_CONSENSUS` outcomes. CoVe changed only 6/450 initial answers: one change
corrected an error and five changed correct answers to incorrect ones. See
[`Analysis/REPORT.md`](Analysis/REPORT.md) and the public aggregate CSVs for
cell-level comparisons.

## Reproduction and validation

```powershell
python run_queue.py status --strict
python src/score.py --source-root "<private ObusQFate workspace>"
python src/make_notebooks.py
python -m pytest tests -q
python src/publication_audit.py
```
