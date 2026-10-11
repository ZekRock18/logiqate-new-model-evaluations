from __future__ import annotations

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = ROOT / "notebooks"


SPECS = [
    (
        "00_protocol_and_sample.ipynb",
        "GPT Sol 5.6 High: Protocol and Fixed Sample",
        """import json
from pathlib import Path
root = Path.cwd()
manifest = json.loads((root / 'sample_manifest.json').read_text(encoding='utf-8'))
print('model:', manifest['model'])
print('reasoning effort:', manifest['reasoning_effort'])
for task, data in manifest['tasks'].items():
    overlap = set(data['test_item_ids']) & set(data['demonstration_item_ids'])
    print(task, 'test=', len(data['test_item_ids']), 'demos=', len(data['demonstration_item_ids']), 'overlap=', len(overlap))""",
    ),
    (
        "01_zero_shot_control.ipynb",
        "Fresh Matched Zero-Shot Control",
        """import pandas as pd
from pathlib import Path
root = Path.cwd()
df = pd.read_csv(root / 'Result' / 'zero_shot_control.csv')
print('responses:', len(df), 'blank:', int(df.model_response.isna().sum()))
display(pd.read_csv(root / 'Analysis' / 'accuracy_by_cell.csv').query("condition == 'zero_shot_control'"))""",
    ),
    (
        "02_obf_to_obf_few_shot.ipynb",
        "Experiment 1: Obfuscated-to-Obfuscated Few-Shot",
        """import pandas as pd
from pathlib import Path
root = Path.cwd()
condition = 'obf_to_obf_few_shot'
df = pd.read_csv(root / 'Result' / f'{condition}.csv')
print('responses:', len(df), 'blank:', int(df.model_response.isna().sum()))
display(pd.read_csv(root / 'Analysis' / 'improvement_over_control.csv').query('condition == @condition'))""",
    ),
    (
        "03_base_to_obf_paired_few_shot.ipynb",
        "Experiment 2: Base-to-Obfuscated Paired Few-Shot",
        """import pandas as pd
from pathlib import Path
root = Path.cwd()
condition = 'base_to_obf_paired_few_shot'
df = pd.read_csv(root / 'Result' / f'{condition}.csv')
print('responses:', len(df), 'blank:', int(df.model_response.isna().sum()))
display(pd.read_csv(root / 'Analysis' / 'improvement_over_control.csv').query('condition == @condition'))""",
    ),
    (
        "04_analogical_prompting.ipynb",
        "Experiment 3: Analogical Prompting",
        """import pandas as pd
from pathlib import Path
root = Path.cwd()
condition = 'analogical_prompting'
df = pd.read_csv(root / 'Result' / f'{condition}.csv')
print('responses:', len(df), 'blank:', int(df.model_response.isna().sum()))
display(pd.read_csv(root / 'Analysis' / 'improvement_over_control.csv').query('condition == @condition'))""",
    ),
    (
        "05_score_and_compare.ipynb",
        "Aggregate Comparison",
        """import json
import pandas as pd
from pathlib import Path
root = Path.cwd()
summary = json.loads((root / 'Analysis' / 'summary.json').read_text(encoding='utf-8'))
print('evaluation units:', summary['total_evaluation_units'])
display(pd.read_csv(root / 'Analysis' / 'condition_totals.csv'))
display(pd.read_csv(root / 'Analysis' / 'paired_retention.csv'))""",
    ),
]


def build() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    for filename, title, code in SPECS:
        notebook = nbf.v4.new_notebook(
            cells=[
                nbf.v4.new_markdown_cell(
                    f"# {title}\n\nGenerated from the frozen public artifacts; row-level gold answers are not embedded."
                ),
                nbf.v4.new_code_cell(code),
            ],
            metadata={
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.11"},
            },
        )
        client = NotebookClient(notebook, timeout=180, kernel_name="python3")
        client.execute(cwd=str(ROOT))
        nbf.write(notebook, NOTEBOOK_DIR / filename)
        print(f"executed {filename}")


if __name__ == "__main__":
    build()
