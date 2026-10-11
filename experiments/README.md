# Prompt-Mitigation Experiments

This directory contains the prompt-level mitigation study for LogiQAte using `deepseek-ai/DeepSeek-V4.1-Flash` through DeepInfra.

## GPT Sol full-50 assigned experiments

[`gpt_sol_6_medium_full_50/`](gpt_sol_6_medium_full_50/) repeats the assigned
experiments and [seven Tier-1 methods](gpt_sol_6_medium_full_50/Tier1/) on the
fixed 50-item sample with `gpt-6-sol` at medium reasoning effort. The run has
4,800 fresh raw responses and 3,450 scored evaluations. On the 250 common
obfuscated targets, the fresh control scored 160/250 (64.0%), obfuscated
few-shot 161/250 (64.4%), paired few-shot 154/250 (61.6%), and analogical
prompting 121/250 (48.4%). The package includes raw responses, executed
notebooks, analysis, tests, and publication audits. See its caveats on CLI
batch context and unavailable sampling metadata before comparing models.

[`gpt_sol_5.6_high_assigned_50/`](gpt_sol_5.6_high_assigned_50/) expands the
three assigned methods to 50 questions per task with `gpt-5.6-sol` at high
reasoning effort. It contains 1,200 fresh responses, including a 450-response
matched control. On the common 250 obfuscated targets, the corrected control
scored 163/250 (65.2%); obfuscated few-shot scored 150/250 (60.0%), paired few-shot
153/250 (61.2%), and analogical prompting 150/250 (60.0%). The package records
the agent-runtime and context-isolation limitations needed to interpret these
results.

The package's [`Tier1/`](gpt_sol_5.6_high_assigned_50/Tier1/) extension runs all
seven Tier-1 methods on their full 50-item matrices: 2,250 scored evaluations
and 3,600 raw generations. Chain of Thought was the strongest method evaluated
on all 250 obfuscated targets at 176/250 (70.4%), a +5.2-point change from the
matched zero-shot control. The extension includes all raw responses, executed
notebooks, aggregates, tests and a publication audit.

## Scope

- 15 deterministic test questions per task, seed `20261006`.
- FOL, Blood Relation L1/L2, Number Series and Direction Sense.
- Three explicitly assigned experiments and seven Tier 1 prompting methods.
- A matched zero-shot control on the same item IDs.
- Prompt version `v2`; ordinary calls at temperature 0; self-consistency uses three paths at temperature 0.7.

## Completion audit

- 1,035/1,035 evaluation units completed.
- 1440/1,440 expected API calls recorded.
- Zero provider transport failures.
- 6 final-marker parse failures and 20 `NO_CONSENSUS` outcomes retained as wrong.
- 630,811 total tokens; provider-estimated cost USD 0.176515.
- All 13 notebooks executed without errors; 8 validation tests passed.

## Three assigned experiments

1. [Obfuscated-to-Obfuscated Few-Shot](experiment_1_obf_to_obf_few_shot/)
2. [Base-to-Obfuscated Paired Few-Shot](experiment_2_base_to_obf_paired_few_shot/)
3. [Analogical Prompting](experiment_3_analogical_prompting/)

On the common 75 obfuscated inputs, the zero-shot control scored 25/75. Experiments 1 and 2 each scored 26/75; Experiment 3 scored 30/75.

## Seven Tier 1 methods

1. [Normalize Then Solve](seven_tier_methods/01_normalize_then_solve/)
2. [Structured Decomposition](seven_tier_methods/02_structured_decomposition/)
3. [Explicit Task Instructions](seven_tier_methods/03_explicit_task_instructions/)
4. [Chain of Thought](seven_tier_methods/04_chain_of_thought/)
5. [Re-reading / System 2 Attention](seven_tier_methods/05_rereading_s2a/)
6. [Self-Consistency](seven_tier_methods/06_self_consistency/)
7. [Self-Verification / CoVe](seven_tier_methods/07_self_verification_cove/)

## Shared materials

[`common/`](common/) contains the zero-shot control, protocol, public manifest, versioned templates, aggregate tables, executed preparation/scoring notebooks, implementation source and tests.

[`logs/`](logs/) contains the public execution ledger, completion summary and
validation record. The repository-level [`wiki/`](../wiki/Home.md) indexes all
documentation and artifacts.

## Public-release boundary

This package intentionally excludes API credentials, private scoring manifests, row-level gold-answer files and raw provider transcripts. Aggregate tables retain all failures in their denominators.
