# Agent evaluation prompt

You are the model being evaluated on LogiQAte. Work through the queue until it
is complete. The Python file is a queue and checkpoint manager; it does not call
an API and must not be replaced with a regex or heuristic solver.

From this directory, run:

```bash
python -X utf8 run_row_by_row.py instructions
python -X utf8 run_row_by_row.py status
python -X utf8 run_row_by_row.py next
```

For each row:

1. Read the complete text between `PROMPT_BEGIN` and `PROMPT_END`.
2. Solve that one prompt yourself using your own reasoning.
3. Follow the output format requested inside the prompt.
4. Save only the final answer:

   ```bash
   python -X utf8 run_row_by_row.py answer RESPONSE_ID --response "FINAL ANSWER"
   ```

5. Run `next` again and continue. Do not stop merely to report progress.

Rules:

- Treat every row as an independent request.
- Use only the prompt printed by `next`.
- Do not inspect answer keys, prior results, analysis files, or other project
  directories.
- Do not create helper solvers, hard-coded answer maps, bulk answer scripts,
  API calls, web searches, or external decoding tools.
- Never submit a blank, `UNKNOWN`, `ERROR`, `SKIPPED`, `N/A`, a refusal,
  an explanation, or a confidence score. Make a genuine best-effort choice.
- Record answers only through the `answer` command. Never copy Dataset files
  over Result files.
- Do not edit prompts, IDs, row order, Dataset files, Result files, or the queue
  script directly.
- If the session ends, stop cleanly; the next session resumes automatically.

When `next` reports `COMPLETE`, verify the run:

```bash
python -X utf8 run_row_by_row.py status --strict
```

Claim completion only if that command exits successfully.

