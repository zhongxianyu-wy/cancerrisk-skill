# CancerRisk v1.4 — P2: Single Integrated Report, Full-Fidelity Content

**Status:** Design approved (2026-06-09). Next: writing-plans → execute subagent-driven in a fresh session.
**Builds on:** P1 (single-report pipeline, merged into `v1.4` @ `a221b69`).
**Base branch:** `v1.4`. Execute on a new worktree/branch `v1.4-p2-report-fidelity` (mirror P1).

## Goal
Upgrade `report.html` from the P1 **scaffold** (6 empty section containers) to
**content-aligned** with the two reference designs:
- `temp/html-preview-2.html` — jizaoan-**negative** case
- `temp/html-preview-7.html` — jizaoan-**positive** case

All six sections populated from `report.json`. **Every datum must be
evidence-sourced / PUA-safe** — no LLM-invented IDs, probabilities, intervals, or
advice. No new math engine; reuse P1's deterministic outputs.

## Decisions (brainstorm 2026-06-09)
- **Fidelity bar = content alignment**, not pixel-perfect clone. Reuse temp's
  CSS/structure; the bar is correct data in every section + traceable sources.
- **Lifestyle + health-summary content source = CP4** (`health_summary_structured_summary.json::assessment_result.*`).
  These HTML blocks are structured by the agent at CP4 from the external
  health-management **API response** — same provenance as the rest of the health
  summary, so PUA-acceptable. Not a new evidence-store vocabulary; not invented.
- **P2 this round = spec + plan only**; implementation executes in a fresh session
  (subagent-driven, like P1).
- **Testing adds a jizaoan-positive variant** (test_1/test_2 are both negative) to
  cover the `-7` branch.

## Architecture (3 layers, mirrors P1; only Layer 1 touches the engine)

### Layer 1 — `scripts/build_report_json.py` enrichment (pure remap, no math)
Add to the assembled `report.json`:
- `person.name` ← `health_summary_structured_summary.json::patient_data.name`
  (fallback to `person_id` when absent / "未提供").
- `health_summary.blocks` ← the CP4 `assessment_result.*` HTML strings:
  `risk_level`, `core_risk_factors`, `overall_assessment`, `abnormal_table`,
  `disease_cards`, `advice_list`, `conclusion_table`. Carry verbatim (they are
  pre-built HTML). Keep existing P1 keys
  (`status`/`abnormal_non_cancer_count`/`items`) for backward compatibility.
- Everything else (snapshot / voi / tumor_markers / jizaoan_result /
  jizaoan_top_cancers / brca_status / evidence_version) unchanged.
- Stays pure: read + remap + atomic write. Missing blocks degrade to empty
  string / `None` gracefully.

### Layer 2 — `templates/integrated_report_v14.html` buildout (bulk of the work)
Fill the six existing section containers. Data mapping (all sourced, PUA-safe):

| Section id | Content | report.json source |
|---|---|---|
| section-header | name, risk level, date, evidence version | person.name, health_summary.blocks.risk_level, generated_at, evidence_version |
| section-timeline (⏱️ 体检就诊清单) | priority/important/maintain cards | snapshot.cancers[].risk_tier → tier; section4_screening[] recipes (method/population/interval/trigger/source_id) |
| section-clinical-design (🧱 循证 1+X) | abnormal findings + disease cards + screening design | health_summary.blocks.abnormal_table + disease_cards; section4_screening |
| section-liquid-biopsy (🧬) | jizaoan branch + tumor markers | `{% if jizaoan_result=="positive" %}`→深度说明 `{% else %}`→独立合规展示; voi (吉早安 entry), jizaoan_top_cancers, tumor_markers[] |
| section-package (📦 组合套餐预算) | recommendation tiers + budget | voi.rankings[] (recommendation 常规/推荐/强烈推荐, cost_rmb, cost_level, invasiveness) |
| section-lifestyle (🥗) | personalized intervention + disclaimer | health_summary.blocks.advice_list + overall_assessment; disclaimer |
| genetic branch | hereditary-risk block | `{% if brca_status=="positive" %}` |

**Rendering rule:** CP4 HTML blocks (abnormal_table, disease_cards, advice_list,
risk_level, conclusion_table) render with `| safe` (trusted, agent-built).
Scalar/loop fields (person, cancer names, voi numbers, tumor_markers) stay
**autoescaped** (P1 enabled autoescape). This split is the key escaping contract.

### Layer 3 — `scripts/render_report.py`
Unchanged from P1 (thin Jinja render, StrictUndefined + autoescape). The `| safe`
filters live in the template, not the renderer.

## Testing
- Extend `tests/test_p1_template_structure.py` (or a new `test_p2_*`): assert each
  section renders **real data bindings** (not just the container id) for both a
  negative and a positive `report.json` fixture; assert brca-positive branch;
  assert CP4 HTML blocks appear unescaped and scalar fields appear escaped.
- Unit: `build_report_json` carries `person.name` + `health_summary.blocks`;
  graceful when blocks absent.
- **Acceptance (integration):** re-run `test_1` + `test_2` (negative) from the
  worktree end-to-end; **plus a jizaoan-positive variant** (e.g. test_1 inputs
  with `answers.q_jizaoan_result="positive"` + top1/top2) to exercise the `-7`
  branch. Verify report.html sections carry real content matching the temp
  reference structure; report.json still `schema_version=report-v1`.

## Non-goals (defer)
- Pixel-perfect byte-identical match to temp (fonts, spacing micro-tuning).
- New deterministic builders / new evidence-store vocabularies.
- Longitudinal single-indicator view (separate v1.5 direction in spec.md).

## Execution shape
Multi-task plan, subagent-driven (like P1), on `v1.4-p2-report-fidelity`:
T1 enrich build_report_json (+tests) → T2–T7 build sections + jizaoan/brca
branches (TDD per section) → T8 integration acceptance (test_1/test_2 + positive
variant) → merge into v1.4 → Task: re-run darwin/skill-creator eval (expect dim8
↑ as the "audit-grade report" gap closes).

## Risks / watch-items
- **Escaping contract** (`| safe` only on trusted CP4 blocks) — get this wrong and
  you either show raw `<table>` tags or open an injection surface. Tests must
  assert both sides.
- **CP4 block shape**: the skeleton is `assessment_result.*` (HTML strings). If a
  run skips CP4 fills, blocks are empty → sections must degrade gracefully, not
  crash (StrictUndefined: guard with `default`).
- **Positive-jizaoan fixture**: validate_answers requires top1/top2 when
  result=positive — the variant's answers.json must satisfy the cascade.
