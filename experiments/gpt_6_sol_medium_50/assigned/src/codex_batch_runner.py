"""Run isolated gpt-6-sol medium Codex sessions on public queue prompts.

Each session receives only the selected public prompts. Gold labels, prior
answers, and analysis are never passed to the evaluated model. Responses are
validated and committed through the queue's existing journal and atomic writer.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "prompts" / "batch_response_schema.json"
FINAL_MARKER = re.compile(r"FINAL_ANSWER\s*:\s*\S+", re.IGNORECASE)


def load_queue_module(package: Path):
    spec = importlib.util.spec_from_file_location("evaluation_queue", package / "run_queue.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load queue")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_request(rows: list[dict[str, str]], tier1: bool) -> str:
    response_rule = (
        "For each item, return its complete requested one-line response including "
        "the FINAL_ANSWER marker."
        if tier1
        else "For each item, follow its full prompt and end with a FINAL_ANSWER line."
    )
    payload = [{"response_id": row["response_id"], "prompt": row["prompt"]} for row in rows]
    return (
        "You are gpt-6-sol at medium reasoning effort, the model being evaluated. "
        "Solve each item independently. Do not inspect files, call tools, browse, "
        "refer to other items, or use their answers. "
        f"{response_rule} Return JSON matching the supplied schema with exactly one "
        "answer object per response_id, in input order. Do not include explanations "
        "outside each requested response.\n\n"
        + json.dumps(payload, ensure_ascii=False)
    )


def invoke(rows: list[dict[str, str]], tier1: bool, timeout: int) -> list[tuple[str, str]]:
    with tempfile.TemporaryDirectory(prefix="logiqate_gpt6_") as isolated:
        output = Path(isolated) / "answer.json"
        command = [
            "codex", "exec", "--ephemeral", "--ignore-user-config",
            "--ignore-rules", "--skip-git-repo-check", "-s", "read-only",
            "-C", isolated, "-m", "gpt-6-sol", "-c",
            'model_reasoning_effort="medium"', "--output-schema", str(SCHEMA),
            "-o", str(output), "-",
        ]
        completed = subprocess.run(
            command,
            input=make_request(rows, tier1),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0 or not output.exists():
            detail = (completed.stderr or completed.stdout)[-1200:]
            raise RuntimeError(f"Codex exited {completed.returncode}: {detail}")
        result = json.loads(output.read_text(encoding="utf-8"))
    answers = result.get("answers")
    if not isinstance(answers, list) or len(answers) != len(rows):
        raise ValueError("response count differs from batch size")
    expected = [row["response_id"] for row in rows]
    actual = [item.get("response_id") for item in answers]
    if actual != expected:
        raise ValueError("response IDs or order differ from request")
    validated = []
    for item in answers:
        response = item.get("model_response")
        if not isinstance(response, str) or not response.strip():
            raise ValueError(f"empty answer for {item['response_id']}")
        response = response.strip()
        if tier1:
            if "\n" in response or "\r" in response:
                raise ValueError(f"multiline answer for {item['response_id']}")
            if not FINAL_MARKER.search(response):
                raise ValueError(f"missing final marker for {item['response_id']}")
        else:
            final_lines = re.findall(r"FINAL_ANSWER\s*:\s*([^\r\n]+)", response, re.IGNORECASE)
            if not final_lines:
                raise ValueError(f"missing final answer for {item['response_id']}")
            response = "FINAL_ANSWER: " + final_lines[-1].strip()
        validated.append((item["response_id"], response))
    return validated


def answer_with_retry(rows: list[dict[str, str]], tier1: bool, timeout: int):
    for attempt in range(3):
        try:
            return invoke(rows, tier1, timeout)
        except Exception as exc:
            if attempt == 2:
                if len(rows) > 1:
                    middle = len(rows) // 2
                    return answer_with_retry(rows[:middle], tier1, timeout) + answer_with_retry(
                        rows[middle:], tier1, timeout
                    )
                raise RuntimeError(f"failed {rows[0]['response_id']}: {exc}") from exc
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def commit(module, queue: str, answers: list[tuple[str, str]], tier1: bool) -> int:
    lock = module.queue_lock if tier1 else module.condition_lock
    with lock(queue):
        path, rows = module.load_pair(queue)
        indexes = {row["response_id"]: index for index, row in enumerate(rows)}
        to_commit = []
        for response_id, response in answers:
            index = indexes.get(response_id)
            if index is None:
                raise ValueError(f"unknown response ID {response_id}")
            old = rows[index]["model_response"].strip()
            if old:
                if old != response:
                    raise ValueError(f"refusing to overwrite {response_id}")
                continue
            if module.unresolved(response):
                raise ValueError(f"unresolved answer {response_id}")
            to_commit.append((index, response))
        for index, response in to_commit:
            if tier1:
                module.append_journal(queue, rows[index], response)
            else:
                module.append_journal(queue, rows[index]["response_id"], response)
            rows[index]["model_response"] = response
        if to_commit:
            module.write_atomic(path, rows)
    return len(to_commit)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("queue")
    parser.add_argument("--tier1", action="store_true")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-items", type=int)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if not 1 <= args.batch_size <= 8 or not 1 <= args.workers <= 8:
        parser.error("batch size must be 1..8 and workers 1..8")
    package = ROOT.parent / "tier1" if args.tier1 else ROOT
    module = load_queue_module(package)
    _, all_rows = module.load_pair(args.queue)
    pending = [row for row in all_rows if module.unresolved(row["model_response"])]
    if args.max_items is not None:
        pending = pending[: args.max_items]
    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    print(f"{args.queue}: {len(pending)} pending, {len(batches)} batches", flush=True)
    completed = 0
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(answer_with_retry, batch, args.tier1, args.timeout): batch
            for batch in batches
        }
        for future in as_completed(futures):
            try:
                answers = future.result()
                completed += commit(module, args.queue, answers, args.tier1)
                print(f"{args.queue}: committed {completed}/{len(pending)}", flush=True)
            except Exception as exc:
                failed_ids = [row["response_id"] for row in futures[future]]
                failures.append((failed_ids, str(exc)))
                print(f"{args.queue}: failed batch {failed_ids}: {exc}", file=sys.stderr, flush=True)
    if failures:
        raise SystemExit(f"{len(failures)} batches failed; rerun this queue to retry unresolved rows")


if __name__ == "__main__":
    main()
