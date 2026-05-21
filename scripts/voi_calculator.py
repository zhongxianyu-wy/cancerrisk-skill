#!/usr/bin/env python3
"""VoI (Value of Information) calculator — ported from cancer-risk-v4.2.

Core formula:

    VoI(test) = individual_incidence_rate × (stage1_5y_OS − late_stage_5y_OS) × 5 × sensitivity

Units: roughly QALY-life-month gain per 100,000 person-years. Higher
score → more screening benefit. ``individual_incidence_rate`` is derived
from the current snapshot posterior, not the unadjusted age/sex prior.

Special case — multi-cancer liquid biopsy (吉早安):
    VoI(吉早安) = Σ for each cancer c in (risk_cancers ∩ jizaoan_coverage):
        individual_incidence[c] × survival_gain_5y[c] × 5 × sensitivity[c]

Recommendation tiers (voi_parameters.json::voi_thresholds):
    ≥ 20  → 强烈推荐
    10-20 → 推荐
    5-10  → 可考虑
    < 5   → 常规

Reference: /Volumes/exp/geneplu_work/1.skill_tijian/28.project_tijian/
           skills/cancer-risk-v4.2/cancer-risk-v4.2.0/scripts/voi_calculator.py
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent

# Map between our cancer_id (English) and v4.2's cancer_name_zh (Chinese).
# Some v4.2 cancers may not exist in our 14; some of ours may not have VoI data.
EN_TO_ZH = {
    "lung_cancer": "肺癌",
    "liver_cancer": "肝癌",
    "gastric_cancer": "胃癌",
    "esophageal_cancer": "食管癌",
    "colorectal_cancer": "结直肠癌",
    "breast_cancer": "乳腺癌",
    "cervical_cancer": "宫颈癌",
    "prostate_cancer": "前列腺癌",
    "bladder_cancer": "膀胱癌",
    "ovarian_cancer": "卵巢癌",
    "kidney_cancer": "肾癌",
    "head_neck_cancer": "头颈肿瘤",
    "biliary_tract_cancer": "胆道肿瘤",
    "thyroid_cancer": "甲状腺癌",
}


@dataclass
class ScreeningVoI:
    cancer_id: str
    cancer_name_zh: str
    method: str
    description: str = ""
    voi_score: float = 0.0
    recommendation: str = ""
    prior_risk: float = 0.0
    sensitivity: float = 0.0
    specificity: float = 0.0
    cost_rmb: int = 0
    cost_level: str = ""
    invasiveness: str = ""
    guideline: str = ""
    is_liquid_biopsy: bool = False
    multi_cancer_breakdown: list[dict[str, Any]] = field(default_factory=list)


def _classify(score: float, thresholds: dict[str, Any]) -> str:
    high = thresholds.get("high_benefit", {}).get("threshold", 20)
    medium = thresholds.get("medium_benefit", {}).get("threshold", 10)
    low = thresholds.get("low_benefit", {}).get("threshold", 5)
    if score >= high:
        return "强烈推荐"
    if score >= medium:
        return "推荐"
    if score >= low:
        return "可考虑"
    return "常规"


def _compute_single_method_voi(
    *,
    cancer_id: str,
    cancer_zh: str,
    method_info: dict[str, Any],
    survival: dict[str, Any],
    incidence_rate_per_100k: float,
    thresholds: dict[str, Any],
    prior_risk: float,
) -> ScreeningVoI:
    """Single-method VoI = individual incidence × (stage1 − late) × 5 × sensitivity."""
    se = float(method_info.get("sensitivity", 0)) / 100.0
    sp = float(method_info.get("specificity", 0)) / 100.0
    stage1 = float(survival.get("stage1_5y_os", 0))
    late = float(survival.get("late_stage_5y_os", 0))
    survival_gain_5y = stage1 - late
    voi = incidence_rate_per_100k * survival_gain_5y * 5 * se
    return ScreeningVoI(
        cancer_id=cancer_id,
        cancer_name_zh=cancer_zh,
        method=method_info.get("method", ""),
        description=method_info.get("description", method_info.get("method", "")),
        voi_score=round(voi, 4),
        recommendation=_classify(voi, thresholds),
        prior_risk=prior_risk,
        sensitivity=se,
        specificity=sp,
        cost_level=method_info.get("cost_level", ""),
        invasiveness=method_info.get("invasiveness", ""),
        guideline=method_info.get("guideline", ""),
    )


def _compute_jizaoan_voi(
    *,
    risk_cancer_ids: list[str],
    cancer_data: dict[str, Any],   # cancer_id → {incidence_rate, prior_risk, survival, jizaoan_sens}
    thresholds: dict[str, Any],
    jizaoan_cost_rmb: int,
    gender: str,
    jizaoan_coverage: list[str],   # Chinese names
) -> ScreeningVoI | None:
    """Multi-cancer liquid biopsy: Σ over (risk ∩ coverage) cancers."""
    coverage_set = {EN_TO_ZH.get(cid, "") for cid in risk_cancer_ids} & set(jizaoan_coverage)
    if not coverage_set:
        return None
    total_voi = 0.0
    breakdown: list[dict[str, Any]] = []
    sens_list: list[float] = []
    for zh_name in coverage_set:
        cid = next((k for k, v in EN_TO_ZH.items() if v == zh_name), None)
        if not cid or cid not in cancer_data:
            continue
        info = cancer_data[cid]
        survival = info["survival"]
        sg5 = float(survival.get("stage1_5y_os", 0)) - float(survival.get("late_stage_5y_os", 0))
        se = info.get("jizaoan_sensitivity", 0)
        rate = info.get("incidence_rate_per_100k", 0)
        voi_c = rate * sg5 * 5 * se
        total_voi += voi_c
        sens_list.append(se)
        breakdown.append({
            "cancer_id": cid,
            "cancer_name_zh": zh_name,
            "incidence_rate_per_100k": rate,
            "survival_gain_5y": sg5,
            "sensitivity": se,
            "voi_contribution": round(voi_c, 4),
        })
    if not breakdown:
        return None
    return ScreeningVoI(
        cancer_id=",".join(sorted(b["cancer_id"] for b in breakdown)),
        cancer_name_zh="+".join(sorted(b["cancer_name_zh"] for b in breakdown)),
        method="吉早安",
        description="吉因加多癌早筛液体活检",
        voi_score=round(total_voi, 4),
        recommendation=_classify(total_voi, thresholds),
        prior_risk=0.0,
        sensitivity=round(sum(sens_list) / max(len(sens_list), 1), 4),
        specificity=0.991,
        cost_rmb=jizaoan_cost_rmb,
        cost_level="high",
        invasiveness="non-invasive",
        guideline="吉早安多癌早筛白皮书",
        is_liquid_biopsy=True,
        multi_cancer_breakdown=breakdown,
    )


def compute_voi_for_cancers(
    *,
    snapshot: dict[str, Any],
    priors_payload: dict[str, Any],
    voi_parameters: dict[str, Any],
    screening_methods: dict[str, Any],
    detection_derived: dict[str, Any],
    person_sex: str | None,
    person_age: int | None,
) -> list[ScreeningVoI]:
    """Top-level entry: build per-cancer VoI ranking + the multi-cancer
    liquid biopsy entry. Returns list sorted by voi_score desc.
    """
    thresholds = voi_parameters.get("voi_thresholds", {})
    survival_data = voi_parameters.get("survival_gain", {}).get("cancers", {})
    cost_data = voi_parameters.get("screening_cost_qaly", {}).get("methods", {})
    rankings: list[ScreeningVoI] = []

    # Per-cancer VoI (primary_screening methods only — jizaoan handled below)
    risk_cancer_ids: list[str] = []
    jizaoan_inputs: dict[str, dict[str, Any]] = {}
    jizaoan_sens_map: dict[str, float] = {}
    # Extract per-cancer Jizaoan sensitivity from detection_performance_derived
    for d in detection_derived.get("derived_detection_performance", []):
        if d.get("test_id") == "jizaoan_multi_cancer_screening":
            jizaoan_sens_map[d["cancer_id"]] = float(d.get("sensitivity", 0))

    for cancer_result in snapshot.get("cancers", []):
        if cancer_result.get("not_applicable"):
            continue
        cancer_id = cancer_result["cancer_id"]
        cancer_zh = EN_TO_ZH.get(cancer_id)
        if not cancer_zh:
            continue

        posterior = cancer_result.get("posterior_probability")
        if posterior is None:
            continue
        posterior = float(posterior)
        if posterior <= 0:
            continue
        # Use the current personalized risk as the incidence term, scaled
        # to per-100k so the legacy thresholds keep their intended magnitude.
        rate = posterior * 100000.0
        prior = float(cancer_result.get("prior_probability") or 0.0)

        survival = survival_data.get(cancer_zh)
        if not survival:
            continue

        screening_data = screening_methods.get("cancers", {}).get(cancer_zh, {})
        primary_methods = screening_data.get("primary_screening", [])
        for m in primary_methods:
            voi_item = _compute_single_method_voi(
                cancer_id=cancer_id, cancer_zh=cancer_zh,
                method_info=m, survival=survival,
                incidence_rate_per_100k=rate,
                thresholds=thresholds, prior_risk=prior,
            )
            method_cost = cost_data.get(m.get("method", ""), {})
            voi_item.cost_rmb = int(method_cost.get("cost_rmb", 0))
            rankings.append(voi_item)

        risk_cancer_ids.append(cancer_id)
        jizaoan_inputs[cancer_id] = {
            "incidence_rate_per_100k": rate,
            "survival": survival,
            "jizaoan_sensitivity": jizaoan_sens_map.get(cancer_id, 0.0),
            "prior_risk": prior,
        }

    # Multi-cancer liquid biopsy (吉早安)
    # Coverage: take from any screening_methods.cancers[].liquid_biopsy method=吉早安
    jizaoan_coverage: list[str] = []
    for zh_name, sd in screening_methods.get("cancers", {}).items():
        liquid = sd.get("liquid_biopsy")
        if liquid and liquid.get("method") == "吉早安":
            jizaoan_coverage.append(zh_name)
    jizaoan_cost = int(cost_data.get("吉早安液体活检", {}).get("cost_rmb", 3000))
    jizaoan_item = _compute_jizaoan_voi(
        risk_cancer_ids=risk_cancer_ids,
        cancer_data=jizaoan_inputs,
        thresholds=thresholds,
        jizaoan_cost_rmb=jizaoan_cost,
        gender=person_sex or "all",
        jizaoan_coverage=jizaoan_coverage,
    )
    if jizaoan_item:
        rankings.append(jizaoan_item)

    rankings.sort(key=lambda x: x.voi_score, reverse=True)
    return rankings


def run_voi_stage(
    *,
    artifacts: Path,
    evidence_store: Path,
    person_sex: str | None,
    person_age: int | None,
) -> dict[str, Any]:
    snapshot = json.loads((artifacts / "snapshot_risk.json").read_text(encoding="utf-8"))
    priors = json.loads((evidence_store / "ontology/cancer_age_sex_priors.json").read_text(encoding="utf-8"))
    voi_params = json.loads((evidence_store / "voi/voi_parameters.json").read_text(encoding="utf-8"))
    screening_methods = json.loads((evidence_store / "voi/screening_methods.json").read_text(encoding="utf-8"))
    detection_derived_path = evidence_store / "assertions/detection_performance_derived.json"
    detection_derived = json.loads(detection_derived_path.read_text(encoding="utf-8")) if detection_derived_path.is_file() else {"derived_detection_performance": []}

    rankings = compute_voi_for_cancers(
        snapshot=snapshot,
        priors_payload=priors,
        voi_parameters=voi_params,
        screening_methods=screening_methods,
        detection_derived=detection_derived,
        person_sex=person_sex,
        person_age=person_age,
    )

    output = {
        "schema_version": "voi-ranking-v1",
        "formula": "VoI = current_individual_probability × 100000 × (stage1_5y_os − late_stage_5y_os) × 5 × sensitivity",
        "thresholds": voi_params.get("voi_thresholds"),
        "rankings": [asdict(r) for r in rankings],
        "total_methods_evaluated": len(rankings),
        "top_recommendation": rankings[0].method if rankings else "",
    }
    out_path = artifacts / "voi_ranking.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--evidence-store", default=str(SKILL_ROOT / "evidence_store"))
    parser.add_argument("--sex", choices=["male", "female"])
    parser.add_argument("--age", type=int)
    args = parser.parse_args()
    out = run_voi_stage(
        artifacts=Path(args.artifacts),
        evidence_store=Path(args.evidence_store),
        person_sex=args.sex,
        person_age=args.age,
    )
    print(f"[voi] rankings={len(out['rankings'])} top={out['top_recommendation']}")


if __name__ == "__main__":
    main()
