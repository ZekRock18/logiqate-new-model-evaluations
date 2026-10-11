from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARENT_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from aggregate import final_answer, normalise  # noqa: E402


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
QUEUE_COUNTS = {
    "normalize_then_solve": 250,
    "structured_decomposition": 250,
    "explicit_task_instructions": 200,
    "chain_of_thought": 450,
    "rereading_s2a": 200,
    "self_consistency_path_1": 450,
    "self_consistency_path_2": 450,
    "self_consistency_path_3": 450,
    "self_verification_cove_initial": 450,
}
METHOD_UNITS = {
    "normalize_then_solve": 250,
    "structured_decomposition": 250,
    "explicit_task_instructions": 200,
    "chain_of_thought": 450,
    "rereading_s2a": 200,
    "self_consistency": 450,
    "self_verification_cove": 450,
}
EXPECTED_MATRIX = {
    "normalize_then_solve": {
        "obfus_fol": ["base", "obfuscation"],
        "obfus_blood_relation": ["base", "obfuscation_l1", "obfuscation_l2"],
    },
    "structured_decomposition": {
        "obfus_blood_relation": ["base", "obfuscation_l1", "obfuscation_l2"],
        "obfus_direction_sense": ["base", "obfuscation"],
    },
    "explicit_task_instructions": {
        "obfus_number_series": ["base", "obfuscation"],
        "obfus_direction_sense": ["base", "obfuscation"],
    },
    "chain_of_thought": {
        "obfus_fol": ["base", "obfuscation"],
        "obfus_blood_relation": ["base", "obfuscation_l1", "obfuscation_l2"],
        "obfus_number_series": ["base", "obfuscation"],
        "obfus_direction_sense": ["base", "obfuscation"],
    },
    "rereading_s2a": {
        "obfus_fol": ["base", "obfuscation"],
        "obfus_blood_relation": ["base", "obfuscation_l2"],
    },
    "self_consistency": {
        "obfus_fol": ["base", "obfuscation"],
        "obfus_blood_relation": ["base", "obfuscation_l1", "obfuscation_l2"],
        "obfus_number_series": ["base", "obfuscation"],
        "obfus_direction_sense": ["base", "obfuscation"],
    },
    "self_verification_cove": {
        "obfus_fol": ["base", "obfuscation"],
        "obfus_blood_relation": ["base", "obfuscation_l1", "obfuscation_l2"],
        "obfus_number_series": ["base", "obfuscation"],
        "obfus_direction_sense": ["base", "obfuscation"],
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == FIELDS
        return list(reader)


def test_exact_fixed_sample_matrix_and_counts():
    manifest = json.loads((ROOT / "tier1_manifest.json").read_text(encoding="utf-8"))
    parent = json.loads((PARENT_ROOT / "sample_manifest.json").read_text(encoding="utf-8"))
    assert manifest["questions_per_task"] == parent["questions_per_task"] == 50
    assert manifest["method_task_matrix"] == EXPECTED_MATRIX
    assert manifest["evaluation_units"] == METHOD_UNITS
    assert manifest["prepared_queue_rows"] == QUEUE_COUNTS
    assert sum(METHOD_UNITS.values()) == 2250
    assert manifest["prepared_model_responses"] == 3150
    assert manifest["pending_cove_verification_responses"] == 450
    assert manifest["total_planned_model_responses"] == 3600
    for task, ids in manifest["task_test_item_ids"].items():
        assert ids == parent["tasks"][task]["test_item_ids"]
        assert len(ids) == len(set(ids)) == 50


def test_prepared_queue_shapes_and_global_response_ids():
    response_ids = []
    cells: dict[str, set[tuple[str, str]]] = {}
    for queue, expected in QUEUE_COUNTS.items():
        rows = read_csv(ROOT / "Dataset" / f"{queue}.csv")
        assert len(rows) == expected
        assert len({row["response_id"] for row in rows}) == expected
        response_ids.extend(row["response_id"] for row in rows)
        condition = rows[0]["condition"]
        cells.setdefault(condition, set()).update((row["task"], row["variant"]) for row in rows)
        assert all(row["prompt"].strip() for row in rows)
        assert all("FINAL_ANSWER:" in row["prompt"] for row in rows)
        assert all(not row["model_response"] for row in rows)
    assert len(response_ids) == len(set(response_ids)) == 3150
    for condition, matrix in EXPECTED_MATRIX.items():
        expected_cells = {(task, variant) for task, variants in matrix.items() for variant in variants}
        assert cells[condition] == expected_cells
    sc_evaluations = []
    for path_index in (1, 2, 3):
        rows = read_csv(ROOT / "Dataset" / f"self_consistency_path_{path_index}.csv")
        assert {row["path_index"] for row in rows} == {str(path_index)}
        assert {row["stage"] for row in rows} == {f"path_{path_index}"}
        sc_evaluations.append({row["evaluation_id"] for row in rows})
    assert sc_evaluations[0] == sc_evaluations[1] == sc_evaluations[2]
    assert len(sc_evaluations[0]) == 450


def test_result_rows_match_datasets_and_latest_journals():
    result_dir = ROOT / "Result"
    for result_path in sorted(result_dir.glob("*.csv")):
        queue = result_path.stem
        dataset_path = ROOT / "Dataset" / result_path.name
        assert dataset_path.exists()
        source = read_csv(dataset_path)
        result = read_csv(result_path)
        assert len(source) == len(result)
        immutable = [column for column in FIELDS if column != "model_response"]
        for expected, actual in zip(source, result):
            assert all(expected[column] == actual[column] for column in immutable)
        journal_path = result_dir / f"_answer_journal_{queue}.jsonl"
        latest = {}
        if journal_path.exists():
            for line in journal_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                assert record["queue"] == queue
                latest[record["response_id"]] = record
        answered = {row["response_id"]: row for row in result if row["model_response"].strip()}
        assert set(answered) == set(latest)
        for response_id, row in answered.items():
            assert latest[response_id]["response"] == row["model_response"]
            assert latest[response_id]["evaluation_id"] == row["evaluation_id"]
            assert final_answer(row["model_response"])


def test_self_consistency_aggregate_invariants_if_present():
    path = ROOT / "Analysis" / "self_consistency_aggregates.csv"
    if not path.exists():
        return
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 450
    assert len({row["evaluation_id"] for row in rows}) == 450
    for row in rows:
        normalized = [row[f"path_{index}_normalized"] for index in (1, 2, 3)]
        count = Counter(normalized)
        winner, votes = count.most_common(1)[0]
        assert int(row["winning_votes"]) == votes
        if votes >= 2:
            assert row["final_answer"] == winner
            assert row["status"] == "answered"
            assert row["agreement"] == ("unanimous" if votes == 3 else "majority")
        else:
            assert row["final_answer"] == "NO_CONSENSUS"
            assert row["status"] == "no_consensus"
            assert row["agreement"] == "none"


def test_cove_dependency_and_aggregate_invariants_if_present():
    verification_path = ROOT / "Dataset" / "self_verification_cove_verification.csv"
    if not verification_path.exists():
        return
    initial_rows = read_csv(ROOT / "Result" / "self_verification_cove_initial.csv")
    verification_rows = read_csv(verification_path)
    initial = {row["evaluation_id"]: row for row in initial_rows}
    assert len(initial) == len(verification_rows) == 450
    for row in verification_rows:
        first = initial[row["evaluation_id"]]
        assert row["depends_on_response_id"] == first["response_id"]
        assert first["model_response"] in row["prompt"]
    aggregate_path = ROOT / "Analysis" / "cove_aggregates.csv"
    if not aggregate_path.exists():
        return
    with aggregate_path.open("r", newline="", encoding="utf-8-sig") as handle:
        aggregates = list(csv.DictReader(handle))
    assert len(aggregates) == 450
    assert len({row["evaluation_id"] for row in aggregates}) == 450
    for row in aggregates:
        assert (row["answer_changed"].lower() == "true") == (
            row["initial_normalized"] != row["final_normalized"]
        )


def test_completed_publication_outputs_if_scored():
    summary_path = ROOT / "Analysis" / "summary.json"
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["conditions"] == 7
    assert summary["task_variant_cells"] == 45
    assert summary["evaluation_units"] == summary["completed_evaluations"] == 2250
    assert summary["raw_model_generations"] == 3600
    with (ROOT / "Analysis" / "accuracy_by_cell.csv").open(
        "r", newline="", encoding="utf-8-sig"
    ) as handle:
        cells = list(csv.DictReader(handle))
    assert len(cells) == 45
    assert all(int(row["total"]) == 50 for row in cells)
    with (ROOT / "Analysis" / "improvement_over_control.csv").open(
        "r", newline="", encoding="utf-8-sig"
    ) as handle:
        improvements = list(csv.DictReader(handle))
    assert len(improvements) == 25


def test_public_artifacts_exclude_private_evidence_and_secrets():
    forbidden_names = {
        "answer" + "_key.json",
        "scoring" + "_manifest.json",
        "scored" + "_responses.csv",
        "incorrect" + "_responses.csv",
        "private" + "_do_not_upload",
    }
    for path in ROOT.rglob("*"):
        assert path.name.lower() not in forbidden_names
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="strict")
        assert not re.search(r"(?:sk|ghp)[-_][A-Za-z0-9]{20,}", text)
        if path.suffix.lower() == ".csv":
            header = text.splitlines()[0].lower() if text else ""
            assert "gold_answer" not in header
            assert "correct_answer" not in header
            assert "is_correct" not in header
        elif path.suffix.lower() == ".json":
            payload = json.loads(text)
            serialized = json.dumps(payload)
            assert '"gold_answer"' not in serialized
            assert '"correct_answer"' not in serialized
            assert '"is_correct"' not in serialized
            assert '"private_row_evidence"' not in serialized


def test_normalization_smoke_cases():
    assert final_answer("Reasoning; FINAL_ANSWER: TRUE") == "TRUE"
    assert normalise("obfus_fol", "true") == "TRUE"
    assert normalise("obfus_blood_relation", "grand-father") == "GRANDFATHER"
    assert normalise("obfus_blood_relation", "2") == normalise("obfus_blood_relation", "Two") == "2"
    assert normalise("obfus_number_series", "The answer is 42") == "42"
    assert normalise("obfus_direction_sense", "5 km north-east") == "5 KM, NORTHEAST"
