from __future__ import annotations

import argparse
import json
import math
import re
import threading
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from config import (
    CONDITIONS,
    CONDITION_ORDER,
    DEFAULT_MODEL,
    DEFAULT_MODEL_REVISION,
    DEFAULT_PROVIDER,
    EXPERIMENT_ROOT,
    PROMPT_VERSION,
    SELECTION_SEED,
    expected_api_call_count,
    expected_evaluation_count,
)
from data import ExperimentItem, iter_test_items, load_public_manifest
from prompts import render_prompt
from providers import DeepInfraProvider, ProviderResult


RAW_DIR = EXPERIMENT_ROOT / "results" / "raw"
METADATA_DIR = EXPERIMENT_ROOT / "results" / "run_metadata"
API_LOG = RAW_DIR / "api_calls.jsonl"
EVALUATION_LOG = RAW_DIR / "evaluations.jsonl"
_WRITE_LOCK = threading.Lock()
_FINAL_MARKER = re.compile(r"FINAL[_ ]ANSWER\s*:\s*(.+)", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with _WRITE_LOCK:
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")
            handle.flush()


def parse_answer(task: str, response: str) -> str:
    matches = _FINAL_MARKER.findall(response or "")
    answer = matches[-1].strip() if matches else (response or "").strip()
    answer = answer.splitlines()[0].strip().strip("`*# ")
    answer = re.sub(r"^[\"']|[\"']$", "", answer).strip()
    if task == "obfus_fol":
        tokens = re.findall(r"\b(TRUE|FALSE)\b", answer, re.IGNORECASE)
        return tokens[-1].upper() if tokens else answer
    if task == "obfus_number_series":
        numbers = re.findall(r"-?\d+(?:\.\d+)?", answer)
        return numbers[-1] if numbers else answer
    return answer.rstrip(".").strip()


def _normalise_for_vote(task: str, answer: str) -> str:
    if task == "obfus_fol":
        return answer.upper()
    if task == "obfus_blood_relation":
        return re.sub(r"[^A-Z]", "", answer.upper())
    if task == "obfus_number_series":
        numbers = re.findall(r"-?\d+(?:\.\d+)?", answer)
        return numbers[-1] if numbers else answer.upper()
    text = answer.upper()
    text = text.replace("NORTH-EAST", "NORTHEAST").replace("NORTH EAST", "NORTHEAST")
    text = text.replace("NORTH-WEST", "NORTHWEST").replace("NORTH WEST", "NORTHWEST")
    text = text.replace("SOUTH-EAST", "SOUTHEAST").replace("SOUTH EAST", "SOUTHEAST")
    text = text.replace("SOUTH-WEST", "SOUTHWEST").replace("SOUTH WEST", "SOUTHWEST")
    phrase_directions = {
        "NORTH OF EAST": "NORTHEAST",
        "EAST OF NORTH": "NORTHEAST",
        "NORTH OF WEST": "NORTHWEST",
        "WEST OF NORTH": "NORTHWEST",
        "SOUTH OF EAST": "SOUTHEAST",
        "EAST OF SOUTH": "SOUTHEAST",
        "SOUTH OF WEST": "SOUTHWEST",
        "WEST OF SOUTH": "SOUTHWEST",
    }
    direction = ""
    for phrase, canonical in phrase_directions.items():
        if phrase in text:
            direction = canonical
            break
    if not direction:
        match = re.search(
            r"\b(NORTHEAST|NORTHWEST|SOUTHEAST|SOUTHWEST|NORTH|SOUTH|EAST|WEST)\b",
            text,
        )
        direction = match.group(1) if match else ""
    distance = None
    sqrt_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\\?SQRT\s*\{?|√)\s*(\d+(?:\.\d+)?)", text)
    if sqrt_match:
        distance = float(sqrt_match.group(1)) * math.sqrt(float(sqrt_match.group(2)))
    else:
        distance_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:KM|M|BLOCKS?)\b", text)
        if distance_match:
            distance = float(distance_match.group(1))
    if direction and distance is not None:
        return f"{distance:.2f} KM|{direction}"
    if direction:
        return direction
    return re.sub(r"\s+", " ", text).strip(" .")


def _max_tokens(condition: str) -> int:
    return 4096


def _has_final_marker(response: str) -> bool:
    return bool(_FINAL_MARKER.search(response or ""))


def _evaluation_key(
    model: str, model_revision: str, condition: str, item: ExperimentItem
) -> str:
    return "|".join(
        (
            model,
            model_revision,
            PROMPT_VERSION,
            condition,
            item.task,
            item.item_id,
            item.variant,
        )
    )


def _load_latest_evaluations() -> dict[str, dict]:
    latest: dict[str, dict] = {}
    if not EVALUATION_LOG.exists():
        return latest
    for line in EVALUATION_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if (
            record.get("condition") != "self_consistency"
            and record.get("status") == "answered"
            and not _has_final_marker(record.get("raw_response", ""))
        ):
            record["status"] = "parse_failure"
        latest[record["evaluation_key"]] = record
    return latest


def _api_record(
    *,
    run_id: str,
    model: str,
    model_revision: str,
    condition: str,
    item: ExperimentItem,
    prompt: str,
    demo_ids: list[str],
    temperature: float,
    seed: int,
    stage: str,
    attempt: int,
    result: ProviderResult,
) -> dict:
    return {
        "run_id": run_id,
        "provider": DEFAULT_PROVIDER,
        "model": model,
        "model_revision": model_revision,
        "task": item.task,
        "item_id": item.item_id,
        "variant": item.variant,
        "condition": condition,
        "stage": stage,
        "attempt": attempt,
        "prompt_version": PROMPT_VERSION,
        "prompt": prompt,
        "demonstration_item_ids": demo_ids,
        "raw_response": result.content,
        "reasoning_content": result.reasoning_content,
        "parsed_answer": parse_answer(item.task, result.content) if result.content else "",
        "status": "answered" if result.ok else "error",
        "temperature": temperature,
        "seed": seed,
        "timestamp_utc": utc_now(),
        "latency_ms": result.latency_ms,
        "token_usage": result.usage,
        "provider_response_id": result.response_id,
        "finish_reason": result.finish_reason,
        "http_status": result.http_status,
        "error": result.error,
    }


def _call_with_retries(
    provider: DeepInfraProvider,
    *,
    run_id: str,
    model: str,
    model_revision: str,
    condition: str,
    item: ExperimentItem,
    prompt: str,
    demo_ids: list[str],
    temperature: float,
    seed: int,
    stage: str,
    max_attempts: int = 3,
) -> tuple[ProviderResult, int]:
    last: ProviderResult | None = None
    for attempt in range(1, max_attempts + 1):
        result = provider.complete(
            model=model,
            prompt=prompt,
            temperature=temperature,
            seed=seed,
            max_tokens=_max_tokens(condition),
        )
        append_jsonl(
            API_LOG,
            _api_record(
                run_id=run_id,
                model=model,
                model_revision=model_revision,
                condition=condition,
                item=item,
                prompt=prompt,
                demo_ids=demo_ids,
                temperature=temperature,
                seed=seed,
                stage=stage,
                attempt=attempt,
                result=result,
            ),
        )
        last = result
        if result.ok:
            return result, attempt - 1
        if result.http_status in {400, 401, 403, 404}:
            break
        if attempt < max_attempts:
            time.sleep(2 ** (attempt - 1))
    assert last is not None
    return last, max(0, attempt - 1)


def _run_item(
    provider: DeepInfraProvider,
    run_id: str,
    model: str,
    model_revision: str,
    condition: str,
    item: ExperimentItem,
) -> dict:
    spec = CONDITIONS[condition]
    prompt, demo_ids = render_prompt(condition, item)
    base_seed = SELECTION_SEED + int(item.item_id.rsplit("-", 1)[1])
    responses: list[ProviderResult] = []
    retry_count = 0
    metadata: dict = {}

    if condition == "self_consistency":
        path_answers: list[str] = []
        for path_index in range(spec.paths):
            result, retries = _call_with_retries(
                provider,
                run_id=run_id,
                model=model,
                model_revision=model_revision,
                condition=condition,
                item=item,
                prompt=prompt,
                demo_ids=demo_ids,
                temperature=spec.temperature,
                seed=base_seed + path_index,
                stage=f"path_{path_index + 1}",
            )
            responses.append(result)
            retry_count += retries
            path_answers.append(
                parse_answer(item.task, result.content)
                if result.ok and _has_final_marker(result.content)
                else "PARSE_ERROR"
            )
        normalized = [_normalise_for_vote(item.task, answer) for answer in path_answers]
        counts = Counter(
            normalized_answer
            for raw_answer, normalized_answer in zip(path_answers, normalized)
            if raw_answer != "PARSE_ERROR" and normalized_answer
        )
        winner, votes = counts.most_common(1)[0] if counts else ("NO_CONSENSUS", 0)
        parsed_answer = winner if votes >= 2 else "NO_CONSENSUS"
        raw_response = json.dumps(path_answers, ensure_ascii=False)
        status = "answered" if votes >= 2 else "no_consensus"
        metadata = {
            "path_answers": path_answers,
            "normalized_path_answers": normalized,
            "winning_votes": votes,
            "agreement": "unanimous" if votes == 3 else "majority" if votes == 2 else "none",
        }
    elif condition == "self_verification_cove":
        initial, retries = _call_with_retries(
            provider,
            run_id=run_id,
            model=model,
            model_revision=model_revision,
            condition=condition,
            item=item,
            prompt=prompt,
            demo_ids=demo_ids,
            temperature=0.0,
            seed=base_seed,
            stage="initial",
        )
        responses.append(initial)
        retry_count += retries
        if initial.ok:
            verify_prompt, _ = render_prompt(
                condition, item, initial_response=initial.content
            )
            verified, retries = _call_with_retries(
                provider,
                run_id=run_id,
                model=model,
                model_revision=model_revision,
                condition=condition,
                item=item,
                prompt=verify_prompt,
                demo_ids=demo_ids,
                temperature=0.0,
                seed=base_seed + 1,
                stage="verification",
            )
            responses.append(verified)
            retry_count += retries
        else:
            verified = initial
        initial_answer = parse_answer(item.task, initial.content) if initial.ok else ""
        parsed_answer = (
            parse_answer(item.task, verified.content)
            if verified.ok and _has_final_marker(verified.content)
            else ""
        )
        raw_response = verified.content
        status = (
            "answered"
            if verified.ok and _has_final_marker(verified.content)
            else "parse_failure"
            if verified.ok
            else "error"
        )
        metadata = {
            "initial_response": initial.content,
            "initial_answer": initial_answer,
            "verification_response": verified.content,
            "answer_changed": _normalise_for_vote(item.task, initial_answer)
            != _normalise_for_vote(item.task, parsed_answer),
        }
    else:
        result, retries = _call_with_retries(
            provider,
            run_id=run_id,
            model=model,
            model_revision=model_revision,
            condition=condition,
            item=item,
            prompt=prompt,
            demo_ids=demo_ids,
            temperature=spec.temperature,
            seed=base_seed,
            stage="single",
        )
        responses.append(result)
        retry_count += retries
        parsed_answer = (
            parse_answer(item.task, result.content)
            if result.ok and _has_final_marker(result.content)
            else ""
        )
        raw_response = result.content
        status = (
            "answered"
            if result.ok and _has_final_marker(result.content)
            else "parse_failure"
            if result.ok
            else "error"
        )

    usage = Counter()
    for response in responses:
        for key, value in response.usage.items():
            if isinstance(value, (int, float)):
                usage[key] += value
    record = {
        "evaluation_key": _evaluation_key(model, model_revision, condition, item),
        "run_id": run_id,
        "provider": DEFAULT_PROVIDER,
        "model": model,
        "model_revision": model_revision,
        "task": item.task,
        "item_id": item.item_id,
        "variant": item.variant,
        "condition": condition,
        "prompt_version": PROMPT_VERSION,
        "prompt": prompt,
        "raw_response": raw_response,
        "parsed_answer": parsed_answer,
        "status": status,
        "temperature": spec.temperature,
        "seed": base_seed,
        "timestamp_utc": utc_now(),
        "demonstration_item_ids": demo_ids,
        "sampling_parameters": {
            "temperature": spec.temperature,
            "paths": spec.paths,
            "passes": spec.passes,
            "max_tokens": _max_tokens(condition),
        },
        "latency_ms": sum(response.latency_ms for response in responses),
        "token_usage": dict(usage),
        "retry_count": retry_count,
        "error": "; ".join(response.error or "" for response in responses if response.error),
        "metadata": metadata,
    }
    append_jsonl(EVALUATION_LOG, record)
    return record


def _units(condition: str, limit_per_task: int | None = None) -> list[ExperimentItem]:
    spec = CONDITIONS[condition]
    output: list[ExperimentItem] = []
    for task, variants in spec.tasks.items():
        items = list(iter_test_items(task, variants))
        if limit_per_task is not None:
            allowed_ids = sorted({item.item_id for item in items})[:limit_per_task]
            items = [item for item in items if item.item_id in allowed_ids]
        output.extend(items)
    return output


def run_condition(
    condition: str,
    *,
    model: str = DEFAULT_MODEL,
    model_revision: str = DEFAULT_MODEL_REVISION,
    workers: int = 8,
    limit_per_task: int | None = None,
    retry_failed: bool = False,
    force: bool = False,
) -> dict:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition: {condition}")
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    latest = _load_latest_evaluations()
    all_units = _units(condition, limit_per_task)
    pending = []
    skipped = 0
    for item in all_units:
        prior = latest.get(_evaluation_key(model, model_revision, condition, item))
        if prior and not force and (not retry_failed or prior.get("status") == "answered"):
            skipped += 1
        else:
            pending.append(item)
    metadata = {
        "run_id": run_id,
        "started_utc": utc_now(),
        "provider": DEFAULT_PROVIDER,
        "model": model,
        "model_revision": model_revision,
        "condition": condition,
        "prompt_version": PROMPT_VERSION,
        "selection_seed": SELECTION_SEED,
        "workers": workers,
        "limit_per_task": limit_per_task,
        "force": force,
        "planned_units": len(all_units),
        "pending_units": len(pending),
        "skipped_existing": skipped,
    }
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata_path = METADATA_DIR / f"{run_id}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    statuses = Counter()
    provider = DeepInfraProvider() if pending else None
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(
                _run_item, provider, run_id, model, model_revision, condition, item
            ): item
            for item in pending
        }
        for future in as_completed(futures):
            item = futures[future]
            try:
                record = future.result()
                statuses[record["status"]] += 1
            except Exception as exc:
                statuses["runner_exception"] += 1
                append_jsonl(
                    EVALUATION_LOG,
                    {
                        "evaluation_key": _evaluation_key(model, model_revision, condition, item),
                        "run_id": run_id,
                        "provider": DEFAULT_PROVIDER,
                        "model": model,
                        "model_revision": model_revision,
                        "task": item.task,
                        "item_id": item.item_id,
                        "variant": item.variant,
                        "condition": condition,
                        "prompt_version": PROMPT_VERSION,
                        "prompt": "",
                        "raw_response": "",
                        "parsed_answer": "",
                        "status": "runner_exception",
                        "temperature": CONDITIONS[condition].temperature,
                        "seed": SELECTION_SEED,
                        "timestamp_utc": utc_now(),
                        "demonstration_item_ids": [],
                        "sampling_parameters": {},
                        "latency_ms": 0,
                        "token_usage": {},
                        "retry_count": 0,
                        "error": f"{type(exc).__name__}: {exc}",
                        "metadata": {},
                    },
                )

    metadata.update(
        {
            "completed_utc": utc_now(),
            "new_status_counts": dict(statuses),
            "complete_units_after_run": skipped + sum(statuses.values()),
        }
    )
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Run resumable October 6 mitigation experiments")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--condition", choices=CONDITION_ORDER)
    group.add_argument("--all", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--model-revision", default=DEFAULT_MODEL_REVISION)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit-per-task", type=int)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    conditions = CONDITION_ORDER if args.all else (args.condition,)
    summaries = []
    for condition in conditions:
        summary = run_condition(
            condition,
            model=args.model,
            model_revision=args.model_revision,
            workers=args.workers,
            limit_per_task=args.limit_per_task,
            retry_failed=args.retry_failed,
            force=args.force,
        )
        summaries.append(summary)
        print(json.dumps(summary, indent=2))
    print(
        json.dumps(
            {
                "conditions": list(conditions),
                "expected_full_evaluations": expected_evaluation_count(),
                "expected_full_api_calls": expected_api_call_count(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
