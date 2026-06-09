# P1 Integration Smoke — test_1 / test_2 (2026-06-09)

Full-flow acceptance of the v1.4 P1 single-report pipeline, run end-to-end
through the **worktree** orchestrator (`scripts/run_formal_analysis.py`) with
real MinerU OCR + health-summary API and agent fills at CP1–CP4.

> ⚠️ The repo-root `cancerrisk-skill/` is the pre-P1 v1.4 checkout. Full-flow
> runs MUST use the worktree's `scripts/run_formal_analysis.py`, or they execute
> the old 4-HTML pipeline (exit-4 manual archive, `*_risk.html`).

## How it was driven (headless convention)
- demographics via `--person-sex/--person-age` (refined.md auto-parse insufficient).
- CP2 `answers.json`: jizaoan `negative`, family-history `no`, genetic-testing
  `no`, smoking/alcohol `never` — a valid minimal set that avoids required
  conditional follow-ups (validated by `validate_answers.py`, 0 errors/smells).
- CP3 candidates filled with `evidence_text` verified as literal substrings of
  each `refined.md`; both validators report all records accepted.
- CP4 via `finalize_structured_summary.py --fills` → `status=ready_for_render`.

## Results

| Criterion | test_1 (single PDF) | test_2 (3 PDF + 3 img) |
|---|---|---|
| ① end-to-end exit 0 | ✅ | ✅ |
| ② `report.html` produced | ✅ 6.0 KB | ✅ 5.9 KB |
| ③ no old 4 HTML in output | ✅ | ✅ |
| ④ `artifacts/report.json` valid, `schema_version=report-v1` | ✅ | ✅ |
| ⑤ archive auto-applied to `docudatabase/<pid>/` | ✅ `applied=True` | ✅ `applied=True` |
| ⑥ no `longitudinal_risk.json` | ✅ | ✅ |
| ⑦ no exit-4 / manual 入档 halt | ✅ | ✅ |

- test_1: 68M, person `smoke_t1`; 15 snapshot cancers, 7 tumor markers, VoI top `吉早安`; jizaoan negative branch rendered (含「阴性」).
- test_2: 29M `钟贤宇` (甲状腺癌术后随访), person `smoke_t2`; 15 cancers, 3 markers, VoI top `鼻咽镜+EBV-DNA`; all 6 sections present.

## Notes / P2 follow-ups (scaffold scope)
- `report.html` is the P1 scaffold (6 section containers + jizaoan/brca Jinja
  branches). Field-level fidelity to temp/html-preview-2/-7 is P2.
- `report.json.health_summary.{abnormal_non_cancer_count,items}` default to
  `0/[]` — the CP4 skeleton uses `assessment_result.*`; mapping those into the
  report is P2.
- Header shows `person.person_id` (e.g. `smoke_t2`), not display name — P2.

Unit suite: 41 passed.
