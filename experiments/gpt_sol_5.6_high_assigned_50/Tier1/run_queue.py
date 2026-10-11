"""Durable agent queues for the seven fixed-sample Tier 1 conditions."""

from __future__ import annotations

import argparse
import contextlib
import csv
import json
import os
import re
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
PROMPT_PATH = ROOT / "prompts" / "tier1_prompt_templates.json"
FIELDS = [
    "queue",
    "condition",
    "stage",
    "path_index",
    "row_number",
    "response_id",
    "evaluation_id",
    "task",
    "item_id",
    "variant",
    "prompt",
    "depends_on_response_id",
    "model_response",
]
BASE_QUEUES = (
    "normalize_then_solve",
    "structured_decomposition",
    "explicit_task_instructions",
    "chain_of_thought",
    "rereading_s2a",
    "self_consistency_path_1",
    "self_consistency_path_2",
    "self_consistency_path_3",
    "self_verification_cove_initial",
)
VERIFICATION_QUEUE = "self_verification_cove_verification"
ALL_QUEUES = BASE_QUEUES + (VERIFICATION_QUEUE,)
INVALID = ("UNKNOWN", "ERROR", "SKIPPED", "NO_ANSWER", "N/A", "I CANNOT", "I CAN'T")
FINAL_MARKER = re.compile(r"FINAL_ANSWER\s*:\s*\S+", re.IGNORECASE)

INSTRUCTIONS = """
You are gpt-5.6-sol at high reasoning effort and are the model being evaluated.
Work only on the named Tier 1 queue. For every item, read only the prompt
printed by `next`, solve it independently using your own reasoning, and submit
the complete requested one-line response through the `answer` command.

Do not inspect answer keys, Analysis, private files, source datasets, another
queue, or any other path's responses. Do not use web search, APIs, helper
solvers, hard-coded answer maps, or bulk answer-generation scripts. A CoVe
verification prompt may include its authorized initial response. Continue
until `status --strict` reports COMPLETE for the queue.
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


def dataset_path(queue: str) -> Path:
    if queue not in ALL_QUEUES:
        raise SystemExit(f"unknown queue {queue!r}")
    path = DATASET_DIR / f"{queue}.csv"
    if not path.exists():
        if queue == VERIFICATION_QUEUE:
            raise SystemExit("CoVe verification is not built; complete initial responses then run build-cove-verification")
        raise SystemExit(f"missing prepared queue: {path}")
    return path


def available_queues() -> tuple[str, ...]:
    return tuple(queue for queue in ALL_QUEUES if (DATASET_DIR / f"{queue}.csv").exists())


def load_pair(queue: str, create: bool = True) -> tuple[Path, list[dict[str, str]]]:
    source = dataset_path(queue)
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


def journal_path(queue: str) -> Path:
    return RESULT_DIR / f"_answer_journal_{queue}.jsonl"


@contextlib.contextmanager
def queue_lock(queue: str):
    path = RESULT_DIR / f".{queue}.lock"
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


def append_journal(queue: str, row: dict[str, str], response: str) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": "gpt-5.6-sol",
        "reasoning_effort": "high",
        "queue": queue,
        "condition": row["condition"],
        "stage": row["stage"],
        "path_index": row["path_index"],
        "response_id": row["response_id"],
        "evaluation_id": row["evaluation_id"],
        "response": response,
    }
    with journal_path(queue).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def cmd_instructions(_: argparse.Namespace) -> int:
    print(INSTRUCTIONS)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    queues = (args.queue,) if args.queue else available_queues()
    total = answered = 0
    for queue in queues:
        _, rows = load_pair(queue)
        done = sum(not unresolved(row["model_response"]) for row in rows)
        total += len(rows)
        answered += done
        print(f"{queue:<40} {done:>4}/{len(rows):<4} answered  {len(rows)-done:>4} unresolved")
    if VERIFICATION_QUEUE not in available_queues():
        print(f"{VERIFICATION_QUEUE:<40} NOT_BUILT")
    print(f"TOTAL{'':<35} {answered:>4}/{total:<4} answered  {total-answered:>4} unresolved")
    if total == answered and (args.queue or VERIFICATION_QUEUE in available_queues()):
        print("COMPLETE")
        return 0
    if args.strict:
        print("INCOMPLETE", file=sys.stderr)
        return 2
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    _, rows = load_pair(args.queue)
    emitted = 0
    for row in rows:
        if unresolved(row["model_response"]):
            print("EVALUATION_ITEM")
            print(f"queue: {row['queue']}")
            print(f"condition: {row['condition']}")
            print(f"stage: {row['stage']}")
            print(f"response_id: {row['response_id']}")
            print("PROMPT_BEGIN")
            print(row["prompt"])
            print("PROMPT_END")
            print(f"SUBMIT_WITH: python run_queue.py answer {row['response_id']} --response \"FULL ONE-LINE RESPONSE\"")
            emitted += 1
            if emitted >= args.count:
                return 0
    if emitted:
        return 0
    print("COMPLETE: no unresolved rows remain")
    return 0


def cmd_answer(args: argparse.Namespace) -> int:
    response = args.response.strip()
    if unresolved(response):
        raise SystemExit("submit a genuine model response")
    if "\n" in response or "\r" in response:
        raise SystemExit("submit the requested full response on one physical line")
    if not FINAL_MARKER.search(response):
        raise SystemExit("response must contain a non-empty FINAL_ANSWER marker")
    matches: list[tuple[str, Path, list[dict[str, str]], int]] = []
    for queue in available_queues():
        result, rows = load_pair(queue)
        for index, row in enumerate(rows):
            if row["response_id"] == args.response_id:
                matches.append((queue, result, rows, index))
    if len(matches) != 1:
        raise SystemExit(f"expected one response ID match, found {len(matches)}")
    queue = matches[0][0]
    with queue_lock(queue):
        result, rows = load_pair(queue)
        index = next(index for index, row in enumerate(rows) if row["response_id"] == args.response_id)
        existing = rows[index]["model_response"].strip()
        if existing:
            if existing == response:
                print(f"ALREADY RECORDED {args.response_id}")
                return 0
            raise SystemExit(f"refusing to overwrite answered response {args.response_id}")
        append_journal(queue, rows[index], response)
        rows[index]["model_response"] = response
        write_atomic(result, rows)
    print(f"RECORDED {args.response_id}")
    return 0


def cmd_build_cove_verification(_: argparse.Namespace) -> int:
    initial_queue = "self_verification_cove_initial"
    _, initial_rows = load_pair(initial_queue)
    unresolved_ids = [row["response_id"] for row in initial_rows if unresolved(row["model_response"])]
    if unresolved_ids:
        raise SystemExit(f"cannot build verification: {len(unresolved_ids)} initial responses remain unresolved")
    templates = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    records: list[dict[str, str]] = []
    for initial in initial_rows:
        prompt = templates["templates"]["cove_verification"].format(
            initial_prompt=initial["prompt"],
            initial_response=initial["model_response"],
        ).strip()
        records.append(
            {
                "queue": VERIFICATION_QUEUE,
                "condition": "self_verification_cove",
                "stage": "verification",
                "path_index": "",
                "row_number": str(len(records) + 1),
                "response_id": f"{initial['evaluation_id']}-verification",
                "evaluation_id": initial["evaluation_id"],
                "task": initial["task"],
                "item_id": initial["item_id"],
                "variant": initial["variant"],
                "prompt": prompt,
                "depends_on_response_id": initial["response_id"],
                "model_response": "",
            }
        )
    target = DATASET_DIR / f"{VERIFICATION_QUEUE}.csv"
    if target.exists():
        existing = read_csv(target)
        if existing != records:
            raise SystemExit("existing CoVe verification dataset differs; refusing to overwrite")
        print(f"UNCHANGED {target} ({len(records)} rows)")
        return 0
    if (RESULT_DIR / target.name).exists():
        raise SystemExit("verification result exists without its dataset; refusing to continue")
    write_atomic(target, records)
    print(f"BUILT {target} ({len(records)} rows)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    instructions = sub.add_parser("instructions")
    instructions.set_defaults(func=cmd_instructions)
    status = sub.add_parser("status")
    status.add_argument("--queue", choices=ALL_QUEUES)
    status.add_argument("--strict", action="store_true")
    status.set_defaults(func=cmd_status)
    nxt = sub.add_parser("next")
    nxt.add_argument("--queue", choices=ALL_QUEUES, required=True)
    nxt.add_argument("--count", type=int, choices=range(1, 11), default=1)
    nxt.set_defaults(func=cmd_next)
    answer = sub.add_parser("answer")
    answer.add_argument("response_id")
    answer.add_argument("--response", required=True)
    answer.set_defaults(func=cmd_answer)
    build_cove = sub.add_parser("build-cove-verification")
    build_cove.set_defaults(func=cmd_build_cove_verification)
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    raise SystemExit(parsed.func(parsed))
