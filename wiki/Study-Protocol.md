# Study Protocol

- Model: `deepseek-ai/DeepSeek-V4.1-Flash` through DeepInfra's OpenAI-compatible Chat Completions API.
- Sample: 15 deterministic test questions per task.
- Tasks: FOL, Blood Relation, Number Series and Direction Sense.
- Variants: base plus each task's applicable obfuscated form; Blood Relation has L1 and L2.
- Control: matched zero-shot evaluation on exactly the same test IDs.
- Demonstrations: two fixed examples per task, disjoint from all test IDs.
- Prompt version: `v2`.
- Decoding: temperature 0 for ordinary calls; self-consistency uses three paths at temperature 0.7.
- Failures: parse failures and no-consensus outcomes remain in the denominator as incorrect.
- Number Series: selected test items exclude the known non-equivalent transformations.

The [public sample manifest](../experiments/common/data/sample_manifest.json)
contains item identifiers and the demonstration/test split without answers. The
[prompt templates](../experiments/common/prompts/prompt_templates.json) are the
frozen prompts used by the run.
