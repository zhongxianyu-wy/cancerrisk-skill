"""Apply v1.3 evidence patches to source JSON files."""
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent / "evidence_store"
PATCHES_FILE = BASE / "versions" / "v1.3_evidence_patches.json"

RISK_FACTORS_FILE = BASE / "ontology" / "risk_factors.json"
RISK_ASSERTIONS_FILE = BASE / "assertions" / "risk_assertions.json"
DETECTION_PERF_FILE = BASE / "assertions" / "detection_performance.json"
IMAGING_FINDINGS_FILE = BASE / "ontology" / "imaging_findings.json"

NEW_VERSION = "evidence-v0003"


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {path}")


def apply_risk_factors_add(rf_data, patches):
    existing_ids = {f["factor_id"] for f in rf_data["risk_factors"]}
    added = 0
    for factor in patches["risk_factors_ADD"]:
        fid = factor["factor_id"]
        if fid in existing_ids:
            print(f"  SKIP (already exists): {fid}")
            continue
        rf_data["risk_factors"].append(factor)
        existing_ids.add(fid)
        added += 1
        print(f"  ADD factor: {fid}")
    rf_data["version"] = NEW_VERSION
    return added


def apply_risk_assertions_update(ra_data, patches):
    idx_by_id = {a["assertion_id"]: i for i, a in enumerate(ra_data["assertions"])}
    updated = 0
    for patch in patches["risk_assertions_UPDATE"]:
        target_id = patch["_target_assertion_id"]
        action = patch.get("_action")
        if action != "update_fields":
            print(f"  SKIP (no update_fields action): {target_id}")
            continue
        if target_id not in idx_by_id:
            print(f"  WARN: assertion not found: {target_id}")
            continue
        assertion = ra_data["assertions"][idx_by_id[target_id]]
        update_keys = [k for k in patch if not k.startswith("_")]
        for key in update_keys:
            assertion[key] = patch[key]
        updated += 1
        print(f"  UPDATE assertion: {target_id} ({', '.join(update_keys)})")
    return updated


def apply_risk_assertions_add(ra_data, patches):
    existing_ids = {a["assertion_id"] for a in ra_data["assertions"]}
    added = 0
    for assertion in patches["risk_assertions_ADD"]:
        aid = assertion["assertion_id"]
        if aid in existing_ids:
            print(f"  SKIP (already exists): {aid}")
            continue
        # Remove patch-only keys not in the schema
        clean = {k: v for k, v in assertion.items() if not k.startswith("_")}
        ra_data["assertions"].append(clean)
        existing_ids.add(aid)
        added += 1
        print(f"  ADD assertion: {aid}")
    ra_data["version"] = NEW_VERSION
    return added


def apply_detection_perf_update(dp_data, patches):
    updated = 0
    for patch in patches["detection_performance_UPDATE"]:
        target = patch["_target"]
        t_id, c_id = target["test_id"], target["cancer_id"]
        matched = None
        for test in dp_data["tests"]:
            if test.get("test_id") == t_id and test.get("cancer_id") == c_id:
                matched = test
                break
        if matched is None:
            print(f"  WARN: test not found: {t_id} / {c_id}")
            continue
        update_keys = [k for k in patch if not k.startswith("_")]
        for key in update_keys:
            matched[key] = patch[key]
        updated += 1
        print(f"  UPDATE detection: {t_id}/{c_id} ({', '.join(update_keys)})")
    return updated


def apply_detection_perf_add(dp_data, patches):
    existing = {(t["test_id"], t.get("cancer_id")) for t in dp_data["tests"]}
    added = 0
    for test in patches["detection_performance_ADD"]:
        key = (test["test_id"], test.get("cancer_id"))
        if key in existing:
            print(f"  SKIP (already exists): {key}")
            continue
        clean = {k: v for k, v in test.items() if not k.startswith("_")}
        dp_data["tests"].append(clean)
        existing.add(key)
        added += 1
        print(f"  ADD detection: {test['test_id']}/{test.get('cancer_id')}")
    return added


def apply_imaging_findings_add(imf_data, patches):
    existing_ids = {f["finding_id"] for f in imf_data["findings"]}
    added = 0
    for finding in patches["imaging_findings_ADD"]:
        fid = finding["finding_id"]
        if fid in existing_ids:
            print(f"  SKIP (already exists): {fid}")
            continue
        imf_data["findings"].append(finding)
        existing_ids.add(fid)
        added += 1
        print(f"  ADD finding: {fid}")
    return added


def main():
    patches = load(PATCHES_FILE)

    print("\n=== Phase 1: risk_factors.json ===")
    rf_data = load(RISK_FACTORS_FILE)
    n = apply_risk_factors_add(rf_data, patches)
    save(RISK_FACTORS_FILE, rf_data)
    print(f"  Total added: {n}")

    print("\n=== Phase 2: risk_assertions.json (UPDATE) ===")
    ra_data = load(RISK_ASSERTIONS_FILE)
    n_upd = apply_risk_assertions_update(ra_data, patches)
    print(f"  Total updated: {n_upd}")

    print("\n=== Phase 3: risk_assertions.json (ADD) ===")
    n_add = apply_risk_assertions_add(ra_data, patches)
    save(RISK_ASSERTIONS_FILE, ra_data)
    print(f"  Total added: {n_add}")

    print("\n=== Phase 4: detection_performance.json (UPDATE) ===")
    dp_data = load(DETECTION_PERF_FILE)
    n_upd = apply_detection_perf_update(dp_data, patches)
    print(f"  Total updated: {n_upd}")

    print("\n=== Phase 5: detection_performance.json (ADD) ===")
    n_add = apply_detection_perf_add(dp_data, patches)
    save(DETECTION_PERF_FILE, dp_data)
    print(f"  Total added: {n_add}")

    print("\n=== Phase 6: imaging_findings.json (ADD) ===")
    imf_data = load(IMAGING_FINDINGS_FILE)
    n_add = apply_imaging_findings_add(imf_data, patches)
    save(IMAGING_FINDINGS_FILE, imf_data)
    print(f"  Total added: {n_add}")

    print("\n=== Patch application complete ===")


if __name__ == "__main__":
    main()
