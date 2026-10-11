# GPT Sol 5.6 High: Assigned Mitigation Experiments on 50 Items

This package evaluates the three prompt-mitigation experiments explicitly
assigned by the supervisors on the fixed 50-question-per-task LogiQAte sample.
The evaluated model is `gpt-5.6-sol` at high reasoning effort, run through a
Codex agent queue with each item assigned its own self-contained prompt.

## Conditions

1. [Obfuscated-to-obfuscated few-shot](01_obf_to_obf_few_shot/) (`k = 2`)
2. [Base-to-obfuscated paired few-shot](02_base_to_obf_paired_few_shot/) (`k = 2` linked pairs)
3. [Analogical prompting](03_analogical_prompting/) with a self-generated analogy

Each condition contains 250 targets: 50 FOL, 50 Blood Relation L1, 50 Blood
Relation L2, 50 Number Series and 50 Direction Sense. Demonstrations are
deterministically selected outside the 50 test IDs, so there is no overlap.

A fresh matched zero-shot control contains all 450 clean and obfuscated forms.
It is generated and answered in the same run so the model identity, reasoning
effort and execution protocol match the three mitigation conditions.

## Layout

```text
Dataset/        public prompts; no gold answers
Result/         append-only agent answers and zero-shot control responses
Analysis/       aggregate scores and comparison tables
notebooks/      executed review notebooks
prompts/        versioned templates
src/            preparation, scoring and notebook generation
tests/          publication and completeness checks
```

Private answer keys and row-level scored evidence are deliberately excluded.
Only aggregates are published. The queue workers must not inspect another
model's outputs, an answer key, or the analysis directory while answering.

The completed [Tier-1 extension](../tier1/) evaluates all seven Tier-1 methods
on the same fixed sample. It contains 2,250 scored evaluation units backed by
3,600 raw generations. Chain of Thought scored 176/250 (70.4%) on the full
obfuscated matrix, compared with 163/250 (65.2%) for the matched zero-shot
control. See the Tier-1 README for the different method matrices and the
limitations on direct cross-method comparisons.

## Model-identity limitation

This is an agent-runtime evaluation, not an OpenAI API Batch run. The runtime
fixes the `gpt-5.6-sol` alias and high reasoning effort, but does not expose a
dated model snapshot, provider response IDs, sampling controls or token-usage
telemetry. `run_provenance.json` records this boundary and hashes every frozen
prompt CSV. Results must be described as a Codex agent run, not as a
snapshot-pinned OpenAI API evaluation. Like the repository's earlier agent
runs, one persistent worker processes multiple independent rows.

Additional interpretation limits:

- batching and persistent workers do not technically enforce context isolation;
  the control is ordered by task/item/variant, so prior rows can prime later
  variants despite the instruction to treat rows independently;
- only submitted final answers are retained, so Analogical Prompting measures
  outcome effects but does not provide process-level evidence that every
  analogy was articulated;
- the frozen source text contains inherited `Â°` mojibake in some Direction
  Sense prompts; it was not changed after inference;
- both deterministic Number Series demonstrations happen to come from block 3,
  while the test set spans blocks 1/2/3; this is recorded in the manifest and
  should be considered when interpreting that task.

## Commands

Preparation requires the private source workspace and is shown for audit:

```powershell
python src/prepare.py --source-root "<private ObusQFate workspace>"
```

Run one condition:

```powershell
python run_queue.py status --condition obf_to_obf_few_shot
python run_queue.py next --condition obf_to_obf_few_shot
python run_queue.py answer RESPONSE_ID --response "FINAL ANSWER"
```

After all four queues resolve (one control and three mitigations), score
privately and validate the public package:

```powershell
python src/score.py --source-root "<private ObusQFate workspace>"
python src/make_notebooks.py
python -m pytest tests -q
```
