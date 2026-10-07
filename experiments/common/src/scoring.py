from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from config import (
    CONDITIONS,
    CONDITION_ORDER,
    DEFAULT_MODEL,
    DEFAULT_MODEL_REVISION,
    EXPERIMENT_ROOT,
    PROMPT_VERSION,
    REPO_ROOT,
    TASK_TITLES,
)
from data import iter_test_items, load_private_manifest
from run import API_LOG, EVALUATION_LOG


ROOT_SRC = REPO_ROOT / "src"
if str(ROOT_SRC) not in sys.path:
    sys.path.insert(0, str(ROOT_SRC))
_spec = importlib.util.spec_from_file_location("logiqate_root_scoring", ROOT_SRC / "scoring.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("could not load repository scorer")
root_scoring = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(root_scoring)

SCORED_DIR = EXPERIMENT_ROOT / "results" / "scored"
TABLE_DIR = EXPERIMENT_ROOT / "results" / "tables"


def pct(numerator: int, denominator: int) -> float:
    return numerator / denominator * 100.0 if denominator else 0.0


def _write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def _latest_evaluations(model: str) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    if not EVALUATION_LOG.exists():
        return latest
    for line in EVALUATION_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("model") == model:
            latest[record["evaluation_key"]] = record
    return latest


def _gold_index() -> dict[tuple[str, str, str], dict]:
    return {
        (record["task"], record["item_id"], record["variant"]): record
        for record in load_private_manifest()["records"]
        if record["split"] == "test"
    }


def _expected_keys(
    model: str, model_revision: str = DEFAULT_MODEL_REVISION
) -> list[tuple[str, str, str, str, str]]:
    output = []
    for condition in CONDITION_ORDER:
        for task, variants in CONDITIONS[condition].tasks.items():
            for item in iter_test_items(task, variants):
                key = "|".join(
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
                output.append((key, condition, item.task, item.item_id, item.variant))
    return output


def _score_records(model: str) -> tuple[list[dict], list[str]]:
    latest = _latest_evaluations(model)
    gold = _gold_index()
    scored: list[dict] = []
    missing: list[str] = []
    for key, condition, task, item_id, variant in _expected_keys(model):
        record = latest.get(key)
        if record is None:
            missing.append(key)
            continue
        gold_record = gold[(task, item_id, variant)]
        prediction = record.get("parsed_answer") or ""
        correct = root_scoring.is_correct(task, prediction, gold_record["correct_answer"])
        scored.append(
            {
                "model": model,
                "condition": condition,
                "task": task,
                "item_id": item_id,
                "variant": variant,
                "status": record.get("status", ""),
                "parsed_answer": prediction,
                "gold_answer": gold_record["correct_answer"],
                "normalized_prediction": root_scoring.NORMALISERS[task](prediction),
                "normalized_gold": root_scoring.NORMALISERS[task](gold_record["correct_answer"]),
                "is_correct": correct,
                "logically_equivalent": gold_record["logically_equivalent"],
                "run_id": record.get("run_id", ""),
                "retry_count": record.get("retry_count", 0),
                "metadata": json.dumps(record.get("metadata") or {}, ensure_ascii=False),
            }
        )
    return scored, missing


def _accuracy_cells(scored: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in scored:
        groups[(row["condition"], row["task"], row["variant"])].append(row)
    output = []
    for (condition, task, variant), rows in sorted(
        groups.items(), key=lambda pair: (CONDITION_ORDER.index(pair[0][0]), pair[0][1], pair[0][2])
    ):
        correct = sum(row["is_correct"] for row in rows)
        failures = sum(row["status"] != "answered" for row in rows)
        output.append(
            {
                "condition": condition,
                "task": task,
                "task_title": TASK_TITLES[task],
                "variant": variant,
                "correct": correct,
                "total": len(rows),
                "accuracy_pct": round(pct(correct, len(rows)), 4),
                "response_or_consensus_failures": failures,
            }
        )
    return output


def _comparison_tables(scored: list[dict], cells: list[dict]) -> tuple[list[dict], list[dict]]:
    cell_index = {(r["condition"], r["task"], r["variant"]): r for r in cells}
    improvements: list[dict] = []
    gaps: list[dict] = []
    for condition in CONDITION_ORDER:
        spec = CONDITIONS[condition]
        for task, variants in spec.tasks.items():
            for variant in variants:
                if variant == "base":
                    continue
                method = cell_index.get((condition, task, variant))
                control = cell_index.get(("zero_shot_control", task, variant))
                if method and control:
                    improvements.append(
                        {
                            "condition": condition,
                            "task": task,
                            "variant": variant,
                            "method_correct": method["correct"],
                            "total": method["total"],
                            "method_accuracy_pct": method["accuracy_pct"],
                            "control_correct": control["correct"],
                            "control_accuracy_pct": control["accuracy_pct"],
                            "improvement_pp": round(
                                method["accuracy_pct"] - control["accuracy_pct"], 4
                            ),
                        }
                    )
                base_condition = condition if (condition, task, "base") in cell_index else "zero_shot_control"
                base = cell_index.get((base_condition, task, "base"))
                if method and base:
                    signed_gap = base["accuracy_pct"] - method["accuracy_pct"]
                    relative = (
                        (method["accuracy_pct"] - base["accuracy_pct"])
                        / base["accuracy_pct"]
                        * 100.0
                        if base["accuracy_pct"]
                        else None
                    )
                    gaps.append(
                        {
                            "condition": condition,
                            "task": task,
                            "variant": variant,
                            "base_source_condition": base_condition,
                            "base_correct": base["correct"],
                            "base_total": base["total"],
                            "base_accuracy_pct": base["accuracy_pct"],
                            "obfuscated_correct": method["correct"],
                            "obfuscated_total": method["total"],
                            "obfuscated_accuracy_pct": method["accuracy_pct"],
                            "signed_base_minus_obf_gap_pp": round(signed_gap, 4),
                            "absolute_gap_pp": round(abs(signed_gap), 4),
                            "relative_obfuscation_change_pct": (
                                round(relative, 4) if relative is not None else None
                            ),
                        }
                    )
    return improvements, gaps


def _paired_retention(scored: list[dict]) -> list[dict]:
    index = {
        (r["condition"], r["task"], r["item_id"], r["variant"]): r for r in scored
    }
    output: list[dict] = []
    for condition in CONDITION_ORDER:
        for task, variants in CONDITIONS[condition].tasks.items():
            for variant in variants:
                if variant == "base":
                    continue
                base_condition = condition
                if not any(
                    key[0] == condition and key[1] == task and key[3] == "base" for key in index
                ):
                    base_condition = "zero_shot_control"
                transitions = Counter()
                paired = 0
                item_ids = sorted(
                    {
                        row["item_id"]
                        for row in scored
                        if row["condition"] == condition
                        and row["task"] == task
                        and row["variant"] == variant
                    }
                )
                for item_id in item_ids:
                    base = index.get((base_condition, task, item_id, "base"))
                    obf = index.get((condition, task, item_id, variant))
                    if base is None or obf is None:
                        continue
                    paired += 1
                    transitions[(base["is_correct"], obf["is_correct"])] += 1
                base_correct = transitions[(True, True)] + transitions[(True, False)]
                output.append(
                    {
                        "condition": condition,
                        "task": task,
                        "variant": variant,
                        "base_source_condition": base_condition,
                        "paired_total": paired,
                        "both_correct": transitions[(True, True)],
                        "base_only_correct": transitions[(True, False)],
                        "obfuscated_only_correct": transitions[(False, True)],
                        "both_wrong": transitions[(False, False)],
                        "base_correct_total": base_correct,
                        "paired_retention_pct": (
                            round(pct(transitions[(True, True)], base_correct), 4)
                            if base_correct
                            else None
                        ),
                    }
                )
    return output


def _special_metrics(scored: list[dict]) -> dict:
    sc_rows = [r for r in scored if r["condition"] == "self_consistency"]
    sc_agreement = Counter()
    for row in sc_rows:
        metadata = json.loads(row["metadata"])
        sc_agreement[metadata.get("agreement", "unknown")] += 1

    cove_rows = [r for r in scored if r["condition"] == "self_verification_cove"]
    cove_changed = cove_corrected = cove_harmed = 0
    gold = _gold_index()
    for row in cove_rows:
        metadata = json.loads(row["metadata"])
        initial = metadata.get("initial_answer", "")
        initial_correct = root_scoring.is_correct(
            row["task"], initial, gold[(row["task"], row["item_id"], row["variant"])]["correct_answer"]
        )
        if metadata.get("answer_changed"):
            cove_changed += 1
        if not initial_correct and row["is_correct"]:
            cove_corrected += 1
        if initial_correct and not row["is_correct"]:
            cove_harmed += 1
    return {
        "self_consistency": {
            "evaluations": len(sc_rows),
            "agreement_counts": dict(sc_agreement),
            "agreement_rate_pct": round(
                pct(sc_agreement["unanimous"] + sc_agreement["majority"], len(sc_rows)), 4
            ),
        },
        "self_verification_cove": {
            "evaluations": len(cove_rows),
            "answer_changed": cove_changed,
            "answer_change_rate_pct": round(pct(cove_changed, len(cove_rows)), 4),
            "incorrect_to_correct": cove_corrected,
            "correction_rate_pct": round(pct(cove_corrected, len(cove_rows)), 4),
            "correct_to_incorrect": cove_harmed,
        },
    }


def _api_usage(model: str) -> dict:
    totals = Counter()
    calls = 0
    finish_reasons = Counter()
    if API_LOG.exists():
        for line in API_LOG.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("model") != model or record.get("prompt_version") != PROMPT_VERSION:
                continue
            calls += 1
            finish_reasons[record.get("finish_reason") or "none"] += 1
            usage = record.get("token_usage") or {}
            for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                totals[key] += usage.get(key) or 0
            totals["estimated_cost"] += usage.get("estimated_cost") or 0
    return {
        "api_calls": calls,
        "prompt_tokens": totals["prompt_tokens"],
        "completion_tokens": totals["completion_tokens"],
        "total_tokens": totals["total_tokens"],
        "estimated_cost_usd": round(totals["estimated_cost"], 6),
        "finish_reason_counts": dict(finish_reasons),
    }


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def _write_report(summary: dict, cells: list[dict], improvements: list[dict], gaps: list[dict]) -> None:
    assigned = {
        "obf_to_obf_few_shot",
        "base_to_obf_paired_few_shot",
        "analogical_prompting",
    }
    assigned_rows = [r for r in improvements if r["condition"] in assigned]
    lines = [
        "# Prompt-Mitigation Results",
        "",
        f"Model: `{summary['model']}`. Completed {summary['completed_evaluations']}/"
        f"{summary['expected_evaluations']} evaluation units; missing: {summary['missing_evaluations']}.",
        "",
        "## Accuracy by condition, task and variant",
        "",
        _markdown_table(
            ["Condition", "Task", "Variant", "Correct", "Accuracy", "Failures"],
            [
                [
                    r["condition"],
                    r["task_title"],
                    r["variant"],
                    f"{r['correct']}/{r['total']}",
                    f"{r['accuracy_pct']:.2f}%",
                    r["response_or_consensus_failures"],
                ]
                for r in cells
            ],
        ),
        "",
        "## Three assigned experiments versus zero-shot obfuscated control",
        "",
        _markdown_table(
            ["Condition", "Task", "Variant", "Method", "Control", "Improvement"],
            [
                [
                    r["condition"],
                    TASK_TITLES[r["task"]],
                    r["variant"],
                    f"{r['method_correct']}/{r['total']} ({r['method_accuracy_pct']:.2f}%)",
                    f"{r['control_correct']}/{r['total']} ({r['control_accuracy_pct']:.2f}%)",
                    f"{r['improvement_pp']:+.2f} pp",
                ]
                for r in assigned_rows
            ],
        ),
        "",
        "## Base-to-obfuscated gaps",
        "",
        _markdown_table(
            ["Condition", "Task", "Variant", "Base source", "Base", "Obfuscated", "Absolute gap"],
            [
                [
                    r["condition"],
                    TASK_TITLES[r["task"]],
                    r["variant"],
                    r["base_source_condition"],
                    f"{r['base_correct']}/{r['base_total']} ({r['base_accuracy_pct']:.2f}%)",
                    f"{r['obfuscated_correct']}/{r['obfuscated_total']} ({r['obfuscated_accuracy_pct']:.2f}%)",
                    f"{r['absolute_gap_pp']:.2f} pp",
                ]
                for r in gaps
            ],
        ),
        "",
        "## Run audit",
        "",
        f"- Response/parsing/consensus failures: {summary['failure_count']}.",
        f"- Provider usage: {summary['api_usage']['api_calls']} calls, "
        f"{summary['api_usage']['total_tokens']} total tokens, estimated cost "
        f"${summary['api_usage']['estimated_cost_usd']:.6f}.",
        f"- Selected non-equivalent Number Series test IDs: {summary['number_series_non_equivalent_ids']}.",
        f"- Self-consistency agreement rate: {summary['special_metrics']['self_consistency']['agreement_rate_pct']:.2f}%.",
        f"- CoVe changed {summary['special_metrics']['self_verification_cove']['answer_changed']} answers; "
        f"corrected {summary['special_metrics']['self_verification_cove']['incorrect_to_correct']} and harmed "
        f"{summary['special_metrics']['self_verification_cove']['correct_to_incorrect']}.",
        "- This is a 15-item-per-task pilot. Report raw counts with percentages and avoid treating small differences as stable effects.",
        "",
    ]
    (TABLE_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def score_results(model: str = DEFAULT_MODEL) -> dict:
    scored, missing = _score_records(model)
    cells = _accuracy_cells(scored)
    improvements, gaps = _comparison_tables(scored, cells)
    paired = _paired_retention(scored)
    special = _special_metrics(scored)
    statuses = Counter(row["status"] for row in scored)
    non_equivalent = sorted(
        {row["item_id"] for row in scored if not row["logically_equivalent"]}
    )
    summary = {
        "model": model,
        "expected_evaluations": len(_expected_keys(model)),
        "completed_evaluations": len(scored),
        "missing_evaluations": len(missing),
        "missing_keys": missing,
        "status_counts": dict(statuses),
        "failure_count": sum(row["status"] != "answered" for row in scored),
        "number_series_non_equivalent_ids": non_equivalent,
        "special_metrics": special,
        "api_usage": _api_usage(model),
    }
    SCORED_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(SCORED_DIR / "scored_responses.csv", scored)
    _write_csv(TABLE_DIR / "accuracy_by_cell.csv", cells)
    _write_csv(TABLE_DIR / "improvement_over_control.csv", improvements)
    _write_csv(TABLE_DIR / "base_obfuscated_gaps.csv", gaps)
    _write_csv(TABLE_DIR / "paired_retention.csv", paired)
    _write_csv(
        TABLE_DIR / "assigned_experiments.csv",
        [
            row
            for row in improvements
            if row["condition"]
            in {
                "obf_to_obf_few_shot",
                "base_to_obf_paired_few_shot",
                "analogical_prompting",
            }
        ],
    )
    (TABLE_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _write_report(summary, cells, improvements, gaps)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Score the LogiQAte mitigation runs")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()
    print(json.dumps(score_results(args.model), indent=2))


if __name__ == "__main__":
    main()
