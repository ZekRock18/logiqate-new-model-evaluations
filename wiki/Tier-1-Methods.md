# Seven Tier-1 methods in the DeepSeek pilot

1. [Normalize Then Solve](../experiments/deepseek_v4_1_flash_15/tier1/01_normalize_then_solve/README.md) — reconstruct a clean representation before solving.
2. [Structured Decomposition](../experiments/deepseek_v4_1_flash_15/tier1/02_structured_decomposition/README.md) — extract entities, relations and constraints into a fixed structure.
3. [Explicit Task Instructions](../experiments/deepseek_v4_1_flash_15/tier1/03_explicit_task_instructions/README.md) — provide task-specific reasoning instructions.
4. [Chain of Thought](../experiments/deepseek_v4_1_flash_15/tier1/04_chain_of_thought/README.md) — request explicit intermediate reasoning before the final marker.
5. [Re-reading / System 2 Attention](../experiments/deepseek_v4_1_flash_15/tier1/05_rereading_s2a/README.md) — re-read and isolate relevant information before answering.
6. [Self-Consistency](../experiments/deepseek_v4_1_flash_15/tier1/06_self_consistency/README.md) — sample three reasoning paths and use majority agreement.
7. [Self-Verification / CoVe](../experiments/deepseek_v4_1_flash_15/tier1/07_self_verification_cove/README.md) — produce an answer, verify it independently and then finalize.

The [Tier 1 index](../experiments/deepseek_v4_1_flash_15/tier1/README.md) records the
task-to-method mapping and aggregate comparison context.
