# Prompt-Mitigation Results

Model: `deepseek-ai/DeepSeek-V4.1-Flash`. Completed 1035/1035 evaluation units; missing: 0.

## Accuracy by condition, task and variant

| Condition | Task | Variant | Correct | Accuracy | Failures |
| --- | --- | --- | --- | --- | --- |
| zero_shot_control | Blood Relation | base | 9/15 | 60.00% | 0 |
| zero_shot_control | Blood Relation | obfuscation_l1 | 8/15 | 53.33% | 0 |
| zero_shot_control | Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 0 |
| zero_shot_control | Direction Sense | base | 6/15 | 40.00% | 0 |
| zero_shot_control | Direction Sense | obfuscation | 4/15 | 26.67% | 0 |
| zero_shot_control | FOL | base | 11/15 | 73.33% | 0 |
| zero_shot_control | FOL | obfuscation | 5/15 | 33.33% | 0 |
| zero_shot_control | Number Series | base | 11/15 | 73.33% | 0 |
| zero_shot_control | Number Series | obfuscation | 2/15 | 13.33% | 0 |
| obf_to_obf_few_shot | Blood Relation | obfuscation_l1 | 5/15 | 33.33% | 0 |
| obf_to_obf_few_shot | Blood Relation | obfuscation_l2 | 5/15 | 33.33% | 0 |
| obf_to_obf_few_shot | Direction Sense | obfuscation | 5/15 | 33.33% | 0 |
| obf_to_obf_few_shot | FOL | obfuscation | 10/15 | 66.67% | 0 |
| obf_to_obf_few_shot | Number Series | obfuscation | 1/15 | 6.67% | 0 |
| base_to_obf_paired_few_shot | Blood Relation | obfuscation_l1 | 6/15 | 40.00% | 0 |
| base_to_obf_paired_few_shot | Blood Relation | obfuscation_l2 | 4/15 | 26.67% | 0 |
| base_to_obf_paired_few_shot | Direction Sense | obfuscation | 5/15 | 33.33% | 0 |
| base_to_obf_paired_few_shot | FOL | obfuscation | 10/15 | 66.67% | 0 |
| base_to_obf_paired_few_shot | Number Series | obfuscation | 1/15 | 6.67% | 0 |
| analogical_prompting | Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 0 |
| analogical_prompting | Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 0 |
| analogical_prompting | Direction Sense | obfuscation | 6/15 | 40.00% | 0 |
| analogical_prompting | FOL | obfuscation | 6/15 | 40.00% | 0 |
| analogical_prompting | Number Series | obfuscation | 3/15 | 20.00% | 0 |
| normalize_then_solve | Blood Relation | base | 10/15 | 66.67% | 0 |
| normalize_then_solve | Blood Relation | obfuscation_l1 | 7/15 | 46.67% | 0 |
| normalize_then_solve | Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 0 |
| normalize_then_solve | FOL | base | 12/15 | 80.00% | 0 |
| normalize_then_solve | FOL | obfuscation | 6/15 | 40.00% | 0 |
| structured_decomposition | Blood Relation | base | 10/15 | 66.67% | 0 |
| structured_decomposition | Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 0 |
| structured_decomposition | Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 0 |
| structured_decomposition | Direction Sense | base | 8/15 | 53.33% | 0 |
| structured_decomposition | Direction Sense | obfuscation | 8/15 | 53.33% | 0 |
| explicit_task_instructions | Direction Sense | base | 8/15 | 53.33% | 0 |
| explicit_task_instructions | Direction Sense | obfuscation | 9/15 | 60.00% | 0 |
| explicit_task_instructions | Number Series | base | 13/15 | 86.67% | 0 |
| explicit_task_instructions | Number Series | obfuscation | 5/15 | 33.33% | 3 |
| chain_of_thought | Blood Relation | base | 10/15 | 66.67% | 0 |
| chain_of_thought | Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 0 |
| chain_of_thought | Blood Relation | obfuscation_l2 | 4/15 | 26.67% | 0 |
| chain_of_thought | Direction Sense | base | 7/15 | 46.67% | 0 |
| chain_of_thought | Direction Sense | obfuscation | 7/15 | 46.67% | 0 |
| chain_of_thought | FOL | base | 12/15 | 80.00% | 0 |
| chain_of_thought | FOL | obfuscation | 9/15 | 60.00% | 0 |
| chain_of_thought | Number Series | base | 12/15 | 80.00% | 1 |
| chain_of_thought | Number Series | obfuscation | 4/15 | 26.67% | 2 |
| rereading_s2a | Blood Relation | base | 11/15 | 73.33% | 0 |
| rereading_s2a | Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 0 |
| rereading_s2a | FOL | base | 13/15 | 86.67% | 0 |
| rereading_s2a | FOL | obfuscation | 7/15 | 46.67% | 0 |
| self_consistency | Blood Relation | base | 10/15 | 66.67% | 2 |
| self_consistency | Blood Relation | obfuscation_l1 | 9/15 | 60.00% | 3 |
| self_consistency | Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 5 |
| self_consistency | Direction Sense | base | 11/15 | 73.33% | 0 |
| self_consistency | Direction Sense | obfuscation | 11/15 | 73.33% | 1 |
| self_consistency | FOL | base | 13/15 | 86.67% | 0 |
| self_consistency | FOL | obfuscation | 8/15 | 53.33% | 0 |
| self_consistency | Number Series | base | 12/15 | 80.00% | 2 |
| self_consistency | Number Series | obfuscation | 4/15 | 26.67% | 7 |
| self_verification_cove | Blood Relation | base | 11/15 | 73.33% | 0 |
| self_verification_cove | Blood Relation | obfuscation_l1 | 7/15 | 46.67% | 0 |
| self_verification_cove | Blood Relation | obfuscation_l2 | 6/15 | 40.00% | 0 |
| self_verification_cove | Direction Sense | base | 8/15 | 53.33% | 0 |
| self_verification_cove | Direction Sense | obfuscation | 8/15 | 53.33% | 0 |
| self_verification_cove | FOL | base | 13/15 | 86.67% | 0 |
| self_verification_cove | FOL | obfuscation | 7/15 | 46.67% | 0 |
| self_verification_cove | Number Series | base | 12/15 | 80.00% | 0 |
| self_verification_cove | Number Series | obfuscation | 1/15 | 6.67% | 0 |

## Three assigned experiments versus zero-shot obfuscated control

| Condition | Task | Variant | Method | Control | Improvement |
| --- | --- | --- | --- | --- | --- |
| obf_to_obf_few_shot | FOL | obfuscation | 10/15 (66.67%) | 5/15 (33.33%) | +33.33 pp |
| obf_to_obf_few_shot | Blood Relation | obfuscation_l1 | 5/15 (33.33%) | 8/15 (53.33%) | -20.00 pp |
| obf_to_obf_few_shot | Blood Relation | obfuscation_l2 | 5/15 (33.33%) | 6/15 (40.00%) | -6.67 pp |
| obf_to_obf_few_shot | Number Series | obfuscation | 1/15 (6.67%) | 2/15 (13.33%) | -6.67 pp |
| obf_to_obf_few_shot | Direction Sense | obfuscation | 5/15 (33.33%) | 4/15 (26.67%) | +6.67 pp |
| base_to_obf_paired_few_shot | FOL | obfuscation | 10/15 (66.67%) | 5/15 (33.33%) | +33.33 pp |
| base_to_obf_paired_few_shot | Blood Relation | obfuscation_l1 | 6/15 (40.00%) | 8/15 (53.33%) | -13.33 pp |
| base_to_obf_paired_few_shot | Blood Relation | obfuscation_l2 | 4/15 (26.67%) | 6/15 (40.00%) | -13.33 pp |
| base_to_obf_paired_few_shot | Number Series | obfuscation | 1/15 (6.67%) | 2/15 (13.33%) | -6.67 pp |
| base_to_obf_paired_few_shot | Direction Sense | obfuscation | 5/15 (33.33%) | 4/15 (26.67%) | +6.67 pp |
| analogical_prompting | FOL | obfuscation | 6/15 (40.00%) | 5/15 (33.33%) | +6.67 pp |
| analogical_prompting | Blood Relation | obfuscation_l1 | 9/15 (60.00%) | 8/15 (53.33%) | +6.67 pp |
| analogical_prompting | Blood Relation | obfuscation_l2 | 6/15 (40.00%) | 6/15 (40.00%) | +0.00 pp |
| analogical_prompting | Number Series | obfuscation | 3/15 (20.00%) | 2/15 (13.33%) | +6.67 pp |
| analogical_prompting | Direction Sense | obfuscation | 6/15 (40.00%) | 4/15 (26.67%) | +13.33 pp |

## Base-to-obfuscated gaps

| Condition | Task | Variant | Base source | Base | Obfuscated | Absolute gap |
| --- | --- | --- | --- | --- | --- | --- |
| zero_shot_control | FOL | obfuscation | zero_shot_control | 11/15 (73.33%) | 5/15 (33.33%) | 40.00 pp |
| zero_shot_control | Blood Relation | obfuscation_l1 | zero_shot_control | 9/15 (60.00%) | 8/15 (53.33%) | 6.67 pp |
| zero_shot_control | Blood Relation | obfuscation_l2 | zero_shot_control | 9/15 (60.00%) | 6/15 (40.00%) | 20.00 pp |
| zero_shot_control | Number Series | obfuscation | zero_shot_control | 11/15 (73.33%) | 2/15 (13.33%) | 60.00 pp |
| zero_shot_control | Direction Sense | obfuscation | zero_shot_control | 6/15 (40.00%) | 4/15 (26.67%) | 13.33 pp |
| obf_to_obf_few_shot | FOL | obfuscation | zero_shot_control | 11/15 (73.33%) | 10/15 (66.67%) | 6.67 pp |
| obf_to_obf_few_shot | Blood Relation | obfuscation_l1 | zero_shot_control | 9/15 (60.00%) | 5/15 (33.33%) | 26.67 pp |
| obf_to_obf_few_shot | Blood Relation | obfuscation_l2 | zero_shot_control | 9/15 (60.00%) | 5/15 (33.33%) | 26.67 pp |
| obf_to_obf_few_shot | Number Series | obfuscation | zero_shot_control | 11/15 (73.33%) | 1/15 (6.67%) | 66.67 pp |
| obf_to_obf_few_shot | Direction Sense | obfuscation | zero_shot_control | 6/15 (40.00%) | 5/15 (33.33%) | 6.67 pp |
| base_to_obf_paired_few_shot | FOL | obfuscation | zero_shot_control | 11/15 (73.33%) | 10/15 (66.67%) | 6.67 pp |
| base_to_obf_paired_few_shot | Blood Relation | obfuscation_l1 | zero_shot_control | 9/15 (60.00%) | 6/15 (40.00%) | 20.00 pp |
| base_to_obf_paired_few_shot | Blood Relation | obfuscation_l2 | zero_shot_control | 9/15 (60.00%) | 4/15 (26.67%) | 33.33 pp |
| base_to_obf_paired_few_shot | Number Series | obfuscation | zero_shot_control | 11/15 (73.33%) | 1/15 (6.67%) | 66.67 pp |
| base_to_obf_paired_few_shot | Direction Sense | obfuscation | zero_shot_control | 6/15 (40.00%) | 5/15 (33.33%) | 6.67 pp |
| analogical_prompting | FOL | obfuscation | zero_shot_control | 11/15 (73.33%) | 6/15 (40.00%) | 33.33 pp |
| analogical_prompting | Blood Relation | obfuscation_l1 | zero_shot_control | 9/15 (60.00%) | 9/15 (60.00%) | 0.00 pp |
| analogical_prompting | Blood Relation | obfuscation_l2 | zero_shot_control | 9/15 (60.00%) | 6/15 (40.00%) | 20.00 pp |
| analogical_prompting | Number Series | obfuscation | zero_shot_control | 11/15 (73.33%) | 3/15 (20.00%) | 53.33 pp |
| analogical_prompting | Direction Sense | obfuscation | zero_shot_control | 6/15 (40.00%) | 6/15 (40.00%) | 0.00 pp |
| normalize_then_solve | FOL | obfuscation | normalize_then_solve | 12/15 (80.00%) | 6/15 (40.00%) | 40.00 pp |
| normalize_then_solve | Blood Relation | obfuscation_l1 | normalize_then_solve | 10/15 (66.67%) | 7/15 (46.67%) | 20.00 pp |
| normalize_then_solve | Blood Relation | obfuscation_l2 | normalize_then_solve | 10/15 (66.67%) | 6/15 (40.00%) | 26.67 pp |
| structured_decomposition | Blood Relation | obfuscation_l1 | structured_decomposition | 10/15 (66.67%) | 9/15 (60.00%) | 6.67 pp |
| structured_decomposition | Blood Relation | obfuscation_l2 | structured_decomposition | 10/15 (66.67%) | 6/15 (40.00%) | 26.67 pp |
| structured_decomposition | Direction Sense | obfuscation | structured_decomposition | 8/15 (53.33%) | 8/15 (53.33%) | 0.00 pp |
| explicit_task_instructions | Number Series | obfuscation | explicit_task_instructions | 13/15 (86.67%) | 5/15 (33.33%) | 53.33 pp |
| explicit_task_instructions | Direction Sense | obfuscation | explicit_task_instructions | 8/15 (53.33%) | 9/15 (60.00%) | 6.67 pp |
| chain_of_thought | FOL | obfuscation | chain_of_thought | 12/15 (80.00%) | 9/15 (60.00%) | 20.00 pp |
| chain_of_thought | Blood Relation | obfuscation_l1 | chain_of_thought | 10/15 (66.67%) | 9/15 (60.00%) | 6.67 pp |
| chain_of_thought | Blood Relation | obfuscation_l2 | chain_of_thought | 10/15 (66.67%) | 4/15 (26.67%) | 40.00 pp |
| chain_of_thought | Number Series | obfuscation | chain_of_thought | 12/15 (80.00%) | 4/15 (26.67%) | 53.33 pp |
| chain_of_thought | Direction Sense | obfuscation | chain_of_thought | 7/15 (46.67%) | 7/15 (46.67%) | 0.00 pp |
| rereading_s2a | FOL | obfuscation | rereading_s2a | 13/15 (86.67%) | 7/15 (46.67%) | 40.00 pp |
| rereading_s2a | Blood Relation | obfuscation_l2 | rereading_s2a | 11/15 (73.33%) | 6/15 (40.00%) | 33.33 pp |
| self_consistency | FOL | obfuscation | self_consistency | 13/15 (86.67%) | 8/15 (53.33%) | 33.33 pp |
| self_consistency | Blood Relation | obfuscation_l1 | self_consistency | 10/15 (66.67%) | 9/15 (60.00%) | 6.67 pp |
| self_consistency | Blood Relation | obfuscation_l2 | self_consistency | 10/15 (66.67%) | 6/15 (40.00%) | 26.67 pp |
| self_consistency | Number Series | obfuscation | self_consistency | 12/15 (80.00%) | 4/15 (26.67%) | 53.33 pp |
| self_consistency | Direction Sense | obfuscation | self_consistency | 11/15 (73.33%) | 11/15 (73.33%) | 0.00 pp |
| self_verification_cove | FOL | obfuscation | self_verification_cove | 13/15 (86.67%) | 7/15 (46.67%) | 40.00 pp |
| self_verification_cove | Blood Relation | obfuscation_l1 | self_verification_cove | 11/15 (73.33%) | 7/15 (46.67%) | 26.67 pp |
| self_verification_cove | Blood Relation | obfuscation_l2 | self_verification_cove | 11/15 (73.33%) | 6/15 (40.00%) | 33.33 pp |
| self_verification_cove | Number Series | obfuscation | self_verification_cove | 12/15 (80.00%) | 1/15 (6.67%) | 73.33 pp |
| self_verification_cove | Direction Sense | obfuscation | self_verification_cove | 8/15 (53.33%) | 8/15 (53.33%) | 0.00 pp |

## Run audit

- Response/parsing/consensus failures: 26.
- Provider usage: 1440 calls, 630811 total tokens, estimated cost $0.176515.
- Selected non-equivalent Number Series test IDs: [].
- Self-consistency agreement rate: 85.19%.
- CoVe changed 18 answers; corrected 1 and harmed 11.
- This is a 15-item-per-task pilot. Report raw counts with percentages and avoid treating small differences as stable effects.
