# Prompt-Mitigation Experiments

This directory contains the prompt-level mitigation study for LogiQAte using `deepseek-ai/DeepSeek-V4.1-Flash` through DeepInfra.

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
