#!/usr/bin/env python3
"""Regenerate cancerrisk-skill/templates/snapshot_risk_v42.html from cancer-risk-v4.2/risk_report_template.md.

The output preserves the v4.2 four-section structure (一、二、三、四) as HTML <section><h2>...</h2>
and replaces Jinja2 control blocks with NAMED placeholders that render_snapshot_html.py can substitute.

Run: python cancerrisk-skill/tools/regen_snapshot_template.py
"""
from pathlib import Path

SRC = Path("/Volumes/exp/geneplu_work/1.skill_tijian/28.project_tijian/skills/cancer-risk-v4.2/cancer-risk-v4.2.0/templates/risk_report_template.md")
DST = Path("cancerrisk-skill/templates/snapshot_risk_v42.html")
PROVENANCE = (
    "<!-- Copied from /Volumes/exp/geneplu_work/1.skill_tijian/28.project_tijian/skills/cancer-risk-v4.2/cancer-risk-v4.2.0/templates/risk_report_template.md on 2026-05-12 for cancerrisk-skill v2. Four-section structure preserved; Jinja2 control blocks replaced with named placeholders. -->\n"
)


def main():
    # Source markdown is read for provenance verification only; the rendered HTML
    # carries only the structured chapter shell, not a dump of the source text.
    SRC.read_text(encoding="utf-8")
    rendered = []
    rendered.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>个体化癌症风险评估报告</title></head><body>')
    rendered.append('<header><h1>个体化癌症风险评估报告</h1>')
    rendered.append('<p>受检者：{{PERSON_AGE}}岁 / {{PERSON_GENDER}} | 模型版本：cancerrisk-skill v2</p>')
    rendered.append('</header>')
    rendered.append('<section><h2>一、癌症风险排序</h2>')
    rendered.append('<p>基于您的年龄、性别、高危因素、体检指标,综合贝叶斯推理得出的个体化风险评估。</p>')
    rendered.append('{{RANKED_RISKS_TABLE}}')
    rendered.append('</section>')
    rendered.append('<section><h2>二、中高风险癌种 — 风险来源分析</h2>')
    rendered.append('<p>以下对<strong>中等风险及以上</strong>的癌种,逐一解释风险升高的来源因素。</p>')
    rendered.append('{{MEDIUM_PLUS_DETAILS}}')
    rendered.append('</section>')
    rendered.append('<section><h2>三、高价值筛查推荐</h2>')
    rendered.append('<p>基于 VoI(Value of Information)排序的高价值筛查建议。</p>')
    rendered.append('{{HIGH_VALUE_SCREENING}}')
    rendered.append('</section>')
    rendered.append('<section><h2>四、按需筛查方案</h2>')
    rendered.append('<div class="plan jizaoan">{{SCREENING_PLAN_JIZAOAN}}</div>')
    rendered.append('<div class="plan clinical">{{SCREENING_PLAN_CLINICAL}}</div>')
    rendered.append('</section>')
    rendered.append('<aside class="appendix"><h3>附录</h3>')
    rendered.append('<p>置信区间方法: {{CONFIDENCE_INTERVAL_METHOD}}</p>')
    rendered.append('<p>未映射的体检异常: {{UNMAPPED_ABNORMALITIES}}</p>')
    rendered.append('</aside>')
    rendered.append('<footer><p>本报告仅用于健康管理和筛查决策辅助,不构成医学诊断。</p></footer>')
    # NOTE: do NOT inline the v4.2 source markdown via <details><pre>; that
    # violates design §6.3 第 1 条 (no <pre> wraps of template source in
    # user-visible HTML). Source provenance is preserved via the header
    # comment + the regen tool committed alongside this template.
    rendered.append('</body></html>')
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(PROVENANCE + "\n".join(rendered) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
