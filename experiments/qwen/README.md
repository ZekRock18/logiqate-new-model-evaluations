# Qwen — available 250-question methods

This folder preserves four supplied Qwen method runs. Each method folder contains its original notebook, response-level result CSV, and summary CSV:

1. [Normalize then solve](01_normalize_then_solve/)
2. [Structured decomposition](02_structured_decomposition/)
3. [Explicit task instructions](03_explicit_task_instructions/)
4. [Chain of thought](04_chain_of_thought/)

The exact model/provider settings should be checked in the notebooks; they are not standardized into the GPT/DeepSeek protocol here. Three other Tier-1 methods and the assigned prompting experiments are not present in this folder. A separately supplied [obfuscated-250 run](../qwen_obfuscated_250/) is preserved as its own release rather than silently merged.
