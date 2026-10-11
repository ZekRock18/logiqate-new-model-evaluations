from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONDITIONS = {
    "zero_shot_control": 450,
    "obf_to_obf_few_shot": 250,
    "base_to_obf_paired_few_shot": 250,
    "analogical_prompting": 250,
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_manifest_has_fixed_full_sample_and_external_demos():
    manifest = json.loads((ROOT / "sample_manifest.json").read_text(encoding="utf-8"))
    assert manifest["model"] == "gpt-5.6-sol"
    assert manifest["reasoning_effort"] == "high"
    for data in manifest["tasks"].values():
        assert len(data["test_item_ids"]) == len(set(data["test_item_ids"])) == 50
        assert len(data["demonstration_item_ids"]) == len(set(data["demonstration_item_ids"])) == 2
        assert not set(data["test_item_ids"]) & set(data["demonstration_item_ids"])
    blocks = list(manifest["tasks"]["obfus_number_series"]["number_series_test_blocks"].values())
    assert {block: blocks.count(block) for block in (1, 2, 3)} == {1: 17, 2: 17, 3: 16}


def test_dataset_matrix_and_global_response_ids():
    ids: list[str] = []
    for condition, expected in CONDITIONS.items():
        records = rows(ROOT / "Dataset" / f"{condition}.csv")
        assert len(records) == expected
        assert {record["condition"] for record in records} == {condition}
        assert all(record["prompt"].strip() for record in records)
        assert all(not record["model_response"].strip() for record in records)
        ids.extend(record["response_id"] for record in records)
    assert len(ids) == len(set(ids)) == 1200


def test_results_complete_and_immutable():
    for condition, expected in CONDITIONS.items():
        dataset = rows(ROOT / "Dataset" / f"{condition}.csv")
        result = rows(ROOT / "Result" / f"{condition}.csv")
        assert len(result) == expected
        assert all(record["model_response"].strip() for record in result)
        for source, submitted in zip(dataset, result):
            for field in source:
                if field != "model_response":
                    assert source[field] == submitted[field]


def test_latest_journal_answers_match_results():
    for condition in CONDITIONS:
        journal = ROOT / "Result" / f"_answer_journal_{condition}.jsonl"
        latest = {}
        for line in journal.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                latest[record["response_id"]] = record["answer"].strip()
        result = rows(ROOT / "Result" / f"{condition}.csv")
        assert len(latest) == len(result)
        assert all(latest[row["response_id"]] == row["model_response"].strip() for row in result)


def test_publication_excludes_private_row_labels_and_secrets():
    forbidden_names = {"answer_key.json", "scoring_manifest.json", "scored_responses.csv"}
    assert not any(path.name in forbidden_names for path in ROOT.rglob("*"))
    for path in ROOT.rglob("*.csv"):
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            fields = csv.DictReader(handle).fieldnames or []
        assert not {"gold", "ground_truth", "correct_answer", "is_correct"} & set(fields)
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".json", ".ipynb"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert ("s" + "k-") not in text
            assert ("gh" + "p_") not in text


def test_public_aggregates_exist_without_row_evidence():
    summary = json.loads((ROOT / "Analysis" / "summary.json").read_text(encoding="utf-8"))
    assert summary["total_evaluation_units"] == 1200
    assert summary["new_responses"] == 1200
    assert len(rows(ROOT / "Analysis" / "condition_totals.csv")) == 4
    assert len(rows(ROOT / "Analysis" / "accuracy_by_cell.csv")) == 24
    assert len(list((ROOT / "notebooks").glob("*.ipynb"))) == 6
