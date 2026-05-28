"""Apply family history evidence patches based on 2026-05-28 literature research.

Adds:
  - 3 new cancer-specific family history factors (cervical, head_neck, biliary)
  - 7 new "multiple relatives" family history factors
  - 13 new assertions
  - 2 source/OR updates to existing assertions (liver, bladder)
  - 10 interaction question template entries
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "evidence_store"
RF_FILE = BASE / "ontology" / "risk_factors.json"
RA_FILE = BASE / "assertions" / "risk_assertions.json"
IQT_FILE = BASE / "interaction" / "interaction_question_templates.json"

NEW_VERSION = "evidence-v0003"

# ── New factors ───────────────────────────────────────────────────────────────

NEW_FACTORS = [
    # New cancer-specific (first-degree)
    {
        "factor_id": "family_history_cervical",
        "factor_name_zh": "宫颈癌家族史（一级亲属，SCC型）",
        "factor_name_en": "Family history of cervical SCC (first-degree)",
        "factor_type": "family_history",
        "applicable_sex": "female",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": True,
        "interaction_question_group": "family_history_cervical",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_head_neck",
        "factor_name_zh": "头颈肿瘤家族史（一级亲属）",
        "factor_name_en": "Family history of head and neck cancer (first-degree)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": True,
        "interaction_question_group": "family_history_head_neck",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_biliary",
        "factor_name_zh": "胆道肿瘤家族史（一级亲属，胆囊癌为主）",
        "factor_name_en": "Family history of biliary tract cancer (first-degree, primarily gallbladder)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": True,
        "interaction_question_group": "family_history_biliary",
        "level_schema": ["present", "absent"],
    },
    # "Multiple affected relatives" variants
    {
        "factor_id": "family_history_gastric_multiple",
        "factor_name_zh": "胃癌家族史（≥2名一级亲属）",
        "factor_name_en": "Family history of gastric cancer (2+ first-degree relatives)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": False,
        "interaction_question_group": "family_history_gastric_multiple",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_esophageal_multiple",
        "factor_name_zh": "食管癌家族史（≥2名一级亲属）",
        "factor_name_en": "Family history of esophageal cancer (2+ first-degree relatives)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": False,
        "interaction_question_group": "family_history_esophageal_multiple",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_ovarian_multiple",
        "factor_name_zh": "卵巢癌家族史（≥2名一级亲属）",
        "factor_name_en": "Family history of ovarian cancer (2+ first-degree relatives)",
        "factor_type": "family_history",
        "applicable_sex": "female",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": False,
        "interaction_question_group": "family_history_ovarian_multiple",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_liver_multiple",
        "factor_name_zh": "肝癌家族史（≥2名一级亲属）",
        "factor_name_en": "Family history of liver cancer (2+ first-degree relatives)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": False,
        "interaction_question_group": "family_history_liver_multiple",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_bladder_multiple",
        "factor_name_zh": "膀胱癌家族史（>1名一级亲属）",
        "factor_name_en": "Family history of bladder cancer (>1 first-degree relative)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": False,
        "interaction_question_group": "family_history_bladder_multiple",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_kidney_multiple",
        "factor_name_zh": "肾癌家族史（≥2名一级亲属）",
        "factor_name_en": "Family history of kidney cancer (2+ first-degree relatives)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": False,
        "interaction_question_group": "family_history_kidney_multiple",
        "level_schema": ["present", "absent"],
    },
    {
        "factor_id": "family_history_thyroid_multiple",
        "factor_name_zh": "甲状腺癌家族史（≥2名一级亲属，家族性NMTC）",
        "factor_name_en": "Family history of thyroid cancer (2+ first-degree relatives, FNMTC)",
        "factor_type": "family_history",
        "applicable_sex": "all",
        "applicable_age_min": None,
        "applicable_age_max": None,
        "interaction_needed_if_missing": False,
        "interaction_question_group": "family_history_thyroid_multiple",
        "level_schema": ["present", "absent"],
    },
]

# ── Updated assertions ────────────────────────────────────────────────────────

ASSERTION_UPDATES = [
    {
        "_target": "asrt_liver_cancer_family_history_liver",
        "ci_low": 2.05,
        "ci_high": 3.16,
        "evidence_grade": "IIA",
        "source_id": "Yang Y et al., Int J Cancer 2014, PMID:24535817",
        "citation_text": "Yang Y et al., 2014 (Int J Cancer). Meta-analysis of 27 studies (21 case-control + 6 cohort), n=133,014 Shanghai cohort. Pooled RR=2.55 (95%CI 2.05-3.16). ≥2 FDR: HR=5.11 (2.10-12.45). Current OR=2.5 represents general (non-HBV-stratified) estimate.",
        "source_doc": "cancer_risk_factors_complete_evidence_20260527.md",
        "source_line": None,
    },
    {
        "_target": "asrt_bladder_cancer_family_history_bladder",
        "effect_value": 1.8,
        "ci_low": 1.2,
        "ci_high": 2.9,
        "evidence_grade": "IIA",
        "source_id": "Koutros S et al., Int J Cancer 2021, PMID:33506540",
        "citation_text": "Koutros S et al., 2021 (Int J Cancer). NE US population-based case-control. Any FDR with bladder cancer: OR=1.8 (95%CI 1.2-2.9). Pooled multi-study 1-FDR estimate: OR=1.42 (Yu 2022, PMID:35027464); current value 1.8 is conservative midpoint.",
        "source_doc": "cancer_risk_factors_complete_evidence_20260527.md",
        "source_line": None,
    },
]

# ── New assertions ────────────────────────────────────────────────────────────

NEW_ASSERTIONS = [
    # --- New cancer-specific (first-degree) ---
    {
        "assertion_id": "asrt_cervical_cancer_family_history_cervical",
        "cancer_id": "cervical_cancer",
        "factor_id": "family_history_cervical",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 2.5,
        "ci_low": 1.1,
        "ci_high": 9.4,
        "evidence_grade": "IIB",
        "population": "female (SCC histology)",
        "source_id": "Zelmanowicz A et al., Int J Cancer 2005, PMID:15818615; Hemminki K 2001, PMID:11263596",
        "citation_text": "Zelmanowicz A et al., 2005 (Int J Cancer): OR 3.2 (Costa Rica) and 2.6 (Eastern US) for SCC in FDR. Hemminki K 2001 (Int J Cancer): Swedish registry SIR~2.0 for invasive SCC. Central estimate OR=2.5. Note: association is SCC-specific; no significant effect for adenocarcinoma. Partially HPV-exposure mediated.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "宫颈癌家族史",
    },
    {
        "assertion_id": "asrt_head_neck_cancer_family_history_head_neck",
        "cancer_id": "head_neck_cancer",
        "factor_id": "family_history_head_neck",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 1.7,
        "ci_low": 1.2,
        "ci_high": 2.3,
        "evidence_grade": "IIA",
        "population": "general adult",
        "source_id": "Negri E et al., Int J Cancer 2009, PMID:18814262",
        "citation_text": "Negri E et al., 2009 (Int J Cancer). INHANCE Consortium pooled analysis of 12 case-control studies (N=8,967 cases + 13,627 controls). Any HNC in FDR: OR=1.7 (1.2-2.3). Sibling affected: OR=2.2 (1.6-3.1). Site-specific: oral/pharyngeal OR=2.6; laryngeal OR=2.8.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "头颈肿瘤家族史",
    },
    {
        "assertion_id": "asrt_biliary_tract_cancer_family_history_biliary",
        "cancer_id": "biliary_tract_cancer",
        "factor_id": "family_history_biliary",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 2.5,
        "ci_low": None,
        "ci_high": None,
        "evidence_grade": "IIB",
        "population": "general adult (gallbladder cancer primary)",
        "source_id": "Hemminki K et al., Cancers 2022, PMID:35454845; Van Dyke AL 2018, PMID:29339358",
        "citation_text": "Hemminki K 2022 (Cancers, Swedish registry): gallbladder cancer concordant FDR SIR=2.76; intrahepatic bile duct SIR=3.81. Hsing AW 2007 (Shanghai): FH of gallstones OR=2.1 (1.4-3.3). CONFLICTING: BiTCaPP prospective pool (12 studies, 1.54M participants, Van Dyke 2018): no significant association between family history and biliary tract cancer overall. Use with caution; OR=2.5 drawn from registry data only.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "胆道肿瘤家族史",
    },
    # --- Multiple relatives variants ---
    {
        "assertion_id": "asrt_gastric_cancer_family_history_gastric_multiple",
        "cancer_id": "gastric_cancer",
        "factor_id": "family_history_gastric_multiple",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 5.0,
        "ci_low": None,
        "ci_high": None,
        "evidence_grade": "IIB",
        "population": "general adult",
        "source_id": "Dhillon PK et al., Int J Cancer 2001, PMID:11391635",
        "citation_text": "Dhillon PK et al., 2001 (Int J Cancer). 2+ FDR with gastric cancer: OR=12.1 (95%CI 1.4-108) — single study, very wide CI. OR=5.0 used as conservative working estimate. No meta-analysis stratifies by FDR count. Treat as directional evidence only.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "胃癌家族史（多名亲属）",
    },
    {
        "assertion_id": "asrt_esophageal_cancer_family_history_esophageal_multiple",
        "cancer_id": "esophageal_cancer",
        "factor_id": "family_history_esophageal_multiple",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 2.93,
        "ci_low": 1.67,
        "ci_high": 5.12,
        "evidence_grade": "IIB",
        "population": "Chinese (Shanxi Province, high-incidence region)",
        "source_id": "Chen T et al., Sci Rep 2015, PMID:26526791",
        "citation_text": "Chen T et al., 2015 (Scientific Reports). Case-control, Shanxi China (1,942 cases, 1,960 controls). ≥2 FDR: OR=2.93 (95%CI 1.67-5.12). Both parents affected: OR=7.96 (95%CI 1.74-36.32). Chinese population, esophageal SCC predominant.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "食管癌家族史（多名亲属）",
    },
    {
        "assertion_id": "asrt_ovarian_cancer_family_history_ovarian_multiple",
        "cancer_id": "ovarian_cancer",
        "factor_id": "family_history_ovarian_multiple",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 10.0,
        "ci_low": 6.16,
        "ci_high": 17.57,
        "evidence_grade": "IIA",
        "population": "female (Swedish general population)",
        "source_id": "Zheng G et al., PLoS One 2018, PMID:30281663",
        "citation_text": "Zheng G et al., 2018 (PLoS One). Swedish Family-Cancer Database (16M persons). Both mother AND sister with ovarian cancer: RR=10.40 (95%CI 6.16-17.57). Best proxy for ≥2 FDR ovarian cancer. Non-Lynch/non-BRCA familial risk.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "卵巢癌家族史（多名亲属）",
    },
    {
        "assertion_id": "asrt_liver_cancer_family_history_liver_multiple",
        "cancer_id": "liver_cancer",
        "factor_id": "family_history_liver_multiple",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 5.11,
        "ci_low": 2.10,
        "ci_high": 12.45,
        "evidence_grade": "IIA",
        "population": "Chinese (Shanghai Women's & Men's Health Studies)",
        "source_id": "Yang Y et al., Int J Cancer 2014, PMID:24535817",
        "citation_text": "Yang Y et al., 2014 (Int J Cancer). Prospective cohort (Shanghai) + meta-analysis. ≥2 FDR with HCC: HR=5.11 (95%CI 2.10-12.45). Overall pooled RR=2.55 (2.05-3.16) across 27 studies.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "肝癌家族史（多名亲属）",
    },
    {
        "assertion_id": "asrt_bladder_cancer_family_history_bladder_multiple",
        "cancer_id": "bladder_cancer",
        "factor_id": "family_history_bladder_multiple",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 2.67,
        "ci_low": 1.84,
        "ci_high": 3.86,
        "evidence_grade": "IIA",
        "population": "general adult (international pooled)",
        "source_id": "Yu EY et al., Cancer Prev Res 2022, PMID:35027464",
        "citation_text": "Yu EY et al., 2022 (Cancer Prevention Research). Pooled international case-control (4,327 cases, 8,948 controls). >1 FDR with bladder cancer: OR=2.67 (95%CI 1.84-3.86).",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "膀胱癌家族史（多名亲属）",
    },
    {
        "assertion_id": "asrt_kidney_cancer_family_history_kidney_multiple",
        "cancer_id": "kidney_cancer",
        "factor_id": "family_history_kidney_multiple",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 6.1,
        "ci_low": 2.37,
        "ci_high": 15.5,
        "evidence_grade": "IIB",
        "population": "Swedish general population",
        "source_id": "Jakobsson RG et al., J Urology 2023, PMID:37862613",
        "citation_text": "Jakobsson RG et al., 2023 (J Urology). Swedish national multiregister case-control study. ≥2 FDR with RCC: OR=6.1 (95%CI 2.37-15.5). Women with ≥2 FDR: OR=21 (4.16-105). Single registry study (IIB).",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "肾癌家族史（多名亲属）",
    },
    {
        "assertion_id": "asrt_thyroid_cancer_family_history_thyroid_multiple",
        "cancer_id": "thyroid_cancer",
        "factor_id": "family_history_thyroid_multiple",
        "factor_level": "present",
        "effect_type": "OR",
        "effect_value": 8.0,
        "ci_low": None,
        "ci_high": None,
        "evidence_grade": "IIB",
        "population": "general adult",
        "source_id": "Fallah M et al., J Med Genet 2013, PMID:23585692; FNMTC literature consensus",
        "citation_text": "Fallah M et al., 2013 (J Med Genet). Nordic registry: ≥1 FDR SIR=2.9 (female). Familial non-medullary thyroid cancer (FNMTC, ≥2 FDR) consensus estimate: 8-10x risk (multiple registry series). OR=8.0 is a conservative consensus point estimate. No single meta-analytic OR with tight CI for ≥2 FDR stratum exists.",
        "source_doc": "family_history_research_20260528.md",
        "source_line": None,
        "v2_factor_zh": "甲状腺癌家族史（多名亲属，FNMTC）",
    },
]

# ── New interaction question groups ──────────────────────────────────────────

def _yes_no_unknown_options(assertion_keys_yes, assertion_keys_no=None):
    """Build standard 3-option yes/no/unknown question options."""
    no_keys = assertion_keys_no or assertion_keys_yes  # same keys for no
    return [
        {"value": "yes", "label": "是", "updates": [
            {"assertion_key": k, "exists": True} for k in assertion_keys_yes
        ]},
        {"value": "no", "label": "否", "updates": [
            {"assertion_key": k, "exists": False} for k in no_keys
        ]},
        {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
            {"assertion_key": k, "exists": "unknown"} for k in no_keys
        ]},
    ]


NEW_QUESTION_GROUPS = [
    # --- New cancer-specific (first-degree) ---
    {
        "question_group": "family_history_cervical",
        "factor_id": "family_history_cervical",
        "prompt": "请补充：一级亲属（母亲/姐妹/女儿）中是否有宫颈癌患者？",
        "factor_type": "family_history",
        "options": _yes_no_unknown_options(
            ["cervical_cancer|family_history_cervical|present|asrt_cervical_cancer_family_history_cervical"]
        ),
    },
    {
        "question_group": "family_history_head_neck",
        "factor_id": "family_history_head_neck",
        "prompt": "请补充：一级亲属（父母/兄弟姐妹/子女）中是否有头颈部肿瘤患者（口腔癌、咽喉癌、舌癌等）？",
        "factor_type": "family_history",
        "options": _yes_no_unknown_options(
            ["head_neck_cancer|family_history_head_neck|present|asrt_head_neck_cancer_family_history_head_neck"]
        ),
    },
    {
        "question_group": "family_history_biliary",
        "factor_id": "family_history_biliary",
        "prompt": "请补充：一级亲属（父母/兄弟姐妹/子女）中是否有胆囊癌或胆管癌患者？",
        "factor_type": "family_history",
        "options": _yes_no_unknown_options(
            ["biliary_tract_cancer|family_history_biliary|present|asrt_biliary_tract_cancer_family_history_biliary"]
        ),
    },
    # --- Multiple relatives variants ---
    {
        "question_group": "family_history_gastric_multiple",
        "factor_id": "family_history_gastric_multiple",
        "prompt": "请补充：一级亲属中患胃癌的人数？（若前述已填写胃癌家族史阳性，此题补充人数）",
        "factor_type": "family_history",
        "options": [
            {"value": "multiple", "label": "≥2名一级亲属患胃癌", "updates": [
                {"assertion_key": "gastric_cancer|family_history_gastric_multiple|present|asrt_gastric_cancer_family_history_gastric_multiple", "exists": True}
            ]},
            {"value": "single", "label": "仅1名一级亲属患胃癌", "updates": [
                {"assertion_key": "gastric_cancer|family_history_gastric_multiple|present|asrt_gastric_cancer_family_history_gastric_multiple", "exists": False}
            ]},
            {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
                {"assertion_key": "gastric_cancer|family_history_gastric_multiple|present|asrt_gastric_cancer_family_history_gastric_multiple", "exists": "unknown"}
            ]},
        ],
    },
    {
        "question_group": "family_history_esophageal_multiple",
        "factor_id": "family_history_esophageal_multiple",
        "prompt": "请补充：一级亲属中患食管癌的人数？",
        "factor_type": "family_history",
        "options": [
            {"value": "multiple", "label": "≥2名一级亲属患食管癌", "updates": [
                {"assertion_key": "esophageal_cancer|family_history_esophageal_multiple|present|asrt_esophageal_cancer_family_history_esophageal_multiple", "exists": True}
            ]},
            {"value": "single", "label": "仅1名一级亲属患食管癌", "updates": [
                {"assertion_key": "esophageal_cancer|family_history_esophageal_multiple|present|asrt_esophageal_cancer_family_history_esophageal_multiple", "exists": False}
            ]},
            {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
                {"assertion_key": "esophageal_cancer|family_history_esophageal_multiple|present|asrt_esophageal_cancer_family_history_esophageal_multiple", "exists": "unknown"}
            ]},
        ],
    },
    {
        "question_group": "family_history_ovarian_multiple",
        "factor_id": "family_history_ovarian_multiple",
        "prompt": "请补充：一级亲属中患卵巢癌的人数？",
        "factor_type": "family_history",
        "options": [
            {"value": "multiple", "label": "≥2名一级亲属（如母亲+姐妹均患卵巢癌）", "updates": [
                {"assertion_key": "ovarian_cancer|family_history_ovarian_multiple|present|asrt_ovarian_cancer_family_history_ovarian_multiple", "exists": True}
            ]},
            {"value": "single", "label": "仅1名一级亲属患卵巢癌", "updates": [
                {"assertion_key": "ovarian_cancer|family_history_ovarian_multiple|present|asrt_ovarian_cancer_family_history_ovarian_multiple", "exists": False}
            ]},
            {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
                {"assertion_key": "ovarian_cancer|family_history_ovarian_multiple|present|asrt_ovarian_cancer_family_history_ovarian_multiple", "exists": "unknown"}
            ]},
        ],
    },
    {
        "question_group": "family_history_liver_multiple",
        "factor_id": "family_history_liver_multiple",
        "prompt": "请补充：一级亲属中患肝癌的人数？",
        "factor_type": "family_history",
        "options": [
            {"value": "multiple", "label": "≥2名一级亲属患肝癌", "updates": [
                {"assertion_key": "liver_cancer|family_history_liver_multiple|present|asrt_liver_cancer_family_history_liver_multiple", "exists": True}
            ]},
            {"value": "single", "label": "仅1名一级亲属患肝癌", "updates": [
                {"assertion_key": "liver_cancer|family_history_liver_multiple|present|asrt_liver_cancer_family_history_liver_multiple", "exists": False}
            ]},
            {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
                {"assertion_key": "liver_cancer|family_history_liver_multiple|present|asrt_liver_cancer_family_history_liver_multiple", "exists": "unknown"}
            ]},
        ],
    },
    {
        "question_group": "family_history_bladder_multiple",
        "factor_id": "family_history_bladder_multiple",
        "prompt": "请补充：一级亲属中患膀胱癌的人数？",
        "factor_type": "family_history",
        "options": [
            {"value": "multiple", "label": ">1名一级亲属患膀胱癌", "updates": [
                {"assertion_key": "bladder_cancer|family_history_bladder_multiple|present|asrt_bladder_cancer_family_history_bladder_multiple", "exists": True}
            ]},
            {"value": "single", "label": "仅1名一级亲属患膀胱癌", "updates": [
                {"assertion_key": "bladder_cancer|family_history_bladder_multiple|present|asrt_bladder_cancer_family_history_bladder_multiple", "exists": False}
            ]},
            {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
                {"assertion_key": "bladder_cancer|family_history_bladder_multiple|present|asrt_bladder_cancer_family_history_bladder_multiple", "exists": "unknown"}
            ]},
        ],
    },
    {
        "question_group": "family_history_kidney_multiple",
        "factor_id": "family_history_kidney_multiple",
        "prompt": "请补充：一级亲属中患肾癌的人数？",
        "factor_type": "family_history",
        "options": [
            {"value": "multiple", "label": "≥2名一级亲属患肾癌", "updates": [
                {"assertion_key": "kidney_cancer|family_history_kidney_multiple|present|asrt_kidney_cancer_family_history_kidney_multiple", "exists": True}
            ]},
            {"value": "single", "label": "仅1名一级亲属患肾癌", "updates": [
                {"assertion_key": "kidney_cancer|family_history_kidney_multiple|present|asrt_kidney_cancer_family_history_kidney_multiple", "exists": False}
            ]},
            {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
                {"assertion_key": "kidney_cancer|family_history_kidney_multiple|present|asrt_kidney_cancer_family_history_kidney_multiple", "exists": "unknown"}
            ]},
        ],
    },
    {
        "question_group": "family_history_thyroid_multiple",
        "factor_id": "family_history_thyroid_multiple",
        "prompt": "请补充：一级亲属中患甲状腺癌的人数？（≥2名提示家族性非髓样甲状腺癌 FNMTC）",
        "factor_type": "family_history",
        "options": [
            {"value": "multiple", "label": "≥2名一级亲属患甲状腺癌（FNMTC）", "updates": [
                {"assertion_key": "thyroid_cancer|family_history_thyroid_multiple|present|asrt_thyroid_cancer_family_history_thyroid_multiple", "exists": True}
            ]},
            {"value": "single", "label": "仅1名一级亲属患甲状腺癌", "updates": [
                {"assertion_key": "thyroid_cancer|family_history_thyroid_multiple|present|asrt_thyroid_cancer_family_history_thyroid_multiple", "exists": False}
            ]},
            {"value": "unknown", "label": "不清楚/暂不提供", "updates": [
                {"assertion_key": "thyroid_cancer|family_history_thyroid_multiple|present|asrt_thyroid_cancer_family_history_thyroid_multiple", "exists": "unknown"}
            ]},
        ],
    },
]


# ── Apply ─────────────────────────────────────────────────────────────────────

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  Saved {path.name}")


def main():
    # 1. risk_factors.json
    print("\n=== risk_factors.json ===")
    rf = load(RF_FILE)
    existing_ids = {f["factor_id"] for f in rf["risk_factors"]}
    added = 0
    for factor in NEW_FACTORS:
        fid = factor["factor_id"]
        if fid in existing_ids:
            print(f"  SKIP (exists): {fid}")
            continue
        rf["risk_factors"].append(factor)
        existing_ids.add(fid)
        added += 1
        print(f"  ADD: {fid}")
    rf["version"] = NEW_VERSION
    save(RF_FILE, rf)
    print(f"  Added {added} factors → total {len(rf['risk_factors'])}")

    # 2. risk_assertions.json — updates
    print("\n=== risk_assertions.json (UPDATE) ===")
    ra = load(RA_FILE)
    idx = {a["assertion_id"]: i for i, a in enumerate(ra["assertions"])}
    for upd in ASSERTION_UPDATES:
        tid = upd["_target"]
        if tid not in idx:
            print(f"  WARN not found: {tid}")
            continue
        entry = ra["assertions"][idx[tid]]
        fields = [k for k in upd if not k.startswith("_")]
        for k in fields:
            entry[k] = upd[k]
        print(f"  UPDATE {tid}: {fields}")

    # 3. risk_assertions.json — new
    print("\n=== risk_assertions.json (ADD) ===")
    existing_asrt = {a["assertion_id"] for a in ra["assertions"]}
    added_asrt = 0
    for asrt in NEW_ASSERTIONS:
        aid = asrt["assertion_id"]
        if aid in existing_asrt:
            print(f"  SKIP (exists): {aid}")
            continue
        ra["assertions"].append(asrt)
        existing_asrt.add(aid)
        added_asrt += 1
        print(f"  ADD: {aid}")
    ra["version"] = NEW_VERSION
    save(RA_FILE, ra)
    print(f"  Added {added_asrt} assertions → total {len(ra['assertions'])}")

    # 4. interaction_question_templates.json
    print("\n=== interaction_question_templates.json ===")
    iqt = load(IQT_FILE)
    existing_groups = {q["question_group"] for q in iqt["questions"]}
    added_q = 0
    for qg in NEW_QUESTION_GROUPS:
        if qg["question_group"] in existing_groups:
            print(f"  SKIP (exists): {qg['question_group']}")
            continue
        iqt["questions"].append(qg)
        existing_groups.add(qg["question_group"])
        added_q += 1
        print(f"  ADD: {qg['question_group']}")
    save(IQT_FILE, iqt)
    print(f"  Added {added_q} question groups → total {len(iqt['questions'])}")


if __name__ == "__main__":
    main()
