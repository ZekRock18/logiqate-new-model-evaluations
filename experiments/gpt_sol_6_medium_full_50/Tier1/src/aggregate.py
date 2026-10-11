from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "Dataset"
RESULT_DIR = ROOT / "Result"
ANALYSIS_DIR = ROOT / "Analysis"
SC_QUEUES = tuple(f"self_consistency_path_{index}" for index in (1, 2, 3))
COVE_QUEUES = (
    "self_verification_cove_initial",
    "self_verification_cove_verification",
)
FINAL_MARKER = re.compile(r"FINAL_ANSWER\s*:\s*(.+)", re.IGNORECASE)
COMPASS = r"\b(NORTHEAST|NORTHWEST|SOUTHEAST|SOUTHWEST|NORTH|SOUTH|EAST|WEST)\b"
DIRECTION_ALIASES = {
    "NORTH-EAST": "NORTHEAST",
    "NORTH EAST": "NORTHEAST",
    "EAST OF NORTH": "NORTHEAST",
    "NORTH-WEST": "NORTHWEST",
    "NORTH WEST": "NORTHWEST",
    "WEST OF NORTH": "NORTHWEST",
    "SOUTH-EAST": "SOUTHEAST",
    "SOUTH EAST": "SOUTHEAST",
    "EAST OF SOUTH": "SOUTHEAST",
    "SOUTH-WEST": "SOUTHWEST",
    "SOUTH WEST": "SOUTHWEST",
    "WEST OF SOUTH": "SOUTHWEST",
}
DIRECTION_ABBREV = {
    "NE": "NORTHEAST",
    "NW": "NORTHWEST",
    "SE": "SOUTHEAST",
    "SW": "SOUTHWEST",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write an empty aggregate: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def final_answer(response: str) -> str:
    matches = list(FINAL_MARKER.finditer(str(response or "").strip()))
    if not matches:
        return ""
    return matches[-1].group(1).strip().strip("`*# ")


def squash(text: str) -> str:
    return re.sub(r"[.,;:]+$", "", re.sub(r"\s+", " ", str(text).strip().upper()))


def normalise_fol(text: str) -> str:
    tokens = re.findall(r"\b(TRUE|FALSE)\b", squash(text))
    return tokens[-1] if tokens else squash(text)


def normalise_blood(text: str) -> str:
    value = squash(text)
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
    numbers = re.findall(r"-?\b\d+\b", str(text))
    return numbers[-1] if numbers else squash(text)


def normalise_direction(text: str) -> str:
    value = squash(text)
    for alias, canonical in DIRECTION_ALIASES.items():
        value = value.replace(alias, canonical)
    for short, canonical in DIRECTION_ABBREV.items():
        value = re.sub(rf"\b{short}\b", canonical, value)
    away = re.search(r"(\w+),?\s*(\d+(?:\.\d+)?)\s*(?:KM|M|BLOCKS?)\s*AWAY", value)
    if away:
        direction, distance = away.groups()
        return f"{distance} KM, {direction}"
    distance_direction = re.search(r"(\d+(?:\.\d+)?)\s*(?:KM|M|BLOCKS?),?\s*(\w+)", value)
    if distance_direction:
        distance, direction = distance_direction.groups()
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


def normalise(task: str, answer: str) -> str:
    return NORMALISERS[task](answer)


def is_correct(task: str, prediction: str, gold: str) -> bool:
    predicted = normalise(task, prediction)
    expected = normalise(task, gold)
    if not predicted or not expected:
        return False
    if predicted == expected:
        return True
    if task != "obfus_direction_sense":
        return False
    predicted_direction = re.search(COMPASS, predicted)
    expected_direction = re.search(COMPASS, expected)
    if (
        not predicted_direction
        or not expected_direction
        or predicted_direction.group(1) != expected_direction.group(1)
    ):
        return False
    predicted_distance = re.search(r"-?\d+(?:\.\d+)?", predicted)
    expected_distance = re.search(r"-?\d+(?:\.\d+)?", expected)
    if not predicted_distance or not expected_distance:
        return True
    return abs(float(predicted_distance.group()) - float(expected_distance.group())) <= 0.05


def _complete_result(queue: str, expected: int) -> list[dict[str, str]]:
    dataset_path = DATASET_DIR / f"{queue}.csv"
    result_path = RESULT_DIR / f"{queue}.csv"
    if not dataset_path.exists() or not result_path.exists():
        raise FileNotFoundError(f"missing Dataset/Result pair for {queue}")
    dataset = read_csv(dataset_path)
    result = read_csv(result_path)
    if len(dataset) != expected or len(result) != expected:
        raise ValueError(f"{queue}: expected {expected} rows, found {len(dataset)}/{len(result)}")
    immutable = [column for column in dataset[0] if column != "model_response"]
    for source, answer in zip(dataset, result):
        if any(source[column] != answer[column] for column in immutable):
            raise ValueError(f"{queue}: immutable Dataset/Result fields differ")
        if not answer["model_response"].strip() or not final_answer(answer["model_response"]):
            raise ValueError(f"{queue}: unresolved or unparsable {answer['response_id']}")
    return result


def aggregate_self_consistency() -> list[dict]:
    path_rows = [_complete_result(queue, 450) for queue in SC_QUEUES]
    indexes = [{row["evaluation_id"]: row for row in rows} for rows in path_rows]
    if any(len(index) != 450 for index in indexes):
        raise ValueError("self-consistency evaluation IDs are not unique")
    evaluation_ids = set(indexes[0])
    if any(set(index) != evaluation_ids for index in indexes[1:]):
        raise ValueError("self-consistency paths do not cover identical evaluations")

    aggregates: list[dict] = []
    for evaluation_id in sorted(evaluation_ids):
        rows = [index[evaluation_id] for index in indexes]
        identity = (rows[0]["task"], rows[0]["item_id"], rows[0]["variant"])
        if any((row["task"], row["item_id"], row["variant"]) != identity for row in rows[1:]):
            raise ValueError(f"self-consistency identity mismatch: {evaluation_id}")
        answers = [final_answer(row["model_response"]) for row in rows]
        normalized = [normalise(row["task"], answer) for row, answer in zip(rows, answers)]
        counts = Counter(value for value in normalized if value)
        winner, votes = counts.most_common(1)[0] if counts else ("", 0)
        consensus = winner if votes >= 2 else "NO_CONSENSUS"
        agreement = "unanimous" if votes == 3 else "majority" if votes == 2 else "none"
        aggregates.append(
            {
                "condition": "self_consistency",
                "evaluation_id": evaluation_id,
                "task": rows[0]["task"],
                "item_id": rows[0]["item_id"],
                "variant": rows[0]["variant"],
                "path_1_response_id": rows[0]["response_id"],
                "path_2_response_id": rows[1]["response_id"],
                "path_3_response_id": rows[2]["response_id"],
                "path_1_answer": answers[0],
                "path_2_answer": answers[1],
                "path_3_answer": answers[2],
                "path_1_normalized": normalized[0],
                "path_2_normalized": normalized[1],
                "path_3_normalized": normalized[2],
                "winning_votes": votes,
                "agreement": agreement,
                "final_answer": consensus,
                "status": "answered" if votes >= 2 else "no_consensus",
            }
        )
    write_csv(ANALYSIS_DIR / "self_consistency_aggregates.csv", aggregates)
    return aggregates


def aggregate_cove() -> list[dict]:
    initial_rows = _complete_result(COVE_QUEUES[0], 450)
    verification_rows = _complete_result(COVE_QUEUES[1], 450)
    initial = {row["evaluation_id"]: row for row in initial_rows}
    verification = {row["evaluation_id"]: row for row in verification_rows}
    if len(initial) != 450 or len(verification) != 450 or set(initial) != set(verification):
        raise ValueError("CoVe initial and verification evaluation IDs do not match")

    aggregates: list[dict] = []
    for evaluation_id in sorted(initial):
        first = initial[evaluation_id]
        second = verification[evaluation_id]
        if second["depends_on_response_id"] != first["response_id"]:
            raise ValueError(f"CoVe dependency mismatch: {evaluation_id}")
        identity = (first["task"], first["item_id"], first["variant"])
        if (second["task"], second["item_id"], second["variant"]) != identity:
            raise ValueError(f"CoVe identity mismatch: {evaluation_id}")
        initial_answer = final_answer(first["model_response"])
        verified_answer = final_answer(second["model_response"])
        initial_normalized = normalise(first["task"], initial_answer)
        final_normalized = normalise(first["task"], verified_answer)
        aggregates.append(
            {
                "condition": "self_verification_cove",
                "evaluation_id": evaluation_id,
                "task": first["task"],
                "item_id": first["item_id"],
                "variant": first["variant"],
                "initial_response_id": first["response_id"],
                "verification_response_id": second["response_id"],
                "initial_answer": initial_answer,
                "initial_normalized": initial_normalized,
                "final_answer": verified_answer,
                "final_normalized": final_normalized,
                "answer_changed": initial_normalized != final_normalized,
                "status": "answered",
            }
        )
    write_csv(ANALYSIS_DIR / "cove_aggregates.csv", aggregates)
    return aggregates


def aggregate() -> dict:
    self_consistency = aggregate_self_consistency()
    cove = aggregate_cove()
    summary = {
        "self_consistency_evaluations": len(self_consistency),
        "self_consistency_raw_paths": len(self_consistency) * 3,
        "self_consistency_agreement": dict(Counter(row["agreement"] for row in self_consistency)),
        "cove_evaluations": len(cove),
        "cove_raw_passes": len(cove) * 2,
        "cove_answers_changed": sum(row["answer_changed"] for row in cove),
    }
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    (ANALYSIS_DIR / "aggregation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(aggregate(), indent=2))
