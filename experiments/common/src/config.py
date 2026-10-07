from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = EXPERIMENT_ROOT.parent
SOURCE_SEED = 20260925
SELECTION_SEED = 20261006
N_TEST = 15
N_DEMONSTRATIONS = 2
PROMPT_VERSION = "v2"
DEFAULT_PROVIDER = "deepinfra"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V4.1-Flash"
DEFAULT_MODEL_REVISION = "provider-hosted-2026-10-06"

TASKS = (
    "obfus_fol",
    "obfus_blood_relation",
    "obfus_number_series",
    "obfus_direction_sense",
)

TASK_TITLES = {
    "obfus_fol": "FOL",
    "obfus_blood_relation": "Blood Relation",
    "obfus_number_series": "Number Series",
    "obfus_direction_sense": "Direction Sense",
}

VARIANTS = {
    "obfus_fol": ("base", "obfuscation"),
    "obfus_blood_relation": ("base", "obfuscation_l1", "obfuscation_l2"),
    "obfus_number_series": ("base", "obfuscation"),
    "obfus_direction_sense": ("base", "obfuscation"),
}

OBFUSCATED_VARIANTS = {
    task: tuple(v for v in variants if v != "base") for task, variants in VARIANTS.items()
}


@dataclass(frozen=True)
class ConditionSpec:
    name: str
    tasks: dict[str, tuple[str, ...]]
    temperature: float = 0.0
    paths: int = 1
    passes: int = 1


def _all_variants(*tasks: str) -> dict[str, tuple[str, ...]]:
    return {task: VARIANTS[task] for task in tasks}


def _obfuscated(*tasks: str) -> dict[str, tuple[str, ...]]:
    return {task: OBFUSCATED_VARIANTS[task] for task in tasks}


CONDITIONS = {
    "zero_shot_control": ConditionSpec("zero_shot_control", _all_variants(*TASKS)),
    "obf_to_obf_few_shot": ConditionSpec("obf_to_obf_few_shot", _obfuscated(*TASKS)),
    "base_to_obf_paired_few_shot": ConditionSpec(
        "base_to_obf_paired_few_shot", _obfuscated(*TASKS)
    ),
    "analogical_prompting": ConditionSpec("analogical_prompting", _obfuscated(*TASKS)),
    "normalize_then_solve": ConditionSpec(
        "normalize_then_solve", _all_variants("obfus_fol", "obfus_blood_relation")
    ),
    "structured_decomposition": ConditionSpec(
        "structured_decomposition",
        _all_variants("obfus_blood_relation", "obfus_direction_sense"),
    ),
    "explicit_task_instructions": ConditionSpec(
        "explicit_task_instructions",
        _all_variants("obfus_number_series", "obfus_direction_sense"),
    ),
    "chain_of_thought": ConditionSpec("chain_of_thought", _all_variants(*TASKS)),
    "rereading_s2a": ConditionSpec(
        "rereading_s2a",
        {
            "obfus_fol": VARIANTS["obfus_fol"],
            "obfus_blood_relation": ("base", "obfuscation_l2"),
        },
    ),
    "self_consistency": ConditionSpec(
        "self_consistency", _all_variants(*TASKS), temperature=0.7, paths=3
    ),
    "self_verification_cove": ConditionSpec(
        "self_verification_cove", _all_variants(*TASKS), passes=2
    ),
}

CONDITION_ORDER = tuple(CONDITIONS)


def expected_evaluation_count(condition: str | None = None) -> int:
    specs = [CONDITIONS[condition]] if condition else CONDITIONS.values()
    return sum(N_TEST * len(variants) for spec in specs for variants in spec.tasks.values())


def expected_api_call_count(condition: str | None = None) -> int:
    specs = [CONDITIONS[condition]] if condition else CONDITIONS.values()
    return sum(
        N_TEST * len(variants) * spec.paths * spec.passes
        for spec in specs
        for variants in spec.tasks.values()
    )
