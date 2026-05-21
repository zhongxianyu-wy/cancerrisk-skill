#!/usr/bin/env python3
"""Task9 router index renderer.

The index page is a routing surface: it summarises the run (status,
counts, audit pointer) and links to the three business reports. It
deliberately does not repeat the cancer-name × posterior table, the ADR
score, or any other business conclusion — those live in their own
reports so a regression here cannot leak through to the user.
"""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DEFAULT = SKILL_ROOT / "templates" / "index_v3.html"
CONFIG_DEFAULT = SKILL_ROOT / "config" / "formal.yaml"


REPORT_DESCRIPTIONS = {
    "health_summary.html": "健康总结：体检要点 + 健康管理评估",
    "snapshot_risk.html": "快照式癌症风险预测（含筛查推荐）",
    "longitudinal_risk.html": "纵向癌症风险趋势（所有可评估癌种）",
}


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _status_pill(status: str) -> str:
    cls = status if status in {"success", "partial", "fail"} else "partial"
    label = {"success": "✅ 成功", "partial": "⚠️ 部分成功", "fail": "❌ 失败"}[cls]
    return f'<span class="status-pill {cls}">{label}</span>'


def _summary_grid(manifest: dict[str, Any]) -> str:
    snapshot = manifest.get("task7_snapshot", {})
    longitudinal = manifest.get("task8_longitudinal", {})
    mineru = manifest.get("mineru", {})
    cards = [
        ("MinerU 状态", _esc(mineru.get("status") or "—")),
        ("处理文件数", _esc(mineru.get("file_count", 0))),
        ("可计算癌种", _esc(snapshot.get("cancers_scored", 0))),
        ("纵向多点趋势癌种", _esc(longitudinal.get("with_trend", 0))),
        ("筛查推荐数（Section 4）", _esc(snapshot.get("section4_count", 0))),
    ]
    chunks = []
    for label, value in cards:
        chunks.append(
            f'<div class="summary-card"><div class="label">{_esc(label)}</div>'
            f'<div class="value">{value}</div></div>'
        )
    return f'<div class="summary-grid">{"".join(chunks)}</div>'


def _report_cards(manifest: dict[str, Any]) -> str:
    cards: list[str] = []
    output_dir = Path(manifest.get("output_dir", ""))
    for name in ("health_summary.html", "snapshot_risk.html", "longitudinal_risk.html"):
        target = output_dir / name
        desc = REPORT_DESCRIPTIONS.get(name, name)
        if target.is_file():
            cards.append(
                f'<a class="report-card" href="{_esc(name)}"><div>'
                f'<div class="name">{_esc(name)}</div>'
                f'<div class="desc">{_esc(desc)}</div></div>'
                f'<div class="arrow">→</div></a>'
            )
        else:
            cards.append(
                f'<div class="report-card missing"><div>'
                f'<div class="name">{_esc(name)}（未生成）</div>'
                f'<div class="desc">{_esc(desc)}</div></div>'
                f'<div class="arrow">→</div></div>'
            )
    return "".join(cards)


def _quality_body(manifest: dict[str, Any]) -> str:
    audit_items: list[str] = []
    for note in manifest.get("audit_notes", []):
        audit_items.append(f'<li><span class="muted">{_esc(note.get("name"))}</span></li>')
    audit_block = ("<ul>" + "".join(audit_items) + "</ul>") if audit_items else '<div class="muted">本次运行无 audit 笔记。</div>'

    failure_block = ""
    failures = manifest.get("failures") or []
    if failures:
        failure_block = (
            '<div style="background:#f8d7da;color:#842029;padding:10px 12px;border-radius:8px;'
            'margin-bottom:10px;font-size:13px;">⚠️ 失败项：'
            + ", ".join(_esc(x) for x in failures) + "</div>"
        )

    archive = manifest.get("task8_archive", {})
    archive_text = (
        f'<p class="muted">个人档案目录：{_esc(archive.get("person_archive_dir"))} '
        f'· 本次写入因子事件 {_esc(archive.get("factor_events_added", 0))} 条 '
        f'· 筛查事件 {_esc(archive.get("screening_events_added", 0))} 条</p>'
    )
    return failure_block + archive_text + "<h3 style=\"font-size:13.5px;margin-top:10px;\">Module audits</h3>" + audit_block


def render_index_html(manifest: dict[str, Any], template_path: Path, disclaimer: str) -> str:
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "__RUN_ID__": _esc(manifest.get("run_id")),
        "__STATUS_PILL__": _status_pill(manifest.get("status", "partial")),
        "__GENERATED_AT__": _esc(manifest.get("generated_at") or datetime.now().isoformat(timespec="seconds")),
        "__EVIDENCE_VERSION__": _esc(manifest.get("evidence_version") or "—"),
        "__SUMMARY_GRID__": _summary_grid(manifest),
        "__REPORT_CARDS__": _report_cards(manifest),
        "__QUALITY_BODY__": _quality_body(manifest),
        "__DISCLAIMER__": _esc(disclaimer).replace("\n", "<br>"),
    }
    out = template
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--template", default=str(TEMPLATE_DEFAULT))
    parser.add_argument("--config", default=str(CONFIG_DEFAULT))
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    disclaimer = str((config.get("safety") or {}).get("disclaimer") or "本报告仅用于健康管理参考。")
    html_text = render_index_html(manifest, Path(args.template), disclaimer)
    Path(args.output).write_text(html_text, encoding="utf-8")
    print(f"[index] {len(html_text)} bytes -> {args.output}")


if __name__ == "__main__":
    main()
