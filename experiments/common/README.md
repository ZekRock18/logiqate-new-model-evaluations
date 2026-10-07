# Shared Protocol and Public Artifacts

These files support all ten mitigation methods.

## Zero-shot control

The zero-shot control used the same 15 item IDs per task and evaluated every base and obfuscated form. It scored **62/135 (45.93%)**.

| Task | Variant | Correct | Accuracy |
| --- | --- | ---: | ---: |
| Blood Relation | base | 9/15 | 60.00% |
| Blood Relation | obfuscation_l1 | 8/15 | 53.33% |
| Blood Relation | obfuscation_l2 | 6/15 | 40.00% |
| Direction Sense | base | 6/15 | 40.00% |
| Direction Sense | obfuscation | 4/15 | 26.67% |
| FOL | base | 11/15 | 73.33% |
| FOL | obfuscation | 5/15 | 33.33% |
| Number Series | base | 11/15 | 73.33% |
| Number Series | obfuscation | 2/15 | 13.33% |

## Contents

- `data/sample_manifest.json` — public item IDs, variants and disjoint demonstration IDs; no answers.
- `prompts/prompt_templates.json` — frozen prompt version `v2`.
- `notebooks/` — executed preparation, zero-shot and scoring notebooks.
- `results/` — aggregate report and machine-readable tables only.
- `src/` and `tests/` — implementation and validation code.
- `requirements.txt` — pinned Python dependencies.

## Reproducibility notes

The original inference workspace also contained a private scoring manifest and append-only raw provider transcripts. They are deliberately not published here. The source references those local inputs for full reruns; this public package is sufficient to audit the protocol, prompts, notebooks and aggregate results without releasing private answer material.
