from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "Dataset"
RESULT_DIR = ROOT / "Result"
PROMPT_PATH = ROOT / "prompts" / "prompt_templates.json"
PUBLIC_MANIFEST = ROOT / "sample_manifest.json"
MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "high"
SOURCE_SEED = 20260925
DEMO_SEED = 20261011
N_TEST = 50
N_DEMOS = 2

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
OBFUSCATED = {task: tuple(v for v in variants if v != "base") for task, variants in VARIANTS.items()}
CONDITIONS = (
    "zero_shot_control",
    "obf_to_obf_few_shot",
    "base_to_obf_paired_few_shot",
    "analogical_prompting",
)
FIELDS = (
    "condition",
    "row_number",
    "response_id",
    "task",
    "item_id",
    "variant",
    "prompt",
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def question_block(item) -> str:
    if item.task == "obfus_fol":
        return item.question
    if item.task == "obfus_number_series":
        return f"Sequence: {item.question}"
    return f"Question: {item.question}"


def slug(text: str) -> str:
    return text.replace("obfus_", "").replace("obfuscation_", "obf_").replace("obfuscation", "obf")


def response_id(condition: str, task: str, item_id: str, variant: str) -> str:
    return f"gpt56-{slug(condition)}-{slug(task)}-{item_id.rsplit('-', 1)[1]}-{slug(variant)}"


def render(condition: str, item, demos: list, templates: dict) -> str:
    task_instruction = templates["task_instructions"][item.task]
    question = question_block(item)
    demonstration_text = ""
    if condition == "obf_to_obf_few_shot":
        blocks = []
        for number, demo in enumerate(demos, 1):
            obf = demo[item.variant]
            blocks.append(
                f"DEMONSTRATION {number}\n{question_block(obf)}\nFINAL_ANSWER: {obf.answer}"
            )
        demonstration_text = "\n\n".join(blocks)
    elif condition == "base_to_obf_paired_few_shot":
        blocks = []
        for number, demo in enumerate(demos, 1):
            base = demo["base"]
            obf = demo[item.variant]
            blocks.append(
                f"PAIRED DEMONSTRATION {number}\n"
                f"CLEAN FORM\n{question_block(base)}\nCLEAN ANSWER: {base.answer}\n\n"
                f"OBFUSCATED FORM\n{question_block(obf)}\nOBFUSCATED ANSWER: {obf.answer}"
            )
        demonstration_text = "\n\n".join(blocks)
    return templates["templates"][condition].format(
        demonstrations=demonstration_text,
        task_instruction=task_instruction,
        question=question,
    ).strip()


def prepare(source_root: Path) -> dict:
    source_root = source_root.resolve()
    dataset_module = load_module("gpt56_source_dataset", source_root / "src" / "dataset.py")
    obfuscate_module = load_module("gpt56_source_obfuscate", source_root / "src" / "obfuscate.py")
    answer_key_path = source_root / "manual_eval" / "private_do_not_upload" / "answer_key.json"
    answer_key = json.loads(answer_key_path.read_text(encoding="utf-8"))
    if answer_key["seed"] != SOURCE_SEED:
        raise ValueError(f"unexpected source seed {answer_key['seed']}")

    zero_records = [record for record in answer_key["records"] if record["setting"] == "zero_shot"]
    test_ids = {
        task: sorted({record["item_id"] for record in zero_records if record["task"] == task})
        for task in TASKS
    }
    if any(len(ids) != N_TEST for ids in test_ids.values()):
        raise AssertionError({task: len(ids) for task, ids in test_ids.items()})

    items = dataset_module.load_all()
    item_index = {(item.task, item.item_id, item.variant): item for item in items}
    ids_by_task = {
        task: sorted({item.item_id for item in items if item.task == task}) for task in TASKS
    }
    demo_ids: dict[str, list[str]] = {}
    number_rows = dataset_module._rows("obfus_number_series")

    def number_equivalent(item_id: str) -> bool:
        index = int(item_id.rsplit("-", 1)[1])
        row = number_rows[index]
        base = obfuscate_module._comparable(row["Base_Series"])
        decoded = obfuscate_module._comparable(
            obfuscate_module.decode(str(row["Obfuscated_Series"]))
        )
        return decoded == base

    for task in TASKS:
        candidates = sorted(set(ids_by_task[task]) - set(test_ids[task]))
        if task == "obfus_number_series":
            candidates = [item_id for item_id in candidates if number_equivalent(item_id)]
        rng = random.Random(f"{DEMO_SEED}:{task}:demonstration")
        demo_ids[task] = sorted(rng.sample(candidates, N_DEMOS))

    templates = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "source_seed": SOURCE_SEED,
        "demonstration_seed": DEMO_SEED,
        "questions_per_task": N_TEST,
        "demonstrations_per_task": N_DEMOS,
        "prompt_version": templates["version"],
        "number_series_non_equivalent_test_ids": [
            item_id for item_id in test_ids["obfus_number_series"] if not number_equivalent(item_id)
        ],
        "tasks": {
            task: {
                "test_item_ids": test_ids[task],
                "demonstration_item_ids": demo_ids[task],
                "evaluated_variants": list(OBFUSCATED[task]),
                "number_series_test_blocks": (
                    {item_id: int(item_id.rsplit("-", 1)[1]) // 100 + 1 for item_id in test_ids[task]}
                    if task == "obfus_number_series" else None
                ),
                "number_series_demonstration_blocks": (
                    {item_id: int(item_id.rsplit("-", 1)[1]) // 100 + 1 for item_id in demo_ids[task]}
                    if task == "obfus_number_series" else None
                ),
            }
            for task in TASKS
        },
        "note": "Public split metadata only. Gold answers are excluded.",
    }
    PUBLIC_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    private_records: list[dict] = []
    for task in TASKS:
        for item_id in test_ids[task]:
            for variant in VARIANTS[task]:
                item = item_index[(task, item_id, variant)]
                private_records.append(
                    {"task": task, "item_id": item_id, "variant": variant, "answer": item.answer}
                )
    private_path = source_root / "manual_eval" / "private_do_not_upload" / "gpt_sol_5.6_high_assigned_50_scoring.json"
    private_path.write_text(
        json.dumps({"model": MODEL, "records": private_records}, indent=2), encoding="utf-8"
    )

    condition_counts: dict[str, int] = {}
    for condition in CONDITIONS:
        rows: list[dict[str, str]] = []
        for task in TASKS:
            demos = [
                {variant: item_index[(task, item_id, variant)] for variant in VARIANTS[task]}
                for item_id in demo_ids[task]
            ]
            variants = VARIANTS[task] if condition == "zero_shot_control" else OBFUSCATED[task]
            for item_id in test_ids[task]:
                for variant in variants:
                    item = item_index[(task, item_id, variant)]
                    rows.append(
                        {
                            "condition": condition,
                            "row_number": str(len(rows) + 1),
                            "response_id": response_id(condition, task, item_id, variant),
                            "task": task,
                            "item_id": item_id,
                            "variant": variant,
                            "prompt": render(condition, item, demos, templates),
                            "model_response": "",
                        }
                    )
        expected = 450 if condition == "zero_shot_control" else 250
        if len(rows) != expected:
            raise AssertionError(f"{condition}: expected {expected}, found {len(rows)}")
        write_csv(DATASET_DIR / f"{condition}.csv", rows)
        condition_counts[condition] = len(rows)

    provenance = {
        "model": MODEL,
        "model_snapshot": None,
        "reasoning_effort": REASONING_EFFORT,
        "execution_mode": "Codex subagent queue with an explicit model override",
        "provider_request_ids_available": False,
        "sampling_parameters_available": False,
        "run_date_utc": "2026-10-11",
        "prompt_version": templates["version"],
        "control": {"status": "fresh matched queue", "responses": 450},
        "new_conditions": condition_counts,
        "dataset_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(DATASET_DIR.glob("*.csv"))
        },
    }
    (ROOT / "run_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source_root), indent=2))


if __name__ == "__main__":
    main()
