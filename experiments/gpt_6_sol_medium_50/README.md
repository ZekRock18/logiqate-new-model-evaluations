# GPT-6 Sol (medium) — 50-question study

This is a fresh rerun on the same fixed 50-question-per-task sample used for GPT-5.6. It includes a matched zero-shot control, the three assigned prompting experiments, and all seven Tier-1 methods: 4,800 raw model responses and 3,450 scored evaluation units.

## Where to start

- [Assigned experiments](assigned/README.md): on 250 shared obfuscated targets, the control scored 64.0%, obfuscated few-shot 64.4%, paired few-shot 61.6%, and analogical prompting 48.4%.
- [Tier-1 methods](tier1/README.md): seven additional approaches with their own applicable task matrices. Explicit Task Instructions gained 11 points over matched control on its 100 obfuscated targets; Chain of Thought gained 0.4 points on 250.
- [Assigned results](assigned/Analysis/REPORT.md) and [Tier-1 results](tier1/Analysis/REPORT.md) contain the aggregate tables.

The two package folders retain public prompts, responses, executed notebooks, code, manifests, and publication audits. Their method folders point to the exact files without copying large CSVs into multiple places. Gold answers and row-level correctness labels remain private.

Results are descriptive. Some items shared a Codex CLI batch context, and a small set of self-consistency path-1 responses had cross-method context carryover. The runtime did not expose a dated model snapshot, sampling settings, request IDs, or token telemetry. Read the package READMEs before making model-to-model claims.
