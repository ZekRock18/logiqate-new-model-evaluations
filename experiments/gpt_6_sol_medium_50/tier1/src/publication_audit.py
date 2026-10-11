from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "PUBLICATION_AUDIT.json"
EXPECTED_COUNTS = {
    "normalize_then_solve": 250,
    "structured_decomposition": 250,
    "explicit_task_instructions": 200,
    "chain_of_thought": 450,
    "rereading_s2a": 200,
    "self_consistency_path_1": 450,
    "self_consistency_path_2": 450,
    "self_consistency_path_3": 450,
    "self_verification_cove_initial": 450,
    "self_verification_cove_verification": 450,
}
EXPECTED_NOTEBOOKS = {
    "01_normalize_then_solve.ipynb",
    "02_structured_decomposition.ipynb",
    "03_explicit_task_instructions.ipynb",
    "04_chain_of_thought.ipynb",
    "05_rereading_s2a.ipynb",
    "06_self_consistency.ipynb",
    "07_self_verification_cove.ipynb",
    "08_aggregate_results.ipynb",
}
EXPECTED_ANALYSIS_ROWS = {
    "accuracy_by_cell.csv": 45,
    "improvement_over_control.csv": 25,
    "base_obfuscated_gaps.csv": 25,
    "paired_retention.csv": 25,
    "condition_totals.csv": 14,
    "self_consistency_aggregates.csv": 450,
    "cove_aggregates.csv": 450,
}
EXPECTED_FIELDS = [
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
]
FORBIDDEN_FILENAMES = {
    "answer_key.json",
    "scoring_manifest.json",
    "scored_responses.csv",
    "incorrect_responses.csv",
    ".env",
}
FORBIDDEN_COLUMNS = {
    "gold",
    "gold_answer",
    "ground_truth",
    "correct_answer",
    "reference_answer",
    "target_answer",
    "normalized_gold",
    "is_correct",
    "correctness",
}
TEXT_SUFFIXES = {".py", ".md", ".json", ".jsonl", ".csv", ".ipynb", ".txt"}


def public_sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()
FINAL_MARKER = re.compile(r"FINAL_ANSWER\s*:\s*\S+", re.IGNORECASE)


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def active_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path != OUTPUT
        and "__pycache__" not in path.parts
        and not path.name.startswith(".")
        and not path.name.endswith(".tmp")
    )


def scan_public_files(files: list[Path]) -> dict:
    forbidden_names = [relative(path) for path in files if path.name.lower() in FORBIDDEN_FILENAMES]
    forbidden_columns: dict[str, list[str]] = {}
    secret_markers: dict[str, list[str]] = {}
    private_paths: dict[str, list[str]] = {}

    secret_patterns = {
        "openai_style_key": re.compile(r"\bs" + r"k-[A-Za-z0-9_-]{16,}"),
        "github_token": re.compile(r"\bgh" + r"p_[A-Za-z0-9]{20,}"),
        "github_fine_grained_token": re.compile(r"\bgithub" + r"_pat_[A-Za-z0-9_]{20,}"),
        "groq_key": re.compile(r"\bg" + r"sk_[A-Za-z0-9]{16,}"),
        "huggingface_token": re.compile(r"\bh" + r"f_[A-Za-z0-9]{20,}"),
        "aws_access_key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    }
    absolute_patterns = {
        "windows_absolute_path": re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/](?:Users|Documents|Github|GitHub|Desktop)[\\/]"),
        "posix_home_path": re.compile(r"/(?:home|Users)/[^/\s\"']+"),
    }
    private_token = "private" + "_do_not_upload"

    for path in files:
        if path.suffix.lower() == ".csv":
            fields, _ = read_csv(path)
            lower_fields = {field.strip().lower() for field in fields}
            exposed = set(FORBIDDEN_COLUMNS & lower_fields)
            if exposed:
                forbidden_columns[relative(path)] = sorted(exposed)

        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        found_secrets = [name for name, pattern in secret_patterns.items() if pattern.search(text)]
        if found_secrets:
            secret_markers[relative(path)] = found_secrets

        # Source code may legitimately locate private scoring inputs. Published data,
        # reports, and executed outputs must never disclose those paths.
        if path.suffix.lower() != ".py":
            found_paths = [name for name, pattern in absolute_patterns.items() if pattern.search(text)]
            if private_token in text:
                found_paths.append("private_scoring_path")
            if found_paths:
                private_paths[relative(path)] = sorted(set(found_paths))

    return {
        "forbidden_filenames": forbidden_names,
        "forbidden_columns": forbidden_columns,
        "secret_markers": secret_markers,
        "private_paths": private_paths,
    }


def validate_results() -> tuple[dict, list[str], list[str], dict[str, list[dict[str, str]]]]:
    details: dict[str, dict] = {}
    violations: list[str] = []
    incomplete: list[str] = []
    loaded: dict[str, list[dict[str, str]]] = {}
    result_dir = ROOT / "Result"
    dataset_dir = ROOT / "Dataset"

    actual_names = {path.stem for path in result_dir.glob("*.csv")} if result_dir.exists() else set()
    extras = sorted(actual_names - set(EXPECTED_COUNTS))
    if extras:
        violations.append(f"unexpected result CSVs: {extras}")

    global_response_ids: list[str] = []
    for queue, expected in EXPECTED_COUNTS.items():
        result_path = result_dir / f"{queue}.csv"
        dataset_path = dataset_dir / f"{queue}.csv"
        entry = {"expected_rows": expected, "dataset_rows": 0, "result_rows": 0, "answered": 0}
        details[queue] = entry
        if not dataset_path.exists():
            incomplete.append(f"missing dataset {relative(dataset_path)}")
            continue
        dataset_fields, dataset_rows = read_csv(dataset_path)
        entry["dataset_rows"] = len(dataset_rows)
        if dataset_fields != EXPECTED_FIELDS:
            violations.append(f"{relative(dataset_path)} has an unexpected schema")
        if len(dataset_rows) != expected:
            violations.append(f"{relative(dataset_path)} has {len(dataset_rows)} rows; expected {expected}")
        if not result_path.exists():
            incomplete.append(f"missing result {relative(result_path)}")
            continue
        result_fields, result_rows = read_csv(result_path)
        loaded[queue] = result_rows
        entry["result_rows"] = len(result_rows)
        entry["answered"] = sum(bool(row.get("model_response", "").strip()) for row in result_rows)
        entry["final_marker_rows"] = sum(bool(FINAL_MARKER.search(row.get("model_response", ""))) for row in result_rows)
        if result_fields != EXPECTED_FIELDS:
            violations.append(f"{relative(result_path)} has an unexpected schema")
        if len(result_rows) != expected:
            violations.append(f"{relative(result_path)} has {len(result_rows)} rows; expected {expected}")
        if entry["answered"] != expected:
            incomplete.append(f"{relative(result_path)} has {expected - entry['answered']} unresolved rows")
        if entry["final_marker_rows"] != entry["answered"]:
            violations.append(f"{relative(result_path)} contains answered rows without FINAL_ANSWER")

        immutable = [field for field in EXPECTED_FIELDS if field != "model_response"]
        if len(dataset_rows) == len(result_rows):
            changed = sum(
                any(source.get(field, "") != result.get(field, "") for field in immutable)
                for source, result in zip(dataset_rows, result_rows)
            )
            entry["immutable_row_mismatches"] = changed
            if changed:
                violations.append(f"{relative(result_path)} changed {changed} immutable rows")
        response_ids = [row.get("response_id", "") for row in result_rows]
        entry["unique_response_ids"] = len(set(response_ids))
        if len(set(response_ids)) != len(response_ids) or "" in response_ids:
            violations.append(f"{relative(result_path)} has missing or duplicate response IDs")
        global_response_ids.extend(response_ids)

    if len(global_response_ids) != len(set(global_response_ids)):
        violations.append("response IDs are not globally unique across result queues")
    return details, violations, incomplete, loaded


def validate_journals(results: dict[str, list[dict[str, str]]]) -> tuple[dict, list[str], list[str]]:
    details: dict[str, dict] = {}
    violations: list[str] = []
    incomplete: list[str] = []
    for queue in EXPECTED_COUNTS:
        path = ROOT / "Result" / f"_answer_journal_{queue}.jsonl"
        if not path.exists():
            incomplete.append(f"missing journal {relative(path)}")
            continue
        latest: dict[str, dict] = {}
        responses_by_id: dict[str, set[str]] = {}
        rows = 0
        malformed = 0
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            rows += 1
            try:
                record = json.loads(line)
                latest[record["response_id"]] = record
                responses_by_id.setdefault(record["response_id"], set()).add(
                    str(record.get("response", "")).strip()
                )
            except (json.JSONDecodeError, KeyError, TypeError):
                malformed += 1
                violations.append(f"{relative(path)} has a malformed record at line {number}")
        result_rows = results.get(queue, [])
        answered_rows = [row for row in result_rows if row.get("model_response", "").strip()]
        known_ids = {row["response_id"] for row in result_rows}
        unknown_journal_ids = sorted(set(latest) - known_ids)
        if unknown_journal_ids:
            violations.append(f"{relative(path)} contains {len(unknown_journal_ids)} unknown response IDs")
        mismatch = 0
        metadata_mismatch = 0
        divergent_duplicate_ids = sum(len(values) > 1 for values in responses_by_id.values())
        for row in answered_rows:
            record = latest.get(row["response_id"])
            if record is None or str(record.get("response", "")).strip() != row["model_response"].strip():
                mismatch += 1
                continue
            for field in ("queue", "condition", "stage", "path_index", "evaluation_id"):
                if str(record.get(field, "")) != row[field]:
                    metadata_mismatch += 1
                    break
        details[queue] = {
            "journal_rows": rows,
            "unique_response_ids": len(latest),
            "duplicate_records": rows - len(latest),
            "divergent_duplicate_ids": divergent_duplicate_ids,
            "malformed_records": malformed,
            "result_rows": len(result_rows),
            "answered_result_rows": len(answered_rows),
            "unknown_response_ids": len(unknown_journal_ids),
            "latest_response_mismatches": mismatch,
            "metadata_mismatches": metadata_mismatch,
        }
        if len(latest) != len(answered_rows):
            message = f"{relative(path)} latest ID count does not match answered result rows"
            if len(answered_rows) < EXPECTED_COUNTS[queue]:
                incomplete.append(message)
            else:
                violations.append(message)
        if mismatch:
            violations.append(f"{relative(path)} has {mismatch} latest-response mismatches")
        if divergent_duplicate_ids:
            violations.append(
                f"{relative(path)} has {divergent_duplicate_ids} response IDs with divergent journal histories"
            )
        if metadata_mismatch:
            violations.append(f"{relative(path)} has {metadata_mismatch} metadata mismatches")
    return details, violations, incomplete


def validate_self_consistency(results: dict[str, list[dict[str, str]]]) -> tuple[dict, list[str], list[str]]:
    queues = [f"self_consistency_path_{index}" for index in (1, 2, 3)]
    violations: list[str] = []
    incomplete: list[str] = []
    if any(queue not in results for queue in queues):
        incomplete.append("self-consistency path results are not all available")
        return {"complete": False}, violations, incomplete

    indices: dict[str, dict[str, dict[str, str]]] = {}
    for index, queue in enumerate(queues, 1):
        rows = results[queue]
        mapping = {row["evaluation_id"]: row for row in rows}
        indices[queue] = mapping
        if len(mapping) != len(rows):
            violations.append(f"{queue} has duplicate evaluation IDs")
        bad = sum(
            row["queue"] != queue
            or row["condition"] != "self_consistency"
            or row["stage"] != f"path_{index}"
            or row["path_index"] != str(index)
            for row in rows
        )
        if bad:
            violations.append(f"{queue} has {bad} invalid path metadata rows")

    key_sets = [set(indices[queue]) for queue in queues]
    aligned = key_sets[0] == key_sets[1] == key_sets[2]
    if not aligned:
        violations.append("self-consistency paths do not have identical evaluation IDs")
    identity_mismatches = 0
    prompt_mismatches = 0
    for evaluation_id in sorted(set.intersection(*key_sets)):
        rows = [indices[queue][evaluation_id] for queue in queues]
        identities = {(row["task"], row["item_id"], row["variant"]) for row in rows}
        if len(identities) != 1:
            identity_mismatches += 1
        if len({row["prompt"] for row in rows}) != 1:
            prompt_mismatches += 1
    if identity_mismatches:
        violations.append(f"self-consistency has {identity_mismatches} cross-path identity mismatches")
    if prompt_mismatches:
        violations.append(f"self-consistency has {prompt_mismatches} cross-path prompt mismatches")
    return {
        "complete": aligned and not identity_mismatches and not prompt_mismatches,
        "path_rows": {queue: len(results[queue]) for queue in queues},
        "aligned_evaluations": len(set.intersection(*key_sets)),
        "identity_mismatches": identity_mismatches,
        "prompt_mismatches": prompt_mismatches,
    }, violations, incomplete


def validate_cove(results: dict[str, list[dict[str, str]]]) -> tuple[dict, list[str], list[str]]:
    initial_queue = "self_verification_cove_initial"
    verify_queue = "self_verification_cove_verification"
    violations: list[str] = []
    incomplete: list[str] = []
    if initial_queue not in results or verify_queue not in results:
        incomplete.append("CoVe initial and verification results are not both available")
        return {"complete": False}, violations, incomplete

    initial_rows = results[initial_queue]
    verify_rows = results[verify_queue]
    initial = {row["evaluation_id"]: row for row in initial_rows}
    verified = {row["evaluation_id"]: row for row in verify_rows}
    if len(initial) != len(initial_rows) or len(verified) != len(verify_rows):
        violations.append("CoVe contains duplicate evaluation IDs within a stage")
    aligned = set(initial) == set(verified)
    if not aligned:
        violations.append("CoVe initial and verification stages do not have identical evaluation IDs")
    metadata_mismatches = dependency_mismatches = prompt_link_mismatches = 0
    for evaluation_id in sorted(set(initial) & set(verified)):
        first = initial[evaluation_id]
        second = verified[evaluation_id]
        if (
            first["queue"] != initial_queue
            or first["condition"] != "self_verification_cove"
            or first["stage"] != "initial"
            or first["path_index"]
            or second["queue"] != verify_queue
            or second["condition"] != "self_verification_cove"
            or second["stage"] != "verification"
            or second["path_index"]
            or (first["task"], first["item_id"], first["variant"])
            != (second["task"], second["item_id"], second["variant"])
        ):
            metadata_mismatches += 1
        if second["depends_on_response_id"] != first["response_id"]:
            dependency_mismatches += 1
        if first["model_response"].strip() not in second["prompt"]:
            prompt_link_mismatches += 1
    if metadata_mismatches:
        violations.append(f"CoVe has {metadata_mismatches} stage metadata mismatches")
    if dependency_mismatches:
        violations.append(f"CoVe has {dependency_mismatches} dependency mismatches")
    if prompt_link_mismatches:
        violations.append(f"CoVe has {prompt_link_mismatches} verifier prompts missing the initial response")
    return {
        "complete": aligned and not metadata_mismatches and not dependency_mismatches and not prompt_link_mismatches,
        "initial_rows": len(initial_rows),
        "verification_rows": len(verify_rows),
        "aligned_evaluations": len(set(initial) & set(verified)),
        "metadata_mismatches": metadata_mismatches,
        "dependency_mismatches": dependency_mismatches,
        "prompt_link_mismatches": prompt_link_mismatches,
    }, violations, incomplete


def validate_notebooks() -> tuple[dict, list[str], list[str]]:
    directory = ROOT / "notebooks"
    actual = {path.name for path in directory.glob("*.ipynb")} if directory.exists() else set()
    missing = sorted(EXPECTED_NOTEBOOKS - actual)
    extras = sorted(actual - EXPECTED_NOTEBOOKS)
    violations: list[str] = []
    incomplete = [f"missing notebook notebooks/{name}" for name in missing]
    if extras:
        violations.append(f"unexpected notebooks: {extras}")
    execution_gaps: dict[str, int] = {}
    for name in sorted(EXPECTED_NOTEBOOKS & actual):
        try:
            document = json.loads((directory / name).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            violations.append(f"notebooks/{name} is not valid notebook JSON")
            continue
        gaps = sum(
            cell.get("cell_type") == "code" and cell.get("execution_count") is None
            for cell in document.get("cells", [])
        )
        execution_gaps[name] = gaps
        if gaps:
            incomplete.append(f"notebooks/{name} has {gaps} unexecuted code cells")
    return {
        "expected": len(EXPECTED_NOTEBOOKS),
        "present": len(EXPECTED_NOTEBOOKS & actual),
        "missing": missing,
        "unexpected": extras,
        "unexecuted_code_cells": execution_gaps,
    }, violations, incomplete


def validate_analysis() -> tuple[dict, list[str], list[str]]:
    directory = ROOT / "Analysis"
    details: dict[str, dict] = {}
    violations: list[str] = []
    incomplete: list[str] = []
    for filename, expected in EXPECTED_ANALYSIS_ROWS.items():
        path = directory / filename
        if not path.exists():
            incomplete.append(f"missing analysis Analysis/{filename}")
            continue
        fields, rows = read_csv(path)
        details[filename] = {"rows": len(rows), "columns": fields}
        if len(rows) != expected:
            violations.append(f"Analysis/{filename} has {len(rows)} rows; expected {expected}")

    sc_path = directory / "self_consistency_aggregates.csv"
    if sc_path.exists():
        _, rows = read_csv(sc_path)
        unique = len({row.get("evaluation_id", "") for row in rows})
        invalid = 0
        for row in rows:
            try:
                votes = int(row.get("winning_votes", ""))
            except ValueError:
                invalid += 1
                continue
            expected_status = "answered" if votes >= 2 else "no_consensus"
            expected_answer = row.get("final_answer", "") != "NO_CONSENSUS" if votes >= 2 else row.get("final_answer", "") == "NO_CONSENSUS"
            expected_agreement = "unanimous" if votes == 3 else "majority" if votes == 2 else "none"
            if (
                votes not in {1, 2, 3}
                or row.get("status") != expected_status
                or not expected_answer
                or row.get("agreement") != expected_agreement
            ):
                invalid += 1
        details.setdefault(sc_path.name, {}).update(
            {"unique_evaluation_ids": unique, "invalid_vote_rows": invalid}
        )
        if unique != 450 or invalid:
            violations.append(
                f"Analysis/{sc_path.name} has unique={unique}, invalid_vote_rows={invalid}"
            )

    cove_path = directory / "cove_aggregates.csv"
    if cove_path.exists():
        _, rows = read_csv(cove_path)
        unique = len({row.get("evaluation_id", "") for row in rows})
        invalid = sum(
            (row.get("answer_changed", "").lower() == "true")
            != (row.get("initial_normalized", "") != row.get("final_normalized", ""))
            or row.get("status") != "answered"
            for row in rows
        )
        details.setdefault(cove_path.name, {}).update(
            {"unique_evaluation_ids": unique, "invalid_stage_rows": invalid}
        )
        if unique != 450 or invalid:
            violations.append(
                f"Analysis/{cove_path.name} has unique={unique}, invalid_stage_rows={invalid}"
            )

    required_documents = ("summary.json", "aggregation_summary.json", "REPORT.md")
    for filename in required_documents:
        if not (directory / filename).exists():
            incomplete.append(f"missing analysis Analysis/{filename}")
    summary_path = directory / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        expected_values = {
            "conditions": 7,
            "task_variant_cells": 45,
            "evaluation_units": 2250,
            "raw_model_generations": 3600,
            "completed_evaluations": 2250,
        }
        mismatches = {
            key: {"expected": value, "actual": summary.get(key)}
            for key, value in expected_values.items()
            if summary.get(key) != value
        }
        details["summary.json"] = {"metric_mismatches": mismatches}
        if mismatches:
            violations.append(f"Analysis/summary.json metric mismatches: {sorted(mismatches)}")
    return details, violations, incomplete


def validate_manifest() -> tuple[dict, list[str], list[str]]:
    path = ROOT / "tier1_manifest.json"
    if not path.exists():
        return {"present": False}, [], ["missing tier1_manifest.json"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    violations: list[str] = []
    expected_evaluations = {
        "normalize_then_solve": 250,
        "structured_decomposition": 250,
        "explicit_task_instructions": 200,
        "chain_of_thought": 450,
        "rereading_s2a": 200,
        "self_consistency": 450,
        "self_verification_cove": 450,
    }
    if payload.get("evaluation_units") != expected_evaluations:
        violations.append("tier1_manifest.json has unexpected evaluation-unit counts")
    if payload.get("total_planned_model_responses") != sum(EXPECTED_COUNTS.values()):
        violations.append("tier1_manifest.json total planned responses is not 3600")
    if payload.get("questions_per_task") != 50:
        violations.append("tier1_manifest.json does not describe 50 questions per task")
    return {
        "present": True,
        "questions_per_task": payload.get("questions_per_task"),
        "evaluation_units": payload.get("evaluation_units"),
        "total_planned_model_responses": payload.get("total_planned_model_responses"),
    }, violations, []


def audit(*, allow_incomplete: bool = False) -> dict:
    files = active_files()
    scan = scan_public_files(files)
    result_counts, result_violations, result_incomplete, results = validate_results()
    journals, journal_violations, journal_incomplete = validate_journals(results)
    self_consistency, sc_violations, sc_incomplete = validate_self_consistency(results)
    cove, cove_violations, cove_incomplete = validate_cove(results)
    notebooks, notebook_violations, notebook_incomplete = validate_notebooks()
    analysis, analysis_violations, analysis_incomplete = validate_analysis()
    manifest, manifest_violations, manifest_incomplete = validate_manifest()

    violations = (
        result_violations
        + journal_violations
        + sc_violations
        + cove_violations
        + notebook_violations
        + analysis_violations
        + manifest_violations
    )
    for category, findings in scan.items():
        if findings:
            violations.append(f"{category}: {len(findings)} finding(s)")
    incomplete = (
        result_incomplete
        + journal_incomplete
        + sc_incomplete
        + cove_incomplete
        + notebook_incomplete
        + analysis_incomplete
        + manifest_incomplete
    )
    status = "fail" if violations else "incomplete" if incomplete else "pass"
    payload = {
        "status": status,
        "expected_scored_evaluation_units": 2250,
        "expected_raw_model_responses": sum(EXPECTED_COUNTS.values()),
        "violations": violations,
        "incomplete": incomplete,
        **scan,
        "manifest": manifest,
        "result_counts": result_counts,
        "journal_reconciliation": journals,
        "self_consistency_invariants": self_consistency,
        "cove_invariants": cove,
        "notebooks": notebooks,
        "analysis": analysis,
        "file_count": len(files),
        "file_sha256": {
            relative(path): public_sha256(path)
            for path in files
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    printable = {key: value for key, value in payload.items() if key != "file_sha256"}
    print(json.dumps(printable, indent=2))
    if status == "fail" or (status == "incomplete" and not allow_incomplete):
        raise SystemExit(1)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the public Tier-1 artifact")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="report missing in-progress artifacts without returning an error",
    )
    args = parser.parse_args()
    audit(allow_incomplete=args.allow_incomplete)


if __name__ == "__main__":
    main()
