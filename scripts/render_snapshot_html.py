#!/usr/bin/env python3
"""Render snapshot_risk.json into snapshot_risk.html (v4.2 layout)."""

from __future__ import annotations

import argparse
import html
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DEFAULT = SKILL_ROOT / "templates" / "snapshot_risk_v42.html"
CONFIG_DEFAULT = SKILL_ROOT / "config" / "formal.yaml"
CONTACT_DEFAULT = SKILL_ROOT / "config" / "contact.json"

_TIER_ZH = {
    "high": "高风险", "medium": "中风险", "low": "低风险",
    "urgent_workup": "高风险", "high_workup": "高风险", "moderate_workup": "中风险",
}
_TIER_CSS = {
    "urgent_workup": "high", "high_workup": "high", "moderate_workup": "medium",
}


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _pct(p: float | None) -> str:
    if p is None:
        return "—"
    if p >= 0.01:
        return f"{p * 100:.2f}%"
    return f"{p * 100:.3f}%"


def _tier_pill(tier: str | None) -> str:
    if not tier:
        return '<span class="tier-pill tier-na">不适用</span>'
    label = _TIER_ZH.get(tier, tier)
    css_cls = _TIER_CSS.get(tier, tier)
    return f'<span class="tier-pill tier-{_esc(css_cls)}">{_esc(label)}</span>'


def _focus_cancers(cancers: list[dict[str, Any]], *, top_n: int = 3, include_above: float = 0.02) -> list[dict[str, Any]]:
    eligible = [
        c for c in cancers
        if c.get("posterior_probability") is not None and not c.get("not_applicable")
    ]
    eligible.sort(key=lambda c: (-(c.get("posterior_probability") or 0.0), c.get("cancer_id", "")))
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for c in eligible[:top_n]:
        selected.append(c)
        seen.add(c.get("cancer_id", ""))
    for c in eligible:
        if c.get("cancer_id") not in seen and float(c.get("posterior_probability") or 0) > include_above:
            selected.append(c)
            seen.add(c.get("cancer_id", ""))
    return selected


def _prob_after_delta(base_log_odds: float | None, delta: float) -> float | None:
    if base_log_odds is None:
        return None
    x = base_log_odds + delta
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _section1_table(cancers: list[dict[str, Any]]) -> str:
    rows = []
    for r in cancers:
        row_class = f"tier-{r['risk_tier']}" if r.get("risk_tier") else "tier-na"
        prob_text = _pct(r.get("posterior_probability"))
        note = ""
        posterior_source = r.get("posterior_source") or {}
        dominant = posterior_source.get("dominant")
        if dominant in {"imaging_ppv", "imaging_ppv_protective_adjusted"}:
            note = "由影像学发现主导（PPV，非年发病率）"
        elif dominant == "imaging_ppv_no_prior":
            note = "仅影像 PPV 评估（本癌种暂无人群先验）"
        elif r.get("not_applicable"):
            note = "不适用（性别不符）"
        elif r.get("status_reason") == "no_prior_data":
            note = "暂无年龄/性别先验，未计算后验概率"
        rows.append(
            f'<tr class="{row_class}"><td>{_esc(r.get("cancer_name_zh") or r["cancer_id"])}</td>'
            f'<td>{_pct(r.get("prior_probability"))}</td>'
            f'<td>{prob_text}</td>'
            f'<td>{_tier_pill(r.get("risk_tier"))}</td>'
            f'<td class="muted">{_esc(note)}</td></tr>'
        )
    header = (
        '<table><tr><th>癌种</th><th>先验概率（年）</th><th>后验概率</th>'
        '<th>风险等级</th><th>备注</th></tr>'
    )
    return header + "".join(rows) + "</table>"


def _section6_imaging_findings(cancers: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for r in cancers:
        findings = r.get("imaging_findings") or []
        if not findings:
            continue
        ps = r.get("posterior_source") or {}
        dominant = ps.get("dominant") in {"imaging_ppv", "imaging_ppv_no_prior", "imaging_ppv_protective_adjusted"}
        header_cls = "imaging-card dominant" if dominant else "imaging-card"
        finding_rows = []
        for f in findings:
            ppv_low, ppv_high = f["malignancy_ppv_range"]
            finding_rows.append(
                f'<li><strong>{_esc(f["finding_name_zh"])}</strong>'
                f' — PPV 参考区间 {ppv_low*100:.0f}–{ppv_high*100:.0f}%'
                f' <span class="muted">[{_esc(f["source_id"])}, 检查日期 {_esc(f["exam_date"])}]</span>'
                f'<br><span class="muted">依据：{_esc(f["evidence_text"][:120])}</span>'
                f'<br><span class="muted">下一步: {_esc(f.get("next_step", "请专科随诊"))}</span></li>'
            )
        blocks.append(
            f'<div class="{header_cls}"><h3 style="font-size:14.5px;">'
            f'{_esc(r.get("cancer_name_zh"))} '
            f'<span class="muted">(影像 PPV 中位值 {ps.get("imaging_ppv_max", 0)*100:.0f}%)</span></h3>'
            f'<ul>{"".join(finding_rows)}</ul>'
            f'</div>'
        )
    if not blocks:
        return '<div class="empty-note">本次未提交任何已分级的影像学疑似病灶。</div>'
    return '<div class="section-body">' + "".join(blocks) + '</div>'


def _section2_body(cancers: list[dict[str, Any]], section_filter: dict[str, Any] | None = None) -> str:
    blocks = []
    section_filter = section_filter or {}
    focus = _focus_cancers(
        cancers,
        top_n=int(section_filter.get("top_n", 3)),
        include_above=float(section_filter.get("include_probability_above", 0.02)),
    )
    for r in focus:
        ps = r.get("posterior_source") or {}
        dominant = ps.get("dominant", "")
        imaging_dominated = dominant in {"imaging_ppv", "imaging_ppv_protective_adjusted", "imaging_ppv_no_prior"}

        comp_rows = []

        if imaging_dominated:
            # Imaging-dominated: only show PPV range, skip Bayesian chain
            findings = r.get("imaging_findings") or []
            ppv_lines = []
            for f in findings:
                lo, hi = f["malignancy_ppv_range"]
                ppv_lines.append(
                    f'<li><strong>{_esc(f["finding_name_zh"])}</strong>'
                    f' — 恶性 PPV 参考区间 {lo*100:.0f}–{hi*100:.0f}%'
                    f' <span class="muted">[{_esc(f["source_id"])}]</span></li>'
                )
            ppv_html = ('<ul style="margin:6px 0 0 0;">' + "".join(ppv_lines) + '</ul>') if ppv_lines else ""
            ppv_max = ps.get("imaging_ppv_max", 0)
            comp_rows.append(
                f'<div class="component-row" style="background:#fff8e1;border-left:3px solid #b34a00;">'
                f'<strong>⚠ 影像学主导</strong>：本癌种后验概率由影像发现的 PPV 决定'
                f'（影像 PPV 中位值 <strong>{ppv_max*100:.0f}%</strong>），'
                f'不使用 Bayes 因子累积链。{ppv_html}</div>'
            )
        else:
            # Standard Bayesian chain
            prior_lo = r.get("prior_log_odds")
            running_lo = prior_lo

            comp_rows.append(
                f'<div class="component-row">'
                f'<strong>起始：人群基线</strong> '
                f'年龄/性别先验 → <strong>{_pct(r.get("prior_probability"))}</strong>'
                f'</div>'
            )

            for c in r.get("components", []):
                delta = c["log_odds_delta"]
                arrow = "↑ 升高风险" if delta > 0 else "↓ 降低风险"
                factor_label = _esc(c.get("factor_name_zh") or c.get("factor_id") or "")
                level_label = _esc(c.get("factor_level") or "")
                approx_mark = " <span class='muted'>（RR近似）</span>" if c.get("approximation") else ""
                evidence = c.get("evidence_text") or ""
                ev_display = _esc(evidence[:80] + ("…" if len(evidence) > 80 else ""))
                if running_lo is not None:
                    running_lo = running_lo + delta
                    prob_after = _prob_after_delta(running_lo, 0.0)
                    prob_str = f"→ 累计风险 <strong>{_pct(prob_after)}</strong>"
                    or_val = math.exp(abs(delta))
                    or_str = f"OR≈{or_val:.2f}"
                else:
                    prob_str = ""
                    or_str = ""
                comp_rows.append(
                    f'<div class="component-row">'
                    f'<strong>{factor_label}</strong>（{level_label}）{approx_mark} '
                    f'<span class="muted">{arrow}，{or_str}</span> {prob_str}'
                    f'<br><span class="muted">依据：{ev_display}</span>'
                    f'</div>'
                )

            for sc in r.get("screening_contributions", []):
                delta = float(sc["log_odds_delta"])
                result_zh = "阴性（保护）" if sc.get("result") == "negative" else "阳性（风险升高）"
                test_label = _esc(sc.get("test_name") or sc.get("test_id") or "")
                if running_lo is not None:
                    running_lo = running_lo + delta
                    prob_after = _prob_after_delta(running_lo, 0.0)
                    prob_str = f"→ 累计风险 <strong>{_pct(prob_after)}</strong>"
                else:
                    prob_str = ""
                comp_rows.append(
                    f'<div class="component-row">'
                    f'<strong>{test_label}</strong> 检测结果：{result_zh} '
                    f'<span class="muted">LR={sc.get("lr", 0):.2f}</span> {prob_str}'
                    f'<br><span class="muted">来源：{_esc(sc.get("source_id") or "")}</span>'
                    f'</div>'
                )

            if len(comp_rows) <= 1:
                comp_rows.append(
                    '<div class="component-row"><strong>基线风险</strong> '
                    '未检测到额外风险因子或筛查贡献，本癌种主要由年龄/性别人群先验决定。</div>'
                )

        blocks.append(
            f'<h3 style="font-size:14.5px;margin-top:14px;">{_esc(r.get("cancer_name_zh"))}'
            f' {_tier_pill(r.get("risk_tier"))}'
            f' <span class="muted">后验概率 {_pct(r.get("posterior_probability"))}</span></h3>'
            + "".join(comp_rows)
        )
    if not blocks:
        return '<div class="empty-note">暂无可展示的重点癌症风险推理。</div>'
    return '<div class="section-body">' + "".join(blocks) + "</div>"


def _section3_body(snapshot: dict[str, Any], contact: dict[str, Any] | None = None) -> str:
    tests = snapshot.get("convenient_screening", {}).get("results", [])
    contact = contact or {}
    hotline = (contact.get("hotline") or {}) if isinstance(contact, dict) else {}
    phone = hotline.get("number", "400-166-6506")
    hours = hotline.get("hours", "")
    order_note = (
        f'<p class="muted" style="margin-top:8px;">吉早安订购电话：'
        f'<strong>{_esc(phone)}</strong>{("（" + _esc(hours) + "）") if hours else ""}</p>'
    )
    if tests:
        return (
            '<div class="section-body">'
            '<p>✅ 已完成吉早安检测，当前风险为矫正后的风险。</p>'
            + order_note + '</div>'
        )
    whatif = snapshot.get("jizaoan_whatif", [])
    if not whatif:
        return (
            '<div class="empty-note">未提供吉早安多癌早筛结果；证据库中无该测试的检出性能数据。</div>'
            + order_note
        )
    rows = "".join(
        f'<tr><td>{_esc(w["cancer_name_zh"])}</td>'
        f'<td>{_pct(w["current_risk"])}</td>'
        f'<td>{_pct(w["risk_if_negative"])}</td></tr>'
        for w in whatif
    )
    table = (
        '<table style="width:100%;margin-top:8px;">'
        '<tr><th>癌种</th><th>当前后验概率</th><th>吉早安阴性后概率</th></tr>'
        + rows + '</table>'
    )
    return (
        '<div class="section-body">'
        '<p>如补充吉早安多癌早筛（ctDNA甲基化），若结果为阴性，各癌种风险将调整如下：</p>'
        + table + order_note + '</div>'
    )


def _section4_body(section4: list[dict[str, Any]]) -> str:
    if not section4:
        return '<div class="empty-note">暂无筛查推荐数据（重点癌种均超出证据库筛查覆盖范围）。</div>'
    blocks = []
    for entry in section4:
        name = _esc(entry.get("cancer_name_zh") or entry.get("cancer_id", ""))
        tier_html = _tier_pill(entry.get("risk_tier"))
        prob_text = _pct(entry.get("posterior_probability"))
        methods = entry.get("standard_screening") or []
        if not methods:
            method_html = '<p class="muted" style="margin-top:6px;">证据库中暂无该癌种的标准筛查方案。</p>'
        else:
            rows = "".join(
                f'<tr>'
                f'<td><strong>{_esc(m.get("method", ""))}</strong></td>'
                f'<td class="muted">{_esc(m.get("population", ""))}</td>'
                f'<td>{_esc(m.get("interval", ""))}</td>'
                f'</tr>'
                for m in methods
            )
            method_html = (
                '<table style="margin-top:8px;"><tr>'
                '<th>筛查方式</th><th>适用人群</th><th>频率</th></tr>'
                + rows + '</table>'
            )
        blocks.append(
            f'<div style="border:1px solid #e1e8ef;border-radius:10px;'
            f'padding:14px 16px;margin-bottom:12px;background:#fff;">'
            f'<div style="font-size:15px;font-weight:600;margin-bottom:4px;">'
            f'{name} {tier_html} '
            f'<span class="muted" style="font-size:13px;font-weight:normal;">后验概率 {prob_text}</span></div>'
            + method_html +
            f'</div>'
        )
    return '<div class="section-body">' + "".join(blocks) + '</div>'


def _section7_voi(voi_output: dict[str, Any], cancers: list[dict[str, Any]] | None = None) -> str:
    """筛查方案推荐：VoI 定义 + 深入筛查策略 + 便捷式筛查策略。"""
    if not isinstance(voi_output, dict):
        voi_output = {}
    all_rankings = voi_output.get("rankings", [])

    liquid_rankings = [r for r in all_rankings if r.get("is_liquid_biopsy")]
    single_rankings = [r for r in all_rankings if not r.get("is_liquid_biopsy")]

    # Focus cancers = same set as section 2
    focus_ids: set[str] = {
        c["cancer_id"] for c in _focus_cancers(cancers or [])
        if c.get("cancer_id")
    }
    # Deep strategy: single-cancer methods for focus cancers, sorted by VoI desc
    deep = sorted(
        [r for r in single_rankings if r.get("cancer_id", "") in focus_ids],
        key=lambda r: r.get("voi_score", 0),
        reverse=True,
    )
    # Fallback: if focus_ids empty or none match, show top-3 single methods
    if not deep:
        deep = sorted(single_rankings, key=lambda r: r.get("voi_score", 0), reverse=True)[:3]

    posterior_map: dict[str, float] = {
        c["cancer_id"]: float(c.get("posterior_probability") or 0)
        for c in (cancers or []) if c.get("cancer_id")
    }
    tier_map: dict[str, str] = {
        c["cancer_id"]: c.get("risk_tier", "")
        for c in (cancers or []) if c.get("cancer_id")
    }

    rec_color = {"强烈推荐": "#842029", "推荐": "#856404", "可考虑": "#0c5460", "常规": "#6c757d"}

    def _voi_card(r: dict[str, Any]) -> str:
        color = rec_color.get(r.get("recommendation", ""), "#6c757d")
        cid = r.get("cancer_id", "")
        post = posterior_map.get(cid)
        tier = tier_map.get(cid, "")
        meta_parts = [
            f'灵敏度 {r["sensitivity"]*100:.0f}%',
            f'特异度 {r["specificity"]*100:.0f}%',
        ]
        if r.get("cost_rmb"):
            meta_parts.append(f'费用 ¥{r["cost_rmb"]}')
        if post is not None:
            meta_parts.insert(0, f'后验概率 {_pct(post)}')
        if tier:
            meta_parts.insert(1, f'风险等级 {_TIER_ZH.get(tier, tier)}')
        bd = ""
        if r.get("is_liquid_biopsy") and r.get("multi_cancer_breakdown"):
            rows = "".join(
                f'<tr><td>{_esc(b["cancer_name_zh"])}</td>'
                f'<td>{b["survival_gain_5y"]:.1f}%</td>'
                f'<td>{b["sensitivity"]*100:.0f}%</td>'
                f'<td>{b["voi_contribution"]:.2f}</td></tr>'
                for b in r["multi_cancer_breakdown"]
            )
            bd = (
                '<table style="margin-top:6px;font-size:12px;width:100%;">'
                '<tr><th>癌种</th><th>5年生存差</th><th>灵敏度</th><th>VoI贡献</th></tr>'
                + rows + '</table>'
            )
        return (
            f'<div class="voi-card" style="margin-bottom:10px;padding:10px 14px;'
            f'border:1px solid #ddd;border-radius:6px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<strong>{_esc(r["method"])}</strong>'
            f'<span style="color:{color};font-weight:600;">'
            f'VoI {r["voi_score"]:.2f} · {_esc(r.get("recommendation",""))}</span>'
            f'</div>'
            f'<div class="muted" style="font-size:12.5px;margin-top:4px;">'
            f'目标癌种：{_esc(r["cancer_name_zh"])} · '
            + " · ".join(_esc(p) for p in meta_parts) +
            f'</div>'
            f'{bd}'
            f'</div>'
        )

    # VoI definition block
    definition_html = (
        '<div style="background:#f0f7ff;border-left:4px solid #2979ff;'
        'padding:10px 14px;border-radius:4px;margin-bottom:14px;font-size:13px;">'
        '<strong>筛查获益评分（VoI）说明</strong>：'
        '综合检测灵敏度、癌症不同分期生存率差异及个体预测发病率，对目标筛查技术进行评分，'
        '评分高低反映该筛查手段对本人的预期健康获益大小。'
        '<br><span class="muted" style="font-size:12px;">'
        '计算公式：（I期5年生存率 − IV期5年生存率）× 5 × 365 × 检测灵敏度 × 个体后验概率'
        '<br>分级：≥10 强烈推荐 / 2.5–10 推荐 / 1–2.5 可考虑 / &lt;1 常规'
        '</span></div>'
    )

    # Deep strategy section
    if deep:
        deep_cards = "".join(_voi_card(r) for r in deep)
        deep_html = (
            '<h4 style="margin:12px 0 6px;font-size:14px;">深入筛查策略</h4>'
            '<p class="muted" style="font-size:12.5px;margin-bottom:8px;">'
            '以下为本次重点癌种的临床推荐筛查手段，按 VoI 从高到低排序：</p>'
            + deep_cards
        )
    else:
        deep_html = (
            '<h4 style="margin:12px 0 6px;font-size:14px;">深入筛查策略</h4>'
            '<div class="empty-note">暂无可评估的临床筛查方案（缺少先验/生存/灵敏度数据）。</div>'
        )

    # Convenient strategy section (吉早安)
    if liquid_rankings:
        conv_cards = "".join(_voi_card(r) for r in liquid_rankings)
        conv_html = (
            '<h4 style="margin:16px 0 6px;font-size:14px;">便捷式筛查策略</h4>'
            '<p class="muted" style="font-size:12.5px;margin-bottom:8px;">'
            '吉早安多癌早筛（ctDNA甲基化液体活检），一次采血覆盖多癌种：</p>'
            + conv_cards
        )
    else:
        conv_html = (
            '<h4 style="margin:16px 0 6px;font-size:14px;">便捷式筛查策略</h4>'
            '<div class="empty-note">暂无吉早安 VoI 数据（证据库未覆盖本次癌种或缺少灵敏度数据）。</div>'
        )

    return definition_html + deep_html + conv_html


def render_snapshot_html(
    snapshot: dict[str, Any],
    template_path: Path,
    disclaimer: str,
    evidence_version: str | None,
    voi_output: dict[str, Any] | None = None,
    contact: dict[str, Any] | None = None,
) -> str:
    template = template_path.read_text(encoding="utf-8")
    person = snapshot.get("person_context", {})
    section4_filter = snapshot.get("section4_filter", {})
    if voi_output is not None:
        snapshot = {**snapshot, "voi_output": voi_output}
    replacements = {
        "__PERSON_SEX__": _esc(person.get("sex") or "未知"),
        "__PERSON_AGE__": _esc(person.get("age") if person.get("age") is not None else "—"),
        "__GENERATED_AT__": _esc(datetime.now().strftime("%Y-%m-%d %H:%M")),
        "__EVIDENCE_VERSION__": _esc(evidence_version or "—"),
        "__SECTION1_TABLE__": _section1_table(snapshot.get("cancers", [])),
        "__SECTION2_BODY__": _section2_body(snapshot.get("cancers", []), section4_filter),
        "__SECTION3_BODY__": _section3_body(snapshot, contact),
        "__SECTION4_BODY__": _section4_body(snapshot.get("section4_screening", [])),
        "__SECTION4_TOP_N__": _esc(section4_filter.get("top_n", 3)),
        "__SECTION5_BODY__": _section5_body(snapshot),
        "__SECTION6_BODY__": _section6_imaging_findings(snapshot.get("cancers", [])),
        "__SECTION7_BODY__": _section7_voi(snapshot.get("voi_output", {}), snapshot.get("cancers", [])),
        "__DISCLAIMER__": _esc(disclaimer).replace("\n", "<br>"),
    }
    out = template
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, help="path to snapshot_risk.json")
    parser.add_argument("--output", required=True, help="path to write snapshot_risk.html")
    parser.add_argument("--template", default=str(TEMPLATE_DEFAULT))
    parser.add_argument("--config", default=str(CONFIG_DEFAULT))
    parser.add_argument("--contact-config", default=str(CONTACT_DEFAULT))
    parser.add_argument("--evidence-version", default=None)
    args = parser.parse_args()

    snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    try:
        contact = json.loads(Path(args.contact_config).read_text(encoding="utf-8")) if args.contact_config else {}
    except (FileNotFoundError, json.JSONDecodeError):
        contact = {}
    disclaimer = str((config.get("safety") or {}).get("disclaimer") or "本报告仅用于健康管理参考。")
    html_text = render_snapshot_html(snapshot, Path(args.template), disclaimer, args.evidence_version, contact=contact)
    Path(args.output).write_text(html_text, encoding="utf-8")
    print(f"[snapshot_html] {len(html_text)} bytes -> {args.output}")


if __name__ == "__main__":
    main()
