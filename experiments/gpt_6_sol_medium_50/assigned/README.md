# GPT-6 Sol (medium), fixed 50-question experiment

This package repeats the assigned prompting experiments and seven Tier-1 methods on the same fixed 50 questions per task used by the [GPT-5.6 study](../../gpt_5_6_sol_high_50/). It is a new model run with freshly generated responses. The public dataset includes prompts and metadata, but no gold labels.

The four assigned queues are `zero_shot_control` (450 responses), `obf_to_obf_few_shot` (250), `base_to_obf_paired_few_shot` (250), and `analogical_prompting` (250). The control is fresh for this model and is required for matched comparisons. The three treatment queues cover obfuscated variants; the control also covers base variants.

For a reader-friendly route through the treatments, see [obfuscated few-shot](01_obf_to_obf_few_shot/), [paired few-shot](02_base_to_obf_paired_few_shot/), and [analogical prompting](03_analogical_prompting/). Each guide links to its exact prompt, response, notebook, and score files.

Each queue is run with `gpt-6-sol` at medium reasoning effort. The public `Dataset/` prompt field is the sole model input. Responses are generated through both Codex subagents and isolated Codex CLI sessions, then committed to the existing append-only answer journals. CLI sessions process at most eight items together and keep separate queues and self-consistency paths in separate sessions. [START.md](START.md) documents manual queue use. The source split, demonstration IDs, queue counts, and prompt hashes are in `sample_manifest.json` and `run_provenance.json`.

The new prompts match the earlier GPT-5.6 run exactly in all 13 initially prepared queues. CLI batches share context among their items, and persistent subagents can retain earlier rows in context. This is a model-setting comparison under related but not perfectly isolated runtime conditions. The runtime does not expose temperature, seed, dated model snapshot, request IDs, or token telemetry.

For assigned conditions, the queue stores the model's final `FINAL_ANSWER` line. In particular, Analogical Prompting asks the model to articulate an analogy, but the multi-line process text from CLI sessions is not retained in the public result CSV. The reported accuracy measures the final answer, not independently verified analogy quality.

All 1,200 assigned responses are complete. On the same 250 obfuscated targets, the fresh zero-shot control scored 160/250 (64.0%); obfuscated few-shot scored 161/250 (64.4%, +0.4 points), paired base-to-obfuscated few-shot scored 154/250 (61.6%, -2.4 points), and analogical prompting scored 121/250 (48.4%, -15.6 points). See [the full report](Analysis/REPORT.md), executed notebooks, and `PUBLICATION_AUDIT.json`. The small +0.4-point result is descriptive, not evidence of a robust improvement.

Scoring uses the private answer file outside this repository. To reproduce the aggregate outputs after collecting responses, run `src/score.py --source-root PATH_TO_OBUSQFATE`, `src/make_notebooks.py`, and `src/publication_audit.py`.

The completed [Tier 1 package](../tier1/README.md) contains 3,600 additional model responses across seven methods. CoVe verification prompts were built from this run's 450 initial CoVe responses.
