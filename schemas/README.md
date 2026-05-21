# `schemas/` — Cross-process artifact contracts

This directory is intentionally minimal. Only artifacts that **another
process or downstream tool reads** belong here. Inline data structures
that exist purely between v3 stages are documented in:

* the producing script's docstring (`scripts/<name>.py`)
* the matching `tests/test_v3_*.py` golden fixtures
* `references/event_format.md` for the slim ⇄ full event-key contract

## Current schemas

| File | Producer | Consumer |
|---|---|---|
| `manifest.schema.json` | `scripts/write_manifest.py` (Task9) | Index router page, downstream dashboards, audit-bot integrations |

## Not in `schemas/` on purpose

| Artifact | Where its contract lives |
|---|---|
| `risk_factor_assertion_template.json` | `scripts/build_assertion_fill_template.py::SCHEMA_VERSION` (`risk-factor-file-fill-v3.3`) + `tests/test_v3_factor_extraction.py::test_slim_factor_level_template_*` |
| `mineru/<data_id>/risk_factor_extraction.candidate.json` | `scripts/llm_factor_extract.py::validate_candidate_payload` |
| `merged_risk_factors.json` | `scripts/merge_risk_factors.py::merge_payloads` docstring + `tests/test_v3_interactive_completion.py::test_merge_*` |
| `snapshot_risk.json` | `scripts/snapshot_risk.py::compute_snapshot` |
| `longitudinal_risk.json` | `scripts/longitudinal_risk.py::compute_longitudinal` |
| `archive_update_proposal.json` | `scripts/archive_manager.py::build_archive_proposal` |
| `demographics.json` | `scripts/demographics.py::resolve` + `tests/test_v3_demographics.py::test_resolve_*` |
| `interactive_questionnaire.json`, `supplemental_*` | `scripts/interactive_completion.py` |

## Why so few JSON schemas?

The v2 skill carried six JSON schemas (`extracted_report`,
`evidence_candidate`, `factor_mapping`, `observation`,
`evidence_update_proposal`, `archive_update_proposal`) that described an
older, very different pipeline. None of them aligned with the v3
artifacts the orchestrator actually emits. They were removed in the v3
production-prep audit because misleading schemas are worse than no
schemas — they suggest a contract exists when none does.

Add a schema here when (and only when) a real cross-process consumer
needs to validate the artifact. Until then the producer's docstring +
the test golden fixtures are the source of truth.
