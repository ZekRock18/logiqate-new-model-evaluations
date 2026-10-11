"""Durable agent queue for the three assigned GPT mitigation conditions."""

from __future__ import annotations

import argparse
import contextlib
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


sys.dont_write_bytecode = True
for stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except OSError:
            pass

ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "Dataset"
RESULT_DIR = ROOT / "Result"
FIELDS = [
    "condition",
    "row_number",
    "response_id",
    "task",
    "item_id",
    "variant",
    "prompt",
    "model_response",
]
CONDITIONS = (
    "zero_shot_control",
    "obf_to_obf_few_shot",
    "base_to_obf_paired_few_shot",
    "analogical_prompting",
)
INVALID = ("UNKNOWN", "ERROR", "SKIPPED", "NO_ANSWER", "N/A", "I CANNOT", "I CAN'T")

INSTRUCTIONS = """
You are gpt-6-sol at medium reasoning effort and are the model being evaluated.
Work only on the named condition queue. For every item, read only the prompt
printed by `next`, solve it independently using your own reasoning, and record
only the requested final answer through the `answer` command.

Do not inspect answer keys, Analysis, other model results, private files, source
datasets, or another condition's responses. Do not use web search, APIs, helper
solvers, hard-coded answer maps, or bulk answer-generation scripts. The solved
demonstrations inside a prompt are authorized experimental context. Continue
until `status --strict` reports COMPLETE.
""".strip()


def unresolved(value: str | None) -> bool:
    text = str(value or "").strip()
    return not text or text.upper().startswith(INVALID)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"{path}: unexpected columns {reader.fieldnames}")
        rows = list(reader)
    if len({row["response_id"] for row in rows}) != len(rows):
        raise ValueError(f"{path}: duplicate response IDs")
    return rows


def write_atomic(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def dataset_path(condition: str) -> Path:
    if condition not in CONDITIONS:
        raise SystemExit(f"unknown condition {condition!r}")
    path = DATASET_DIR / f"{condition}.csv"
    if not path.exists():
        raise SystemExit(f"missing prepared queue: {path}")
    return path


def load_pair(condition: str, create: bool = True) -> tuple[Path, list[dict[str, str]]]:
    source = dataset_path(condition)
    source_rows = read_csv(source)
    result = RESULT_DIR / source.name
    if not result.exists():
        rows = [dict(row) for row in source_rows]
        if create:
            write_atomic(result, rows)
        return result, rows
    rows = read_csv(result)
    if len(rows) != len(source_rows):
        raise ValueError(f"{result}: row count changed")
    immutable = [column for column in FIELDS if column != "model_response"]
    for expected, actual in zip(source_rows, rows):
        for column in immutable:
            if expected[column] != actual[column]:
                raise ValueError(f"{result}: immutable column {column} changed")
    return result, rows


def journal_path(condition: str) -> Path:
    return RESULT_DIR / f"_answer_journal_{condition}.jsonl"


@contextlib.contextmanager
def condition_lock(condition: str):
    """Serialize answer transactions for one condition across processes."""
    path = RESULT_DIR / f".{condition}.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.05)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_journal(condition: str, response_id: str, answer: str) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": "gpt-6-sol",
        "reasoning_effort": "medium",
        "condition": condition,
        "response_id": response_id,
        "answer": answer,
    }
    with journal_path(condition).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def cmd_instructions(_: argparse.Namespace) -> int:
    print(INSTRUCTIONS)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    conditions = (args.condition,) if args.condition else CONDITIONS
    total = answered = 0
    for condition in conditions:
        _, rows = load_pair(condition)
        done = sum(not unresolved(row["model_response"]) for row in rows)
        total += len(rows)
        answered += done
        print(f"{condition:<36} {done:>3}/{len(rows):<3} answered  {len(rows)-done:>3} unresolved")
    print(f"TOTAL{'':<31} {answered:>3}/{total:<3} answered  {total-answered:>3} unresolved")
    if total == answered:
        print("COMPLETE")
        return 0
    if args.strict:
        print("INCOMPLETE", file=sys.stderr)
        return 2
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    _, rows = load_pair(args.condition)
    emitted = 0
    for row in rows:
        if unresolved(row["model_response"]):
            print("EVALUATION_ITEM")
            print(f"condition: {row['condition']}")
            print(f"row_number: {row['row_number']}")
            print(f"response_id: {row['response_id']}")
            print("PROMPT_BEGIN")
            print(row["prompt"])
            print("PROMPT_END")
            print(f"SUBMIT_WITH: python run_queue.py answer {row['response_id']} --response \"FINAL ANSWER\"")
            emitted += 1
            if emitted >= args.count:
                return 0
    if emitted:
        return 0
    print("COMPLETE: no unresolved rows remain")
    return 0


def cmd_answer(args: argparse.Namespace) -> int:
    answer = args.response.strip()
    if unresolved(answer) or "\n" in answer:
        raise SystemExit("submit one genuine final answer on one line")
    matches: list[tuple[str, Path, list[dict[str, str]], int]] = []
    for condition in CONDITIONS:
        result, rows = load_pair(condition)
        for index, row in enumerate(rows):
            if row["response_id"] == args.response_id:
                matches.append((condition, result, rows, index))
    if len(matches) != 1:
        raise SystemExit(f"expected one response ID match, found {len(matches)}")
    condition = matches[0][0]
    with condition_lock(condition):
        result, rows = load_pair(condition)
        index = next(
            index for index, row in enumerate(rows) if row["response_id"] == args.response_id
        )
        existing = rows[index]["model_response"].strip()
        if existing:
            if existing == answer:
                print(f"ALREADY RECORDED {args.response_id}")
                return 0
            raise SystemExit(f"refusing to overwrite answered response {args.response_id}")
        append_journal(condition, args.response_id, answer)
        rows[index]["model_response"] = answer
        write_atomic(result, rows)
    print(f"RECORDED {args.response_id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    instructions = sub.add_parser("instructions")
    instructions.set_defaults(func=cmd_instructions)
    status = sub.add_parser("status")
    status.add_argument("--condition", choices=CONDITIONS)
    status.add_argument("--strict", action="store_true")
    status.set_defaults(func=cmd_status)
    nxt = sub.add_parser("next")
    nxt.add_argument("--condition", choices=CONDITIONS, required=True)
    nxt.add_argument("--count", type=int, choices=range(1, 11), default=1)
    nxt.set_defaults(func=cmd_next)
    answer = sub.add_parser("answer")
    answer.add_argument("response_id")
    answer.add_argument("--response", required=True)
    answer.set_defaults(func=cmd_answer)
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    raise SystemExit(parsed.func(parsed))
