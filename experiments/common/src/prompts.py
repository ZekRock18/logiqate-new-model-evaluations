from __future__ import annotations

import json
from pathlib import Path

from config import CONDITION_ORDER, CONDITIONS, EXPERIMENT_ROOT, PROMPT_VERSION
from data import ExperimentItem, demonstration_items, get_item, iter_test_items, load_public_manifest


TEMPLATE_PATH = EXPERIMENT_ROOT / "prompts" / "prompt_templates.json"
SNAPSHOT_PATH = EXPERIMENT_ROOT / "prompts" / "rendered_prompt_snapshots.jsonl"


def templates() -> dict:
    payload = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    if payload["version"] != PROMPT_VERSION:
        raise ValueError(
            f"prompt version mismatch: config={PROMPT_VERSION}, templates={payload['version']}"
        )
    return payload


def _question_block(item: ExperimentItem) -> str:
    if item.task == "obfus_fol":
        return item.question
    if item.task == "obfus_number_series":
        return f"Sequence: {item.question}"
    return f"Question: {item.question}"


def _obfuscated_demo_variant(task: str, target_variant: str) -> str:
    if target_variant == "base":
        raise ValueError("few-shot obfuscation demonstrations require an obfuscated target")
    return target_variant


def _obf_demo_text(item: ExperimentItem, number: int) -> str:
    return (
        f"DEMONSTRATION {number}\n"
        f"{_question_block(item)}\n"
        f"FINAL_ANSWER: {item.answer}"
    )


def _paired_demo_text(task: str, item_id: str, target_variant: str, number: int) -> str:
    base = get_item(task, item_id, "base")
    obfuscated = get_item(task, item_id, _obfuscated_demo_variant(task, target_variant))
    return (
        f"PAIRED DEMONSTRATION {number}\n"
        f"CLEAN FORM\n{_question_block(base)}\n"
        f"CLEAN ANSWER: {base.answer}\n\n"
        f"OBFUSCATED FORM\n{_question_block(obfuscated)}\n"
        f"OBFUSCATED ANSWER: {obfuscated.answer}"
    )


def render_prompt(
    condition: str,
    item: ExperimentItem,
    *,
    initial_response: str | None = None,
) -> tuple[str, list[str]]:
    payload = templates()
    task_instruction = payload["task_instructions"][item.task]
    question = _question_block(item)
    demo_ids: list[str] = []

    if condition == "zero_shot_control":
        prompt = payload["templates"]["zero_shot"].format(
            task_instruction=task_instruction, question=question
        )
    elif condition == "obf_to_obf_few_shot":
        demos = demonstration_items(item.task, _obfuscated_demo_variant(item.task, item.variant))
        demo_ids = [demo.item_id for demo in demos]
        demonstrations = "\n\n".join(
            _obf_demo_text(demo, i) for i, demo in enumerate(demos, 1)
        )
        prompt = payload["templates"][condition].format(
            demonstrations=demonstrations,
            task_instruction=task_instruction,
            question=question,
        )
    elif condition == "base_to_obf_paired_few_shot":
        demo_ids = load_public_manifest()["tasks"][item.task]["demonstration_item_ids"]
        demonstrations = "\n\n".join(
            _paired_demo_text(item.task, item_id, item.variant, i)
            for i, item_id in enumerate(demo_ids, 1)
        )
        prompt = payload["templates"][condition].format(
            demonstrations=demonstrations,
            task_instruction=task_instruction,
            question=question,
        )
    elif condition == "self_verification_cove" and initial_response is not None:
        prompt = payload["templates"]["cove_verification"].format(
            question=question,
            initial_response=initial_response,
            task_instruction=task_instruction,
        )
    else:
        condition_instruction = payload["condition_instructions"].get(condition, "")
        task_specific = payload.get("task_specific_method_instructions", {}).get(
            condition, {}
        ).get(item.task, "")
        prompt = payload["templates"]["single"].format(
            condition_instruction=condition_instruction,
            task_specific_instruction=task_specific,
            task_instruction=task_instruction,
            question=question,
        )
    return prompt.strip(), demo_ids


def snapshot_prompts() -> dict:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with SNAPSHOT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for condition in CONDITION_ORDER:
            spec = CONDITIONS[condition]
            for task, variants in spec.tasks.items():
                for item in iter_test_items(task, variants):
                    prompt, demo_ids = render_prompt(condition, item)
                    record = {
                        "condition": condition,
                        "prompt_version": PROMPT_VERSION,
                        "task": item.task,
                        "item_id": item.item_id,
                        "variant": item.variant,
                        "demonstration_item_ids": demo_ids,
                        "prompt": prompt,
                    }
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1
    return {"snapshot_path": str(SNAPSHOT_PATH), "prompt_count": count}


def validate_prompt_snapshot() -> dict:
    if not SNAPSHOT_PATH.exists():
        snapshot_prompts()
    records = [json.loads(line) for line in SNAPSHOT_PATH.read_text(encoding="utf-8").splitlines()]
    keys = [
        (r["condition"], r["task"], r["item_id"], r["variant"]) for r in records
    ]
    if len(keys) != len(set(keys)):
        raise AssertionError("duplicate rendered prompt snapshot key")
    for record in records:
        prompt = record["prompt"]
        if "FINAL_ANSWER:" not in prompt:
            raise AssertionError(f"missing final marker: {record['condition']}/{record['item_id']}")
        public = load_public_manifest()["tasks"][record["task"]]
        if set(record["demonstration_item_ids"]) & set(public["test_item_ids"]):
            raise AssertionError("demonstration/test overlap in rendered prompt")
    expected = sum(
        15 * len(variants) for spec in CONDITIONS.values() for variants in spec.tasks.values()
    )
    if len(records) != expected:
        raise AssertionError(f"expected {expected} prompt snapshots, found {len(records)}")
    return {"prompt_count": len(records), "unique_keys": len(set(keys)), "version": PROMPT_VERSION}


if __name__ == "__main__":
    print(json.dumps(snapshot_prompts(), indent=2))
    print(json.dumps(validate_prompt_snapshot(), indent=2))
