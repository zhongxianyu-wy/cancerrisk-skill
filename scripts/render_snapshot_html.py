#!/usr/bin/env python3
"""Render snapshot_risk.json into snapshot_risk.html (5-section v4.2 layout)."""

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
        return '<span class="tier-pill tier-na">N/A</span>'
    return f'<span class="tier-pill tier-{tier}">{_esc(tier)}</span>'


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
        tier = r.get("risk_tier") or ("不适用" if r.get("not_applicable") else "无prior")
        row_class = f"tier-{r['risk_tier']}" if r.get("risk_tier") else "tier-na"
        prob_text = _pct(r.get("posterior_probability"))
        note = ""
        # v6: imaging-dominated cases need a distinct label so users
        # don't confuse PPV with annual incidence.
        posterior_source = r.get("posterior_source") or {}
        dominant = posterior_source.get("dominant")
        if dominant == "imaging_ppv":
            note = "由影像学发现主导（PPV，非年发病率）"
        elif dominant == "imaging_ppv_no_prior":
            note = "仅影像 PPV 评估（本癌种暂无人群先验）"
        elif r.get("not_applicable"):
            note = "不适用（性别不符）"
        elif r.get("status_reason") == "no_prior_data":
            note = "暂无年龄/性别先验，未计算 posterior"
        rows.append(
            f'<tr class="{row_class}"><td>{_esc(r.get("cancer_name_zh") or r["cancer_id"])}</td>'
            f'<td>{_pct(r.get("prior_probability"))}</td>'
            f'<td>{prob_text}</td>'
            f'<td>{_tier_pill(r.get("risk_tier"))}</td>'
            f'<td class="muted">{_esc(note)}</td></tr>'
        )
    header = (
        '<table><tr><th>癌种</th><th>先验概率（年）</th><th>预测概率</th>'
        '<th>风险等级</th><th>备注</th></tr>'
    )
    return header + "".join(rows) + "</table>"


def _section6_imaging_findings(cancers: list[dict[str, Any]]) -> str:
    """v6: dedicated section listing all imaging PPV findings + the
    dominant-source narrative when PPV beats Bayes."""
    blocks: list[str] = []
    for r in cancers:
        findings = r.get("imaging_findings") or []
        if not findings:
            continue
        ps = r.get("posterior_source") or {}
        # Both imaging_ppv (PPV beats Bayes) and imaging_ppv_no_prior (no Bayes
        # path at all) warrant the dominant card style and narrative display.
        dominant = ps.get("dominant") in {"imaging_ppv", "imaging_ppv_no_prior"}
        header_cls = "imaging-card dominant" if dominant else "imaging-card"
        finding_rows = []
        for f in findings:
            ppv_low, ppv_high = f["malignancy_ppv_range"]
            finding_rows.append(
                f'<li><strong>{_esc(f["finding_name_zh"])}</strong>'
                f' — PPV 参考区间 {ppv_low*100:.0f}-{ppv_high*100:.0f}%'
                f' <span class="muted">[{_esc(f["source_id"])}, 检查日期 {_esc(f["exam_date"])}]</span>'
                f'<br><span class="muted">evidence: {_esc(f["evidence_text"][:120])}</span>'
                f'<br><span class="muted">下一步: {_esc(f.get("next_step", "请专科随诊"))}</span></li>'
            )
        narrative_html = ""
        if dominant and ps.get("narrative"):
            narrative_html = (
                f'<p class="muted" style="margin-top:8px;color:#b34a00;">'
                f'⚠ {_esc(ps["narrative"])}</p>'
            )
        blocks.append(
            f'<div class="{header_cls}"><h3 style="font-size:14.5px;">'
            f'{_esc(r.get("cancer_name_zh"))} '
            f'<span class="muted">(影像 PPV 中位值 {ps.get("imaging_ppv_max", 0)*100:.0f}%, '
            f'Bayes 后验 {_pct(ps.get("bayes_posterior_for_comparison"))})</span></h3>'
            f'<ul>{"".join(finding_rows)}</ul>'
            f'{narrative_html}</div>'
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
        comp_rows = []
        for c in r["components"]:
            cls = "component-row approximation" if c.get("approximation") else "component-row"
            evidence = c.get("evidence_text") or ""
            evidence_display = _esc(evidence[:80] + ("…" if len(evidence) > 80 else ""))
            note_parts = []
            if c.get("approximation"):
                note_parts.append("RR/HR 近似")
            if c.get("exam_date"):
                note_parts.append(f"date={c['exam_date']}")
            if c.get("source"):
                note_parts.append(f"source={c['source']}")
            extra = " · ".join(note_parts)
            comp_rows.append(
                f'<div class="{cls}"><strong>{_esc(c.get("factor_id"))}</strong>'
                f' / level={_esc(c.get("factor_level"))}'
                f' / log_odds_delta={c["log_odds_delta"]:+.3f}'
                f' / OR≈{c.get("calculation_value")} <span class="muted">[{_esc(extra)}]</span><br>'
                f'<span class="muted">evidence: {evidence_display}</span></div>'
            )
        for sc in r.get("screening_contributions", []):
            before = _prob_after_delta(r.get("posterior_log_odds"), -float(sc["log_odds_delta"]))
            after = _prob_after_delta(r.get("posterior_log_odds"), 0.0)
            direction = "降低" if sc.get("result") == "negative" else "升高"
            delta_text = ""
            if before is not None and after is not None:
                delta_text = f" / 筛查后{direction} {abs(before-after)*100:.3f}个百分点"
            comp_rows.append(
                f'<div class="component-row"><strong>{_esc(sc.get("test_name") or sc.get("test_id"))}</strong>'
                f' / result={_esc(sc.get("result"))}'
                f' / LR={sc.get("lr", 0):.2f}'
                f' / log_odds_delta={sc["log_odds_delta"]:+.3f}{_esc(delta_text)}'
                f' <span class="muted">[{_esc(sc.get("source_id"))}]</span></div>'
            )
        ps = r.get("posterior_source") or {}
        if ps.get("narrative"):
            comp_rows.append(
                f'<div class="component-row"><strong>主导依据</strong> '
                f'{_esc(ps.get("dominant"))}<br><span class="muted">{_esc(ps.get("narrative"))}</span></div>'
            )
        if not comp_rows:
            comp_rows.append(
                '<div class="component-row"><strong>基线风险</strong> '
                '未检测到额外风险因子或筛查贡献，本癌种主要由年龄/性别人群先验决定。</div>'
            )
        blocks.append(
            f'<h3 style="font-size:14.5px;margin-top:14px;">{_esc(r.get("cancer_name_zh"))}'
            f' <span class="muted">prior={_pct(r.get("prior_probability"))} · '
            f'posterior={_pct(r.get("posterior_probability"))}</span></h3>'
            + "".join(comp_rows)
        )
    if not blocks:
        return '<div class="empty-note">暂无可展示的重点癌症风险推理。</div>'
    return "<div class=\"section-body\">" + "".join(blocks) + "</div>"


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
        '<tr><th>癌种</th><th>当前风险</th><th>吉早安阴性后风险</th></tr>'
        + rows + '</table>'
    )
    return (
        '<div class="section-body">'
        '<p>如补充吉早安多癌早筛（ctDNA甲基化），若结果为阴性，各癌种风险将调整如下：</p>'
        + table + order_note + '</div>'
    )


def _section4_body(section4: list[dict[str, Any]]) -> str:
    """Legacy probability-tier-filtered screening — kept for back-compat."""
    if not section4:
        return (
            '<div class="empty-note">按当前评估暂无中等及以上风险的癌种，'
            '建议遵循常规体检与个性化健康管理建议。</div>'
        )
    cards = []
    for c in section4:
        plans = []
        for plan in c.get("standard_screening", []):
            plans.append(
                f'<div class="plan"><strong>{_esc(plan.get("method"))}</strong>：'
                f'{_esc(plan.get("population"))} / {_esc(plan.get("interval"))} / '
                f'触发条件：{_esc(plan.get("trigger"))} <span class="muted">[{_esc(plan.get("source_id"))}]</span></div>'
            )
        if not plans:
            plans.append('<div class="plan muted">证据库暂未维护此癌种的标准筛查建议。</div>')
        cards.append(
            f'<div class="cancer-card"><h3>{_esc(c.get("cancer_name_zh"))} {_tier_pill(c.get("risk_tier"))}'
            f' <span class="muted">posterior={_pct(c.get("posterior_probability"))}</span></h3>'
            + "".join(plans) + "</div>"
        )
    return "".join(cards)


def _section7_voi(voi_output: dict[str, Any], cancers: list[dict[str, Any]] | None = None) -> str:
    """v6: VoI-ranked screening recommendations (v4.2 methodology).

    For cancers that have imaging PPV findings but no prior (e.g.
    thyroid_cancer), the VoI loop produces nothing — link the user
    back to Section 6 explicitly so they don't think "the system
    didn't see my thyroid nodule".
    """
    # Defensive: orchestrator may not have written voi_ranking.json yet
    # on an interim re-run; surface a clean note instead of KeyError.
    if not isinstance(voi_output, dict):
        voi_output = {}
    all_rankings = voi_output.get("rankings", [])

    # Partition: liquid-biopsy (multi-cancer) always shown; single-cancer filtered.
    liquid_rankings = [r for r in all_rankings if r.get("is_liquid_biopsy")]
    single_rankings = [r for r in all_rankings if not r.get("is_liquid_biopsy")]

    posterior_map: dict[str, float] = {
        c["cancer_id"]: float(c.get("posterior_probability") or 0)
        for c in (cancers or [])
        if c.get("cancer_id")
    }
    THRESHOLD = 0.005  # 0.5%
    qualified = [r for r in single_rankings if posterior_map.get(r.get("cancer_id", ""), 0) >= THRESHOLD]
    if len(qualified) < 3:
        qualified = sorted(
            single_rankings,
            key=lambda r: posterior_map.get(r.get("cancer_id", ""), 0),
            reverse=True,
        )[:3]
    rankings = liquid_rankings + qualified

    # Build "see Section 6" reminders for any cancer with imaging PPV
    # but no entry in the VoI ranking (typically: missing_priors cancers).
    voi_cancer_ids: set[str] = set()
    for r in rankings:
        cid = r.get("cancer_id", "")
        for piece in cid.split(","):
            voi_cancer_ids.add(piece.strip())
    cross_ref: list[str] = []
    for c in cancers or []:
        if c.get("imaging_findings") and c["cancer_id"] not in voi_cancer_ids:
            cross_ref.append(
                f'<li><strong>{_esc(c.get("cancer_name_zh"))}</strong>'
                f'：影像 PPV 路径已评估（详见第六节"影像学发现"）；'
                f'本节因缺少人群先验或筛查方案数据未排序，临床处置以影像评级 + 活检/专科会诊为主。</li>'
            )
    cross_ref_html = ""
    if cross_ref:
        cross_ref_html = (
            '<div class="empty-note" style="margin-top:8px;border-left:3px solid #b34a00;background:#fff8e1;">'
            '<strong>⚠ 仅 PPV 路径评估（不在 VoI 排序内）：</strong>'
            '<ul style="margin-top:4px;padding-left:18px;">' + "".join(cross_ref) + '</ul>'
            '</div>'
        )
    if not rankings:
        return ('<div class="empty-note">暂无可评估的筛查方案 VoI（缺少先验/生存/灵敏度数据）。</div>'
                + cross_ref_html)
    rec_color = {"强烈推荐": "#842029", "推荐": "#856404", "可考虑": "#0c5460", "常规": "#6c757d"}
    cards = []
    for r in rankings:
        color = rec_color.get(r["recommendation"], "#6c757d")
        bd = ""
        if r.get("is_liquid_biopsy") and r.get("multi_cancer_breakdown"):
            rows = "".join(
                f'<tr><td>{_esc(b["cancer_name_zh"])}</td>'
                f'<td>{b["incidence_rate_per_100k"]:.2f}/100k</td>'
                f'<td>{b["survival_gain_5y"]:.1f}%</td>'
                f'<td>{b["sensitivity"]*100:.1f}%</td>'
                f'<td>+{b["voi_contribution"]:.2f}</td></tr>'
                for b in r["multi_cancer_breakdown"]
            )
            bd = (
                '<table style="margin-top:6px;font-size:12px;width:100%;">'
                '<tr><th>癌种</th><th>发病率</th><th>5年生存差</th><th>灵敏度</th><th>VoI贡献</th></tr>'
                + rows + '</table>'
            )
        cards.append(
            f'<div class="voi-card">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<strong>{_esc(r["method"])}</strong>'
            f'<span style="color:{color};font-weight:600;">VoI {r["voi_score"]:.2f} · {r["recommendation"]}</span>'
            f'</div>'
            f'<div class="muted" style="font-size:12.5px;margin-top:4px;">'
            f'目标癌种: {_esc(r["cancer_name_zh"])} · 灵敏度 {r["sensitivity"]*100:.1f}% · '
            f'特异度 {r["specificity"]*100:.1f}% · 费用 ¥{r["cost_rmb"]} · '
            f'{_esc(r["invasiveness"])} · {_esc(r.get("guideline", ""))}</div>'
            f'{bd}'
            f'</div>'
        )
    return (
        '<p class="muted" style="margin-bottom:8px;font-size:13px;">'
        f'公式：{_esc(voi_output.get("formula",""))}<br>'
        f'分级阈值：≥20 强烈推荐 / 10-20 推荐 / 5-10 可考虑 / &lt;5 常规'
        '</p>'
        + "".join(cards)
        + cross_ref_html
    )


def _section5_body(snapshot: dict[str, Any]) -> str:
    summary = snapshot.get("uncertainties_summary", {})
    items: list[str] = []
    missing = summary.get("cancers_missing_prior", [])
    not_applicable = summary.get("cancers_not_applicable", [])
    approx_count = summary.get("approximation_components", 0)
    if missing:
        items.append(f"<li>缺少先验概率而未计算的癌种：{_esc('、'.join(missing))}（需补充 incidence 数据）</li>")
    if not_applicable:
        items.append(f"<li>性别不适用的癌种：{_esc('、'.join(not_applicable))}</li>")
    if approx_count:
        items.append(f"<li>使用 RR/HR 近似换算 log-odds 的组件数：{approx_count}（已标记 approximation）</li>")
    detail_items: list[str] = []
    for cancer in snapshot.get("cancers", []):
        for u in cancer.get("uncertainties", []):
            detail_items.append(
                f"<li>{_esc(cancer.get('cancer_name_zh'))}: {_esc(u.get('reason'))} "
                f"<span class='muted'>{_esc(u.get('detail') or u.get('factor_id') or u.get('assertion_id') or '')}</span></li>"
            )
    body_chunks: list[str] = []
    if items:
        body_chunks.append("<ul>" + "".join(items) + "</ul>")
    if detail_items:
        body_chunks.append("<details><summary>展开按癌种的不确定性条目</summary><ul>" + "".join(detail_items) + "</ul></details>")
    if not body_chunks:
        body_chunks.append('<div class="empty-note">本次预测未发现额外不确定性来源。</div>')
    body_chunks.append(
        '<p class="muted" style="margin-top:10px;">本节同时承载“证据库外异常提示”：'
        '体检中存在但不在本体证据库中的发现（如甲状腺结节、ALT 升高等）不参与概率推断，'
        '请结合健康总结报告与临床随访意见处理。</p>'
    )
    return "<div class=\"section-body\">" + "".join(body_chunks) + "</div>"


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
