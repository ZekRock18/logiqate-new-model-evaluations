from __future__ import annotations

import json
import importlib.util
import random
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

from config import (
    EXPERIMENT_ROOT,
    N_DEMONSTRATIONS,
    N_TEST,
    REPO_ROOT,
    SELECTION_SEED,
    SOURCE_SEED,
    TASKS,
    VARIANTS,
)


ROOT_SRC = REPO_ROOT / "src"


def _load_source_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT_SRC / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


source_dataset = _load_source_module("logiqate_source_dataset", "dataset.py")
source_obfuscate = _load_source_module("logiqate_source_obfuscate", "obfuscate.py")


SOURCE_ANSWER_KEY = REPO_ROOT / "manual_eval" / "private_do_not_upload" / "answer_key.json"
PUBLIC_MANIFEST = EXPERIMENT_ROOT / "data" / "sample_manifest.json"
PRIVATE_MANIFEST = EXPERIMENT_ROOT / "private_do_not_upload" / "scoring_manifest.json"


@dataclass(frozen=True)
class ExperimentItem:
    task: str
    item_id: str
    variant: str
    question: str
    answer: str


def _source_pool() -> dict[str, dict[str, dict[str, str]]]:
    payload = json.loads(SOURCE_ANSWER_KEY.read_text(encoding="utf-8"))
    if payload.get("seed") != SOURCE_SEED:
        raise ValueError(f"unexpected source seed: {payload.get('seed')}")
    pool: dict[str, dict[str, dict[str, str]]] = {task: {} for task in TASKS}
    for record in payload["records"]:
        if record["setting"] != "zero_shot":
            continue
        pool[record["task"]].setdefault(record["item_id"], {})[record["variant"]] = record[
            "correct_answer"
        ]
    return pool


def _number_block(item_id: str) -> int:
    return int(item_id.rsplit("-", 1)[1]) // 100 + 1


def _select_test_ids(pool: dict[str, dict[str, dict[str, str]]], task: str) -> list[str]:
    ids = sorted(pool[task])
    rng = random.Random(f"{SELECTION_SEED}:{task}:test")
    if task != "obfus_number_series":
        return sorted(rng.sample(ids, N_TEST))
    selected: list[str] = []
    for block in (1, 2, 3):
        candidates = [item_id for item_id in ids if _number_block(item_id) == block]
        if len(candidates) < 5:
            raise ValueError(f"Number Series block {block} has only {len(candidates)} candidates")
        selected.extend(rng.sample(candidates, 5))
    return sorted(selected)


def _select_demo_ids(pool_ids: list[str], test_ids: list[str], task: str) -> list[str]:
    candidates = sorted(set(pool_ids) - set(test_ids))
    rng = random.Random(f"{SELECTION_SEED}:{task}:demonstration")
    return sorted(rng.sample(candidates, N_DEMONSTRATIONS))


def _number_equivalent(item_id: str) -> bool:
    index = int(item_id.rsplit("-", 1)[1])
    row = source_dataset._rows("obfus_number_series")[index]
    base = source_obfuscate._comparable(row["Base_Series"])
    decoded = source_obfuscate._comparable(
        source_obfuscate.decode(str(row["Obfuscated_Series"]))
    )
    return decoded == base


def prepare_sample() -> dict:
    pool = _source_pool()
    public_tasks: dict[str, dict] = {}
    private_records: list[dict] = []

    for task in TASKS:
        test_ids = _select_test_ids(pool, task)
        demo_ids = _select_demo_ids(list(pool[task]), test_ids, task)
        public_tasks[task] = {
            "variants": list(VARIANTS[task]),
            "test_item_ids": test_ids,
            "demonstration_item_ids": demo_ids,
            "number_series_blocks": (
                {item_id: _number_block(item_id) for item_id in test_ids}
                if task == "obfus_number_series"
                else None
            ),
        }
        for split, ids in (("test", test_ids), ("demonstration", demo_ids)):
            for item_id in ids:
                for variant in VARIANTS[task]:
                    private_records.append(
                        {
                            "task": task,
                            "item_id": item_id,
                            "variant": variant,
                            "split": split,
                            "correct_answer": pool[task][item_id][variant],
                            "logically_equivalent": (
                                _number_equivalent(item_id)
                                if task == "obfus_number_series" and variant == "obfuscation"
                                else True
                            ),
                        }
                    )

    public = {
        "source_seed": SOURCE_SEED,
        "selection_seed": SELECTION_SEED,
        "questions_per_task": N_TEST,
        "demonstrations_per_task": N_DEMONSTRATIONS,
        "tasks": public_tasks,
        "note": "Public split metadata only; correct answers are intentionally excluded.",
    }
    private = {
        "source_seed": SOURCE_SEED,
        "selection_seed": SELECTION_SEED,
        "note": "PRIVATE: never upload this file or expose test answers to a tested model.",
        "records": private_records,
    }

    PUBLIC_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    PRIVATE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_MANIFEST.write_text(json.dumps(public, indent=2), encoding="utf-8")
    PRIVATE_MANIFEST.write_text(json.dumps(private, indent=2), encoding="utf-8")
    validate_manifests()
    return public


def load_public_manifest() -> dict:
    if not PUBLIC_MANIFEST.exists():
        prepare_sample()
    return json.loads(PUBLIC_MANIFEST.read_text(encoding="utf-8"))


def load_private_manifest() -> dict:
    if not PRIVATE_MANIFEST.exists():
        prepare_sample()
    return json.loads(PRIVATE_MANIFEST.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _item_index() -> dict[tuple[str, str, str], ExperimentItem]:
    records = load_private_manifest()["records"]
    answers = {
        (r["task"], r["item_id"], r["variant"]): r["correct_answer"] for r in records
    }
    index: dict[tuple[str, str, str], ExperimentItem] = {}
    relevant_ids = {(r["task"], r["item_id"]) for r in records}
    for item in source_dataset.load_all():
        if (item.task, item.item_id) not in relevant_ids:
            continue
        key = (item.task, item.item_id, item.variant)
        index[key] = ExperimentItem(
            item.task, item.item_id, item.variant, item.question, answers[key]
        )
    return index


def get_item(task: str, item_id: str, variant: str) -> ExperimentItem:
    try:
        return _item_index()[(task, item_id, variant)]
    except KeyError as exc:
        raise KeyError(f"missing selected item {task}/{item_id}/{variant}") from exc


def iter_test_items(task: str, variants: tuple[str, ...]):
    manifest = load_public_manifest()
    for item_id in manifest["tasks"][task]["test_item_ids"]:
        for variant in variants:
            yield get_item(task, item_id, variant)


def demonstration_items(task: str, variant: str) -> list[ExperimentItem]:
    manifest = load_public_manifest()
    return [
        get_item(task, item_id, variant)
        for item_id in manifest["tasks"][task]["demonstration_item_ids"]
    ]


def validate_manifests() -> dict:
    public = json.loads(PUBLIC_MANIFEST.read_text(encoding="utf-8"))
    private = json.loads(PRIVATE_MANIFEST.read_text(encoding="utf-8"))
    if "correct_answer" in PUBLIC_MANIFEST.read_text(encoding="utf-8"):
        raise AssertionError("public manifest contains a correct_answer field")
    private_keys = {
        (r["task"], r["item_id"], r["variant"], r["split"]) for r in private["records"]
    }
    for task in TASKS:
        task_data = public["tasks"][task]
        test_ids = task_data["test_item_ids"]
        demo_ids = task_data["demonstration_item_ids"]
        if len(test_ids) != N_TEST or len(set(test_ids)) != N_TEST:
            raise AssertionError(f"{task}: test set is not {N_TEST} unique IDs")
        if len(demo_ids) != N_DEMONSTRATIONS or len(set(demo_ids)) != N_DEMONSTRATIONS:
            raise AssertionError(f"{task}: invalid demonstration set")
        if set(test_ids) & set(demo_ids):
            raise AssertionError(f"{task}: demonstration/test overlap")
        for split, ids in (("test", test_ids), ("demonstration", demo_ids)):
            for item_id in ids:
                for variant in VARIANTS[task]:
                    if (task, item_id, variant, split) not in private_keys:
                        raise AssertionError(f"missing variant: {task}/{item_id}/{variant}/{split}")
    blocks = public["tasks"]["obfus_number_series"]["number_series_blocks"].values()
    if {block: list(blocks).count(block) for block in (1, 2, 3)} != {1: 5, 2: 5, 3: 5}:
        raise AssertionError("Number Series sample is not balanced 5/5/5")
    return {
        "tasks": len(TASKS),
        "test_items_per_task": N_TEST,
        "demonstrations_per_task": N_DEMONSTRATIONS,
        "private_records": len(private["records"]),
        "number_series_non_equivalent_test_items": sorted(
            {
                r["item_id"]
                for r in private["records"]
                if r["task"] == "obfus_number_series"
                and r["split"] == "test"
                and not r["logically_equivalent"]
            }
        ),
    }


if __name__ == "__main__":
    prepare_sample()
    print(json.dumps(validate_manifests(), indent=2))
