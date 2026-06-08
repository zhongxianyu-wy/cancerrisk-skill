---
name: cancerrisk-formal-v3
description: |
  Use when converting health-checkup files (体检报告, 体检文件, medical checkup, 癌症风险分析,
  cancer risk report, health checkup analysis, 体检报告分析) into a single integrated
  audit-grade CancerRisk report (report.html) with MinerU OCR, ontology-backed
  factor filling, deterministic snapshot risk math, screening recommendations,
  and an auto-updated per-person health record archive. Output path <out> is a writable directory;
  person ID <person-id> is a stable ASCII slug (e.g. zhangsan_m68).
  Triggers: 体检, 体检报告, cancer risk, 癌症风险, 健康档案, checkup analysis.
safety: |
  Reports are health-management and screening-decision aids only. They must
  never produce a diagnosis, treatment plan, medication advice, or triage.
---

# CancerRisk Formal Skill

This skill is a thin operating guide. Load the referenced files only when
the current stage needs them. The orchestrator is the single entrypoint:

```bash
uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/run_formal_analysis.py \
  --input <file-or-folder> \
  --analysis-output <out> \
  --person-id <stable_id>
```

Default personal health record location:
`cancerrisk-skill/docudatabase/<person_id>/` (same directory level as
this `SKILL.md`). Override `--archives-root` only for explicit tests or
deliberate relocation.

## Use / Refuse

Use for:

- health-checkup files that need a single integrated cancer-risk report
  (`report.html`);
- reruns that refresh the same person's health archive;
- reruns against updated evidence, answers, or archive history.

Refuse or redirect for diagnosis, treatment selection, medication
dosing, urgent triage, or single-symptom clinical Q&A.

## Non-Negotiables

- LLM/agent work may only fill factual fields from source text or user
  answers. It must not invent factor IDs, cancer IDs, probabilities,
  OR/RR/HR, LR, sensitivity, specificity, screening intervals, or advice.
- Use only closed vocabularies emitted by the orchestrator:
  `risk_factor_master.json`, `structured_risk_factors_timeline`,
  `tumor_markers.candidate.json`, and evidence-store JSON.
- `evidence_text` must be a literal substring of the named source md.
- Do not skip required user answers in real runs. If answers are missing,
  stop and ask the user.
- The personal health archive updates automatically after the snapshot risk
  stage; `archive_update_proposal.json` is kept as an audit trail of what was
  merged into `docudatabase/<person_id>/`.
- For the four agent checkpoints below, do the file reads/writes in this
  agent loop. Do not delegate these deterministic fills to sub-agents.

## Pipeline Stages

| # | Stage | Script | Key output | Action needed? |
|---|---|---|---|---|
| 1 | MinerU OCR | `mineru_client.py` | `artifacts/mineru/<id>/content.md` | — |
| 2 | **Refine** | _(agent writes `refined.md`)_ | `artifacts/mineru/<id>/refined.md` | **CP1** |
| 3 | Demographics | `demographics.py` | `artifacts/demographics.json` | — |
| 4 | Master template scaffold | `build_assertion_fill_template.py` | `risk_factor_master.json`, candidate scaffolds | — |
| 5 | **Interactive answers** | `interactive_completion.py` | `interactive_questionnaire.json` | **CP2** |
| 6 | **Master fill + audit** | _(agent fills candidates; validates; writes `cp3_audit_result.json`)_ | candidate JSONs + `cp3_audit_result.json` | **CP3/3.1** |
| 7 | Risk factor gate | `risk_factor_gate.py` | `structured_risk_factors_timeline.json` | — |
| 8 | Health-summary API | `render_health_summary.py` | `health_summary_api_response.md` | — |
| 9 | **Health-summary structuring** | `finalize_structured_summary.py` | `health_summary_structured_summary.json` | **CP4** |
| 10 | Snapshot + VoI | `snapshot_risk.py` + `voi_calculator.py` | `snapshot_risk.json`, `voi_ranking.json` | — |
| 11 | Archive (auto) | `archive_manager.py` | `archive_update_proposal.json` + `docudatabase/<person_id>/` | — |
| 12 | Integrated report | `build_report_json.py` + `render_report.py` + `write_manifest.py` | `report.json`, `report.html`, `manifest.json` | — |

Rows 2, 5, 6, and 9 require agent action; the archive is applied automatically (no user confirmation step). All other rows run automatically inside `run_formal_analysis.py`.

## Minimal Workflow

> **Flag convention**: In steps 3–10, `...` means carry the same
> `--input <input> --analysis-output <out> --person-id <id>` from
> step 1. Add `--answers <file>` from step 4 onward. Never drop flags
> between steps.

1. Run MinerU and stop:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/run_formal_analysis.py \
     --input <input> --analysis-output <out> --stop-after mineru
   ```

2. 🔴 **CHECKPOINT · 🛑 STOP — CP1 Refine** (agent action required)

   For each `artifacts/mineru/<data_id>/content.md`, **first check content quality**:
   - If `content.md` is fewer than 20 lines **or** contains none of {检查, 化验, 报告, 结果, 项目}: the OCR output is likely empty or corrupt — **stop, alert the user** ("content.md looks empty or non-medical — please verify the input file and re-run MinerU"), do **not** write `refined.md`.
   - Otherwise: write `refined.md` in the same folder keeping demographics, abnormal rows, tumor-marker rows including normal values, imaging/test conclusions, and positive findings.

   See `references/runtime_workflow.md`.

3. Run to interactive:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/run_formal_analysis.py ... \
     --stop-after interactive
   ```

4. 🔴 **CHECKPOINT · 🛑 STOP — CP2 Interactive answers** (agent action required)

   After `--stop-after interactive` the orchestrator exits with **code 0**
   and prints `[stop-after=interactive] questionnaire written`. This is
   your cue to collect answers before continuing. (Exit code 8 fires only
   if you skip this checkpoint and re-run without `--answers`.)

   **4a. Read the questionnaire** — open `<out>/artifacts/interactive_questionnaire.json`
   and inspect the `questions` array. Each entry has `question_id`, `type`,
   `prompt`, and (for choice questions) `options`.

   **4b. Socratic Q&A — one question per call, triggers resolved immediately**

   **Three hard rules:**
   - **One question per AskUserQuestion call.** Never bundle.
   - **Trigger fires → resolve the follow-up chain before moving on.** Do not continue to the next unrelated question while a triggered follow-up is outstanding.
   - **Incomplete answer → re-ask using the completeness criteria below; loop until the criteria are met.** Do not write a partial value and continue.

   Work through the questionnaire's `questions` array in order. For each question:
   0. **`conditional_on` check (before showing the question)**: if the question has a `conditional_on` field, look up `conditional_on.question_id` in the answers collected so far. If the recorded value **does not equal** `conditional_on.value` → **skip** this question entirely. If it matches (or there is no `conditional_on`) → continue.
   1. Present the `prompt` verbatim and, for `single_choice` / `multi_select`, list the option `label` strings as choices. **After the user replies, map the selected label back to the matching option's `value` string and record that value** (e.g., user sees "阳性" → record `"positive"`; user sees "阴性" → record `"negative"`). Never record the raw label as the answer.
   2. Wait for the user's response.
   3. Apply the trigger rules below before moving to the next question.
   4. Use `"unknown"` only when the user explicitly declines to answer.

   **Trigger rules (mandatory in-sequence — never defer to a later question):**

   | Question answered | User's answer | Immediate action before next question |
   |---|---|---|
   | `q_family_history_cancer` | `"yes"` | Ask `q_family_history_detail`: "请说明具体家族史 — 哪种癌症、有多少位亲属患病？（例如：父亲胃癌1人、母亲乳腺癌多人）" |
   | `q_family_history_detail` (any draft) | Text lacks a specific cancer name **or** lacks a relative count | Ask again: "请确认具体癌症类型和患病亲属人数，缺一不可。" — repeat until **both** are present |
   | `q_jizaoan_result` | `"positive"` | Ask `q_jizaoan_top1`: "吉早安报告溯源的第1位癌种是哪个？" then `q_jizaoan_top2`: "第2位癌种是哪个？（如报告只给了1个，选「不清楚」）" |

   **Completeness criteria:**
   - `q_family_history_detail` is complete only when the user's text names at least one **specific cancer** (胃癌 / 乳腺癌 / 肺癌 / 肝癌 / 结直肠癌 / 食管癌 / 甲状腺癌 etc.) **AND** a relative count (1人 / 多人 / ≥2人) for each mentioned cancer. "有家族史" or "父亲有癌" alone is **not** complete — ask the clarifying follow-up.
   - `q_jizaoan_top1` should be a specific cancer ID when result is `"positive"`. Ask the user to check their jizaoan report. If they confirm they cannot locate it, accept `"unknown"` as a last resort — the signal is recorded as unresolved but the pipeline continues. Do not accept `"unknown"` before making at least one request to locate the report.

   **Never pre-fill, guess, or infer any answer from the report.** "No smoking mentioned" is not evidence the patient never smoked.

   **4c. Write `<out>/answers.json`** containing only answers collected in 4b:

   ```json
   {"answers": {"<question_id>": "<user's actual answer>", ...}}
   ```

   - Keys and value formats come from the questionnaire, not from this file.
   - `text_fill` value must be the user's verbatim string — do not reformat or summarize.
   - Omit any key whose `conditional_on` trigger was not met.
   - ⛔ Do not write any key before the user has answered that question in this session.

   **4d. Validate before re-running** (recommended):

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/validate_answers.py \
     --questionnaire <out>/artifacts/interactive_questionnaire.json \
     --answers <out>/answers.json
   ```

   Exit 0 = safe to continue. Exit 1 = hard error (fix answers first). Exit 2 = file not found.

   Fast ask-first path — run this **before** the first pipeline invocation
   when sex/age are already known, to preview the questionnaire:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/build_questionnaire.py \
     --sex <male|female> --age <age> --output /tmp/q.json
   ```

5. Run to master template:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/run_formal_analysis.py ... \
     --stop-after master-template
   ```

6. 🔴 **CHECKPOINT · 🛑 STOP — CP3 Master fill + imaging + tumor markers** (agent action required)

   _(Extractor role: translate report findings into timeline records.)_

   **Knowledge-layer fill order (v1.3+):**
   Step A — Fill `artifacts/indicator_fill_schemas.json` (24 lightweight templates, one per observable exam/lab indicator — only `exists`, `tier_id`, `evidence_text`, `confidence`).
   Step B — Run `merge_filled_template.py` to map tier selections to full evidence-backed `risk_factor_assertion_template.json`.
   Step C — Fill `structured_risk_factors_timeline.candidate.json` and `tumor_markers.candidate.json` using the merged template.

   The indicator fill schema (Step A) contains only indicator+unit+tier descriptions — no OR values, no cancer associations. Focus on correctly identifying which tier applies for each indicator found in the refined report.

   Fill `structured_risk_factors_timeline.candidate.json` and
   `tumor_markers.candidate.json` using only emitted allowlists. Validate:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/validate_timeline_candidate.py \
     --candidate <out>/artifacts/structured_risk_factors_timeline.candidate.json
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/validate_tumor_markers.py \
     --candidate <out>/artifacts/tumor_markers.candidate.json
   ```

   Then re-run with `--stop-after cp3-verify`:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/run_formal_analysis.py ... \
     --stop-after cp3-verify
   ```

7. 🔴 **CHECKPOINT · 🛑 STOP — CP3.1 Verification audit** (mandatory, independent auditor role)

   _(Auditor role: verify completeness — cognitive reset from CP3 extractor context.)_
   The orchestrator prints a structured audit task. As an **independent
   auditor** (not the CP3 extractor), re-read each `refined.md` and
   check for omissions:

   - Read every `refined.md` listed in the audit task independently.
   - Identify ALL clinical abnormal findings in the document.
   - For each finding not in the recorded list, look up a matching
     `factor_key` in `risk_factor_master.json`.
   - If found: add the record to `structured_risk_factors_timeline.candidate.json`
     (same format as CP3 records; `evidence_text` must be a literal
     substring of the source `refined.md`).
   - If no matching `factor_key` exists: do not force-fit; it will
     appear in the "证据库外异常提示" section automatically.
   - If no omissions are found: proceed without editing the candidate.
   - Also check `artifacts/structured_risk_factors_timeline.json` →
     `rejected_records`; for each entry review the `reject_reason` and
     correct the corresponding record in the candidate if possible.

   After the audit, **write `artifacts/cp3_audit_result.json`** before
   running step 8 — the pipeline will halt at exit code 9 if this file
   is missing:

   ```json
   {"no_omissions": true}
   ```
   or, if omissions were found and added:
   ```json
   {"no_omissions": false, "added_factor_keys": ["factor_key_1", ...]}
   ```

   Additionally, if any finding from the report **cannot be matched to an
   evidence risk factor due to incomplete information** (e.g., a thyroid
   nodule reported without TIRADS grade, a lesion without size/density
   grading), record it in `unmatched_findings` so the snapshot report can
   display a PS note explaining why those findings were not scored:

   ```json
   {
     "no_omissions": false,
     "added_factor_keys": [],
     "unmatched_findings": [
       {
         "finding_text": "甲状腺结节，大小约1.2×0.8cm（无TIRADS分级）",
         "reason": "分级未明确，无法匹配TIRADS 4a/4b风险因子",
         "related_cancer": "thyroid_cancer"
       }
     ]
   }
   ```

   `finding_text` should be a brief literal quote from the report.
   `reason` is a concise human-readable explanation (one clause).
   `related_cancer` is optional; omit if ambiguous.

   Then continue to health-summary:

8. Run to health-summary API:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/run_formal_analysis.py ... \
     --stop-after health-summary-api
   ```

9. 🔴 **CHECKPOINT · 🛑 STOP — CP4 Health-summary structuring** (agent action required)

   Convert the API markdown into `health_summary_structured_summary.json`. **MUST use
   `finalize_structured_summary.py` — do NOT write the JSON directly
   (direct writes are truncated by most agent runtimes):**

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/finalize_structured_summary.py \
     --analysis-output <out> --fills <fills.json>
   ```

10. Run the final pipeline:

   ```bash
   uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python cancerrisk-skill/scripts/run_formal_analysis.py ... \
     --person-id <id>
   ```

   The orchestrator runs snapshot risk + VoI, **auto-updates the person's
   archive** under `docudatabase/<person_id>/`, assembles `report.json`, and
   renders the single integrated **`report.html`** (plus `manifest.json` as an
   audit trail). Exit code 0 means the report is ready; `report.html` is the
   user-facing deliverable. `archive_update_proposal.json` records what was
   merged into the archive (no separate confirmation step — archiving is
   automatic).

## Archive Contract

After the snapshot risk stage, the current run is automatically deduped and
merged into the personal health record at `docudatabase/<person_id>/`. The
record preserves each person's timeline history across runs and feeds future
reruns; `archive_update_proposal.json` is kept as the audit trail of the merge.

Default structure:

```text
cancerrisk-skill/docudatabase/
├── person_index.json
└── <person_id>/
    ├── factor_timeline.json
    ├── screening_test_timeline.json
    ├── report_index.json
    └── snapshots/YYYY-MM-DD.json
```

Every archive path must go through
`scripts/archive_manager.py::resolve_person_archive`. Details:
`references/risk_prediction.md`.

## Output Contract

Final user-facing report:

- `report.html` — the single integrated report (assembled from `report.json`).

Key audit artifacts:

- `report.json`
- `conversion_manifest.json`
- `interactive_questionnaire.json`
- `interactive_answers.md`
- `risk_factor_master.json`
- `structured_risk_factors_timeline.candidate.json`
- `structured_risk_factors_timeline.json`
- `tumor_markers.candidate.json`
- `tumor_markers.json`
- `merged_risk_factors.json`
- `health_summary_api_response.md`
- `health_summary_structured_summary.json`
- `snapshot_risk.json`
- `voi_ranking.json`
- `archive_update_proposal.json`
- `manifest.json`

## Progressive References

Open only the file needed for the current task:

| Need | File |
|---|---|
| Full checkpoint recipes and run order | `references/runtime_workflow.md` |
| MinerU API/client behavior | `references/mineru_api.md` |
| Evidence ontology and derived assertions | `references/evidence_ontology.md` |
| Health-summary API/template structuring | `references/health_summary_rebuild.md` |
| Snapshot, VoI, archive rules | `references/risk_prediction.md` |
| Timeline event shape and slim/full keys | `references/event_format.md` |
| Runtime config | `config/formal.yaml` |
| Deterministic implementation | `scripts/*.py` |
| Regression contracts | `tests/test_v3_*.py`, `tests/test_v4_*.py` |

## Safety Boundaries

- Reports are decision aids, not diagnoses.
- Cancers outside the ontology never affect probability math.
- Sex-mismatched cancers use `posterior_probability: null`.
- Conversion/extraction failures halt before probability math.
- Production MinerU should use a user token in `config/local.yaml`; the
  bundled demo token is only a fallback.

## Verification

```bash
uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python -m pytest -q
```

Run focused tests for edited areas before full verification.

## PUA Protocol (Anti-Skip Enforcement)

**This section is binding. Any violation is a critical failure.**

### TL;DR

- 🔴 **CP1 (Refine):** write `refined.md` for every `content.md`; re-run with next `--stop-after`.
- 🔴 **CP2 (Interactive):** ask the user every question; collect answers; re-run with `--answers`.
- 🔴 **CP3/3.1 (Master fill + audit):** fill candidates, validate, run independent audit, write `cp3_audit_result.json`, re-run.
- 🔴 **CP4 (Health-summary structuring):** convert the API markdown via `finalize_structured_summary.py`; re-run for the final report. (Archiving is automatic — no confirmation step.)

### Prohibited behaviors — the agent MUST NOT:

- Skip any checkpoint (CP1–CP4) for any reason, including "to save time" or "the data looks complete."
- Produce a health-risk analysis, cancer probability, or screening recommendation using its own knowledge instead of running the pipeline scripts.
- Declare a stage complete without running the required script and verifying its exit code.
- Pre-fill interactive questionnaire answers (Checkpoint 2) with values inferred from the report — the user must answer every question explicitly.
- Pre-populate `answers.json` before asking the user, or write any `question_id` key whose question was not presented to the actual user in this session.
- Skip a `text_fill` follow-up question (e.g. `q_family_history_detail`) when its `conditional_on` trigger was met — a trigger match makes the follow-up **mandatory**, ask it immediately after the trigger question.
- Ask all questionnaire questions in a single batch without checking `conditional_on` follow-ups — each trigger question must be immediately followed by its gated `text_fill` question if the user's answer matches the trigger value.
- Summarize pipeline results using language that implies the full analysis is done when only a partial stage has run.

### Verification gate before each checkpoint:

Before proceeding to the next checkpoint, the agent must confirm in its response:
- The script command that was run (exact command with all flags).
- The exit code received.
- The output artifact that was produced (file path + existence check).

If any of these three items is missing or failed, the agent must stop and report to the user rather than continuing.

### Exit code reference

| Code | Source | Meaning | Required action |
|---|---|---|---|
| 0 | — | Normal completion | Proceed to next step |
| 1 | MinerU / health-summary API | Request failed | Report exact error; retry once after user confirms; do **not** proceed |
| 2 | MinerU | All files failed OCR | Report error; halt; ask user to verify input files |
| 3 | CP1 | `refined.md` missing or fails structure check | Write/fix `refined.md` per recipe; re-run |
| 5 | Demographics | Sex or age missing | Re-run with `--person-sex`/`--person-age` or add answers to `--answers` |
| 6 | Archive | `--person-id` not provided with populated archive | Re-run with `--person-id <stable-slug>` |
| 7 | Archive | Person ID needs user confirmation | Present `archive_person_id_prompt.json`; add `person_id_choice` to `--answers` |
| 8 | CP2 | Interactive answers empty | Complete CP2: present questionnaire, collect answers, re-run with `--answers` |
| 9 | CP3.1 | `cp3_audit_result.json` missing | Complete CP3.1 audit, write result file, re-run |

Any other non-zero exit code is **unrecoverable**: print stderr verbatim and halt.

### Error recovery rules

1. **Do not self-summarize** "the task is done" or imply completion after an error.
2. **Do not skip checkpoints** by jumping to a later stage without completing the current one.
3. **Re-read the SKILL.md checkpoint** for the current stage and retry from there.
4. If the same error recurs twice, halt immediately and report the exact error message plus the failing command to the user — do not attempt further recovery.
5. **Never generate numeric values** (OR/RR/HR, probabilities, sensitivity, specificity, LR, screening intervals) as error recovery — all numbers must come from `evidence_store/`.
6. The interactive Q&A (Checkpoint 2) must never be bypassed or pre-filled; missing answers always require a user response. After each trigger question, check the questionnaire for `text_fill` questions that `conditional_on` that trigger — if the user's answer matches, ask the follow-up immediately before writing `answers.json`.

### Common failure scenarios

| Failure | Symptom | Required action |
|---|---|---|
| MinerU API failure | Non-zero exit at `--stop-after mineru`; `content.md` absent or empty | Report exact error; do **not** proceed to CP1; retry once after user confirms network/token |
| Health-summary API timeout | Step 8 hangs >120 s or returns HTTP 5xx | Report timeout; retry once; if still failing, halt at `health-summary-api` stage and notify user |
| CP3 validation failure | `validate_timeline_candidate.py` or `validate_tumor_markers.py` exits non-zero | Correct only the flagged fields in the candidate JSON, re-validate; do **not** delete passing records |
| Artifact not found | `refined.md`, `interactive_questionnaire.json`, `cp3_audit_result.json`, or candidate JSON missing | Identify which step should have produced it; rerun from that step's `--stop-after`; do **not** fabricate |

### Consequence of skipping:

If the agent skips a checkpoint or generates numeric values without running the pipeline, the output is **invalid and must be discarded**. The agent must:
1. Announce that a protocol violation occurred.
2. Identify which checkpoint was skipped.
3. Restart from that checkpoint — not continue from the current position.

## Platform Adaptation: Workbuddy

When running in the Workbuddy environment:

- Use the user's personal MinerU token from `config/local.yaml` (set once via `--save-mineru-token`).
- Archive root is `cancerrisk-skill/docudatabase/` relative to the skill root; use `--archives-root` only for explicit relocation.
- Recommended output directory naming: `<analysis_output>/<person_id>/<YYYYMMDD>/` for uniqueness across runs.
- All Python commands use the `uv run` prefix exactly as documented in this file — do not strip it.
- The `<person-id>` argument must be a stable ASCII slug matching the person's existing archive entry (create a new one on first run by choosing a consistent slug).
