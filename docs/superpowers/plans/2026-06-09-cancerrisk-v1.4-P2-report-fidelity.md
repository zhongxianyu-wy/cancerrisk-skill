# CancerRisk v1.4 — P2: Report Full-Fidelity Content — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax. Build the skill via skill-creator guidance where SKILL.md/structure changes; after P2 completes, run skill-creator + darwin joint eval (spec §6).

**Goal:** Populate the six P1 scaffold sections of `report.html` with real, evidence-sourced content content-aligned to `temp/html-preview-2` (jizaoan-negative) and `-7` (jizaoan-positive).

**Architecture:** Three layers (mirrors P1). Layer 1: enrich `build_report_json.py` to carry `person.name` + `health_summary.blocks` (CP4 `assessment_result.*` HTML). Layer 2: build out `templates/integrated_report_v14.html` section by section from `report.json`. Layer 3: renderer unchanged (P1 thin Jinja, StrictUndefined + autoescape; CP4 HTML blocks use `| safe` in the template). No new math engine.

**Tech Stack:** Python 3.11 + uv (PyYAML/jsonschema/jinja2/requests); Jinja2; pytest; `test/test_1`+`test/test_2` + a jizaoan-positive variant for integration.

**Base/branch:** Create worktree `v1.4-p2-report-fidelity` off `v1.4` via superpowers:using-git-worktrees BEFORE Task 1.

**Design ref:** `docs/superpowers/specs/2026-06-09-cancerrisk-v1.4-P2-report-fidelity-design.md`

**Test command (all tasks):**
```
uv run --python 3.11 --with pytest --with PyYAML --with jsonschema --with jinja2 --with requests python -m pytest <path> -q
```

---

## Reference data shapes (verified from a real P1 run)

`report.json` already carries (P1):
- `person`: `{person_id, sex, age}` — P2 adds `name`.
- `snapshot.cancers[]`: `{cancer_id, cancer_name_zh, posterior_probability, risk_tier, imaging_findings, uncertainties, components, ...}`. `risk_tier` ∈ {`low`,`moderate`,`high`,`moderate_workup`,`high_workup`,`pathology_confirmed`,`null`}.
- `snapshot.section4_screening[]`: `{cancer_id, cancer_name_zh, posterior_probability, risk_tier, standard_screening:[{method, population, interval, trigger, source_id}]}`.
- `voi.rankings[]`: `{cancer_name_zh, method, description, voi_score, recommendation, sensitivity, specificity, cost_rmb, cost_level, invasiveness, guideline, is_liquid_biopsy, multi_cancer_breakdown}`. `recommendation` ∈ {`强烈推荐`,`推荐`,`可考虑`,`常规`}.
- `voi.top_recommendation`: str.
- `jizaoan_result` ∈ {negative,positive,unknown}; `jizaoan_top_cancers[]`; `tumor_markers[]`; `brca_status`; `evidence_version`.

CP4 `health_summary_structured_summary.json` carries `patient_data.name` and `assessment_result.{risk_level, core_risk_factors, overall_assessment, abnormal_table, disease_cards, advice_list, conclusion_table}` (the last four are HTML-table/list strings).

**Card-tier mapping (timeline / clinical):** `high`/`high_workup`/`pathology_confirmed` → **priority**; `moderate`/`moderate_workup` → **important**; `low` → **maintain**; `null`/not-applicable → omit from timeline.

---

## Task 1 — Enrich `build_report_json.py`: person.name + health_summary.blocks

**Files:**
- Modify: `scripts/build_report_json.py`
- Test: `tests/test_p2_build_report_blocks.py` (create)

- [ ] **Step 1: Write the failing test**
```python
import json, importlib.util
from pathlib import Path
def _load():
    spec = importlib.util.spec_from_file_location("brj", Path(__file__).parent.parent/"scripts"/"build_report_json.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def _write(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

def test_blocks_and_name_carried(tmp_path):
    art = tmp_path/"artifacts"; art.mkdir()
    _write(art/"snapshot_risk.json", {"cancers":[],"section4_screening":[],"uncertainties_summary":{},"person_context":{"sex":"male","age":68}})
    _write(art/"voi_ranking.json", {})
    _write(art/"health_summary_structured_summary.json", {
        "patient_data":{"name":"张三"},
        "assessment_result":{"risk_level":"🟠 高风险","abnormal_table":"<table><tr><td>X</td></tr></table>",
            "disease_cards":"<table></table>","advice_list":"<ul><li>戒烟</li></ul>",
            "conclusion_table":"<table></table>","core_risk_factors":"A","overall_assessment":"B"}})
    m = _load()
    rep = m.assemble_report_json(artifacts=art, out=tmp_path, answers_path=None,
                                person_id="p1", run_id="r1", evidence_version="ev1")
    assert rep["person"]["name"] == "张三"
    b = rep["health_summary"]["blocks"]
    assert b["risk_level"] == "🟠 高风险"
    assert "<table>" in b["abnormal_table"]
    assert b["advice_list"] == "<ul><li>戒烟</li></ul>"

def test_blocks_graceful_when_absent(tmp_path):
    art = tmp_path/"artifacts"; art.mkdir()
    _write(art/"snapshot_risk.json", {"cancers":[],"section4_screening":[],"uncertainties_summary":{},"person_context":{}})
    m = _load()
    rep = m.assemble_report_json(artifacts=art, out=tmp_path, answers_path=None,
                                person_id="p1", run_id="r1", evidence_version=None)
    assert rep["person"]["name"] in (None, "p1")     # fallback
    assert rep["health_summary"]["blocks"]["risk_level"] in (None, "")
```

- [ ] **Step 2: Run, verify FAIL** (`AttributeError`/`KeyError` on `blocks`/`name`).

- [ ] **Step 3: Implement.** In `assemble_report_json`, after reading `health` (the structured summary):
```python
    patient = health.get("patient_data", {}) if isinstance(health, dict) else {}
    ar = health.get("assessment_result", {}) if isinstance(health, dict) else {}
    _BLOCK_KEYS = ("risk_level","core_risk_factors","overall_assessment",
                   "abnormal_table","disease_cards","advice_list","conclusion_table")
```
Add `"name": patient.get("name") or person_id` to the `person` dict. Add to the `health_summary` dict:
```python
        "blocks": {k: ar.get(k) for k in _BLOCK_KEYS},
```
Keep existing `status`/`abnormal_non_cancer_count`/`items` keys unchanged.

- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Run full suite** (`tests/ -q`) — no regressions (P1 tests still 41+).
- [ ] **Step 6: Commit** `feat(p2-task1): carry person.name + CP4 health_summary.blocks into report.json`

---

## Task 2 — section-header full content

**Files:** Modify `templates/integrated_report_v14.html`; Test `tests/test_p2_sections.py` (create).

- [ ] **Step 1: Failing test** — render with a context having `person.name="张三"`, `health_summary.blocks.risk_level="🟠 高风险"`, `generated_at`, `evidence_version="ev1"`, `disclaimer`. Assert output contains `张三`, `高风险`, `ev1`. Use the real template under `Environment(FileSystemLoader('templates'), undefined=StrictUndefined, autoescape=select_autoescape(['html']))`.
- [ ] **Step 2: Run, verify FAIL** (header lacks these bindings).
- [ ] **Step 3: Implement** in `#section-header`: title `{{ person.name }}个性化体检方案`; a risk badge `{{ health_summary.blocks.risk_level | default('', true) }}`; meta line `生成于 {{ generated_at }} · evidence {{ evidence_version | default('N/A', true) }}`. Borrow `.sec-title`/header CSS from `temp/html-preview-2.html`.
- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Commit** `feat(p2-task2): section-header full content`

---

## Task 3 — section-timeline (⏱️ 体检就诊清单 cards)

**Files:** Modify template; add tests to `tests/test_p2_sections.py`.

- [ ] **Step 1: Failing test** — context with two `snapshot.section4_screening` entries (one `risk_tier="high_workup"`, one `"moderate_workup"`, each with a `standard_screening[0]` of method/interval/trigger/source_id). Assert: output contains both methods; the high one is in a `priority` card and the moderate one in an `important` card (assert the CSS class strings `timeline-card priority` / `timeline-card important` appear with the right method text nearby).
- [ ] **Step 2: Run, verify FAIL.**
- [ ] **Step 3: Implement** in `#section-timeline`: iterate `section4_screening`, map `risk_tier` → card class via the mapping table above, render `method` (title), `population`/`interval`/`trigger` (body), `来源: source_id` (footnote). Skip entries whose tier maps to none. Reuse temp `.timeline-card.priority/.important/.maintain` CSS.
- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Commit** `feat(p2-task3): section-timeline screening cards by risk tier`

---

## Task 4 — section-clinical-design (🧱 循证 1+X)

**Files:** Modify template; tests in `tests/test_p2_sections.py`.

- [ ] **Step 1: Failing test** — context with `health_summary.blocks.abnormal_table="<table id=ab>..</table>"` and `disease_cards="<table id=dc>..</table>"`. Assert BOTH appear **unescaped** in output (i.e. `<table id=ab>` present, not `&lt;table`). This locks the `| safe` escaping contract.
- [ ] **Step 2: Run, verify FAIL** (autoescape escapes them without `| safe`).
- [ ] **Step 3: Implement** in `#section-clinical-design`: `{{ health_summary.blocks.abnormal_table | safe }}` and `{{ health_summary.blocks.disease_cards | safe }}`, with a short "循证 1+X 临床体检设计" intro. (Screening-recipe reuse from Task 3 data is optional here; keep it to the two blocks for the escaping contract.)
- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Add the negative escaping test** — a scalar field with `<script>` (e.g. a crafted `person.name="<b>x</b>"`) appears **escaped** (`&lt;b&gt;`). Verify PASS. This proves only trusted blocks use `| safe`.
- [ ] **Step 6: Commit** `feat(p2-task4): section-clinical-design 1+X with safe CP4 blocks + escaping tests`

---

## Task 5 — section-liquid-biopsy (🧬 jizaoan branch + tumor markers)

**Files:** Modify template; tests in `tests/test_p2_sections.py`.

- [ ] **Step 1: Failing tests** — (a) NEGATIVE context (`jizaoan_result="negative"`): output contains `独立合规展示` (or equivalent compliance framing) and the literal `阴性`. (b) POSITIVE context (`jizaoan_result="positive"`, `jizaoan_top_cancers=["肺癌"]`): output contains `阳性信号` and `肺癌`. (c) a `tumor_markers=[{name/test_id, value, result}]` row renders.
- [ ] **Step 2: Run, verify FAIL.**
- [ ] **Step 3: Implement** in `#section-liquid-biopsy`: `{% if jizaoan_result == "positive" %}` → 阳性信号深度说明 block listing `jizaoan_top_cancers` + the 吉早安 voi entry; `{% else %}` → 独立合规展示 (阴性) block. Below: a tumor-markers table iterating `tumor_markers` (test name, value, negative/positive). Pull the 吉早安 entry from `voi.rankings` where `method == "吉早安"` or `is_liquid_biopsy`.
- [ ] **Step 4: Run, verify PASS (both branches).**
- [ ] **Step 5: Commit** `feat(p2-task5): section-liquid-biopsy jizaoan pos/neg branch + tumor markers`

---

## Task 6 — section-package (📦 组合套餐预算)

**Files:** Modify template; tests in `tests/test_p2_sections.py`.

- [ ] **Step 1: Failing test** — context with `voi.rankings` of mixed `recommendation` (`强烈推荐`/`推荐`/`常规`) each with `cost_rmb`/`cost_level`/`invasiveness`. Assert recommended methods appear with their cost and are grouped/sorted by recommendation tier (assert `强烈推荐` entry appears before `常规` entry in output order).
- [ ] **Step 2: Run, verify FAIL.**
- [ ] **Step 3: Implement** in `#section-package`: sort `voi.rankings` by tier order [强烈推荐, 推荐, 可考虑, 常规], render each as a budget row (method, recommendation badge, `¥{{ cost_rmb }}`, invasiveness, `指南: {{ guideline }}`). Reuse temp package CSS.
- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Commit** `feat(p2-task6): section-package VoI budget by recommendation tier`

---

## Task 7 — section-lifestyle (🥗) + genetic (brca) branch

**Files:** Modify template; tests in `tests/test_p2_sections.py`.

- [ ] **Step 1: Failing tests** — (a) context with `health_summary.blocks.advice_list="<ul><li>戒烟限酒</li></ul>"` → output contains `戒烟限酒` **unescaped** in `#section-lifestyle`, plus the `{{ disclaimer }}`. (b) `brca_status="positive"` → a hereditary-risk block appears; `brca_status="negative"` → it does not.
- [ ] **Step 2: Run, verify FAIL.**
- [ ] **Step 3: Implement** `#section-lifestyle`: `{{ health_summary.blocks.advice_list | safe }}` + `{{ health_summary.blocks.overall_assessment | safe }}` + footer `{{ disclaimer }}`. Add `{% if brca_status == "positive" %}` hereditary block (header or liquid-biopsy section).
- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Run full suite** — no regressions.
- [ ] **Step 6: Commit** `feat(p2-task7): section-lifestyle advice + brca hereditary branch`

---

## Task 8 — Integration acceptance (test_1 / test_2 / positive variant)

**Non-headless; real full-flow from the P2 worktree** (use the worktree's `scripts/run_formal_analysis.py`, NOT the repo-root checkout — see p1_smoke_results.md).

- [ ] **Step 1:** Reuse the P1 smoke artifacts approach for `test_1` (negative) and `test_2` (negative): drive CP1–CP4 (refined.md, answers.json, CP3 candidates, cp3_audit, finalize CP4), run final, confirm `report.html` now shows real content in all 6 sections (person name, timeline cards, 1+X tables, package budget, lifestyle advice) and report.json `schema_version=report-v1`.
- [ ] **Step 2: Positive variant** — copy test_1's prepared output dir; set `answers.json` `q_jizaoan_result="positive"`, `q_jizaoan_top1="lung_cancer"`, `q_jizaoan_top2="unknown"` (satisfy validate_answers cascade); re-run final; confirm `#section-liquid-biopsy` renders the 阳性信号深度说明 branch with the top cancer.
- [ ] **Step 3:** Verify the escaping contract on a real run (CP4 tables unescaped; person fields escaped).
- [ ] **Step 4: Commit** `test(p2-task8): integration — full-fidelity report.html, pos/neg jizaoan branches`
- [ ] **Step 5:** Clean worktree pollution (`git checkout -- scripts/__pycache__ docudatabase/person_index.json`; rm smoke docudatabase dirs + untracked .pyc) before finishing.

---

## After all tasks
- Run full `pytest tests/ -q` (P1 41 + new P2 tests).
- Use superpowers:finishing-a-development-branch → merge into `v1.4` (user-gated).
- Post-merge: re-run darwin + skill-creator joint eval (expect dim8 ↑ as the "audit-grade report" gap closes); record any residue as P3/v1.5.
- Then P3 doc hygiene (stale test refs in SKILL.md, name version, parent CLAUDE.md sync).

## Self-review notes (author)
- Spec coverage: Layer 1 (T1), 6 sections (T2–T7), escaping contract (T4 both sides), pos/neg jizaoan (T5+T8), brca (T7), integration+positive variant (T8) — all spec sections covered.
- Escaping contract is the highest-risk item; T4 tests both `| safe` (CP4 blocks unescaped) and scalar escaping. Don't merge if either side fails.
- No new math/evidence files (YAGNI per spec non-goals).
