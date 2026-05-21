#!/usr/bin/env python3
"""Task4 risk-factor candidate validation helpers.

Task4 is a skill-native fill step performed by the agent that is running
this skill (per SKILL.md). The orchestrator scaffolds a per-file
``risk_factor_extraction.candidate.json`` next to each MinerU
``content.md``, the agent edits ``llm_fill`` / ``file_context`` in place,
and the gate then validates and admits records.

This module holds only the small surface that other scripts and tests
import: field-set constants, schema versions, and a payload validator.
There is no external API call, no prompt-package writer, and no
``awaiting_skill_llm_generation`` placeholder path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SLIM_FILL_SCHEMA_VERSION = "risk-factor-file-fill-v3.3"
ASSERTION_FILL_SCHEMA_VERSION = "risk-factor-assertion-fill-v3.2"

SLIM_RECORD_REQUIRED_FIELDS = {
    "factor_key",
    "factor_id",
    "factor_name",
    "factor_type",
    "factor_level",
    "risk_evidence_values",
    "exists",
    "evidence_text",
    "source_section",
    "source_page",
    "negated",
    "confidence",
    "raw_field_description",
}

FIXED_ASSERTION_FIELDS = {
    "assertion_key",
    "assertion_id",
    "cancer_id",
    "factor_id",
    "factor_name",
    "factor_type",
    "factor_level",
    "effect_type",
    "effect_value",
    "applicable_sex",
    "interaction_needed_if_missing",
    "interaction_question_group",
    "expected_evidence",
    "synonyms",
    "llm_fill",
}

LLM_FILL_REQUIRED_FIELDS = {
    "exists",
    "exam_date",
    "evidence_text",
    "source_file",
    "source_section",
    "source_page",
    "negated",
    "confidence",
    "raw_field_description",
}

# Optional numeric measurement fields — present only when the factor has a
# quantitative value (tumor marker concentration, nodule size in mm, etc.).
LLM_FILL_OPTIONAL_FIELDS = {
    "measurement_value",
    "measurement_unit",
}

LLM_FILL_FIELDS = LLM_FILL_REQUIRED_FIELDS | LLM_FILL_OPTIONAL_FIELDS

FILE_CONTEXT_FIELDS = {"exam_date", "source_file", "source_data_id"}


def _is_slim_payload(payload: dict[str, Any]) -> bool:
    if payload.get("schema_version") == SLIM_FILL_SCHEMA_VERSION:
        return True
    return "risk_factor_templates" in payload or (
        "records" in payload and any("factor_key" in record for record in payload.get("records") or [])
    )


def _records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("records")
    if records is None:
        records = payload.get("risk_factor_templates") or payload.get("assertion_templates")
    if not isinstance(records, list):
        raise ValueError("candidate JSON must contain records, risk_factor_templates, or assertion_templates list")
    return records


def validate_candidate_payload(payload: dict[str, Any]) -> None:
    """Raise ``ValueError`` if a Task4 candidate JSON is structurally broken."""
    records = _records(payload)
    if _is_slim_payload(payload):
        file_context = payload.get("file_context")
        if not isinstance(file_context, dict):
            raise ValueError("slim candidate JSON must contain a file_context object")
        missing_ctx = FILE_CONTEXT_FIELDS - set(file_context)
        if missing_ctx:
            raise ValueError(f"file_context missing fields: {sorted(missing_ctx)}")
        for idx, record in enumerate(records):
            missing = SLIM_RECORD_REQUIRED_FIELDS - set(record)
            if missing:
                raise ValueError(f"records[{idx}] missing slim fields: {sorted(missing)}")
        return

    for idx, record in enumerate(records):
        missing = FIXED_ASSERTION_FIELDS - set(record)
        if missing:
            raise ValueError(f"records[{idx}] missing fixed assertion fields: {sorted(missing)}")
        fill = record.get("llm_fill")
        if not isinstance(fill, dict):
            raise ValueError(f"records[{idx}].llm_fill must be an object")
        missing_fill = LLM_FILL_REQUIRED_FIELDS - set(fill)
        extra_fill = set(fill) - LLM_FILL_FIELDS
        if missing_fill:
            raise ValueError(f"records[{idx}].llm_fill missing fields: {sorted(missing_fill)}")
        if extra_fill:
            raise ValueError(f"records[{idx}].llm_fill contains unsupported fields: {sorted(extra_fill)}")


def is_candidate_filled(payload: dict[str, Any]) -> bool:
    """Return True when the agent has touched the candidate.

    The orchestrator uses this to distinguish "agent has not run yet"
    (scaffold = all defaults) from "agent reviewed this file". A candidate
    counts as filled when **any** of:

    * a record has ``exists`` explicitly set to ``True``, ``False``, or
      ``"unknown"`` with evidence / non-zero confidence
    * a record has ``evidence_text`` or ``confidence > 0``
    * ``file_context.exam_date`` is set on the slim payload (signals the
      agent reviewed the file even when *zero* ontology factors apply —
      e.g. a single-page ancillary scan)

    Without the third clause, ancillary files with no ontology-relevant
    findings would force the orchestrator to either pretend a finding is
    present or refuse to continue. The ``exam_date`` signal is cheap for
    the agent to set and gives a verifiable "yes I read this" marker.
    """
    if _is_slim_payload(payload):
        file_context = payload.get("file_context") or {}
        if file_context.get("exam_date"):
            return True
    records = _records(payload)
    if not records:
        return False
    if _is_slim_payload(payload):
        for record in records:
            exists = record.get("exists")
            evidence = record.get("evidence_text")
            confidence = record.get("confidence") or 0
            if exists in {True, False} or (exists == "unknown" and (evidence or confidence > 0)):
                return True
            if evidence or confidence > 0:
                return True
        return False
    for record in records:
        fill = record.get("llm_fill") or {}
        if fill.get("exists") in {True, False}:
            return True
        if fill.get("evidence_text") or (fill.get("confidence") or 0) > 0:
            return True
    return False


def scaffold_slim_candidate(
    template_payload: dict[str, Any],
    *,
    source_data_id: str,
    source_file: str | None,
) -> dict[str, Any]:
    """Return a per-file slim candidate payload ready for the agent to edit."""
    if not _is_slim_payload(template_payload):
        raise ValueError("scaffold_slim_candidate expects a slim assertion-fill template payload")
    records = _records(template_payload)
    return {
        "schema_version": SLIM_FILL_SCHEMA_VERSION,
        "evidence_version": template_payload.get("evidence_version"),
        "filters": template_payload.get("filters", {}),
        "file_context": {
            "exam_date": None,
            "source_file": source_file,
            "source_data_id": source_data_id,
        },
        "records": [dict(record) for record in records],
    }


def load_candidate(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_candidate(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
