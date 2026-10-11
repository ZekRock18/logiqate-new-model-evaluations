from __future__ import annotations

import argparse
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = ROOT / "notebooks"

METHODS = (
    (
        "normalize_then_solve",
        "Normalize Then Solve",
        ("normalize_then_solve",),
        "Rewrite into a meaning-preserving representation before solving.",
    ),
    (
        "structured_decomposition",
        "Structured Decomposition",
        ("structured_decomposition",),
        "Extract atomic relations or movements and compose them explicitly.",
    ),
    (
        "explicit_task_instructions",
        "Explicit Task Instructions",
        ("explicit_task_instructions",),
        "Apply the task-specific decoding and navigation instructions.",
    ),
    (
        "chain_of_thought",
        "Chain of Thought",
        ("chain_of_thought",),
        "Prompt for decode, derivation, and a concise sanity check.",
    ),
    (
        "rereading_s2a",
        "Re-reading / System 2 Attention",
        ("rereading_s2a",),
        "Read twice, isolate relevant facts, and solve the reduced problem.",
    ),
    (
        "self_consistency",
        "Self-Consistency",
        (
            "self_consistency_path_1",
            "self_consistency_path_2",
            "self_consistency_path_3",
        ),
        "Generate three separately queued paths and majority-vote normalized answers.",
    ),
    (
        "self_verification_cove",
        "Self-Verification / CoVe",
        (
            "self_verification_cove_initial",
            "self_verification_cove_verification",
        ),
        "Retain the initial response and a separate verifier response; score the verifier.",
    ),
)


SETUP = """from pathlib import Path
import json
import pandas as pd
from IPython.display import display

root = Path.cwd().resolve()
manifest_path = root / 'tier1_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}

def read_public_csv(path):
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path, keep_default_na=False)
    forbidden = {'gold', 'ground_truth', 'correct_answer', 'normalized_gold', 'is_correct'}
    exposed = forbidden.intersection(str(column).lower() for column in frame.columns)
    if exposed:
        raise ValueError(f'public analysis contains forbidden row-level columns: {sorted(exposed)}')
    return frame

print('model:', manifest.get('model', 'not prepared'))
print('reasoning effort:', manifest.get('reasoning_effort', 'not prepared'))
print('prompt version:', manifest.get('prompt_version', 'not prepared'))
"""


def method_code(condition: str, queues: tuple[str, ...]) -> str:
    return f"""condition = {condition!r}
queues = {queues!r}
coverage = []
result_frames = []
for queue in queues:
    dataset_path = root / 'Dataset' / f'{{queue}}.csv'
    result_path = root / 'Result' / f'{{queue}}.csv'
    dataset = read_public_csv(dataset_path)
    result = read_public_csv(result_path)
    answered = 0
    if not result.empty and 'model_response' in result:
        answered = int(result['model_response'].astype(str).str.strip().ne('').sum())
        result_frames.append(result.assign(source_queue=queue))
    coverage.append({{
        'queue': queue,
        'dataset_rows': len(dataset),
        'result_rows': len(result),
        'answered_rows': answered,
        'unresolved_rows': max(len(result) - answered, 0),
    }})

display(pd.DataFrame(coverage))
if result_frames:
    results = pd.concat(result_frames, ignore_index=True)
    group_columns = [column for column in ('task', 'variant', 'stage', 'path_index') if column in results]
    display(
        results.groupby(group_columns, dropna=False)
        .agg(responses=('response_id', 'count'), answered=('model_response', lambda values: values.astype(str).str.strip().ne('').sum()))
        .reset_index()
    )
else:
    print('Result files are not available yet.')

analysis_dir = root / 'Analysis'
shown = 0
if analysis_dir.exists():
    for path in sorted(analysis_dir.glob('*.csv')):
        frame = read_public_csv(path)
        if frame.empty:
            continue
        selector = None
        if 'condition' in frame.columns:
            selector = frame['condition'].astype(str).eq(condition)
        elif 'method' in frame.columns:
            selector = frame['method'].astype(str).eq(condition)
        if selector is not None and bool(selector.any()):
            print(path.name)
            selected = frame.loc[selector].reset_index(drop=True)
            if 'evaluation_id' in selected.columns and len(selected) > 100:
                print('public row-level aggregate rows:', len(selected))
                grouping = [column for column in ('task', 'variant', 'agreement', 'status', 'answer_changed') if column in selected]
                if grouping:
                    display(selected.groupby(grouping, dropna=False).size().rename('rows').reset_index())
            else:
                display(selected)
            shown += 1
if not shown:
    print('No condition-level public analysis tables are available yet.')
"""


AGGREGATE_CODE = """expected = {
    'normalize_then_solve': 250,
    'structured_decomposition': 250,
    'explicit_task_instructions': 200,
    'chain_of_thought': 450,
    'rereading_s2a': 200,
    'self_consistency_path_1': 450,
    'self_consistency_path_2': 450,
    'self_consistency_path_3': 450,
    'self_verification_cove_initial': 450,
    'self_verification_cove_verification': 450,
}
coverage = []
for queue, expected_rows in expected.items():
    dataset = read_public_csv(root / 'Dataset' / f'{queue}.csv')
    result = read_public_csv(root / 'Result' / f'{queue}.csv')
    answered = 0 if result.empty else int(result['model_response'].astype(str).str.strip().ne('').sum())
    coverage.append({
        'queue': queue,
        'expected_rows': expected_rows,
        'dataset_rows': len(dataset),
        'result_rows': len(result),
        'answered_rows': answered,
    })
coverage_frame = pd.DataFrame(coverage)
display(coverage_frame)
print('planned scored evaluation units:', sum((250, 250, 200, 450, 200, 450, 450)))
print('planned raw generations:', sum(expected.values()))

analysis_dir = root / 'Analysis'
if analysis_dir.exists():
    for path in sorted(analysis_dir.glob('*.csv')):
        frame = read_public_csv(path)
        print(path.name)
        if 'evaluation_id' in frame.columns and len(frame) > 100:
            print('public row-level aggregate rows:', len(frame))
            grouping = [column for column in ('condition', 'task', 'variant', 'agreement', 'status', 'answer_changed') if column in frame]
            if grouping:
                display(frame.groupby(grouping, dropna=False).size().rename('rows').reset_index())
        else:
            display(frame)
    summary_path = analysis_dir / 'summary.json'
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        safe_keys = {
            'model', 'reasoning_effort', 'prompt_version', 'scoring_policy',
            'conditions', 'task_variant_cells', 'evaluation_units',
            'raw_model_generations', 'completed_evaluations', 'condition_totals',
            'special_metrics', 'status_counts',
        }
        display({key: value for key, value in summary.items() if key in safe_keys})
    aggregation_path = analysis_dir / 'aggregation_summary.json'
    if aggregation_path.exists():
        display(json.loads(aggregation_path.read_text(encoding='utf-8')))
else:
    print('Analysis directory is not available yet.')
"""


def notebook(title: str, description: str, code: str):
    return nbf.v4.new_notebook(
        cells=[
            nbf.v4.new_markdown_cell(
                f"# {title}\n\n{description}\n\n"
                "This executed notebook uses only public prompts, responses, and aggregate analysis. "
                "It does not embed answer keys or row-level correctness labels."
            ),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(code),
        ],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
    )


def build(*, execute: bool = True) -> list[Path]:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for number, (condition, title, queues, description) in enumerate(METHODS, 1):
        filename = f"{number:02d}_{condition}.ipynb"
        document = notebook(title, description, method_code(condition, queues))
        if execute:
            NotebookClient(document, timeout=300, kernel_name="python3").execute(cwd=str(ROOT))
        target = NOTEBOOK_DIR / filename
        nbf.write(document, target)
        outputs.append(target)
        print(f"{'executed' if execute else 'generated'} {filename}")

    aggregate = notebook(
        "Aggregate Tier-1 Results",
        "Coverage and public aggregate comparisons for all seven Tier-1 methods.",
        AGGREGATE_CODE,
    )
    if execute:
        NotebookClient(aggregate, timeout=300, kernel_name="python3").execute(cwd=str(ROOT))
    aggregate_path = NOTEBOOK_DIR / "08_aggregate_results.ipynb"
    nbf.write(aggregate, aggregate_path)
    outputs.append(aggregate_path)
    print(f"{'executed' if execute else 'generated'} {aggregate_path.name}")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate public Tier-1 review notebooks")
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="write notebooks without executing them",
    )
    args = parser.parse_args()
    build(execute=not args.generate_only)


if __name__ == "__main__":
    main()
