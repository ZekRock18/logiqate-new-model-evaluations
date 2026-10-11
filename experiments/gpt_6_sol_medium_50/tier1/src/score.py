from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PARENT_ROOT = ROOT.parent / "assigned"
RESULT_DIR = ROOT / "Result"
ANALYSIS_DIR = ROOT / "Analysis"
MODEL = "gpt-6-sol"
TASK_TITLES = {
    "obfus_fol": "FOL",
    "obfus_blood_relation": "Blood Relation",
    "obfus_number_series": "Number Series",
    "obfus_direction_sense": "Direction Sense",
}
METHODS = {
    "normalize_then_solve": {
        "obfus_fol": ("base", "obfuscation"),
        "obfus_blood_relation": ("base", "obfuscation_l1", "obfuscation_l2"),
    },
    "structured_decomposition": {
        "obfus_blood_relation": ("base", "obfuscation_l1", "obfuscation_l2"),
        "obfus_direction_sense": ("base", "obfuscation"),
    },
    "explicit_task_instructions": {
        "obfus_number_series": ("base", "obfuscation"),
        "obfus_direction_sense": ("base", "obfuscation"),
    },
    "chain_of_thought": {
        "obfus_fol": ("base", "obfuscation"),
        "obfus_blood_relation": ("base", "obfuscation_l1", "obfuscation_l2"),
        "obfus_number_series": ("base", "obfuscation"),
        "obfus_direction_sense": ("base", "obfuscation"),
    },
    "rereading_s2a": {
        "obfus_fol": ("base", "obfuscation"),
        "obfus_blood_relation": ("base", "obfuscation_l2"),
    },
    "self_consistency": {
        "obfus_fol": ("base", "obfuscation"),
        "obfus_blood_relation": ("base", "obfuscation_l1", "obfuscation_l2"),
        "obfus_number_series": ("base", "obfuscation"),
        "obfus_direction_sense": ("base", "obfuscation"),
    },
    "self_verification_cove": {
        "obfus_fol": ("base", "obfuscation"),
        "obfus_blood_relation": ("base", "obfuscation_l1", "obfuscation_l2"),
        "obfus_number_series": ("base", "obfuscation"),
        "obfus_direction_sense": ("base", "obfuscation"),
    },
}
METHOD_ORDER = tuple(METHODS)
SINGLE_METHODS = METHOD_ORDER[:5]
EXPECTED_UNITS = {
    "normalize_then_solve": 250,
    "structured_decomposition": 250,
    "explicit_task_instructions": 200,
    "chain_of_thought": 450,
    "rereading_s2a": 200,
    "self_consistency": 450,
    "self_verification_cove": 450,
}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate import (  # noqa: E402
    aggregate_cove,
    aggregate_self_consistency,
    final_answer,
    is_correct,
    normalise,
    read_csv,
    write_csv,
)


def _response_answer(response: str) -> str:
    parsed = final_answer(response)
    return parsed if parsed else str(response or "").strip()


def _load_private_gold(source_root: Path) -> dict[tuple[str, str, str], str]:
    path = (
        source_root.resolve()
        / "manual_eval"
        / "private_do_not_upload"
        / "gpt_sol_6_medium_full_50_scoring.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    gold = {
        (row["task"], row["item_id"], row["variant"]): row["answer"]
        for row in payload["records"]
    }
    if len(gold) != 450:
        raise ValueError(f"expected 450 private fixed-sample answers, found {len(gold)}")
    return gold


def _load_single_method(condition: str) -> list[dict]:
    path = RESULT_DIR / f"{condition}.csv"
    rows = read_csv(path)
    if len(rows) != EXPECTED_UNITS[condition]:
        raise ValueError(f"{condition}: expected {EXPECTED_UNITS[condition]} rows, found {len(rows)}")
    output = []
    for row in rows:
        response = row["model_response"].strip()
        if not response:
            raise ValueError(f"{condition}: unresolved {row['response_id']}")
        answer = final_answer(response)
        output.append(
            {
                "condition": condition,
                "evaluation_id": row["evaluation_id"],
                "task": row["task"],
                "item_id": row["item_id"],
                "variant": row["variant"],
                "prediction": answer,
                "status": "answered" if answer else "parse_failure",
            }
        )
    return output


def _evaluation_rows() -> tuple[list[dict], list[dict], list[dict]]:
    rows: list[dict] = []
    for condition in SINGLE_METHODS:
        rows.extend(_load_single_method(condition))
    self_consistency = aggregate_self_consistency()
    rows.extend(
        {
            "condition": "self_consistency",
            "evaluation_id": row["evaluation_id"],
            "task": row["task"],
            "item_id": row["item_id"],
            "variant": row["variant"],
            "prediction": row["final_answer"],
            "status": row["status"],
        }
        for row in self_consistency
    )
    cove = aggregate_cove()
    rows.extend(
        {
            "condition": "self_verification_cove",
            "evaluation_id": row["evaluation_id"],
            "task": row["task"],
            "item_id": row["item_id"],
            "variant": row["variant"],
            "prediction": row["final_answer"],
            "status": row["status"],
        }
        for row in cove
    )
    if len(rows) != 2250 or len({row["evaluation_id"] for row in rows}) != 2250:
        raise ValueError("Tier 1 evaluation rows are not exactly 2,250 unique units")
    actual = Counter(row["condition"] for row in rows)
    if actual != Counter(EXPECTED_UNITS):
        raise ValueError({"expected": EXPECTED_UNITS, "actual": dict(actual)})
    return rows, self_consistency, cove


def _score_rows(rows: list[dict], gold: dict[tuple[str, str, str], str]) -> list[dict]:
    scored = []
    for row in rows:
        key = (row["task"], row["item_id"], row["variant"])
        expected = gold[key]
        prediction = row["prediction"]
        scored.append(
            {
                **row,
                "gold": expected,
                "normalized_prediction": normalise(row["task"], prediction),
                "normalized_gold": normalise(row["task"], expected),
                "correct": is_correct(row["task"], prediction, expected),
            }
        )
    return scored


def _control_rows(gold: dict[tuple[str, str, str], str]) -> list[dict]:
    rows = read_csv(PARENT_ROOT / "Result" / "zero_shot_control.csv")
    if len(rows) != 450:
        raise ValueError(f"parent zero-shot control should contain 450 rows, found {len(rows)}")
    output = []
    for row in rows:
        key = (row["task"], row["item_id"], row["variant"])
        prediction = _response_answer(row["model_response"])
        expected = gold[key]
        output.append(
            {
                "task": row["task"],
                "item_id": row["item_id"],
                "variant": row["variant"],
                "correct": is_correct(row["task"], prediction, expected),
            }
        )
    return output


def _accuracy_cells(scored: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in scored:
        grouped[(row["condition"], row["task"], row["variant"])].append(row)
    cells = []
    for condition in METHOD_ORDER:
        for task, variants in METHODS[condition].items():
            for variant in variants:
                rows = grouped[(condition, task, variant)]
                if len(rows) != 50:
                    raise ValueError(f"{condition}/{task}/{variant}: expected 50, found {len(rows)}")
                hits = sum(row["correct"] for row in rows)
                cells.append(
                    {
                        "model": MODEL,
                        "condition": condition,
                        "task": task,
                        "task_title": TASK_TITLES[task],
                        "variant": variant,
                        "correct": hits,
                        "total": 50,
                        "accuracy_pct": round(hits * 2.0, 4),
                        "response_or_consensus_failures": sum(
                            row["status"] != "answered" for row in rows
                        ),
                    }
                )
    if len(cells) != 45:
        raise ValueError(f"expected 45 accuracy cells, found {len(cells)}")
    return cells


def _control_cells(control: list[dict]) -> dict[tuple[str, str], dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in control:
        grouped[(row["task"], row["variant"])].append(row)
    output = {}
    for key, rows in grouped.items():
        if len(rows) != 50:
            raise ValueError(f"control {key}: expected 50, found {len(rows)}")
        hits = sum(row["correct"] for row in rows)
        output[key] = {"correct": hits, "total": 50, "accuracy_pct": hits * 2.0}
    if len(output) != 9:
        raise ValueError(f"expected 9 zero-shot control cells, found {len(output)}")
    return output


def _comparisons(cells: list[dict], control_cells: dict) -> tuple[list[dict], list[dict]]:
    index = {(row["condition"], row["task"], row["variant"]): row for row in cells}
    improvements = []
    gaps = []
    for condition in METHOD_ORDER:
        for task, variants in METHODS[condition].items():
            base = index[(condition, task, "base")]
            for variant in variants:
                if variant == "base":
                    continue
                method = index[(condition, task, variant)]
                control = control_cells[(task, variant)]
                improvements.append(
                    {
                        "condition": condition,
                        "task": task,
                        "variant": variant,
                        "method_correct": method["correct"],
                        "control_correct": control["correct"],
                        "total": 50,
                        "method_accuracy_pct": method["accuracy_pct"],
                        "control_accuracy_pct": control["accuracy_pct"],
                        "improvement_pp": round(
                            method["accuracy_pct"] - control["accuracy_pct"], 4
                        ),
                    }
                )
                gaps.append(
                    {
                        "condition": condition,
                        "task": task,
                        "variant": variant,
                        "base_source_condition": condition,
                        "base_correct": base["correct"],
                        "obfuscated_correct": method["correct"],
                        "total": 50,
                        "base_accuracy_pct": base["accuracy_pct"],
                        "obfuscated_accuracy_pct": method["accuracy_pct"],
                        "base_minus_obfuscated_pp": round(
                            base["accuracy_pct"] - method["accuracy_pct"], 4
                        ),
                    }
                )
    if len(improvements) != 25 or len(gaps) != 25:
        raise ValueError("expected 25 obfuscated-cell comparisons")
    return improvements, gaps


def _paired_retention(scored: list[dict]) -> list[dict]:
    index = {
        (row["condition"], row["task"], row["item_id"], row["variant"]): row
        for row in scored
    }
    output = []
    for condition in METHOD_ORDER:
        for task, variants in METHODS[condition].items():
            for variant in variants:
                if variant == "base":
                    continue
                item_ids = sorted(
                    row["item_id"]
                    for row in scored
                    if row["condition"] == condition
                    and row["task"] == task
                    and row["variant"] == variant
                )
                transitions = Counter()
                for item_id in item_ids:
                    base = index[(condition, task, item_id, "base")]["correct"]
                    obfuscated = index[(condition, task, item_id, variant)]["correct"]
                    transitions[(base, obfuscated)] += 1
                base_correct = transitions[(True, True)] + transitions[(True, False)]
                output.append(
                    {
                        "condition": condition,
                        "task": task,
                        "variant": variant,
                        "both_correct": transitions[(True, True)],
                        "base_only_correct": transitions[(True, False)],
                        "obfuscated_only_correct": transitions[(False, True)],
                        "both_wrong": transitions[(False, False)],
                        "total": len(item_ids),
                        "paired_retention_pct": (
                            round(100 * transitions[(True, True)] / base_correct, 4)
                            if base_correct
                            else None
                        ),
                    }
                )
    return output


def _condition_totals(scored: list[dict]) -> list[dict]:
    output = []
    for condition in METHOD_ORDER:
        all_rows = [row for row in scored if row["condition"] == condition]
        obfuscated = [row for row in all_rows if row["variant"] != "base"]
        for scope, rows in (
            ("all applicable variants", all_rows),
            ("obfuscated variants", obfuscated),
        ):
            hits = sum(row["correct"] for row in rows)
            output.append(
                {
                    "condition": condition,
                    "scope": scope,
                    "correct": hits,
                    "total": len(rows),
                    "accuracy_pct": round(100 * hits / len(rows), 4),
                }
            )
    return output


def _special_metrics(scored: list[dict], self_consistency: list[dict], cove: list[dict], gold: dict) -> dict:
    agreement = Counter(row["agreement"] for row in self_consistency)
    changed = corrected = harmed = 0
    final_index = {
        row["evaluation_id"]: row
        for row in scored
        if row["condition"] == "self_verification_cove"
    }
    for row in cove:
        key = (row["task"], row["item_id"], row["variant"])
        initial_correct = is_correct(row["task"], row["initial_answer"], gold[key])
        final_correct = final_index[row["evaluation_id"]]["correct"]
        if row["answer_changed"]:
            changed += 1
        if not initial_correct and final_correct:
            corrected += 1
        if initial_correct and not final_correct:
            harmed += 1
    return {
        "self_consistency": {
            "evaluations": 450,
            "raw_paths": 1350,
            "agreement_counts": dict(agreement),
            "agreement_rate_pct": round(
                100 * (agreement["unanimous"] + agreement["majority"]) / 450, 4
            ),
        },
        "self_verification_cove": {
            "evaluations": 450,
            "raw_passes": 900,
            "answer_changed": changed,
            "answer_change_rate_pct": round(100 * changed / 450, 4),
            "incorrect_to_correct": corrected,
            "correct_to_incorrect": harmed,
        },
    }


def _write_report(summary: dict, totals: list[dict]) -> None:
    obfuscated = [row for row in totals if row["scope"] == "obfuscated variants"]
    lines = [
        "# GPT-6 Sol Medium: Full-50 Tier-1 Results",
        "",
        "All seven Tier-1 methods use the parent's fixed 50-item sample and fresh matched zero-shot control.",
        "",
        "| Condition | Correct | Accuracy |",
        "| --- | ---: | ---: |",
    ]
    for row in obfuscated:
        lines.append(
            f"| {row['condition']} | {row['correct']}/{row['total']} | {row['accuracy_pct']:.2f}% |"
        )
    special = summary["special_metrics"]
    lines.extend(
        [
            "",
            "Methods cover different task matrices, so these micro-accuracies are not directly comparable across methods. Matched cell-level changes versus the zero-shot control are the primary comparison.",
            "",
            "## Special multi-pass metrics",
            "",
            f"- Self-Consistency agreement rate: {special['self_consistency']['agreement_rate_pct']:.2f}%.",
            f"- CoVe changed {special['self_verification_cove']['answer_changed']}/450 answers, "
            f"corrected {special['self_verification_cove']['incorrect_to_correct']} and harmed "
            f"{special['self_verification_cove']['correct_to_incorrect']}.",
            "",
            "Cell accuracy, matched-control improvement, base/obfuscated gaps and paired-retention tables are public aggregates.",
            "Row-level gold answers and correctness labels are intentionally excluded.",
            "",
        ]
    )
    (ANALYSIS_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def score(source_root: Path) -> dict:
    gold = _load_private_gold(source_root)
    evaluations, self_consistency, cove = _evaluation_rows()
    scored = _score_rows(evaluations, gold)
    control = _control_rows(gold)
    cells = _accuracy_cells(scored)
    control_cells = _control_cells(control)
    improvements, gaps = _comparisons(cells, control_cells)
    retention = _paired_retention(scored)
    totals = _condition_totals(scored)
    special = _special_metrics(scored, self_consistency, cove, gold)

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(ANALYSIS_DIR / "accuracy_by_cell.csv", cells)
    write_csv(ANALYSIS_DIR / "improvement_over_control.csv", improvements)
    write_csv(ANALYSIS_DIR / "base_obfuscated_gaps.csv", gaps)
    write_csv(ANALYSIS_DIR / "paired_retention.csv", retention)
    write_csv(ANALYSIS_DIR / "condition_totals.csv", totals)

    private_path = (
        source_root.resolve()
        / "manual_eval"
        / "private_do_not_upload"
        / "gpt_sol_6_medium_tier1_scored.csv"
    )
    write_csv(private_path, scored)
    summary = {
        "model": MODEL,
        "reasoning_effort": "medium",
        "conditions": 7,
        "task_variant_cells": 45,
        "evaluation_units": 2250,
        "raw_model_generations": 3600,
        "completed_evaluations": len(scored),
        "status_counts": dict(Counter(row["status"] for row in scored)),
        "scoring_policy": "Parent-package task normalizers with digit/word Blood Relation count equivalence; Direction distance tolerance is 0.05.",
        "condition_totals": totals,
        "special_metrics": special,
    }
    (ANALYSIS_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    _write_report(summary, totals)
    return {**summary, "private_row_evidence": str(private_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Score the full-50 Tier 1 run privately")
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(score(args.source_root), indent=2))


if __name__ == "__main__":
    main()
