from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "PUBLICATION_AUDIT.json"
FORBIDDEN_NAMES = {
    "answer_key.json",
    "scoring_manifest.json",
    "scored_responses.csv",
    "incorrect_responses.csv",
    ".env",
}
FORBIDDEN_COLUMNS = {"gold", "ground_truth", "correct_answer", "is_correct", "normalized_gold"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".jsonl", ".csv", ".ipynb", ".txt"}
EXPECTED_COUNTS = {
    "zero_shot_control": 450,
    "obf_to_obf_few_shot": 250,
    "base_to_obf_paired_few_shot": 250,
    "analogical_prompting": 250,
}


def public_sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def audit() -> dict:
    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and path != OUTPUT)
    bad_names = [str(path.relative_to(ROOT)) for path in files if path.name in FORBIDDEN_NAMES]
    bad_columns: dict[str, list[str]] = {}
    secret_markers: dict[str, list[str]] = {}
    for path in files:
        if path.suffix.lower() == ".csv":
            with path.open("r", newline="", encoding="utf-8-sig") as handle:
                fields = csv.DictReader(handle).fieldnames or []
            forbidden = sorted(FORBIDDEN_COLUMNS & set(fields))
            if forbidden:
                bad_columns[str(path.relative_to(ROOT))] = forbidden
        if path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore")
            patterns = {
                "github_token": re.compile(r"\bgh" + r"p_[A-Za-z0-9]{20,}"),
                "openai_style_key": re.compile(r"\bs" + r"k-[A-Za-z0-9_-]{16,}"),
            }
            found = [name for name, pattern in patterns.items() if pattern.search(text)]
            if found:
                secret_markers[str(path.relative_to(ROOT))] = found
    result_counts = {}
    missing_results = []
    for path in sorted((ROOT / "Result").glob("*.csv")):
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        result_counts[path.stem] = {
            "rows": len(rows),
            "answered": sum(bool(row["model_response"].strip()) for row in rows),
        }
    for condition, expected in EXPECTED_COUNTS.items():
        if condition not in result_counts:
            missing_results.append(condition)
        elif result_counts[condition] != {"rows": expected, "answered": expected}:
            missing_results.append(condition)
    unexpected_results = sorted(set(result_counts) - set(EXPECTED_COUNTS))
    journal_reconciliation = {}
    missing_journals = []
    for condition in EXPECTED_COUNTS:
        path = ROOT / "Result" / f"_answer_journal_{condition}.jsonl"
        if not path.exists():
            missing_journals.append(condition)
            continue
        latest = {}
        journal_rows = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                latest[record["response_id"]] = record["answer"].strip()
                journal_rows += 1
        result_path = ROOT / "Result" / f"{condition}.csv"
        with result_path.open("r", newline="", encoding="utf-8-sig") as handle:
            result_rows = list(csv.DictReader(handle))
        mismatch_count = sum(
            latest.get(row["response_id"]) != row["model_response"].strip()
            for row in result_rows
        )
        journal_reconciliation[condition] = {
            "journal_rows": journal_rows,
            "unique_response_ids": len(latest),
            "result_rows": len(result_rows),
            "mismatch_count": mismatch_count,
        }
    reconciliation_ok = not missing_journals and all(
        item["mismatch_count"] == 0 and item["unique_response_ids"] == item["result_rows"]
        for item in journal_reconciliation.values()
    )
    unexpected_journals = sorted(
        path.stem.removeprefix("_answer_journal_")
        for path in (ROOT / "Result").glob("_answer_journal_*.jsonl")
        if path.stem.removeprefix("_answer_journal_") not in EXPECTED_COUNTS
    )
    payload = {
        "status": "pass" if not bad_names and not bad_columns and not secret_markers
        and not missing_results and not unexpected_results and reconciliation_ok
        and not unexpected_journals else "fail",
        "forbidden_filenames": bad_names,
        "forbidden_columns": bad_columns,
        "secret_markers": secret_markers,
        "result_counts": result_counts,
        "missing_or_incomplete_results": missing_results,
        "unexpected_results": unexpected_results,
        "journal_reconciliation": journal_reconciliation,
        "missing_journals": missing_journals,
        "unexpected_journals": unexpected_journals,
        "file_count": len(files),
        "file_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): public_sha256(path)
            for path in files
            if "__pycache__" not in path.parts
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if payload["status"] != "pass":
        raise SystemExit(json.dumps(payload, indent=2))
    print(json.dumps({key: value for key, value in payload.items() if key != "file_sha256"}, indent=2))
    return payload


if __name__ == "__main__":
    audit()
