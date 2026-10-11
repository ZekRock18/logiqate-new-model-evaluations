# GPT-5.6 Sol (high) — 50-question study

This model was evaluated on a fixed sample of 50 questions per task. The run includes a fresh zero-shot control, three assigned prompting experiments, and seven Tier-1 methods. In total, it records 4,800 model responses and 3,450 scored evaluation units.

## Where to start

- [Assigned experiments](assigned/README.md): the control and the three mitigation prompts. On the same 250 obfuscated targets, control scored 65.2%; all three mitigation conditions scored below it.
- [Tier-1 methods](tier1/README.md): seven further approaches, including three-path self-consistency and two-pass CoVe. Chain of Thought scored 70.4% on 250 obfuscated targets, 5.2 points above matched control.
- [Assigned results](assigned/Analysis/REPORT.md) and [Tier-1 results](tier1/Analysis/REPORT.md) give the complete aggregate tables.

The assigned and Tier-1 folders are separately runnable packages. Each keeps its public prompts, responses, notebooks, scripts, manifests, and audits together; method folders inside them are short guides linking to the exact artifacts without making duplicate copies. The private answer key and row-level correctness evidence are outside this repository.

This is a Codex agent-runtime run at high reasoning effort, not a snapshot-pinned API benchmark. Its dated model snapshot, temperature, seed, request IDs, and token telemetry were unavailable. Consult each package's provenance before comparing this run with another model.
