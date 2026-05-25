#!/usr/bin/env python3
"""Render longitudinal_risk.json into longitudinal_risk.html."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DEFAULT = SKILL_ROOT / "templates" / "longitudinal_risk_v3.html"
CONFIG_DEFAULT = SKILL_ROOT / "config" / "formal.yaml"


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _pct(p: float | None) -> str:
    if p is None:
        return "—"
    if p >= 0.01:
        return f"{p * 100:.2f}%"
    return f"{p * 100:.3f}%"


def _summary_grid(longitudinal: dict[str, Any]) -> str:
    s = longitudinal.get("summary", {})
    cards = [
        ("分析癌种总数", s.get("total", 0)),
        ("有多点趋势", s.get("with_trend", 0)),
        ("仅单点（含 single_point/snapshot_only）", s.get("single_point", 0) + s.get("snapshot_only", 0)),
        ("仅本次基线", s.get("baseline_only", 0)),
        ("无可计算 posterior", s.get("no_posterior", 0)),
    ]
    chunks = []
    for label, value in cards:
        chunks.append(
            f'<div class="summary-card"><div class="label">{_esc(label)}</div>'
            f'<div class="value">{_esc(value)}</div></div>'
        )
    return f'<div class="summary-grid">{"".join(chunks)}</div>'


def _baseline_banner(longitudinal: dict[str, Any]) -> str:
    if not longitudinal.get("baseline_only"):
        return ""
    return (
        '<div class="baseline-banner" style="background:#fff8e1;border:1px solid #ffd54f;'
        'padding:12px 16px;border-radius:8px;margin:0 0 16px 0;color:#7a5300;">'
        '<strong>仅单次数据，无法展示趋势</strong>：尚未在档案中找到该用户的历史体检快照。'
        '本次结果已存为基线，下次再上传体检后会自动启用纵向趋势分析。'
        '</div>'
    )


def _trend_pill(trend: str) -> str:
    _ZH = {"rising": "上升", "falling": "下降", "stable": "稳定", "no_history": "无历史", "baseline_only": "仅基线"}
    label = _ZH.get(trend, trend)
    return f'<span class="trend-pill {_esc(trend)}">{_esc(label)}</span>'


def _cancer_card(entry: dict[str, Any]) -> str:
    name = _esc(entry.get("cancer_name_zh") or entry["cancer_id"])
    posterior = _pct(entry.get("current_posterior_probability"))
    trend = entry.get("trend", "no_history")
    if entry.get("current_posterior_probability") is None:
        reason = entry.get("status_reason") or ("不适用（性别不符）" if entry.get("not_applicable") else "无可计算 posterior")
        baseline_note = ""
        if trend == "baseline_only":
            baseline_note = '<div class="empty-note muted">仅基线快照，无历史轨迹可比较。</div>'
        return (
            f'<div class="cancer-card"><h3>{name} {_trend_pill(trend)}</h3>'
            f'<div class="empty-note">{_esc(reason)}</div>{baseline_note}</div>'
        )
    history_rows = []
    for h in entry.get("history", []):
        added = []
        for c in h.get("added_components", []):
            added.append(
                f'{_esc(c.get("factor_id"))}(Δ={c.get("log_odds_delta", 0):+.3f})'
            )
        screening = h.get("screening")
        screening_text = ""
        if screening:
            screening_text = (
                f'{_esc(screening.get("test_id"))}={_esc(screening.get("result"))}'
                f' Δ={screening.get("log_odds_delta", 0):+.3f}'
            )
        added_text = "、".join(added) if added else ""
        if not added_text and not screening_text:
            change_text = '<span class="muted">无新增因子</span>'
        else:
            change_text = "<br>".join(filter(None, [added_text, screening_text]))
        history_rows.append(
            f'<tr><td>{_esc(h.get("exam_date") or "—")}</td>'
            f'<td>{_pct(h.get("posterior_probability"))}</td>'
            f'<td>{_esc(h.get("risk_tier") or "—")}</td>'
            f'<td>{change_text}</td></tr>'
        )
    history_table = (
        '<table class="history-table"><tr><th>时间点</th><th>预测概率</th>'
        '<th>风险等级</th><th>该点新增因子</th></tr>'
        + "".join(history_rows) + "</table>"
    )
    return (
        f'<div class="cancer-card"><h3>{name} {_trend_pill(trend)}'
        f' <span class="muted">当前 posterior={posterior}</span></h3>'
        + history_table
        + "</div>"
    )


def render_longitudinal_html(
    longitudinal: dict[str, Any],
    template_path: Path,
    disclaimer: str,
) -> str:
    template = template_path.read_text(encoding="utf-8")
    person = longitudinal.get("person_context") or {}
    if longitudinal.get("cancers"):
        cards = "".join(_cancer_card(e) for e in longitudinal["cancers"])
    else:
        cards = '<div class="empty-note">本次评估暂无可纵向分析的癌种。</div>'
    banner = _baseline_banner(longitudinal)
    # v6: surface the archive lookup result so the user sees
    # "system found N prior records" vs "fresh person, no history yet".
    lookup = longitudinal.get("archive_lookup") or {}
    if lookup:
        status = lookup.get("status", "unknown")
        files = lookup.get("files", {})
        status_color = {"found": "#155724", "fresh_person": "#856404", "missing_root": "#842029"}.get(status, "#555")
        status_label = {
            "found": "✓ 找到既往档案",
            "fresh_person": "ℹ 该患者首次评估（无既往档案）",
            "missing_root": "ℹ 全新档案根目录",
        }.get(status, status)
        archive_banner = (
            '<div style="background:#f8f9fa;border-left:4px solid '
            f'{status_color};padding:10px 14px;margin:8px 0;font-size:13px;">'
            f'<strong style="color:{status_color};">{_esc(status_label)}</strong>'
            f'<br><span class="muted">person_id={_esc(lookup.get("person_id",""))}'
            f' · 路径 {_esc(lookup.get("person_dir",""))}</span>'
            f'<br><span class="muted">既往因子事件 {files.get("factor_timeline",{}).get("entries",0)} '
            f'· 筛查事件 {files.get("screening_test_timeline",{}).get("entries",0)} '
            f'· 历史 snapshot {files.get("snapshots_dir",{}).get("snapshot_count",0)}</span>'
            '</div>'
        )
    else:
        archive_banner = ""
    replacements = {
        "__PERSON_SEX__": _esc(person.get("sex") or "未知"),
        "__PERSON_AGE__": _esc(person.get("age") if person.get("age") is not None else "—"),
        "__GENERATED_AT__": _esc(datetime.now().strftime("%Y-%m-%d %H:%M")),
        "__SUMMARY_GRID__": _summary_grid(longitudinal),
        "__BASELINE_BANNER__": archive_banner + banner,
        "__CANCER_CARDS__": archive_banner + banner + cards,
        "__DISCLAIMER__": _esc(disclaimer).replace("\n", "<br>"),
    }
    out = template
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--longitudinal", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--template", default=str(TEMPLATE_DEFAULT))
    parser.add_argument("--config", default=str(CONFIG_DEFAULT))
    args = parser.parse_args()

    longitudinal = json.loads(Path(args.longitudinal).read_text(encoding="utf-8"))
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    disclaimer = str((config.get("safety") or {}).get("disclaimer") or "本报告仅用于健康管理参考。")
    html_text = render_longitudinal_html(longitudinal, Path(args.template), disclaimer)
    Path(args.output).write_text(html_text, encoding="utf-8")
    print(f"[longitudinal_html] {len(html_text)} bytes -> {args.output}")


if __name__ == "__main__":
    main()
