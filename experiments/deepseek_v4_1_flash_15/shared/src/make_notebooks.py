from __future__ import annotations

import json
from pathlib import Path

from config import CONDITION_ORDER, EXPERIMENT_ROOT


NOTEBOOKS = {
    "00_prepare_15_question_sample.ipynb": None,
    "01_zero_shot_control.ipynb": "zero_shot_control",
    "02_obf_to_obf_few_shot.ipynb": "obf_to_obf_few_shot",
    "03_base_to_obf_paired_few_shot.ipynb": "base_to_obf_paired_few_shot",
    "04_analogical_prompting.ipynb": "analogical_prompting",
    "05_normalize_then_solve.ipynb": "normalize_then_solve",
    "06_structured_decomposition.ipynb": "structured_decomposition",
    "07_explicit_task_instructions.ipynb": "explicit_task_instructions",
    "08_chain_of_thought.ipynb": "chain_of_thought",
    "09_rereading_s2a.ipynb": "rereading_s2a",
    "10_self_consistency.ipynb": "self_consistency",
    "11_self_verification_cove.ipynb": "self_verification_cove",
    "12_score_and_compare.ipynb": "score",
}


def _cell(cell_type: str, source: str) -> dict:
    cell = {"cell_type": cell_type, "metadata": {}, "source": source.splitlines(keepends=True)}
    if cell_type == "code":
        cell.update({"execution_count": None, "outputs": []})
    return cell


def _bootstrap() -> str:
    return """from pathlib import Path
import sys

EXPERIMENT_ROOT = next(
    path for path in (Path.cwd(), *Path.cwd().parents)
    if (path / "src" / "config.py").exists() and (path / "prompts" / "prompt_templates.json").exists()
)
sys.path.insert(0, str(EXPERIMENT_ROOT / "src"))
print(f"Experiment root: {EXPERIMENT_ROOT}")"""


def _notebook(name: str, action: str | None) -> dict:
    title = name.removesuffix(".ipynb").replace("_", " ").title()
    cells = [
        _cell(
            "markdown",
            f"# {title}\n\nThis notebook is a reviewable entry point. Shared implementation lives in `../src/`. Raw API records are append-only and completed units are skipped on rerun.",
        ),
        _cell("code", _bootstrap()),
    ]
    if action is None:
        cells.extend(
            [
                _cell(
                    "code",
                    "from data import prepare_sample, validate_manifests\nfrom prompts import snapshot_prompts, validate_prompt_snapshot",
                ),
                _cell(
                    "code",
                    "manifest = prepare_sample()\nsnapshot_prompts()\n{\n    'manifest_validation': validate_manifests(),\n    'prompt_validation': validate_prompt_snapshot(),\n}",
                ),
            ]
        )
    elif action == "score":
        cells.extend(
            [
                _cell("code", "from scoring import score_results"),
                _cell("code", "summary = score_results()\nsummary"),
            ]
        )
    else:
        cells.extend(
            [
                _cell("markdown", "Set `DEEPINFRA_API_KEY` in the kernel environment before running the next cell. The credential is never stored in this notebook."),
                _cell("code", "from run import run_condition"),
                _cell(
                    "code",
                    f"summary = run_condition(\n    {action!r},\n    workers=8,\n)\nsummary",
                ),
            ]
        )
    for index, cell in enumerate(cells):
        cell["id"] = f"cell-{index:02d}"
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def make_notebooks() -> list[str]:
    notebook_dir = EXPERIMENT_ROOT / "notebooks"
    notebook_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, action in NOTEBOOKS.items():
        path = notebook_dir / name
        path.write_text(json.dumps(_notebook(name, action), indent=1), encoding="utf-8")
        written.append(str(path))
    expected_conditions = [value for value in NOTEBOOKS.values() if value not in {None, "score"}]
    if expected_conditions != list(CONDITION_ORDER):
        raise AssertionError("notebook order does not match condition order")
    return written


if __name__ == "__main__":
    print(json.dumps(make_notebooks(), indent=2))
