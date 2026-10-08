from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


COMMON_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ROOT = COMMON_ROOT.parent
sys.path.insert(0, str(COMMON_ROOT / "src"))

from config import (  # noqa: E402
    CONDITIONS,
    N_DEMONSTRATIONS,
    N_TEST,
    TASKS,
    expected_api_call_count,
    expected_evaluation_count,
)


def load_json(relative_path: str) -> dict:
    return json.loads((COMMON_ROOT / relative_path).read_text(encoding="utf-8"))


def test_public_manifest_invariants():
    manifest = load_json("data/sample_manifest.json")
    assert manifest["questions_per_task"] == N_TEST == 15
    assert manifest["demonstrations_per_task"] == N_DEMONSTRATIONS == 2
    assert set(manifest["tasks"]) == set(TASKS)
    for task in TASKS:
        test_ids = manifest["tasks"][task]["test_item_ids"]
        demonstration_ids = manifest["tasks"][task]["demonstration_item_ids"]
        assert len(test_ids) == len(set(test_ids)) == N_TEST
        assert len(demonstration_ids) == len(set(demonstration_ids)) == N_DEMONSTRATIONS
        assert set(test_ids).isdisjoint(demonstration_ids)


def test_public_manifest_contains_no_answers():
    text = (COMMON_ROOT / "data" / "sample_manifest.json").read_text(encoding="utf-8")
    assert "correct_answer" not in text
    assert "gold_answer" not in text


def test_full_matrix_counts():
    assert expected_evaluation_count() == 1035
    assert expected_api_call_count() == 1440


def test_required_condition_mapping():
    assert set(CONDITIONS["normalize_then_solve"].tasks) == {
        "obfus_fol",
        "obfus_blood_relation",
    }
    assert set(CONDITIONS["structured_decomposition"].tasks) == {
        "obfus_blood_relation",
        "obfus_direction_sense",
    }
    assert set(CONDITIONS["explicit_task_instructions"].tasks) == {
        "obfus_number_series",
        "obfus_direction_sense",
    }
    assert CONDITIONS["self_consistency"].paths == 3
    assert CONDITIONS["self_consistency"].temperature == 0.7


def test_prompt_template_coverage():
    payload = load_json("prompts/prompt_templates.json")
    covered_conditions = (
        set(payload["condition_instructions"])
        | set(payload["task_specific_method_instructions"])
        | {"obf_to_obf_few_shot", "base_to_obf_paired_few_shot"}
    )
    assert set(CONDITIONS).issubset(covered_conditions)
    assert {
        "single",
        "zero_shot",
        "obf_to_obf_few_shot",
        "base_to_obf_paired_few_shot",
        "cove_verification",
    }.issubset(payload["templates"])


def test_summary_is_complete():
    summary = load_json("results/summary.json")
    assert summary["expected_evaluations"] == 1035
    assert summary["completed_evaluations"] == 1035
    assert summary["missing_evaluations"] == 0
    assert summary["api_usage"]["api_calls"] == 1440
    assert sum(summary["status_counts"].values()) == 1035


def test_accuracy_table_covers_every_condition():
    with (COMMON_ROOT / "results" / "accuracy_by_cell.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert {row["condition"] for row in rows} == set(CONDITIONS)
    assert all(int(row["total"]) == 15 for row in rows)


def test_all_notebooks_are_valid_json():
    notebooks = sorted(EXPERIMENT_ROOT.rglob("*.ipynb"))
    assert len(notebooks) == 13
    for notebook in notebooks:
        payload = json.loads(notebook.read_text(encoding="utf-8"))
        assert payload["nbformat"] == 4
