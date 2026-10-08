# Three Assigned Experiments

## Experiment 1: Obfuscated-to-Obfuscated Few-Shot

Two solved obfuscated demonstrations precede a new obfuscated target. It tests
whether exposure to the obfuscated input distribution alone improves
robustness. [Documentation and artifacts](../experiments/experiment_1_obf_to_obf_few_shot/README.md)

## Experiment 2: Base-to-Obfuscated Paired Few-Shot

Each demonstration links a clean problem to its equivalent obfuscated form and
shows the shared answer. It tests whether explicit invariance demonstrations
improve transfer. [Documentation and artifacts](../experiments/experiment_2_base_to_obf_paired_few_shot/README.md)

## Experiment 3: Analogical Prompting

The model is instructed to identify the underlying clean reasoning pattern and
solve the obfuscated target by analogy. [Documentation and artifacts](../experiments/experiment_3_analogical_prompting/README.md)

On the common 75 obfuscated inputs, the zero-shot control scored 25/75.
Experiments 1 and 2 each scored 26/75, and Experiment 3 scored 30/75.
