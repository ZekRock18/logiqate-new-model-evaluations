# Model experiments

Start with a model folder, then open the method you want to inspect. A method guide links directly to its inputs, recorded responses, notebook, and scored output. Model-level `assigned/` and `tier1/` packages keep shared controls, manifests, code, and audits together so the runs remain reproducible without duplicating large CSVs.

## Cross-model summary tables

- [Zero-shot results across all models](zero_shot_results.md) — obfuscated-variant accuracy by task, model, and overall.
- [Mitigation technique results across all models](mitigation_results.md) — assigned and Tier-1 methods on obfuscated variants, with matched zero-shot controls.

| Model run | Sample and available work | Start here |
| --- | --- | --- |
| DeepSeek-V4.1-Flash | 15-question pilot; three assigned prompts and seven Tier-1 methods | [DeepSeek guide](deepseek_v4_1_flash_15/) |
| GPT-5.6 Sol, high | 50-question study; control, three assigned prompts, seven Tier-1 methods | [GPT-5.6 guide](gpt_5_6_sol_high_50/) |
| GPT-6 Sol, medium | 50-question study; control, three assigned prompts, seven Tier-1 methods | [GPT-6 guide](gpt_6_sol_medium_50/) |
| Llama 3.1 via Ollama | Three supplied Tier-1 methods | [Llama guide](llama/) |
| Phi-4 via Ollama | Three supplied Tier-1 methods | [Phi guide](phi/) |
| Qwen | Four supplied methods | [Qwen guide](qwen/) |
| Qwen, obfuscated 250 | Four supplied methods in a separate release | [Qwen obfuscated guide](qwen_obfuscated_250/) |

The seven Tier-1 methods are Normalize Then Solve, Structured Decomposition, Explicit Task Instructions, Chain of Thought, Re-reading/System 2 Attention, Self-Consistency, and Self-Verification/CoVe. The three assigned methods are Obfuscated-to-Obfuscated Few-Shot, Base-to-Obfuscated Paired Few-Shot, and Analogical Prompting. A folder lists only methods for which files actually exist; an absent method is not a zero score.

## Reading results responsibly

Compare a method with its fresh zero-shot control on the **same items and variants**. Methods do not all cover the same task matrix, and the DeepSeek pilot has 15 rather than 50 questions per task. The GPT runs used Codex model aliases; dated snapshots and sampling parameters were unavailable. Each model guide links to its specific caveats and provenance.

Public results intentionally exclude credentials, private answer keys, and row-level correctness labels. Raw responses are published where available, along with aggregate scores and notebook/code artifacts needed to understand the run. The [project wiki](../wiki/Home.md) describes the study protocol and broader paper context.
