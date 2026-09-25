"""Universal agent-driven LogiQAte evaluation queue.

This file does not call an API and does not solve puzzles with regexes. Instead,
any coding agent with terminal access can use it as a durable queue:

    python run_row_by_row.py instructions
    python run_row_by_row.py next
    python run_row_by_row.py answer RESPONSE_ID --response "FINAL ANSWER"
    python run_row_by_row.py status --strict

The coding model reads one prompt from ``next``, reasons about it itself, and
records only its final answer. Every answer is atomically checkpointed in Result.
The same commands work in Claude Code, OpenCode, Codex, Cursor, Cline, Roo Code,
Windsurf, or another coding agent that can run terminal commands.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


sys.dont_write_bytecode = True


def configure_utf8_stdio() -> None:
    """Prevent Windows cp1252 crashes when prompts contain Unicode."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="backslashreplace")
            except (AttributeError, OSError):
                pass


configure_utf8_stdio()
RUN_DIR = Path(__file__).resolve().parent
DATASET_DIR = RUN_DIR / "Dataset"
RESULT_DIR = RUN_DIR / "Result"
JOURNAL_PATH = RESULT_DIR / "_answer_journal.jsonl"
REQUIRED_COLUMNS = ["setting", "row_number", "response_id", "prompt", "model_response"]
VALID_SETTINGS = {"zero_shot", "few_shot", "cot"}
INVALID_PREFIXES = (
    "UNKNOWN",
    "ERROR",
    "SKIPPED",
    "NO_ANSWER",
    "NO ANSWER",
    "N/A",
    "I CANNOT",
    "I CAN'T",
    "UNABLE TO",
)

AGENT_INSTRUCTIONS = """
You are the model being evaluated. Work through the supplied benchmark queue one
item at a time using your own reasoning.

Protocol:
1. Run: python run_row_by_row.py status
2. Run: python run_row_by_row.py next
3. Read the complete prompt printed between PROMPT_BEGIN and PROMPT_END.
4. Solve that single item yourself. Think privately and follow its requested
   output format exactly.
5. Record only the final answer:
   python run_row_by_row.py answer RESPONSE_ID --response "FINAL ANSWER"
6. Repeat steps 2-5 until `next` reports COMPLETE.
7. Finish with: python run_row_by_row.py status --strict

Mandatory evaluation rules:
- Treat every row as an independent model request. Do not carry an answer from
  another row, even when questions look related.
- Do not write or use regex solvers, heuristic solvers, hardcoded answer maps,
  bulk answer-generation scripts, API calls, web searches, or external sources.
- Do not inspect any answer key, analysis file, previous result, or other project
  directory. Use only the prompt printed by `next`.
- Never submit UNKNOWN, ERROR, SKIPPED, N/A, a blank, a refusal, an explanation,
  or a confidence score. Make a genuine best-effort choice and submit only the
  final answer requested by the item.
- Do not modify Dataset, Result, response IDs, prompts, row order, or this script
  except through the `answer` command.
- Never write a fix script that copies Dataset rows over Result. The `answer`
  command maintains an append-only recovery journal and is the only safe way to
  record or replace an answer.
- Continue for as many rows as your current session permits. If the session must
  end, stop cleanly; another session can resume from the next unresolved row.
- Do not claim completion unless `status --strict` exits successfully.
""".strip()


def is_unresolved(value: str | None) -> bool:
    text = str(value or "").strip()
    return not text or text.upper().startswith(INVALID_PREFIXES)


def source_paths(dataset_filter: str | None = None) -> list[Path]:
    paths = sorted(DATASET_DIR.glob("*.csv"))
    if dataset_filter:
        needle = dataset_filter.casefold()
        paths = [path for path in paths if needle in path.name.casefold()]
    if not paths:
        suffix = f" matching {dataset_filter!r}" if dataset_filter else ""
        raise SystemExit(f"No dataset CSV files found in {DATASET_DIR}{suffix}")
    return paths


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValueError(f"{path}: expected {REQUIRED_COLUMNS}, found {reader.fieldnames}")
        rows = list(reader)

    seen: set[str] = set()
    for line_number, row in enumerate(rows, 2):
        if row["setting"] not in VALID_SETTINGS:
            raise ValueError(f"{path}:{line_number}: invalid setting {row['setting']!r}")
        response_id = row["response_id"].strip()
        if not response_id or response_id in seen:
            raise ValueError(f"{path}:{line_number}: missing or duplicate response_id")
        if not row["prompt"].strip():
            raise ValueError(f"{path}:{line_number}: blank prompt")
        seen.add(response_id)
    return rows


def write_csv_atomic(path: Path, rows: list[dict[str, str]]) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def append_journal(record: dict) -> None:
    """Durably record an answer before changing its result CSV."""
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    with JOURNAL_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def journal_answers() -> dict[str, dict]:
    """Return the latest durable answer record for each response ID."""
    latest: dict[str, dict] = {}
    if not JOURNAL_PATH.exists():
        return latest
    with JOURNAL_PATH.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{JOURNAL_PATH}:{line_number}: invalid JSON") from exc
            response_id = str(record.get("response_id", "")).strip()
            answer = str(record.get("answer", "")).strip()
            if not response_id or is_unresolved(answer):
                raise ValueError(f"{JOURNAL_PATH}:{line_number}: invalid answer record")
            latest[response_id] = record
    return latest


def restore_from_journal(filename: str, rows: list[dict[str, str]]) -> int:
    """Make the append-only journal authoritative over stale/blank CSV values."""
    latest = journal_answers()
    restored = 0
    for row in rows:
        record = latest.get(row["response_id"])
        if not record or record.get("dataset_file") != filename:
            continue
        answer = str(record["answer"]).strip()
        if row["model_response"].strip() != answer:
            row["model_response"] = answer
            restored += 1
    return restored


def load_pair(source: Path, create_result: bool) -> tuple[Path, list[dict[str, str]]]:
    source_rows = read_csv(source)
    destination = RESULT_DIR / source.name
    if not destination.exists():
        rows = [dict(row) for row in source_rows]
        restored = restore_from_journal(source.name, rows)
        if create_result or restored:
            write_csv_atomic(destination, rows)
        return destination, rows

    rows = read_csv(destination)
    if len(rows) != len(source_rows):
        raise ValueError(f"{destination}: row count differs from {source}")
    immutable = ("setting", "row_number", "response_id", "prompt")
    for line_number, (expected, actual) in enumerate(zip(source_rows, rows), 2):
        for column in immutable:
            if expected[column] != actual[column]:
                raise ValueError(f"{destination}:{line_number}: {column} differs from Dataset")
    restored = restore_from_journal(source.name, rows)
    if restored:
        write_csv_atomic(destination, rows)
        print(f"RECOVERED {restored} journaled answer(s) in {source.name}", file=sys.stderr)
    return destination, rows


def all_records(dataset_filter: str | None, create_results: bool = False):
    for source in source_paths(dataset_filter):
        destination, rows = load_pair(source, create_results)
        yield source, destination, rows


def command_instructions(_: argparse.Namespace) -> int:
    print(AGENT_INSTRUCTIONS)
    return 0


def command_status(args: argparse.Namespace) -> int:
    grand_total = grand_answered = 0
    print("LogiQAte queue status")
    print("-" * 72)
    for source, _, rows in all_records(args.dataset):
        answered = sum(not is_unresolved(row["model_response"]) for row in rows)
        unresolved = len(rows) - answered
        grand_total += len(rows)
        grand_answered += answered
        print(f"{source.name:<40} {answered:>4}/{len(rows):<4} answered  {unresolved:>4} unresolved")
    remaining = grand_total - grand_answered
    print("-" * 72)
    print(f"TOTAL{'':<35} {grand_answered:>4}/{grand_total:<4} answered  {remaining:>4} unresolved")
    if args.strict and remaining:
        print("INCOMPLETE", file=sys.stderr)
        return 2
    if remaining == 0:
        print("COMPLETE")
    return 0


def command_next(args: argparse.Namespace) -> int:
    for source, _, rows in all_records(args.dataset, create_results=True):
        for row in rows:
            if is_unresolved(row["model_response"]):
                payload = {
                    "dataset_file": source.name,
                    "setting": row["setting"],
                    "row_number": row["row_number"],
                    "response_id": row["response_id"],
                    "prompt": row["prompt"],
                }
                if args.json:
                    print(json.dumps(payload, ensure_ascii=False, indent=2))
                else:
                    print("EVALUATION_ITEM")
                    print(f"dataset_file: {source.name}")
                    print(f"setting: {row['setting']}")
                    print(f"row_number: {row['row_number']}")
                    print(f"response_id: {row['response_id']}")
                    print("PROMPT_BEGIN")
                    print(row["prompt"])
                    print("PROMPT_END")
                    print(
                        f"SUBMIT_WITH: python run_row_by_row.py answer {row['response_id']} "
                        "--response \"FINAL ANSWER\""
                    )
                return 0
    print("COMPLETE: no unresolved rows remain")
    return 0


def command_protect(args: argparse.Namespace) -> int:
    """Seed the recovery journal from legitimate answers already in Result."""
    latest = journal_answers()
    protected = 0
    already_protected = 0
    for source, _, rows in all_records(args.dataset):
        for row in rows:
            answer = row["model_response"].strip()
            if is_unresolved(answer):
                continue
            prior = latest.get(row["response_id"])
            if prior and prior.get("answer") == answer and prior.get("dataset_file") == source.name:
                already_protected += 1
                continue
            record = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "action": "protect-existing",
                "dataset_file": source.name,
                "response_id": row["response_id"],
                "answer": answer,
            }
            append_journal(record)
            latest[row["response_id"]] = record
            protected += 1
    print(f"PROTECTED {protected} existing answer(s); {already_protected} already journaled")
    return 0


def validate_response(response: str) -> str:
    response = response.strip()
    if is_unresolved(response):
        raise ValueError("A genuine final answer is required; non-answers are rejected")
    if "\n" in response:
        raise ValueError("Submit only the final answer on one line, without reasoning")
    return response


def command_answer(args: argparse.Namespace) -> int:
    response = args.response
    if response is None:
        if sys.stdin.isatty():
            raise SystemExit("Provide --response \"FINAL ANSWER\" or pipe the answer on stdin")
        response = sys.stdin.read()
    response = validate_response(response)

    matches = []
    for source, destination, rows in all_records(args.dataset, create_results=True):
        for index, row in enumerate(rows):
            if row["response_id"] == args.response_id:
                matches.append((source, destination, rows, index))
    if not matches:
        raise SystemExit(f"Unknown response_id: {args.response_id}")
    if len(matches) > 1:
        raise SystemExit(f"Duplicate response_id across datasets: {args.response_id}")

    source, destination, rows, index = matches[0]
    current = rows[index]["model_response"].strip()
    if current and not is_unresolved(current) and not args.replace:
        raise SystemExit(
            f"Response {args.response_id} is already answered. Use --replace only for a deliberate correction."
        )
    rows[index]["model_response"] = response
    append_journal({
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "action": "replace" if current else "answer",
        "dataset_file": source.name,
        "response_id": args.response_id,
        "answer": response,
        "previous_answer": current,
    })
    write_csv_atomic(destination, rows)

    answered = sum(not is_unresolved(row["model_response"]) for row in rows)
    remaining = len(rows) - answered
    print(f"RECORDED {args.response_id}: {response}")
    print(f"{source.name}: {answered}/{len(rows)} answered, {remaining} unresolved")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    instructions = subparsers.add_parser("instructions", help="print the universal agent protocol")
    instructions.set_defaults(func=command_instructions)

    status = subparsers.add_parser("status", help="show completion counts")
    status.add_argument("--dataset", help="only filenames containing this text")
    status.add_argument("--strict", action="store_true", help="exit nonzero until complete")
    status.set_defaults(func=command_status)

    next_item = subparsers.add_parser("next", help="print the next unresolved prompt")
    next_item.add_argument("--dataset", help="only filenames containing this text")
    next_item.add_argument("--json", action="store_true", help="print machine-readable JSON")
    next_item.set_defaults(func=command_next)

    protect = subparsers.add_parser(
        "protect", help="snapshot existing Result answers into the recovery journal"
    )
    protect.add_argument("--dataset", help="only filenames containing this text")
    protect.set_defaults(func=command_protect)

    answer = subparsers.add_parser("answer", help="checkpoint one final answer")
    answer.add_argument("response_id")
    answer.add_argument("--response", help="one-line final answer; stdin is also supported")
    answer.add_argument("--dataset", help="only filenames containing this text")
    answer.add_argument("--replace", action="store_true", help="deliberately replace an existing answer")
    answer.set_defaults(func=command_answer)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
