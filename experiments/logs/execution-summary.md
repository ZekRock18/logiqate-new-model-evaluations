# Execution Summary

## Final production run

- Provider: DeepInfra, OpenAI-compatible Chat Completions API.
- Model: `deepseek-ai/DeepSeek-V4.1-Flash`.
- Prompt version: `v2`.
- Expected and completed evaluation units: 1,035/1,035.
- API calls: 1,440.
- Prompt tokens: 298,609.
- Completion tokens: 332,202.
- Total tokens: 630,811.
- Provider-estimated cost: USD 0.176515.
- Provider transport failures: 0.
- Final-marker parse failures retained as wrong: 6.
- Self-consistency `NO_CONSENSUS` outcomes retained as wrong: 20.
- Answered outcomes: 1,009.

## Special-method audit

- Self-consistency evaluated 135 units: 82 unanimous votes, 33 majority votes and 20 without consensus. Agreement rate: 85.1852%.
- Self-verification/CoVe evaluated 135 units and changed 18 final answers. It changed 1 incorrect answer to correct and 11 correct answers to incorrect.
- No selected Number Series test ID was among the known non-equivalent transformations.

The aggregate tables in [`../common/results/`](../common/results/) retain every
failure in the denominator.
