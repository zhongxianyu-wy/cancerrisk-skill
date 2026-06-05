#!/usr/bin/env python3
"""
Patch evidence_store_v14 with:
1. Lynch syndrome risk factors + assertions (from 09-遗传性高危基因证据.md)
2. Pancreatic cancer epidemiologic risk factor assertions (from research_findings.md)
3. Thyroid cancer risk factor assertions (from research_findings.md)
4. Jizaoan pancreatic cancer detection entry (from research_findings.md §5.3)
5. Screening recommendations: head_neck NPC/EBV, kidney not-recommended,
   biliary not-recommended + PSC-MRI, thyroid, pancreatic

Run from the worktree root:
    python3 scripts/patch_evidence_store_v14.py evidence_store_v14
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_risk_factors(store: Path) -> None:
    path = store / "ontology/risk_factors.json"
    data = read_json(path)
    existing_ids = {f["factor_id"] for f in data["risk_factors"]}

    new_factors = [
        # ── Lynch MMR gene carriers ───────────────────────────────────────
        {
            "factor_id": "lynch_mlh1_carrier",
            "factor_name_zh": "林奇综合征 MLH1 致病突变携带者",
            "factor_name_en": "Lynch syndrome MLH1 pathogenic variant carrier",
            "factor_type": "genetic",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
            "positive_test_definition": "胚系 MLH1 基因致病/可能致病变异(PV/LPV)，或 IHC MLH1 缺失+胚系检测确认",
        },
        {
            "factor_id": "lynch_msh2_carrier",
            "factor_name_zh": "林奇综合征 MSH2 致病突变携带者",
            "factor_name_en": "Lynch syndrome MSH2 pathogenic variant carrier",
            "factor_type": "genetic",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
            "positive_test_definition": "胚系 MSH2/EPCAM 基因致病/可能致病变异，或 IHC MSH2 缺失+胚系检测确认",
        },
        {
            "factor_id": "lynch_msh6_carrier",
            "factor_name_zh": "林奇综合征 MSH6 致病突变携带者",
            "factor_name_en": "Lynch syndrome MSH6 pathogenic variant carrier",
            "factor_type": "genetic",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
            "positive_test_definition": "胚系 MSH6 基因致病/可能致病变异，或 IHC MSH6 缺失+胚系检测确认",
        },
        {
            "factor_id": "lynch_pms2_carrier",
            "factor_name_zh": "林奇综合征 PMS2 致病突变携带者",
            "factor_name_en": "Lynch syndrome PMS2 pathogenic variant carrier",
            "factor_type": "genetic",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
            "positive_test_definition": "胚系 PMS2 基因致病/可能致病变异，或 IHC PMS2 缺失+胚系检测确认",
        },
        {
            "factor_id": "lynch_unspecified_carrier",
            "factor_name_zh": "林奇综合征携带者(基因未明)",
            "factor_name_en": "Lynch syndrome carrier (gene unspecified)",
            "factor_type": "genetic",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
            "positive_test_definition": "临床确诊 Lynch 综合征但未完成分型，或 MMR 家族性筛查阳性且基因未明",
        },
        # ── Pancreatic cancer epidemiologic factors ───────────────────────
        {
            "factor_id": "smoking_pancreatic",
            "factor_name_zh": "吸烟(胰腺癌相关)",
            "factor_name_en": "Smoking (pancreatic cancer association)",
            "factor_type": "lifestyle",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
        },
        {
            "factor_id": "family_history_pancreatic_first",
            "factor_name_zh": "胰腺癌家族史(一级亲属)",
            "factor_name_en": "First-degree family history of pancreatic cancer",
            "factor_type": "family_history",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
        },
        {
            "factor_id": "obesity_pancreatic",
            "factor_name_zh": "肥胖(BMI≥30)(胰腺癌相关)",
            "factor_name_en": "Obesity BMI≥30 (pancreatic cancer association)",
            "factor_type": "lifestyle",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
        },
        {
            "factor_id": "chronic_pancreatitis",
            "factor_name_zh": "慢性胰腺炎",
            "factor_name_en": "Chronic pancreatitis",
            "factor_type": "comorbidity",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
        },
        {
            "factor_id": "brca2_pancreatic_mutation",
            "factor_name_zh": "BRCA2 携带者(胰腺癌高危)",
            "factor_name_en": "BRCA2 pathogenic variant (pancreatic cancer risk)",
            "factor_type": "genetic",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
        },
        # ── Thyroid cancer risk factors ────────────────────────────────────
        {
            "factor_id": "thyroid_family_history_first",
            "factor_name_zh": "甲状腺癌家族史(一级亲属)",
            "factor_name_en": "First-degree family history of thyroid cancer",
            "factor_type": "family_history",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
        },
        {
            "factor_id": "radiation_exposure_head_neck_childhood",
            "factor_name_zh": "儿童期头颈部外照射史",
            "factor_name_en": "Childhood head-neck external radiation exposure",
            "factor_type": "exposure",
            "applicable_sex": "all",
            "applicable_age_min": None,
            "applicable_age_max": None,
            "level_schema": ["present", "absent"],
            "interaction_needed_if_missing": False,
        },
    ]

    added = 0
    for f in new_factors:
        if f["factor_id"] not in existing_ids:
            data["risk_factors"].append(f)
            existing_ids.add(f["factor_id"])
            added += 1

    write_json(path, data)
    print(f"[risk_factors] added {added} new factor definitions")


def patch_risk_assertions(store: Path) -> None:
    path = store / "assertions/risk_assertions.json"
    data = read_json(path)
    existing_ids = {a["assertion_id"] for a in data["assertions"]}

    new_assertions = [
        # ── Lynch → colorectal_cancer ─────────────────────────────────────
        # Source: 09-遗传性高危基因证据.md §2.2 (NCCN Genetic/Familial High-Risk LS 2025 V1)
        {
            "assertion_id": "asrt_colorectal_cancer_lynch_mlh1",
            "cancer_id": "colorectal_cancer",
            "factor_id": "lynch_mlh1_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 27.0,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 47,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; MLH1 CRC lifetime risk 46-61%, OR=(0.53/0.47)/(0.04/0.96)≈27",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征 MLH1 携带者",
        },
        {
            "assertion_id": "asrt_colorectal_cancer_lynch_msh2",
            "cancer_id": "colorectal_cancer",
            "factor_id": "lynch_msh2_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 17.0,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 48,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; MSH2 CRC lifetime risk 33-52%, OR=(0.42/0.58)/(0.04/0.96)≈17",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征 MSH2 携带者",
        },
        {
            "assertion_id": "asrt_colorectal_cancer_lynch_msh6",
            "cancer_id": "colorectal_cancer",
            "factor_id": "lynch_msh6_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 8.9,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 49,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; MSH6 CRC lifetime risk 10-44%, OR=(0.27/0.73)/(0.04/0.96)≈8.9",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征 MSH6 携带者",
        },
        {
            "assertion_id": "asrt_colorectal_cancer_lynch_pms2",
            "cancer_id": "colorectal_cancer",
            "factor_id": "lynch_pms2_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 3.9,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 50,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; PMS2 CRC lifetime risk 8.7-20%, OR=(0.14/0.86)/(0.04/0.96)≈3.9",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征 PMS2 携带者",
        },
        {
            "assertion_id": "asrt_colorectal_cancer_lynch_unspecified",
            "cancer_id": "colorectal_cancer",
            "factor_id": "lynch_unspecified_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 27.0,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 53,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; 基因未明取保守上界=MLH1 OR≈27",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征携带者(基因未明)",
        },
        # ── Lynch → gastric_cancer ────────────────────────────────────────
        {
            "assertion_id": "asrt_gastric_cancer_lynch_mlh1",
            "cancer_id": "gastric_cancer",
            "factor_id": "lynch_mlh1_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 7.9,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 51,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; MLH1 gastric lifetime risk 5-7%, OR=(0.06/0.94)/(0.008/0.992)≈7.9",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征 MLH1 携带者",
        },
        {
            "assertion_id": "asrt_gastric_cancer_lynch_msh2",
            "cancer_id": "gastric_cancer",
            "factor_id": "lynch_msh2_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 6.0,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 52,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; MSH2 gastric lifetime risk 0.2-9%, OR=(0.046/0.954)/(0.008/0.992)≈6.0",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征 MSH2 携带者",
        },
        {
            "assertion_id": "asrt_gastric_cancer_lynch_unspecified",
            "cancer_id": "gastric_cancer",
            "factor_id": "lynch_unspecified_carrier",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 7.9,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "guideline-derived",
            "population": None,
            "source_id": "NCCN_LS_2025_V1",
            "source_doc": "09-遗传性高危基因证据.md",
            "source_line": 53,
            "citation_text": "NCCN Genetic/Familial High-Risk LS 2025 V1; 基因未明取保守上界=MLH1 胃癌 OR≈7.9",
            "v2_assertion_id": None,
            "v2_factor_zh": "林奇综合征携带者(基因未明)",
        },
        # ── Pancreatic cancer epidemiologic factors ────────────────────────
        # Smoking: meta-analysis OR 1.74 (PMC9265847)
        {
            "assertion_id": "asrt_pancreatic_cancer_smoking_pancreatic",
            "cancer_id": "pancreatic_cancer",
            "factor_id": "smoking_pancreatic",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 1.74,
            "ci_low": 1.61,
            "ci_high": 1.87,
            "evidence_grade": "IA",
            "population": None,
            "source_id": "PMC9265847",
            "source_doc": "research_findings.md",
            "source_line": 67,
            "citation_text": "Meta-analysis, current smokers vs never smokers, OR=1.74 (95% CI 1.61-1.87); PMC9265847",
            "v2_assertion_id": None,
            "v2_factor_zh": "吸烟(胰腺癌相关)",
        },
        # Family history: PanScan pooled OR 1.76 (PMC9265847)
        {
            "assertion_id": "asrt_pancreatic_cancer_family_history_first",
            "cancer_id": "pancreatic_cancer",
            "factor_id": "family_history_pancreatic_first",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 1.76,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "IIA",
            "population": None,
            "source_id": "PMC9265847_PanScan",
            "source_doc": "research_findings.md",
            "source_line": 104,
            "citation_text": "PanScan 7-study pooled analysis, first-degree relative pancreatic cancer, OR=1.76; PMC9265847",
            "v2_assertion_id": None,
            "v2_factor_zh": "胰腺癌家族史(一级亲属)",
        },
        # Obesity: meta RR 1.19 (PMC2394383)
        {
            "assertion_id": "asrt_pancreatic_cancer_obesity",
            "cancer_id": "pancreatic_cancer",
            "factor_id": "obesity_pancreatic",
            "factor_level": "present",
            "effect_type": "RR",
            "effect_value": 1.19,
            "ci_low": 1.10,
            "ci_high": 1.29,
            "evidence_grade": "IIA",
            "population": None,
            "source_id": "PMC2394383",
            "source_doc": "research_findings.md",
            "source_line": 114,
            "citation_text": "Meta-analysis, obesity BMI≥30 vs normal, RR=1.19 (95% CI 1.10-1.29); PMC2394383",
            "v2_assertion_id": None,
            "v2_factor_zh": "肥胖(BMI≥30)",
        },
        # Chronic pancreatitis: 5-year RR ~7.9 (PMC8963838, post-reverse-causation)
        {
            "assertion_id": "asrt_pancreatic_cancer_chronic_pancreatitis",
            "cancer_id": "pancreatic_cancer",
            "factor_id": "chronic_pancreatitis",
            "factor_level": "present",
            "effect_type": "RR",
            "effect_value": 7.9,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "IIA",
            "population": None,
            "source_id": "PMC8963838",
            "source_doc": "research_findings.md",
            "source_line": 92,
            "citation_text": "Meta-analysis, chronic pancreatitis, 5-year follow-up RR≈7.9 (excludes reverse causation); PMC8963838",
            "v2_assertion_id": None,
            "v2_factor_zh": "慢性胰腺炎(5年以上随访)",
        },
        # BRCA2 → pancreatic cancer: RR 3.51 (BCLC, nature/bjc2012483)
        {
            "assertion_id": "asrt_pancreatic_cancer_brca2",
            "cancer_id": "pancreatic_cancer",
            "factor_id": "brca2_pancreatic_mutation",
            "factor_level": "present",
            "effect_type": "RR",
            "effect_value": 3.51,
            "ci_low": 1.87,
            "ci_high": 6.58,
            "evidence_grade": "IIA",
            "population": None,
            "source_id": "BCLC_BJC2012_brca2_pancreatic",
            "source_doc": "research_findings.md",
            "source_line": 125,
            "citation_text": "Breast Cancer Linkage Consortium, BRCA2 pancreatic cancer RR=3.51 (95% CI 1.87-6.58); nature/bjc2012483",
            "v2_assertion_id": None,
            "v2_factor_zh": "BRCA2 携带者(胰腺癌高危)",
        },
        # ── Thyroid cancer risk factors ────────────────────────────────────
        # Family history OR 4.1 (PMC3208119, first-degree relatives)
        {
            "assertion_id": "asrt_thyroid_cancer_family_history_first",
            "cancer_id": "thyroid_cancer",
            "factor_id": "thyroid_family_history_first",
            "factor_level": "present",
            "effect_type": "OR",
            "effect_value": 4.1,
            "ci_low": 1.7,
            "ci_high": 9.9,
            "evidence_grade": "IIA",
            "population": None,
            "source_id": "PMC3208119",
            "source_doc": "research_findings.md",
            "source_line": 35,
            "citation_text": "First-degree family history thyroid cancer → DTC, OR=4.1 (95% CI 1.7-9.9); PMC3208119",
            "v2_assertion_id": None,
            "v2_factor_zh": "甲状腺癌家族史(一级亲属)",
        },
        # Childhood radiation: RR=3.2 at 0.2 Gy (PMC5505197)
        # We use RR as effect_type so build_derived treats as approximation
        {
            "assertion_id": "asrt_thyroid_cancer_childhood_radiation",
            "cancer_id": "thyroid_cancer",
            "factor_id": "radiation_exposure_head_neck_childhood",
            "factor_level": "present",
            "effect_type": "RR",
            "effect_value": 3.2,
            "ci_low": None,
            "ci_high": None,
            "evidence_grade": "IIA",
            "population": "childhood_head_neck_radiation",
            "source_id": "PMC5505197",
            "source_doc": "research_findings.md",
            "source_line": 23,
            "citation_text": "Pooled 9-cohort, ERR/Gy=11.0, fitted RR=3.2 at 0.2Gy childhood exposure; PMC5505197",
            "v2_assertion_id": None,
            "v2_factor_zh": "儿童期头颈部外照射史",
        },
    ]

    added = 0
    for a in new_assertions:
        if a["assertion_id"] not in existing_ids:
            data["assertions"].append(a)
            existing_ids.add(a["assertion_id"])
            added += 1

    write_json(path, data)
    print(f"[risk_assertions] added {added} new assertions (total: {len(data['assertions'])})")


def patch_detection_performance(store: Path) -> None:
    path = store / "assertions/detection_performance.json"
    data = read_json(path)

    # Check if pancreatic jizaoan entry already exists
    existing = [
        e for e in data["tests"]
        if e["test_id"] == "jizaoan_multi_cancer_screening"
        and e["cancer_id"] == "pancreatic_cancer"
    ]
    if existing:
        print("[detection_performance] jizaoan pancreatic entry already exists, skipping")
        return

    # Add pancreatic cancer jizaoan entry (sensitivity 66.7% from 中山大学 independent validation)
    # Source: research_findings.md §5.3, same source as other jizaoan entries
    new_entry = {
        "test_id": "jizaoan_multi_cancer_screening",
        "test_name": "吉早安多癌早筛",
        "cancer_id": "pancreatic_cancer",
        "sensitivity": 0.667,
        "specificity": 0.991,
        "population": "general adult population",
        "source_id": "jizaoan_white_paper_v2026",
        "notes": (
            "中山大学肿瘤防治中心独立验证队列(2025-11)胰腺癌灵敏度 66.7%，特异性 99.0%。"
            "来源：research_findings.md §5.3；与其他7癌种同一研究。"
        ),
    }

    # Insert after the ovarian jizaoan entry (index 6, 0-based)
    # Find last jizaoan entry and insert after it
    last_jizaoan_idx = max(
        i for i, e in enumerate(data["tests"])
        if e["test_id"] == "jizaoan_multi_cancer_screening"
    )
    data["tests"].insert(last_jizaoan_idx + 1, new_entry)

    write_json(path, data)
    print(f"[detection_performance] added jizaoan pancreatic_cancer entry")


def patch_screening_recommendations(store: Path) -> None:
    path = store / "screening/screening_recommendations.json"
    data = read_json(path)

    existing_ids = {r["cancer_id"] for r in data["recommendations"]}

    # ── Update head_neck_cancer: add NPC EBV screening ────────────────────
    for r in data["recommendations"]:
        if r["cancer_id"] == "head_neck_cancer":
            # Replace standard_screening list with updated version
            r["standard_screening"] = [
                {
                    "method": "鼻咽癌(NPC)EBV 抗体血清筛查 (VCA-IgA + EBNA1-IgA)",
                    "population": "中国南方高发区居民，30–69 岁（非高发区不推荐）",
                    "interval": "高发区定期筛查（具体间隔参照当地卫生部门指引）",
                    "trigger": "高危人群（鼻咽癌高发区居民）",
                    "source_id": "PMC11249388_NPC_EBV_screening",
                    "note": "中国卫生部推荐：鼻咽癌高发区 30-69 岁使用 EBV 抗体(VCA-IgA/EBNA1-IgA)筛查；口腔癌/喉癌目前无权威人群筛查推荐（待定）",
                },
            ]
            break

    # ── Update kidney_cancer: state general-pop not recommended ──────────
    for r in data["recommendations"]:
        if r["cancer_id"] == "kidney_cancer":
            r["standard_screening"] = [
                {
                    "method": "不推荐对一般人群筛查",
                    "population": "一般人群",
                    "interval": "不适用",
                    "trigger": "一般人群",
                    "source_id": "PMC10160199_EAU2024_RCC_no_screening",
                    "note": "EAU 2024 指南及系统综述：不推荐对任何人群常规筛查 RCC；遗传综合征(如 VHL)高危人群可考虑靶向监测但证据有限、无标准间隔（待定）",
                },
            ]
            break

    # ── Update biliary_tract_cancer: general-pop not recommended + PSC MRI ──
    for r in data["recommendations"]:
        if r["cancer_id"] == "biliary_tract_cancer":
            r["standard_screening"] = [
                {
                    "method": "不推荐对一般人群筛查",
                    "population": "一般人群",
                    "interval": "不适用",
                    "trigger": "一般人群",
                    "source_id": "cancer_org_gallbladder_no_screening",
                    "note": "目前无可靠且成本效益合理的胆道癌早筛工具；多来源指南明确不推荐一般人群筛查",
                },
                {
                    "method": "MRI/MRCP ± CA19-9",
                    "population": "原发性硬化性胆管炎(PSC)患者",
                    "interval": "每年1次",
                    "trigger": "高危人群(PSC)",
                    "source_id": "PMC3205332_AASLD_PSC_screening",
                    "note": "AASLD 指南推荐 PSC 患者年度 MRI/MRCP 监测（胆管癌终生风险 5-20%）",
                },
            ]
            break

    # ── Add thyroid_cancer screening entry ────────────────────────────────
    if "thyroid_cancer" not in existing_ids:
        data["recommendations"].append({
            "cancer_id": "thyroid_cancer",
            "cancer_name": "甲状腺癌",
            "standard_screening": [
                {
                    "method": "甲状腺超声（TI-RADS 系统分类）",
                    "population": "高危人群：有儿童期头颈放疗史、一级亲属甲状腺癌史、MEN2/RET 突变",
                    "interval": "高危人群定期随访（具体间隔遵医嘱）",
                    "trigger": "高危人群",
                    "source_id": "guideline_china_thyroid_2022",
                    "note": "一般人群不推荐常规筛查；超声 TI-RADS 系统用于已发现结节的恶性风险分层（非人群筛查工具）",
                },
            ],
        })

    # ── Add pancreatic_cancer screening entry ─────────────────────────────
    if "pancreatic_cancer" not in existing_ids:
        data["recommendations"].append({
            "cancer_id": "pancreatic_cancer",
            "cancer_name": "胰腺癌",
            "standard_screening": [
                {
                    "method": "不推荐对一般人群筛查；高危人群 EUS 或 MRI/MRCP",
                    "population": "高危人群：家族性胰腺癌(≥2名一级亲属)、BRCA2/PALB2/ATM 携带者、Lynch 综合征",
                    "interval": "每年1次（高危人群）",
                    "trigger": "高危人群",
                    "source_id": "guideline_china_pancreatic_2022",
                    "note": "一般人群无证据支持常规筛查；高危人群 NCCN/IAMP 推荐年度 EUS 或 MRI/MRCP",
                },
            ],
        })

    write_json(path, data)
    print(f"[screening_recommendations] patched head_neck/kidney/biliary; added thyroid/pancreatic")


def main() -> None:
    store = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evidence_store_v14")
    if not store.exists():
        print(f"ERROR: store not found: {store}", file=sys.stderr)
        sys.exit(1)

    print(f"Patching {store}...")
    patch_risk_factors(store)
    patch_risk_assertions(store)
    patch_detection_performance(store)
    patch_screening_recommendations(store)
    print("Patch complete.")


if __name__ == "__main__":
    main()
