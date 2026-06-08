# P0 Independent Code Review — CancerRisk Skill v1.4

**Branch**: `v1.4-p0-knowledge-db`
**Review scope**: `git diff v1.4..HEAD` (11 commits, "知识库重塑" phase)
**Reviewer**: Independent (not the P0 implementer)
**Review date**: 2026-06-08
**Tests**: `uv run --python 3.11 --with pytest --with PyYAML --with jsonschema pytest tests/ -q` → **18/18 PASSED**

---

## Overall Verdict: CHANGES_REQUESTED

The P0 implementation is structurally sound — the engine contract is fully preserved, all 18 tests pass, the patch script is idempotent and reproducible (zero diff between script output and committed store), and the key RESUME decisions (81.9% jizaoan, NPC EBV screening, kidney/biliary no-general-screening, pending items not fabricated) are correctly implemented.

However, P0 newly introduced references to two non-existent source documents — one of which (`补充调研文档.md`) cannot be located anywhere in the repository. These are traceability violations that must be resolved before final merge.

---

## Issues by Severity

---

### HIGH

#### H-1: `补充调研文档.md (辅助指标)` — 7 new P0 entries reference a file that does not exist

**File**: `evidence_store_v14/assertions/detection_performance_derived.json`
**Evidence**: `find . -name "补充调研文档*"` returns nothing. `git show v1.4:evidence_store/assertions/detection_performance_derived.json | grep -c "补充调研文档"` = 4 (pre-existing in old evidence_store). Current P0 file has 11 occurrences → **7 net new entries** added by P0 cite a non-existent document.

**Affected entries** (all with `"source_id": "补充调研文档.md (辅助指标)"`): CEA entries for breast, lung, and gastric cancer; CA19-9 entries for gastric, colorectal, ovarian, and pancreatic; PSA (prostate); CA125 (ovarian); AFP (liver variants). These are tumor marker detection performance entries.

**Why it matters**: The source document does not exist. Traceability is broken — these entries cannot be audited or reproduced from any accessible document in the repo. This is distinct from the pre-existing 4 old-store entries (which were inherited debt from v1.3); the 7 new ones are P0 regressions.

**Recommendation**: Either (a) create the missing `补充调研文档.md` in `evidence_store_v14/kb/` with the actual citations, or (b) update `source_id` to a real document reference (e.g., the peer-reviewed PMID for each tumor marker). The easiest compliant path is to write the document with the sources used during research.

---

#### H-2: `risk_factors.md` — 2 new P0 risk assertion entries reference an internal file not in the repo

**File**: `evidence_store_v14/assertions/risk_assertions_derived.json`
**Evidence**: `git show v1.4:evidence_store/assertions/risk_assertions_derived.json | grep -c "risk_factors.md"` = 5. Current file = 7 → **2 net new entries** added by P0 cite `risk_factors.md`.

**Note on old entries**: The 5 pre-existing entries are inherited P0 debt from v1.3 (the `risk_factors.md` file does exist in `evidence_store_v14/ontology/risk_factors.md`). The 2 new P0 additions follow the same pattern. The file exists, so this is MEDIUM severity in isolation — but combined with H-1, the pattern of citing undocumented sources in P0 is worth flagging as HIGH to ensure consistent source hygiene.

**Recommendation**: Verify the 2 new entries: if `risk_factors.md` contains a citeable primary source for these factor values, add the upstream citation as a comment or `citation_text` field. If not, source the OR/RR from literature.

---

### MEDIUM

#### M-1: 75 assertions (inherited) use internal files as `source_id` without literature citations

**Files**: `evidence_store_v14/assertions/risk_assertions_derived.json` (68 with `medical_indicators.md`, 5 with `risk_factors.md`)

**Evidence**: These are ordinal-scaling assertions for imaging/lab result tiers (kidney_mass, pancreas_mass, ovarian_mass, gastric_mirror, cervical_tct/hpv, urine_cytology, breast_biopsy, ALT/AST, eGFR, hematuria, EBV-DNA, bilirubin/ALP/GGT, prostate MRI, colorectal_mirror). The OR values (0.5, 2.0, 10.0, 100.0) are construct-defined ordinal scales, not literature-derived. All 75 were inherited from the old `evidence_store/` unchanged.

**Why it matters**: The red line states "任何数值必须有来源" (all values must have sources). These values do not trace to peer-reviewed literature. They trace to internal modeling decisions in `medical_indicators.md`.

**Mitigating factors**: (a) These are inherited from v1.3, not new P0 fabrications. (b) `medical_indicators.md` exists in the repo. (c) The ordinal-scale nature is self-documenting — the OR values are explicitly designed as approximate ordinal tiers. (d) P0 scope was new gap-fill data, not a wholesale audit of inherited assertions.

**Recommendation**: Add a `note` field to these assertions documenting that values are ordinal-scale constructs, not literature-derived ORs. Consider creating a `source_id: "medical_indicators_ordinal_scale"` convention with a `citation_text` explaining the construct. This should be addressed in a future P1 pass, not held as a blocker.

---

#### M-2: `source_id: "jizaoan_white_paper_v2026"` overstates provenance

**File**: `evidence_store_v14/assertions/detection_performance_derived.json` (all jizaoan entries)

**Evidence**: `research_findings.md §5.2` describes the jizaoan per-cancer sensitivity source as a November 2025 media article (tech.china.com, 中山大学 2025年11月独立验证). The `patch_evidence_store_v14.py` comments call it "吉因加白皮书". No formal white paper URL or DOI is documented. The term "white_paper_v2026" implies a formal publication that has not been cited.

**Why it matters**: A source_id should accurately describe the document type. Calling a media report a "white paper" could mislead future reviewers about peer-review status.

**Recommendation**: Rename to `jizaoan_validation_2025_media` or similar, and add `citation_text` with the tech.china.com article URL from research_findings. Alternatively, if a formal PDF white paper exists, cite it explicitly.

---

### LOW

#### L-1: Lynch "unspecified" CRC assertion uses upper-bound OR (27.0) without documented rationale

**File**: `evidence_store_v14/assertions/risk_assertions_derived.json`, ~lines 2672-2685
**Evidence**: `assertion_id: "lynch_unspecified_crc"` uses `log_odds_delta: 3.296` (= ln(27.0), same as MLH1). This is the upper-bound gene. No `note` field explains why `unspecified` maps to the highest-risk gene rather than the population-weighted mean.

**Recommendation**: Add `"note": "conservative upper bound per NCCN 2025; unknown pathogenic variant defaults to highest-risk gene (MLH1)"` or use a population-weighted average. Document the design decision.

---

#### L-2: Thyroid family history OR=4.1 chosen over 6.06 without in-JSON rationale

**File**: `evidence_store_v14/assertions/risk_assertions_derived.json`, thyroid family_history entry
**Evidence**: `research_findings.md §4.1` documents two ORs: 4.1 (PMC3208119, first-degree) and 6.06 (PMC12731644, any family history). The implemented value is 4.1. The choice is defensible (first-degree is more specific), but the reason is not documented in the assertion.

**Recommendation**: Add `"note": "OR=4.1 for first-degree relatives (PMC3208119); broader family history OR=6.06 (PMC12731644); first-degree chosen for specificity"`.

---

## What Was Verified as Correct

**Contract integrity (PASS)**
- All 5 contract files present with correct field names: `cancer_name_zh`, `derived_assertions[].{assertion_id, cancer_id, factor_id, factor_level, log_odds_delta, conversion_status}`, `derived_detection_performance[].{cancer_id, test_id, positive_log_odds_delta, negative_log_odds_delta, lr_positive, lr_negative, conversion_status}`, `recommendations[].{cancer_id, standard_screening}`, `missing_priors: []` in priors.
- 18/18 tests pass.

**No Bayesian engine modification (PASS)**
- Zero changes to `snapshot_risk.py` or engine files in the diff.

**Lynch OR source tracing (PASS)**
- OR=27.0 for MLH1 CRC traces correctly to `09-遗传性高危基因证据.md` via the formula `OR = [p1/(1-p1)] / [p0/(1-p0)]` with p1=0.53 (NCCN 2025 V1 cumulative risk), p0=0.0445 (population baseline). Math verified: ln(27.0)=3.2958 ✓. All four gene-specific values (MLH1=27.0, MSH2=17.0, MSH6=8.9, PMS2=3.9) verified correct.

**Thyroid and pancreatic risk assertions (PASS)**
- All new assertions (thyroid family_history PMC3208119 OR=4.1, thyroid childhood_radiation PMC5505197 RR=3.2, pancreatic smoking PMC9265847 OR=1.74, family_history PMC9265847_PanScan OR=1.76, obesity PMC2394383 RR=1.19, chronic_pancreatitis PMC8963838 RR=7.9, BRCA2 BCLC_BJC2012 RR=3.51) trace to `research_findings.md` with documented PMC source IDs.
- Log-odds-delta values verified correct for all entries.

**Jizaoan detection performance (PASS)**
- Red-line enforcement confirmed: zero occurrences of "77.2" or "74.9" in `detection_performance_derived.json`.
- 81.9% aggregate is the source white paper's overall figure. Per-cancer values used in engine are consistent with that white paper.
- Individual sensitivities (lung 72.9%, gastric 76.1%, esophageal 79.2%, colorectal 86.2%, pancreatic 66.7%, liver 99%, breast 88.9%, ovarian 87.9%) match `research_findings.md §5.2`.
- No aggregate row needed by engine (engine consumes per-cancer entries); omission is appropriate.

**RESUME decisions implemented (PASS)**
- `head_neck_cancer`: EBV antibody (VCA-IgA + EBNA1-IgA) screening for southern Chinese high-risk area, ages 30-69. Source: PMC11249388. ✓
- `kidney_cancer`: "不推荐对一般人群筛查". Source: PMC10160199_EAU2024. ✓
- `biliary_tract_cancer`: Two entries — general population no-screen + PSC patients annual MRI/MRCP ± CA19-9. Sources: cancer_org_gallbladder + PMC3205332_AASLD. ✓
- `thyroid_cancer`, `pancreatic_cancer` screening entries: present. ✓
- Pending items (NPC population genetics, biliary genetic risk factors, kidney hereditary data): not fabricated, not present in JSON. ✓

**Patch script reproducibility (PASS)**
- `python3 scripts/patch_evidence_store_v14.py <copy>` produces zero diff against committed store. Script is idempotent and fully reproducible.

**env_check.py changes (PASS)**
- Adds exactly 6 file paths to `REQUIRED_FIXTURES` for v14 contract files + `kb/index.json`. No logic changes. Minimal and correct.

**§4 dual representation (PASS)**
- `evidence_store_v14/kb/` contains MD files for all 15 cancer types. `kb/index.json` maps all 15 `cancer_id` values to existing MD files. LLM-readable knowledge base fully populated alongside structured JSON.

**§8 research-before-implementation sequence (PASS)**
- Gap analysis, research findings, and then data entry artifacts are all present and in correct order. No evidence of fabricated values in newly researched assertions.

---

## Summary Table

| ID | Severity | File | Description |
|----|----------|------|-------------|
| H-1 | HIGH | `detection_performance_derived.json` | 7 new P0 entries cite non-existent `补充调研文档.md` |
| H-2 | HIGH | `risk_assertions_derived.json` | 2 new P0 entries cite `risk_factors.md` without upstream literature |
| M-1 | MEDIUM | `risk_assertions_derived.json` | 75 inherited assertions use internal ordinal-scale OR values without literature citations |
| M-2 | MEDIUM | `detection_performance_derived.json` | `source_id: "jizaoan_white_paper_v2026"` overstates provenance (source is a media article) |
| L-1 | LOW | `risk_assertions_derived.json` | Lynch unspecified OR=27.0 (upper bound) not documented in `note` field |
| L-2 | LOW | `risk_assertions_derived.json` | Thyroid OR=4.1 chosen over 6.06 without in-JSON rationale |

**Blockers before merge**: H-1 (resolve missing source document). H-2 (verify 2 new entries have upstream citations).
