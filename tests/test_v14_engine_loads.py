"""
冒烟测试 — evidence_store_v14 契约文件齐全可解析 + 引擎可导入
T6: engine-contract smoke tests
"""
import json
import pathlib
import sys


def test_v14_contract_files_parse():
    """5 个引擎契约文件可解析（不抛错即契约齐全）"""
    es = pathlib.Path("evidence_store_v14")
    for f in [
        "assertions/risk_assertions_derived.json",
        "assertions/detection_performance_derived.json",
        "ontology/cancer_age_sex_priors.json",
        "ontology/cancers.json",
        "screening/screening_recommendations.json",
    ]:
        json.loads((es / f).read_text(encoding="utf-8"))


def test_snapshot_module_importable():
    """snapshot_risk 引擎模块可 import（验证无语法错误、依赖齐全）"""
    sys.path.insert(0, "scripts")
    import importlib
    importlib.import_module("snapshot_risk")
