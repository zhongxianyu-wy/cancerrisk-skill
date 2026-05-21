#!/usr/bin/env python3
"""Task8 longitudinal cancer risk analysis.

For every cancer that snapshot_risk produced a posterior for, replay the
log-odds calculation along the archive timeline so the report can show
how each posterior moved across time. Cancers without a snapshot
posterior (sex-mismatched or missing-prior) are still surfaced but
without a trend block. There is no top-N filter — the user asked for all
applicable cancers to be analysed.

The orchestrator runs this before archive apply. The script reads the
existing per-person timeline, merges the current run's events in memory,
and never mutates the archive. If no historical timepoints exist for a
cancer's contributing factors, the trend collapses to a single point that
matches the current snapshot.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from snapshot_risk import logit, sigmoid, assign_tier

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "longitudinal-risk-v1"


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _factor_dedup_key(record: dict[str, Any]) -> str | None:
    return record.get("assertion_key") or record.get("factor_key")


def _merge_factor_timeline(
    archived: dict[str, Any],
    current_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Merge archived factor entries with current-run entries in memory.

    The archive is not mutated here. This lets longitudinal analysis use
    prior history plus the current exam before the user confirms入档.
    """
    merged = {"entries": list(archived.get("entries", []))}
    seen = {
        (_factor_dedup_key(entry), entry.get("exam_date"), entry.get("source_data_id"))
        for entry in merged["entries"]
        if _factor_dedup_key(entry)
    }
    for entry in current_entries:
        dk = _factor_dedup_key(entry)
        if not dk:
            continue
        key = (dk, entry.get("exam_date"), entry.get("source_data_id"))
        if key in seen:
            continue
        merged["entries"].append(entry)
        seen.add(key)
    return merged


def _merge_screening_timeline(
    archived: dict[str, Any],
    current_tests: list[dict[str, Any]],
) -> dict[str, Any]:
    merged = {"entries": list(archived.get("entries", []))}
    seen = {
        (entry.get("test_id"), entry.get("exam_date"), entry.get("source_data_id"))
        for entry in merged["entries"]
        if entry.get("test_id")
    }
    for test in current_tests:
        tid = test.get("test_id")
        if not tid:
            continue
        key = (tid, test.get("exam_date"), test.get("source_data_id"))
        if key in seen:
            continue
        merged["entries"].append(test)
        seen.add(key)
    return merged


def _replace_now_dates(entries: list[dict[str, Any]], run_date: str | None) -> list[dict[str, Any]]:
    resolved_date = run_date or datetime.now().strftime("%Y-%m-%d")
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        item = dict(entry)
        if item.get("exam_date") == "now":
            item["exam_date"] = resolved_date
        normalized.append(item)
    return normalized


def _derived_by_assertion_id(derived: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {d["assertion_id"]: d for d in derived.get("derived_assertions", [])}


def _derived_by_factor_level(derived: dict[str, Any]) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    """Index derived assertions by ``(cancer_id, factor_id, factor_level)``."""
    index: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for d in derived.get("derived_assertions", []):
        key = (d.get("cancer_id"), d.get("factor_id"), d.get("factor_level"))
        if all(key):
            index.setdefault(key, []).append(d)
    return index


def _detection_by_cancer_id(detection: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_cancer: dict[str, list[dict[str, Any]]] = {}
    for d in detection.get("derived_detection_performance", []):
        by_cancer.setdefault(d["cancer_id"], []).append(d)
    return by_cancer


def _ppv_series_for_cancer(
    cancer_id: str,
    factor_timeline: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return per-exam-date PPV observations for imaging_finding entries."""
    points: dict[str, dict[str, Any]] = {}
    for entry in factor_timeline.get("entries", []):
        if entry.get("factor_type") != "imaging_finding":
            continue
        if entry.get("cancer_id") != cancer_id:
            continue
        if entry.get("exists") is not True:
            continue
        ppv = entry.get("ppv_point_used")
        if ppv is None:
            continue
        date = entry.get("exam_date") or "unknown"
        existing = points.get(date)
        if existing is None or float(ppv) > float(existing["ppv_point_used"]):
            points[date] = {
                "exam_date": date,
                "factor_id": entry.get("factor_id"),
                "finding_name_zh": entry.get("finding_name_zh"),
                "ppv_point_used": float(ppv),
                "malignancy_ppv_range": entry.get("malignancy_ppv_range"),
                "measurement_value": entry.get("measurement_value"),
                "measurement_unit": entry.get("measurement_unit"),
            }
    return sorted(points.values(), key=lambda p: p["exam_date"])


def _trend_verdicts_for_cancer(
    cancer_id: str,
    factor_timeline: dict[str, Any],
    protein_marker_ids: set[str],
    change_threshold: float,
) -> tuple[str, str, list[dict[str, Any]]]:
    """Compute imaging and marker group verdicts for trend correction.

    Returns (imaging_verdict, marker_verdict, evidence_list).
    Verdict values: "increasing" | "decreasing" | "no_data".
    Internal conflict within a group → "no_data" for that group.
    """
    # Collect latest two measurements per (group, factor_id)
    imaging_measurements: dict[str, list[tuple[str, float]]] = {}  # factor_id → [(date, val)]
    marker_measurements: dict[str, list[tuple[str, float]]] = {}

    for entry in factor_timeline.get("entries", []):
        if entry.get("exists") is not True:
            continue
        val = entry.get("measurement_value")
        if val is None:
            continue
        try:
            val = float(val)
        except (TypeError, ValueError):
            continue
        date = entry.get("exam_date") or ""
        fid = entry.get("factor_id") or ""

        if entry.get("factor_type") == "imaging_finding" and entry.get("cancer_id") == cancer_id:
            imaging_measurements.setdefault(fid, []).append((date, val))
        elif fid in protein_marker_ids:
            ak = entry.get("assertion_key") or ""
            fk = entry.get("factor_key") or ""
            if ak.startswith(cancer_id + "|") or fk.startswith(cancer_id + "|"):
                marker_measurements.setdefault(fid, []).append((date, val))

    def _factor_trend(measurements: dict[str, list[tuple[str, float]]]) -> tuple[str, list[dict[str, Any]]]:
        """Return group verdict and per-factor evidence."""
        trends: list[str] = []
        evidence: list[dict[str, Any]] = []
        for fid, pts in measurements.items():
            pts_sorted = sorted(pts, key=lambda x: x[0])
            if len(pts_sorted) < 2:
                continue
            curr_date, curr_val = pts_sorted[-1]
            prev_date, prev_val = pts_sorted[-2]
            if prev_val == 0:
                continue
            delta = (curr_val - prev_val) / abs(prev_val)
            if delta > change_threshold:
                label = "up"
            elif delta < -change_threshold:
                label = "down"
            else:
                label = "stable"
            trends.append(label)
            evidence.append({
                "factor_id": fid,
                "prev_value": prev_val,
                "curr_value": curr_val,
                "prev_date": prev_date,
                "curr_date": curr_date,
                "delta_pct": round(delta * 100, 1),
                "trend": label,
            })
        if not trends or all(t == "stable" for t in trends):
            return "no_data", evidence
        has_up = any(t == "up" for t in trends)
        has_down = any(t == "down" for t in trends)
        if has_up and has_down:
            return "no_data", evidence  # internal conflict
        if has_up:
            return "increasing", evidence
        return "decreasing", evidence

    img_verdict, img_evidence = _factor_trend(imaging_measurements)
    mrk_verdict, mrk_evidence = _factor_trend(marker_measurements)
    all_evidence = img_evidence + mrk_evidence
    return img_verdict, mrk_verdict, all_evidence


def _apply_trend_correction(
    base_probability: float,
    imaging_verdict: str,
    marker_verdict: str,
    growth_multiplier: float,
    remission_multiplier: float,
) -> tuple[float, str]:
    """Apply trend correction to base_probability. Returns (corrected, correction_type)."""
    # Cross-group conflict resolution: imaging wins
    if imaging_verdict == "increasing" and marker_verdict == "decreasing":
        verdict = "increasing"
    elif imaging_verdict == "decreasing" and marker_verdict == "increasing":
        verdict = "decreasing"
    elif imaging_verdict == "increasing" or marker_verdict == "increasing":
        verdict = "increasing"
    elif imaging_verdict == "decreasing" or marker_verdict == "decreasing":
        verdict = "decreasing"
    else:
        verdict = "unchanged"

    if verdict == "increasing":
        corrected = min(base_probability * growth_multiplier, 1.0)
        return corrected, "growth"
    if verdict == "decreasing":
        corrected = max(base_probability * remission_multiplier, 0.0)
        return corrected, "remission"
    return base_probability, "unchanged"


def _timeline_points_for_cancer(
    cancer_id: str,
    factor_timeline: dict[str, Any],
    screening_timeline: dict[str, Any],
    derived_by_id: dict[str, dict[str, Any]],
    derived_by_fl: dict[tuple[str, str, str], list[dict[str, Any]]],
    detection_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Group archive entries by exam_date, retaining cancer-relevant ones.

    Accepts both cancer-expanded ``assertion_key`` entries (join via
    ``assertion_id``, gate on ``cancer_id``) and slim ``factor_key``
    entries (join via ``(cancer_id, factor_id, factor_level)``).
    """
    points: dict[str, dict[str, Any]] = {}
    for entry in factor_timeline.get("entries", []):
        if entry.get("exists") is not True:
            continue
        matches: list[dict[str, Any]] = []
        ak = entry.get("assertion_key") or ""
        if ak:
            if not ak.startswith(cancer_id + "|"):
                continue
            assertion_id = ak.split("|")[-1]
            derived = derived_by_id.get(assertion_id)
            if derived and derived.get("conversion_status") == "usable":
                matches.append(derived)
        else:
            factor_id = entry.get("factor_id")
            factor_level = entry.get("factor_level")
            if not factor_id or not factor_level:
                continue
            for d in derived_by_fl.get((cancer_id, factor_id, factor_level), []):
                if d.get("conversion_status") == "usable":
                    matches.append(d)
        if not matches:
            continue
        date = entry.get("exam_date") or "unknown"
        bucket = points.setdefault(date, {"exam_date": date, "components": [], "screening": None})
        for derived in matches:
            bucket["components"].append({
                "assertion_key": derived.get("assertion_key") or ak,
                "factor_id": entry.get("factor_id"),
                "factor_level": entry.get("factor_level"),
                "log_odds_delta": float(derived["log_odds_delta"]),
                "source": entry.get("source"),
                "approximation": bool(derived.get("approximation", False)),
            })

    for entry in screening_timeline.get("entries", []):
        result = entry.get("result")
        if result not in {"negative", "positive"}:
            continue
        # v6 P1: multiple detections per cancer (tumor markers + jizaoan).
        # Find the one whose test_id matches this screening entry.
        cancer_detections = detection_by_id.get(cancer_id) or []
        if isinstance(cancer_detections, dict):
            cancer_detections = [cancer_detections]  # legacy single-record fallback
        detection = next(
            (d for d in cancer_detections
             if d.get("test_id") == entry.get("test_id")
             and d.get("conversion_status") == "usable"),
            None,
        )
        if not detection:
            continue
        if result == "positive" and cancer_id not in (entry.get("top_cancers") or []):
            continue
        delta = float(
            detection["positive_log_odds_delta"]
            if result == "positive"
            else detection["negative_log_odds_delta"]
        )
        date = entry.get("exam_date") or "unknown"
        bucket = points.setdefault(date, {"exam_date": date, "components": [], "screening": None})
        bucket["screening"] = {
            "test_id": entry.get("test_id"),
            "result": result,
            "log_odds_delta": delta,
            "approximation": bool(detection.get("probability_boundary_adjustment", False)),
        }

    ordered = sorted(points.values(), key=lambda p: p["exam_date"])
    return ordered


def _replay_posteriors(prior_log_odds: float, points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    series: list[dict[str, Any]] = []
    cumulative = prior_log_odds
    seen_components: set[str] = set()
    for point in points:
        added_components = []
        for c in point["components"]:
            if c["assertion_key"] in seen_components:
                continue
            seen_components.add(c["assertion_key"])
            cumulative += c["log_odds_delta"]
            added_components.append(c)
        screening = point.get("screening")
        screening_delta = screening["log_odds_delta"] if screening else 0.0
        # Screening tests are applied per timepoint (each result is its own
        # likelihood update) — they do not accumulate across visits.
        posterior_log_odds = cumulative + screening_delta
        series.append({
            "exam_date": point["exam_date"],
            "posterior_log_odds": posterior_log_odds,
            "posterior_probability": sigmoid(posterior_log_odds),
            "added_components": added_components,
            "screening": screening,
        })
    return series


def compute_longitudinal(
    *,
    snapshot: dict[str, Any],
    factor_timeline: dict[str, Any],
    screening_timeline: dict[str, Any],
    derived_assertions: dict[str, Any],
    detection_derived: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or {}
    tiers = (config.get("risk_prediction", {}) or {}).get("risk_tiers") or []
    trend_cfg = (config.get("tumor_trend") or {}) if isinstance(config, dict) else {}
    protein_marker_ids: set[str] = set(trend_cfg.get("protein_marker_factor_ids") or [])
    growth_mult = float(trend_cfg.get("growth_multiplier") or 2.0)
    remission_mult = float(trend_cfg.get("remission_multiplier") or 0.5)
    change_threshold = float(trend_cfg.get("change_threshold") or 0.30)

    derived_by_id = _derived_by_assertion_id(derived_assertions)
    derived_by_fl = _derived_by_factor_level(derived_assertions)
    detection_by_id = _detection_by_cancer_id(detection_derived)

    # Phase 3: detect whether there is ANY historical archive entry. If not,
    # every cancer becomes baseline_only — we still surface a card per cancer
    # so the user sees the full panel and the html banner can announce
    # "仅单次数据，无法展示趋势".
    has_history = bool(factor_timeline.get("entries")) or bool(screening_timeline.get("entries"))

    cancer_trends: list[dict[str, Any]] = []
    for cancer in snapshot.get("cancers", []):
        cancer_id = cancer["cancer_id"]
        base_posterior = cancer.get("posterior_probability")
        trend_entry: dict[str, Any] = {
            "cancer_id": cancer_id,
            "cancer_name_zh": cancer.get("cancer_name_zh"),
            "applicable_sex": cancer.get("applicable_sex"),
            "status_reason": cancer.get("status_reason"),
            "not_applicable": cancer.get("not_applicable", False),
            "current_posterior_probability": base_posterior,
            "corrected_posterior_probability": base_posterior,
            "current_risk_tier": cancer.get("risk_tier"),
            "history": [],
            "ppv_series": [],
            "trend": "no_history",
            "trend_correction": {
                "correction_type": "unchanged",
                "multiplier": 1.0,
                "imaging_verdict": "no_data",
                "marker_verdict": "no_data",
                "evidence": [],
            },
        }

        # PPV series from imaging findings (tracked independently of Bayes).
        trend_entry["ppv_series"] = _ppv_series_for_cancer(cancer_id, factor_timeline)

        if base_posterior is None:
            trend_entry["trend"] = "baseline_only" if not has_history else "no_history"
            cancer_trends.append(trend_entry)
            continue
        prior_log_odds = cancer.get("prior_log_odds")
        if prior_log_odds is None:
            trend_entry["trend"] = "baseline_only" if not has_history else "no_history"
            cancer_trends.append(trend_entry)
            continue

        # Trend correction: compare latest vs previous measurements.
        img_verdict, mrk_verdict, evidence = _trend_verdicts_for_cancer(
            cancer_id, factor_timeline, protein_marker_ids, change_threshold,
        )
        corrected, correction_type = _apply_trend_correction(
            base_posterior, img_verdict, mrk_verdict, growth_mult, remission_mult,
        )
        multiplier = (
            growth_mult if correction_type == "growth"
            else remission_mult if correction_type == "remission"
            else 1.0
        )
        trend_entry["corrected_posterior_probability"] = corrected
        trend_entry["trend_correction"] = {
            "correction_type": correction_type,
            "multiplier": multiplier,
            "imaging_verdict": img_verdict,
            "marker_verdict": mrk_verdict,
            "evidence": evidence,
        }

        points = _timeline_points_for_cancer(
            cancer_id, factor_timeline, screening_timeline,
            derived_by_id, derived_by_fl, detection_by_id,
        )
        series = _replay_posteriors(prior_log_odds, points)
        if not series:
            # Fall back to the snapshot value as a single anchor point.
            trend_entry["history"] = [{
                "exam_date": None,
                "posterior_probability": base_posterior,
                "posterior_log_odds": cancer["posterior_log_odds"],
                "risk_tier": cancer.get("risk_tier"),
                "added_components": [],
                "screening": None,
            }]
            trend_entry["trend"] = "baseline_only" if not has_history else "snapshot_only"
        else:
            trend_entry["history"] = [{
                "exam_date": s["exam_date"],
                "posterior_probability": s["posterior_probability"],
                "posterior_log_odds": s["posterior_log_odds"],
                "risk_tier": assign_tier(s["posterior_probability"], tiers) if tiers else None,
                "added_components": s["added_components"],
                "screening": s["screening"],
            } for s in series]
            if len(series) == 1:
                trend_entry["trend"] = "single_point"
            else:
                delta = series[-1]["posterior_probability"] - series[0]["posterior_probability"]
                if abs(delta) < 1e-6:
                    trend_entry["trend"] = "stable"
                elif delta > 0:
                    trend_entry["trend"] = "increasing"
                else:
                    trend_entry["trend"] = "decreasing"
        cancer_trends.append(trend_entry)

    return {
        "schema_version": SCHEMA_VERSION,
        "person_context": snapshot.get("person_context"),
        "risk_tier_thresholds": tiers,
        "has_history": has_history,
        "baseline_only": not has_history,
        "cancers": cancer_trends,
        "summary": {
            "total": len(cancer_trends),
            "with_trend": sum(1 for c in cancer_trends if c["trend"] in {"increasing", "decreasing", "stable"}),
            "with_history": sum(1 for c in cancer_trends if c["trend"] in {"increasing", "decreasing", "stable", "single_point", "snapshot_only"}),
            "single_point": sum(1 for c in cancer_trends if c["trend"] == "single_point"),
            "snapshot_only": sum(1 for c in cancer_trends if c["trend"] == "snapshot_only"),
            "baseline_only": sum(1 for c in cancer_trends if c["trend"] == "baseline_only"),
            "no_history": sum(1 for c in cancer_trends if c["trend"] == "no_history"),
            "no_posterior": sum(1 for c in cancer_trends if c["current_posterior_probability"] is None),
        },
    }


def run_longitudinal_stage(
    *,
    artifacts: Path,
    archives_root: Path,
    person_id: str,
    evidence_store: Path,
    config_path: Path,
) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    snapshot = _read_json(artifacts / "snapshot_risk.json", {})
    merged_current = _read_json(artifacts / "merged_risk_factors.json", {"factor_events": [], "screening_tests": []})
    current_timeline = _read_json(artifacts / "structured_risk_factors_timeline.json", {})
    current_run_date = current_timeline.get("run_date") if isinstance(current_timeline, dict) else None
    # v6: ALWAYS look up the predetermined per-id folder first
    # (exists or not, the lookup is observable + path convention is
    # enforced in archive_manager.resolve_person_archive).
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import archive_manager
    lookup = archive_manager.resolve_person_archive(archives_root, person_id)
    person_dir = Path(lookup["person_dir"])
    print(
        f"[task8][longitudinal] archive lookup: person_id={person_id} "
        f"dir={person_dir} status={lookup['status']} "
        f"factor_entries={lookup['files']['factor_timeline']['entries']} "
        f"screening_entries={lookup['files']['screening_test_timeline']['entries']} "
        f"snapshots={lookup['files']['snapshots_dir']['snapshot_count']}",
        file=sys.stderr,
    )
    archived_factor_timeline = _read_json(person_dir / "factor_timeline.json", {"entries": []})
    archived_screening_timeline = _read_json(person_dir / "screening_test_timeline.json", {"entries": []})
    factor_timeline = _merge_factor_timeline(
        archived_factor_timeline,
        _replace_now_dates(list(merged_current.get("factor_events", [])), current_run_date),
    )
    screening_timeline = _merge_screening_timeline(
        archived_screening_timeline,
        _replace_now_dates(list(merged_current.get("screening_tests", [])), current_run_date),
    )
    derived = _read_json(evidence_store / "assertions/risk_assertions_derived.json", {"derived_assertions": []})
    detection = _read_json(evidence_store / "assertions/detection_performance_derived.json", {"derived_detection_performance": []})

    longitudinal = compute_longitudinal(
        snapshot=snapshot,
        factor_timeline=factor_timeline,
        screening_timeline=screening_timeline,
        derived_assertions=derived,
        detection_derived=detection,
        config=config,
    )
    # v6: carry the lookup result in the output for downstream audit.
    longitudinal["archive_lookup"] = lookup
    longitudinal["analysis_input"] = {
        "archived_factor_entries": len(archived_factor_timeline.get("entries", [])),
        "archived_screening_entries": len(archived_screening_timeline.get("entries", [])),
        "current_factor_entries": len(merged_current.get("factor_events", [])),
        "current_screening_entries": len(merged_current.get("screening_tests", [])),
        "merged_factor_entries": len(factor_timeline.get("entries", [])),
        "merged_screening_entries": len(screening_timeline.get("entries", [])),
        "current_run_date": current_run_date,
        "archive_mutated": False,
    }
    risk_cfg = config.get("risk_prediction", {}) if isinstance(config, dict) else {}
    output_name = risk_cfg.get("longitudinal_output_json", "longitudinal_risk.json")
    (artifacts / output_name).write_text(json.dumps(longitudinal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return longitudinal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--archives-root", required=True)
    parser.add_argument("--person-id", required=True)
    parser.add_argument("--evidence-store", default=str(SKILL_ROOT / "evidence_store"))
    parser.add_argument("--config", default=str(SKILL_ROOT / "config" / "formal.yaml"))
    args = parser.parse_args()

    longitudinal = run_longitudinal_stage(
        artifacts=Path(args.artifacts),
        archives_root=Path(args.archives_root),
        person_id=args.person_id,
        evidence_store=Path(args.evidence_store),
        config_path=Path(args.config),
    )
    print(f"[longitudinal] {longitudinal['summary']}")


if __name__ == "__main__":
    main()
