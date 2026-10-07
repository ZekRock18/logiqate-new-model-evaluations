from __future__ import annotations

import json
import sys
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_ROOT / "src"))

from config import (  # noqa: E402
    CONDITIONS,
    N_TEST,
    TASKS,
    expected_api_call_count,
    expected_evaluation_count,
)
from data import (  # noqa: E402
    PUBLIC_MANIFEST,
    demonstration_items,
    get_item,
    load_public_manifest,
    prepare_sample,
    validate_manifests,
)
from prompts import render_prompt, snapshot_prompts, validate_prompt_snapshot  # noqa: E402
from run import _normalise_for_vote, parse_answer  # noqa: E402


def setup_module():
    prepare_sample()
    snapshot_prompts()


def test_manifest_invariants():
    result = validate_manifests()
    assert result["tasks"] == 4
    assert result["test_items_per_task"] == 15
    manifest = load_public_manifest()
    for task in TASKS:
        assert len(set(manifest["tasks"][task]["test_item_ids"])) == N_TEST
        assert not (
            set(manifest["tasks"][task]["test_item_ids"])
            & set(manifest["tasks"][task]["demonstration_item_ids"])
        )


def test_public_manifest_has_no_answer_fields():
    payload = json.loads(PUBLIC_MANIFEST.read_text(encoding="utf-8"))
    assert "correct_answer" not in json.dumps(payload)
    assert "gold_answer" not in json.dumps(payload)


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


def test_prompt_snapshots_complete_and_parseable():
    result = validate_prompt_snapshot()
    assert result["prompt_count"] == 1035


def test_few_shot_prompt_uses_disjoint_demonstrations():
    manifest = load_public_manifest()
    task = "obfus_fol"
    item_id = manifest["tasks"][task]["test_item_ids"][0]
    item = get_item(task, item_id, "obfuscation")
    prompt, demo_ids = render_prompt("base_to_obf_paired_few_shot", item)
    assert "PAIRED DEMONSTRATION" in prompt
    assert set(demo_ids).isdisjoint(manifest["tasks"][task]["test_item_ids"])


def test_task_specific_answer_parser():
    assert parse_answer("obfus_fol", "Reasoning\nFINAL_ANSWER: true") == "TRUE"
    assert parse_answer("obfus_number_series", "FINAL_ANSWER: -42") == "-42"
    assert parse_answer("obfus_blood_relation", "FINAL_ANSWER: Sister-in-law") == "Sister-in-law"
    assert parse_answer("obfus_direction_sense", "FINAL_ANSWER: 5 km, North-East") == "5 km, North-East"


def test_direction_vote_canonicalizes_equivalent_forms():
    forms = [
        r"4\sqrt{5} km, approximately 63.4 degrees north of east",
        "8.94 km, 63.4 degrees North of East",
        "4√5 km (about 8.94 km) at 63.4 degrees North of East",
    ]
    assert {_normalise_for_vote("obfus_direction_sense", value) for value in forms} == {
        "8.94 KM|NORTHEAST"
    }
