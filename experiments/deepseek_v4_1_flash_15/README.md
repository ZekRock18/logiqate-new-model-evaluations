# DeepSeek-V4.1-Flash — 15-question pilot

This is the earlier, smaller prompt-mitigation study. It uses 15 underlying questions per task (75 obfuscated targets), through DeepInfra. Start with the [shared protocol](shared/README.md) for the sample, matched zero-shot control, prompts, implementation, and combined results.

The fresh zero-shot control answered 25/75 obfuscated targets correctly. Obfuscated few-shot and paired few-shot each answered 26/75; analogical prompting answered 30/75. These pilot counts are not directly comparable to the later 50-question GPT runs.

## Assigned prompting experiments

1. [Obfuscated-to-obfuscated few-shot](assigned/01_obf_to_obf_few_shot/README.md)
2. [Base-to-obfuscated paired few-shot](assigned/02_base_to_obf_paired_few_shot/README.md)
3. [Analogical prompting](assigned/03_analogical_prompting/README.md)

The [Tier-1 directory](tier1/README.md) holds all seven additional methods, each with its own notebook, results, and explanation. The [execution record](provenance/README.md) documents the run and validation.

Public files do not include credentials, gold-answer keys, private scoring manifests, or raw provider transcripts. Read the aggregate report before interpreting a percentage: methods cover different task/variant subsets.
