from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PARENT_ROOT = ROOT.parent
DATASET_DIR = ROOT / "Dataset"
RESULT_DIR = ROOT / "Result"
PROMPT_PATH = ROOT / "prompts" / "tier1_prompt_templates.json"
PARENT_MANIFEST_PATH = PARENT_ROOT / "sample_manifest.json"
MANIFEST_PATH = ROOT / "tier1_manifest.json"
MODEL = "gpt-6-sol"
REASONING_EFFORT = "medium"
N_TEST = 50

TASKS = (
    "obfus_fol",
    "obfus_blood_relation",
    "obfus_number_series",
    "obfus_direction_sense",
)
VARIANTS = {
    "obfus_fol": ("base", "obfuscation"),
    "obfus_blood_relation": ("base", "obfuscation_l1", "obfuscation_l2"),
    "obfus_number_series": ("base", "obfuscation"),
    "obfus_direction_sense": ("base", "obfuscation"),
}
METHODS = {
    "normalize_then_solve": {
        "obfus_fol": VARIANTS["obfus_fol"],
        "obfus_blood_relation": VARIANTS["obfus_blood_relation"],
    },
    "structured_decomposition": {
        "obfus_blood_relation": VARIANTS["obfus_blood_relation"],
        "obfus_direction_sense": VARIANTS["obfus_direction_sense"],
    },
    "explicit_task_instructions": {
        "obfus_number_series": VARIANTS["obfus_number_series"],
        "obfus_direction_sense": VARIANTS["obfus_direction_sense"],
    },
    "chain_of_thought": {task: VARIANTS[task] for task in TASKS},
    "rereading_s2a": {
        "obfus_fol": VARIANTS["obfus_fol"],
        "obfus_blood_relation": ("base", "obfuscation_l2"),
    },
    "self_consistency": {task: VARIANTS[task] for task in TASKS},
    "self_verification_cove": {task: VARIANTS[task] for task in TASKS},
}
SINGLE_METHODS = (
    "normalize_then_solve",
    "structured_decomposition",
    "explicit_task_instructions",
    "chain_of_thought",
    "rereading_s2a",
)
FIELDS = (
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
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def slug(text: str) -> str:
    return (
        text.replace("obfus_", "")
        .replace("obfuscation_", "obf_")
        .replace("obfuscation", "obf")
    )


def question_block(item) -> str:
    if item.task == "obfus_fol":
        return item.question
    if item.task == "obfus_number_series":
        return f"Sequence: {item.question}"
    return f"Question: {item.question}"


def evaluation_id(condition: str, task: str, item_id: str, variant: str) -> str:
    suffix = item_id.rsplit("-", 1)[1]
    return f"gpt6-tier1-{slug(condition)}-{slug(task)}-{suffix}-{slug(variant)}"


def response_id(evaluation: str, stage: str, path_index: int | None = None) -> str:
    if path_index is not None:
        return f"{evaluation}-path{path_index}"
    if stage == "single":
        return evaluation
    return f"{evaluation}-{stage}"


def render(condition: str, item, templates: dict) -> str:
    condition_instruction = templates["condition_instructions"][condition]
    task_specific = (
        templates.get("task_specific_method_instructions", {})
        .get(condition, {})
        .get(item.task, "")
    )
    return templates["templates"]["single"].format(
        condition_instruction=condition_instruction,
        task_specific_instruction=task_specific,
        task_instruction=templates["task_instructions"][item.task],
        question=question_block(item),
    ).strip()


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def build_rows(
    queue: str,
    condition: str,
    stage: str,
    task_matrix: dict[str, tuple[str, ...]],
    item_index: dict,
    test_ids: dict[str, list[str]],
    templates: dict,
    path_index: int | None = None,
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for task, variants in task_matrix.items():
        for item_id in test_ids[task]:
            for variant in variants:
                item = item_index[(task, item_id, variant)]
                evaluation = evaluation_id(condition, task, item_id, variant)
                records.append(
                    {
                        "queue": queue,
                        "condition": condition,
                        "stage": stage,
                        "path_index": str(path_index or ""),
                        "row_number": str(len(records) + 1),
                        "response_id": response_id(evaluation, stage, path_index),
                        "evaluation_id": evaluation,
                        "task": task,
                        "item_id": item_id,
                        "variant": variant,
                        "prompt": render(condition, item, templates),
                        "depends_on_response_id": "",
                        "model_response": "",
                    }
                )
    return records


def prepare(source_root: Path) -> dict:
    if any(RESULT_DIR.glob("*.csv")):
        raise RuntimeError("refusing to regenerate Tier1 datasets after result files exist")
    templates = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    if templates["version"] != "gpt6-tier1-v1":
        raise ValueError(f"unexpected prompt version {templates['version']!r}")
    parent_manifest = json.loads(PARENT_MANIFEST_PATH.read_text(encoding="utf-8"))
    if parent_manifest["questions_per_task"] != N_TEST:
        raise ValueError("parent sample is not the fixed 50-item sample")
    test_ids = {
        task: list(parent_manifest["tasks"][task]["test_item_ids"])
        for task in TASKS
    }
    for task, ids in test_ids.items():
        if len(ids) != N_TEST or len(set(ids)) != N_TEST:
            raise ValueError(f"{task}: expected 50 unique fixed IDs")

    source_root = source_root.resolve()
    dataset_module = load_module("gpt6_tier1_source_dataset", source_root / "src" / "dataset.py")
    items = dataset_module.load_all()
    item_index = {(item.task, item.item_id, item.variant): item for item in items}
    required = {
        (task, item_id, variant)
        for task in TASKS
        for item_id in test_ids[task]
        for variant in VARIANTS[task]
    }
    missing = sorted(required - set(item_index))
    if missing:
        raise ValueError(f"source dataset is missing {len(missing)} fixed rows")

    queue_counts: dict[str, int] = {}
    for condition in SINGLE_METHODS:
        rows = build_rows(
            condition,
            condition,
            "single",
            METHODS[condition],
            item_index,
            test_ids,
            templates,
        )
        write_csv(DATASET_DIR / f"{condition}.csv", rows)
        queue_counts[condition] = len(rows)

    for path_index in (1, 2, 3):
        queue = f"self_consistency_path_{path_index}"
        rows = build_rows(
            queue,
            "self_consistency",
            f"path_{path_index}",
            METHODS["self_consistency"],
            item_index,
            test_ids,
            templates,
            path_index,
        )
        write_csv(DATASET_DIR / f"{queue}.csv", rows)
        queue_counts[queue] = len(rows)

    cove_queue = "self_verification_cove_initial"
    cove_rows = build_rows(
        cove_queue,
        "self_verification_cove",
        "initial",
        METHODS["self_verification_cove"],
        item_index,
        test_ids,
        templates,
    )
    write_csv(DATASET_DIR / f"{cove_queue}.csv", cove_rows)
    queue_counts[cove_queue] = len(cove_rows)

    expected_counts = {
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
    if queue_counts != expected_counts:
        raise AssertionError({"expected": expected_counts, "actual": queue_counts})

    manifest = {
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "prompt_version": templates["version"],
        "fixed_sample_source": "../sample_manifest.json",
        "fixed_sample_sha256": hashlib.sha256(PARENT_MANIFEST_PATH.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "questions_per_task": N_TEST,
        "task_test_item_ids": test_ids,
        "method_task_matrix": {
            method: {task: list(variants) for task, variants in matrix.items()}
            for method, matrix in METHODS.items()
        },
        "evaluation_units": {
            method: N_TEST * sum(len(variants) for variants in matrix.values())
            for method, matrix in METHODS.items()
        },
        "prepared_queue_rows": queue_counts,
        "prepared_model_responses": sum(queue_counts.values()),
        "pending_cove_verification_responses": 450,
        "total_planned_model_responses": sum(queue_counts.values()) + 450,
        "dataset_sha256": {
            path.name: hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for path in sorted(DATASET_DIR.glob("*.csv"))
        },
        "note": "No gold answers or correctness labels are included. CoVe verification is built only after all initial responses are retained.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare fixed-sample GPT Tier 1 queues")
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source_root), indent=2))


if __name__ == "__main__":
    main()
