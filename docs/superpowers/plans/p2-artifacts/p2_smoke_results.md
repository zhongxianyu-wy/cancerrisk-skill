# P2 Integration Acceptance — test_1 / test_2 / positive variant (2026-06-10)

Full-fidelity report content, run end-to-end on branch `v1.4-p2-report-fidelity`
(repo-root checkout on the P2 branch — single checkout, no worktree gotcha).
Reused the P1 CP1–CP4 artifacts under `/tmp/p1smoke_t1` and `/tmp/p1smoke_t2`;
re-ran the final stage with P2 code.

## Results

| Case | jizaoan | Result |
|---|---|---|
| test_1 (single PDF, 68M) | negative | ✅ report.html 9.8 KB (vs 6.0 KB P1 scaffold) |
| test_2 (3 PDF + 3 img, 29M 钟贤宇) | negative | ✅ report.html 9.3 KB, header shows real name 钟贤宇 |
| positive variant (test_1 + `q_jizaoan_result=positive`, top1=lung_cancer) | positive | ✅ 阳性信号深度说明 branch + lung_cancer rendered |

All runs exit 0; report.json `schema_version=report-v1` with new `person.name` + `health_summary.blocks`.

## Per-section verification (test_1, real run)
- **header**: person.name + risk badge (`🟠 高风险（ADR 47.4）`) + evidence version. ✅
- **timeline (⏱️)**: screening cards with method/interval/trigger/source_id, tiered by `risk_tier` (priority/important/maintain classes). ✅
- **clinical-design (🧱)**: `abnormal_table` (慢性萎缩性胃炎) + `disease_cards` (胃恶性肿瘤) render as **real unescaped `<table>`**. ✅
- **liquid-biopsy (🧬)**: negative=独立合规展示(阴性) / positive=阳性信号深度说明; tumor markers table. ✅
- **package (📦)**: VoI rows sorted by recommendation tier with cost/invasiveness/guideline. ✅
- **lifestyle (🥗)**: `advice_list` rendered unescaped + disclaimer. ✅

## Escaping contract (verified on real run)
- Trusted CP4 HTML blocks (abnormal_table / disease_cards / advice_list) appear **unescaped** (`<table` present, `&lt;table` absent).
- Scalar fields autoescaped (unit test `test_scalar_fields_escaped`: `<b>` → `&lt;b&gt;`).

## Notes / scope
- `person.name` falls back to `person_id` when CP4 `patient_data.name` is "未提供"
  (test_1 → `smoke_t1`); test_2 carries the real name 钟贤宇.
- `lab_results_table` is intentionally NOT carried (design block-key set = risk_level/
  core_risk_factors/overall_assessment/abnormal_table/disease_cards/advice_list/
  conclusion_table). Possible P2.1/P3 refinement if lab rows are wanted in 1+X.
- Unit suite: 53 passed (P1 41 + P2-T1 3 + P2 sections 9).
