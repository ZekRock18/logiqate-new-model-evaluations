# GPT-6 Sol (medium), Tier 1 methods

This package uses the fixed 50-question sample and fresh `gpt-6-sol` responses at medium reasoning effort. Its prompts and task matrices follow the earlier GPT-5.6 Sol Tier 1 protocol. The public queues contain no gold labels or prior model responses.

Method guides: [Normalize Then Solve](01_normalize_then_solve/), [Structured Decomposition](02_structured_decomposition/), [Explicit Task Instructions](03_explicit_task_instructions/), [Chain of Thought](04_chain_of_thought/), [Re-reading / S2A](05_rereading_s2a/), [Self-Consistency](06_self_consistency/), and [Self-Verification / CoVe](07_self_verification_cove/).

| Method | Evaluation units | Raw responses |
| --- | ---: | ---: |
| Normalize Then Solve | 250 | 250 |
| Structured Decomposition | 250 | 250 |
| Explicit Task Instructions | 200 | 200 |
| Chain of Thought | 450 | 450 |
| Re-reading / S2A | 200 | 200 |
| Self-Consistency (three independent paths) | 450 | 1,350 |
| Self-Verification / CoVe (initial + verifier) | 450 | 900 |
| Total | 2,250 | 3,600 |

All 3,600 raw responses are complete. The nine initial queues total 3,150 responses. The tenth, CoVe verification queue was built from the recorded 450 initial responses. For replay, use `python -X utf8 run_queue.py instructions`, `next`, `answer`, and `status --strict`; preserve blinded self-consistency paths and a separate CoVe verifier.

`tier1_manifest.json` fixes the sample, method matrix, counts, and prepared dataset hashes. `src/aggregate.py` combines the three self-consistency paths and CoVe passes. The 2,250 scored evaluations, eight executed notebooks, tests, and publication audit are complete. See [the report](Analysis/REPORT.md) and aggregate tables. The matched zero-shot control is in the parent package.

On matched obfuscated cells, Explicit Task Instructions scored 69/100 versus 58/100 for control (+11 points). Structured Decomposition scored 92/150 versus 90/150 (+1.3 points); Chain of Thought scored 161/250 versus 160/250 (+0.4 points). Normalize Then Solve scored 98/150 versus 102/150 (-2.7 points); Re-reading/S2A scored 60/100 versus 68/100 (-8 points); Self-Consistency tied control at 160/250; and CoVe scored 139/250 versus 160/250 (-8.4 points). Different methods cover different task matrices; these are descriptive matched-cell changes, not a common all-method ranking.

The model snapshot, provider request IDs, sampling temperature, and seed are not exposed by this Codex runtime, so only model family and reasoning effort are documented. Some responses are produced in isolated CLI sessions containing up to eight items; those items share a context despite the instruction to solve independently. Other responses come from persistent Codex subagents. The three self-consistency paths have separate workers or isolated sessions, and the CoVe verifier runs after initial responses are fixed. Prompt-level compliance and context independence within sessions are not independently verifiable from public files. Methods cover different task matrices; compare each method with its matched control cells.

The first ten path-1 self-consistency responses came from a worker that had previously answered some Normalize Then Solve prompts on overlapping items. Path 2 and path 3 had independent CLI sessions; no worker saw another self-consistency path's responses. This limited cross-method carryover should be considered when interpreting the self-consistency result.

Scoring retains the prior operational normalizers for comparability: FOL takes the last `TRUE`/`FALSE` token, Number Series takes the last integer, and Blood Relation accepts equivalent digit and word counts. The Direction Sense normalizer collapses `KM`, `M`, and `BLOCKS` to one numeric form and accepts a matching direction when either side lacks a distance. That inherited behavior can inflate Direction accuracy and affect self-consistency votes or CoVe change metrics.
