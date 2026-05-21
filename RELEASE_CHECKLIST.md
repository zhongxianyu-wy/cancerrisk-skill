# Release Checklist (v3)

Run this list before promoting CancerRisk v3 to a new environment.
The order matches the orchestrator stage order so a failure here maps
1:1 to where the production flow would break.

## 0. Environment

- [ ] `python -V` ≥ 3.10
- [ ] `python cancerrisk-skill/scripts/env_check.py --json` reports
      `status: pass` (or `warning` when `curl` is missing and Task6 is
      not in scope for this deployment).
- [ ] All dependencies from `requirements.txt` are installed
      (`PyYAML`, `jsonschema`, `jinja2`, `requests`).
- [ ] `pytest tests/ -q --ignore=tests/test_formal_end_to_end_pdf.py`
      green (≥125 tests as of evidence-v0002).

## 1. Configuration

- [ ] `cancerrisk-skill/config/formal.yaml` reviewed for the target
      environment.
  - [ ] `mineru.demo_token` replaced with the operator's own MinerU
        token, or `--save-mineru-token <token>` has been run to put a
        user token into the gitignored `config/local.yaml`.
  - [ ] `mineru.token_source` set to `user` in production; leaving it
        as `demo` is acceptable only for smoke tests.
  - [ ] `health_summary.api.*` URLs match the actually reachable
        upstream (`jiyinjia.jinbaisen.com` token endpoint +
        `ydai.jinbaisen.com/api/v1` chat endpoint) — Task6 will fail
        otherwise.
  - [ ] `person_context` defaults left as is; the orchestrator prints
        a loud `WARNING` when these defaults are silently consumed.
  - [ ] `risk_prediction.risk_tiers` thresholds reflect the clinical
        policy you want (current defaults: `low ≤ 0.5%`,
        `medium ≤ 2%`, `high > 2%`).
- [ ] `config/contact.json` matches the screening hotline / URL
      strings you want appearing in the rendered HTML.
- [ ] `evidence_store/versions/evidence_version.json` matches the tag
      you intend to ship; `versions/changelog.md` has an entry for it.

## 2. Evidence store integrity

- [ ] `pytest tests/test_v3_evidence_ontology.py -q` green.
- [ ] `cancer_age_sex_priors.json` exists and the `missing_priors`
      list reflects the cancers you accept as un-scored (currently 7:
      esophageal, cervical, ovarian, bladder, kidney, head_neck,
      biliary_tract).
- [ ] `risk_assertions_derived.json` and
      `detection_performance_derived.json` rebuilt against the
      current `risk_assertions.json` / `detection_performance.json`
      (`build_derived_evidence.py` is idempotent).

## 3. Stage-by-stage smoke

Run on `test/true_test/` (or the deployment's smoke fixture) with
`--reuse-mineru-cache` when a recent cache exists.

- [ ] **MinerU**: `--stop-after mineru` writes
      `artifacts/conversion_manifest.json` with `status=success` and
      one `mineru/<data_id>/` directory per input file.
- [ ] **Demographics**: `--stop-after demographics` resolves sex+age
      from one of {CLI, report extraction, interactive answers}.
      Verify `artifacts/demographics.json::source` is the expected
      value for the smoke input.
- [ ] **Task4 scaffold**: `--stop-after assertion-template` produces
      `artifacts/risk_factor_assertion_template.json` filtered for
      the resolved sex+age, plus a candidate scaffold per `data_id`.
- [ ] **Task4 agent fill**: every
      `mineru/<data_id>/risk_factor_extraction.candidate.json` has
      been touched by the skill agent (see SKILL.md "Task4 fill
      recipe"); `llm_factor_extract.is_candidate_filled` returns
      `True` for each.
- [ ] **Task4 gate**: `--stop-after risk-factor-gate` writes
      `structured_risk_factors.json`,
      `risk_factor_assertion_status.json`,
      `needs_confirmation_factors.json`,
      `refined_content_bundle.md`. Exit code is 0.
- [ ] **Task5 interactive**: `--stop-after interactive` writes
      `interactive_questionnaire.json`,
      `supplemental_risk_factor_updates.json`,
      `supplemental_risk_factors.{md,json}`,
      `merged_risk_factors.json`. Every entry in
      `merged_risk_factors.json::screening_tests` carries a non-null
      `exam_date`.
- [ ] **Task6**: phase A reaches `jiyinjia.jinbaisen.com` and
      `ydai.jinbaisen.com`; raw markdown lands in
      `health_summary_api_response.md`. Phase B
      (`health_summary_structured_summary.json::status` =
      `ready_for_render`) is completed by the agent per SKILL.md
      "Task6 structuring recipe". Phase C renders
      `health_summary.html` with **zero** unresolved `{{...}}` /
      `__...__` placeholders.
- [ ] **Task7**: `snapshot_risk.json::cancers` contains 13 entries;
      sex-mismatched and missing-prior cancers are surfaced with
      `posterior_probability: null` and a clear `status_reason`.
      `snapshot_risk.html` renders cleanly.
- [ ] **Task8 archive**: `--auto-apply-archive` applies explicitly; production
      runs stop at `--stop-after archive-proposal` and require
      explicit operator confirmation before the timeline is touched.
- [ ] **Task8 longitudinal**: `longitudinal_risk.json::cancers`
      covers every cancer with a posterior (no top-N filtering).
      Cancers without history collapse to `snapshot_only` or
      `single_point`; multi-point timelines report `with_trend`.
- [ ] **Task9**: `manifest.json` validates against
      `schemas/manifest.schema.json`. `index.html` links the three
      business reports without leaking per-cancer business
      conclusions into the router page.

## 4. Final user-facing outputs

`analysis_output/` contains exactly four HTML files **and no more**:

- [ ] `index.html`
- [ ] `health_summary.html`
- [ ] `snapshot_risk.html`
- [ ] `longitudinal_risk.html`

Each report:

- [ ] Renders the safety disclaimer pulled from
      `config/formal.yaml::safety.disclaimer`.
- [ ] Contains no LLM-generated probabilities, OR/RR/HR, sensitivity,
      specificity, or screening intervals (those numbers come from
      `evidence_store/` only).
- [ ] Marks sex-specific cancers as `not_applicable` /
      `posterior_probability: null` when the person's sex does not
      match.

## 5. Audit trail

- [ ] `module_audits/` has one note per stage that ran.
- [ ] `manifest.json::status` is `success` for a clean run, `partial`
      when at least one report failed to render, `fail` when the
      pipeline aborted before Task9.
- [ ] `manifest.json::audit_notes` lists every per-stage audit file.
- [ ] MinerU's `token_source` and `token_fingerprint` (last 4 chars
      only — never the full token) are visible in `manifest.json` and
      the stderr log.

## 6. Operator entrypoints

- [ ] qwenpaw / workbuddy integration points still wire to
      `scripts/run_formal_analysis.py`.
- [ ] `SKILL.md::Runtime workflow` describes the **current** two
      agent checkpoints (Task4 fill, Task6 structuring).
- [ ] No `_legacy/` or `tests/_legacy/` referenced by any production
      script (these directories should be removed before release).
