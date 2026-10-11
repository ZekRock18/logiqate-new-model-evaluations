from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RESULT_DIR = ROOT / "Result"
ANALYSIS_DIR = ROOT / "Analysis"
MODEL = "gpt-5.6-sol"
CONDITIONS = (
    "zero_shot_control",
    "obf_to_obf_few_shot",
    "base_to_obf_paired_few_shot",
    "analogical_prompting",
)
TASK_TITLES = {
    "obfus_fol": "FOL",
    "obfus_blood_relation": "Blood Relation",
    "obfus_number_series": "Number Series",
    "obfus_direction_sense": "Direction Sense",
}
COMPASS = r"\b(NORTHEAST|NORTHWEST|SOUTHEAST|SOUTHWEST|NORTH|SOUTH|EAST|WEST)\b"
DIRECTION_ALIASES = {
    "NORTH-EAST": "NORTHEAST", "NORTH EAST": "NORTHEAST", "EAST OF NORTH": "NORTHEAST",
    "NORTH-WEST": "NORTHWEST", "NORTH WEST": "NORTHWEST", "WEST OF NORTH": "NORTHWEST",
    "SOUTH-EAST": "SOUTHEAST", "SOUTH EAST": "SOUTHEAST", "EAST OF SOUTH": "SOUTHEAST",
    "SOUTH-WEST": "SOUTHWEST", "SOUTH WEST": "SOUTHWEST", "WEST OF SOUTH": "SOUTHWEST",
}
DIRECTION_ABBREV = {"NE": "NORTHEAST", "NW": "NORTHWEST", "SE": "SOUTHEAST", "SW": "SOUTHWEST"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def final_answer(text: str) -> str:
    text = str(text or "").strip()
    matches = list(re.finditer(r"FINAL_ANSWER\s*:\s*(.+)", text, re.I))
    return matches[-1].group(1).strip() if matches else text


def squash(text: str) -> str:
    return re.sub(r"[.,;:]+$", "", re.sub(r"\s+", " ", str(text).strip().upper()))


def normalise_fol(text: str) -> str:
    tokens = re.findall(r"\b(TRUE|FALSE)\b", squash(final_answer(text)))
    return tokens[-1] if tokens else squash(final_answer(text))


def normalise_blood(text: str) -> str:
    value = squash(final_answer(text))
    count_aliases = {
        "0": "0", "ZERO": "0",
        "1": "1", "ONE": "1",
        "2": "2", "TWO": "2",
        "3": "3", "THREE": "3",
        "4": "4", "FOUR": "4",
        "5": "5", "FIVE": "5",
        "6": "6", "SIX": "6",
        "7": "7", "SEVEN": "7",
        "8": "8", "EIGHT": "8",
        "9": "9", "NINE": "9",
        "10": "10", "TEN": "10",
    }
    if value in count_aliases:
        return count_aliases[value]
    return re.sub(r"[^A-Z]", "", value)


def normalise_series(text: str) -> str:
    numbers = re.findall(r"-?\b\d+\b", final_answer(text))
    return numbers[-1] if numbers else squash(final_answer(text))


def normalise_direction(text: str) -> str:
    value = squash(final_answer(text))
    for alias, canonical in DIRECTION_ALIASES.items():
        value = value.replace(alias, canonical)
    for short, canonical in DIRECTION_ABBREV.items():
        value = re.sub(rf"\b{short}\b", canonical, value)

    away = re.search(r"(\w+),?\s*(\d+(?:\.\d+)?)\s*(?:KM|M|BLOCKS?)\s*AWAY", value)
    if away:
        direction, distance = away.groups()
        return f"{distance} KM, {direction}"
    dist_dir = re.search(r"(\d+(?:\.\d+)?)\s*(?:KM|M|BLOCKS?),?\s*(\w+)", value)
    if dist_dir:
        distance, direction = dist_dir.groups()
        return f"{distance} KM, {direction}"
    direction = re.search(COMPASS, value)
    if direction:
        return direction.group(1)
    distance = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:KM|M|BLOCKS?)\b", value)
    if distance:
        return f"{distance.group(1)} KM"
    return value


NORMALISERS = {
    "obfus_fol": normalise_fol,
    "obfus_blood_relation": normalise_blood,
    "obfus_number_series": normalise_series,
    "obfus_direction_sense": normalise_direction,
}


def correct(task: str, prediction: str, gold: str) -> bool:
    pred = NORMALISERS[task](prediction)
    truth = NORMALISERS[task](gold)
    if not pred or not truth:
        return False
    if pred == truth:
        return True
    if task != "obfus_direction_sense":
        return False
    pred_dir = re.search(COMPASS, pred)
    truth_dir = re.search(COMPASS, truth)
    if not pred_dir or not truth_dir or pred_dir.group(1) != truth_dir.group(1):
        return False
    pred_dist = re.search(r"-?\d+(?:\.\d+)?", pred)
    truth_dist = re.search(r"-?\d+(?:\.\d+)?", truth)
    if not pred_dist or not truth_dist:
        return True
    return abs(float(pred_dist.group(0)) - float(truth_dist.group(0))) <= 0.05


def score(source_root: Path) -> dict:
    private_path = source_root.resolve() / "manual_eval" / "private_do_not_upload" / "gpt_sol_5.6_high_assigned_50_scoring.json"
    private = json.loads(private_path.read_text(encoding="utf-8"))
    gold = {
        (row["task"], row["item_id"], row["variant"]): row["answer"]
        for row in private["records"]
    }
    scored: list[dict] = []
    for condition in CONDITIONS:
        path = RESULT_DIR / f"{condition}.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        for row in read_csv(path):
            prediction = row["model_response"].strip()
            if not prediction:
                raise ValueError(f"unresolved response {row['response_id']}")
            answer = gold[(row["task"], row["item_id"], row["variant"])]
            scored.append(
                {
                    "condition": condition,
                    "response_id": row["response_id"],
                    "task": row["task"],
                    "item_id": row["item_id"],
                    "variant": row["variant"],
                    "prediction": prediction,
                    "gold": answer,
                    "normalized_prediction": NORMALISERS[row["task"]](prediction),
                    "normalized_gold": NORMALISERS[row["task"]](answer),
                    "correct": correct(row["task"], prediction, answer),
                }
            )

    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in scored:
        groups[(row["condition"], row["task"], row["variant"])].append(row)
    cells: list[dict] = []
    for (condition, task, variant), rows in sorted(groups.items()):
        hits = sum(row["correct"] for row in rows)
        cells.append(
            {
                "model": MODEL,
                "condition": condition,
                "task": task,
                "task_title": TASK_TITLES[task],
                "variant": variant,
                "correct": hits,
                "total": len(rows),
                "accuracy_pct": round(100 * hits / len(rows), 4),
            }
        )

    control_cells = {
        (row["task"], row["variant"]): row for row in cells if row["condition"] == "zero_shot_control"
    }
    improvements: list[dict] = []
    for row in cells:
        if row["condition"] == "zero_shot_control" or row["variant"] == "base":
            continue
        control = control_cells[(row["task"], row["variant"])]
        improvements.append(
            {
                "condition": row["condition"],
                "task": row["task"],
                "variant": row["variant"],
                "method_correct": row["correct"],
                "control_correct": control["correct"],
                "total": row["total"],
                "method_accuracy_pct": row["accuracy_pct"],
                "control_accuracy_pct": control["accuracy_pct"],
                "improvement_pp": round(row["accuracy_pct"] - control["accuracy_pct"], 4),
            }
        )

    by_key = {
        (row["condition"], row["task"], row["item_id"], row["variant"]): row for row in scored
    }
    retention: list[dict] = []
    for condition in CONDITIONS[1:]:
        for task, variants in {
            "obfus_fol": ("obfuscation",),
            "obfus_blood_relation": ("obfuscation_l1", "obfuscation_l2"),
            "obfus_number_series": ("obfuscation",),
            "obfus_direction_sense": ("obfuscation",),
        }.items():
            for variant in variants:
                ids = sorted({row["item_id"] for row in scored if row["condition"] == condition and row["task"] == task and row["variant"] == variant})
                counts = Counter()
                for item_id in ids:
                    base_ok = by_key[("zero_shot_control", task, item_id, "base")]["correct"]
                    method_ok = by_key[(condition, task, item_id, variant)]["correct"]
                    counts[(base_ok, method_ok)] += 1
                retention.append(
                    {
                        "condition": condition,
                        "task": task,
                        "variant": variant,
                        "both_correct": counts[(True, True)],
                        "base_only": counts[(True, False)],
                        "method_only": counts[(False, True)],
                        "both_wrong": counts[(False, False)],
                        "total": len(ids),
                    }
                )

    condition_totals: list[dict] = []
    for condition in CONDITIONS:
        relevant = [row for row in scored if row["condition"] == condition and (condition != "zero_shot_control" or row["variant"] != "base")]
        hits = sum(row["correct"] for row in relevant)
        condition_totals.append(
            {
                "condition": condition,
                "scope": "obfuscated variants",
                "correct": hits,
                "total": len(relevant),
                "accuracy_pct": round(100 * hits / len(relevant), 4),
            }
        )

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(ANALYSIS_DIR / "accuracy_by_cell.csv", cells)
    write_csv(ANALYSIS_DIR / "improvement_over_control.csv", improvements)
    write_csv(ANALYSIS_DIR / "paired_retention.csv", retention)
    write_csv(ANALYSIS_DIR / "condition_totals.csv", condition_totals)

    private_scored = source_root.resolve() / "manual_eval" / "private_do_not_upload" / "gpt_sol_5.6_high_assigned_50_scored.csv"
    write_csv(private_scored, scored)
    summary = {
        "model": MODEL,
        "reasoning_effort": "high",
        "control_responses": 450,
        "new_responses": 1200,
        "total_evaluation_units": 1200,
        "scoring_policy": "Repository task normalizers with digit/word Blood Relation count equivalence; Direction distance tolerance is 0.05.",
        "condition_totals": condition_totals,
        "private_row_evidence": str(private_scored),
    }
    public_summary = {key: value for key, value in summary.items() if not key.startswith("private_")}
    (ANALYSIS_DIR / "summary.json").write_text(json.dumps(public_summary, indent=2), encoding="utf-8")

    control = condition_totals[0]
    lines = [
        "# GPT Sol 5.6 High Assigned-Mitigation Results",
        "",
        "All three assigned conditions use 50 underlying items per task and 250 obfuscated targets.",
        "The matched zero-shot row is the fresh control on the same 250 obfuscated forms.",
        "",
        "| Condition | Correct | Accuracy | Change from control |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in condition_totals:
        delta = row["accuracy_pct"] - control["accuracy_pct"]
        lines.append(
            f"| {row['condition']} | {row['correct']}/{row['total']} | {row['accuracy_pct']:.2f}% | {delta:+.2f} pp |"
        )
    lines.extend(
        [
            "",
            "Cell-level accuracy, improvement and paired-retention tables are generated from private scoring evidence.",
            "Row-level gold answers and correctness labels are intentionally not published.",
        ]
    )
    (ANALYSIS_DIR / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(score(args.source_root), indent=2))


if __name__ == "__main__":
    main()
