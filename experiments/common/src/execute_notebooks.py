from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient

from config import EXPERIMENT_ROOT


def execute_notebooks(pattern: str = "*.ipynb") -> list[str]:
    paths = sorted((EXPERIMENT_ROOT / "notebooks").glob(pattern))
    executed: list[str] = []
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        client = NotebookClient(
            notebook,
            timeout=600,
            kernel_name="python3",
            resources={"metadata": {"path": str(path.parent)}},
        )
        client.execute()
        nbformat.write(notebook, path)
        executed.append(str(path))
        print(f"executed: {path.name}")
    return executed


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute mitigation notebooks in filename order")
    parser.add_argument("--pattern", default="*.ipynb")
    args = parser.parse_args()
    paths = execute_notebooks(args.pattern)
    print(f"completed {len(paths)} notebook(s)")


if __name__ == "__main__":
    main()
