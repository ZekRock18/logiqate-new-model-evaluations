# Evaluated-agent instructions

Run exactly one assigned condition from this directory:

```powershell
python -X utf8 run_queue.py instructions
python -X utf8 run_queue.py status --condition CONDITION
python -X utf8 run_queue.py next --condition CONDITION --count 5
```

For each emitted item, solve only the prompt between `PROMPT_BEGIN` and
`PROMPT_END`, then checkpoint the requested final answer:

```powershell
python -X utf8 run_queue.py answer RESPONSE_ID --response "FINAL ANSWER"
```

Repeat until strict status reports `COMPLETE`. Treat rows independently. Do not
inspect answer keys, analysis files, source datasets, other result folders or
other condition responses. Do not use web search, APIs, helper solvers,
hard-coded mappings or another model. Solved demonstrations inside the emitted
prompt are authorized experimental context.
