# CancerRisk v1.4 — P1: Pipeline to Single Integrated Report

> **For agentic workers:** REQUIRED SUB-SKILL: 用 superpowers:subagent-driven-development 逐任务实现。改 skill 结构(SKILL.md/scripts)按 `skill-creator` 写作指引;P1 完成后跑 skill-creator 评测环 + darwin 迭代(spec §6)。步骤用 `- [ ]` 复选框跟踪。

**Branch:** `v1.4-p1-single-report`(基于 v1.4,P0 已并入)
**Design refs:** `docs/superpowers/specs/2026-06-05-cancerrisk-v1.4-design.md` §1D/§2/§5/§9
**Spec refs:** `spec.md` §1D/§2/§7
**P1 verify gate(design §9 / spec §5):** 旧 3 个 HTML 交付移除;健康总结/快照风险降为内部 JSON;orchestrator 跑到新 `report` 检查点并产出 `report.html`;`test/test_1`+`test/test_2` 全流程通过。

---

## Controller OQ 决议(2026-06-08,执行前已定)

- **OQ-1(模版粒度)**:P1 = **脚手架级**模版(渲染通过、出 report.html、含阳/阴 + 遗传 Jinja 分支占位);字段级全保真对齐 temp/-2/-7 归 **P2**(依设计 §9/§11)。
- **OQ-2(manifest.json)**:**保留生产**为审计产物(`write_manifest.py` 仍跑,reports 键改为 `{"report.html": ...}`),仅不再喂 `index.html` 路由页。
- **OQ-3(自动入档)**:**自动入档,移除 exit-4 人工确认**——用户本轮明确"个人健康档案库需自动保存更新"。spec §1E 旧"用户确认"被本决策覆盖。
- **OQ-4(肿瘤标志物路径)**:assembler 用 `tumor_markers.json` → `tumor_markers.candidate.json` 回退;Task 2 在 gate 通过后由 orchestrator 物化 `tumor_markers.json`。

---

## Goal

把管线从产出 4 个 HTML(`health_summary.html`/`snapshot_risk.html`/`longitudinal_risk.html`/`index.html`)改为产出**单一整合报告** `report.html`,由一个组装的 `report.json` 驱动。

**范围边界**:P1 = 管线管道(退役旧交付、接 `report` 检查点、脚手架渲染器);P2 = 全保真(精确对齐 html-preview-2/7 的板块内容、阳/阴/遗传分支正确)。

## Architecture

| Layer | v1.3 | v1.4 P1 |
|---|---|---|
| stop-afters | health-summary/snapshot/longitudinal | 移除三者;新增 `report` |
| Task7 输出 | snapshot_risk.html | 仅 snapshot_risk.json(内部),不出 HTML |
| Task8b 纵向 | longitudinal_risk.py + render → HTML | 整段移除(D3) |
| Task8c | exit-4 人工入档确认 | 自动入档(auto_apply=True) |
| Task9 | render_index + write_manifest → index.html | build_report_json + render_report → report.json + report.html;manifest 仍产但不喂 index |
| SKILL.md | 4-HTML 契约 / exit-4 流程 | 单报告契约 / 自动入档 |

**内部 JSON 中间件(数学引擎不动)**:`health_summary_structured_summary.json`(CP4)、`snapshot_risk.json`(snapshot_risk.py,D2)、`voi_ranking.json`、`tumor_markers(.candidate).json`(CP3)、`answers.json`(CP2)。

**新产物**:`artifacts/report.json`(`build_report_json.py` 组装)、`<out>/report.html`(`render_report.py` 渲染 `templates/integrated_report_v14.html`)。

**report.json 顶层 schema(P1 脚手架,字段级映射归 P2)**:
```json
{"schema_version":"report-v1","run_id":"...","generated_at":"...",
 "person":{"person_id":"...","sex":"...","age":0},
 "jizaoan_result":"negative|positive|unknown","jizaoan_top_cancers":[],
 "brca_status":"negative|positive|unknown",
 "health_summary":{"status":"...","abnormal_non_cancer_count":0,"items":[]},
 "snapshot":{"cancers":[],"section4_screening":[],"uncertainties_summary":{}},
 "voi":{"top_recommendation":null,"rankings":[],"total_methods_evaluated":0},
 "tumor_markers":[],"evidence_version":null}
```

## Tech Stack
Python 3.11 + uv(PyYAML/jsonschema/jinja2/requests);Jinja2 渲染;pytest 单测;`test/test_1`+`test/test_2` 全流程集成。不改 `snapshot_risk.py`/`voi_calculator.py`/`finalize_structured_summary.py`/`archive_manager.py`。

---

## Tasks

### Task 1 — 接 `report` 检查点;退役旧 stop-after 与 HTML 渲染调用(orchestrator)
**Files:** `scripts/run_formal_analysis.py`;`tests/test_p1_orchestrator_stop_after.py`(新)
- [ ] 写失败测试:断言 `STOP_AFTER_CHOICES` 含 `"report"`、不含 `"health-summary"/"snapshot"/"longitudinal"`。
  ```python
  import importlib.util
  from pathlib import Path
  def _load():
      spec = importlib.util.spec_from_file_location("rfa", Path(__file__).parent.parent/"scripts"/"run_formal_analysis.py")
      mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
  def test_report_present(): assert "report" in _load().STOP_AFTER_CHOICES
  def test_old_removed():
      m=_load()
      for r in ("health-summary","snapshot","longitudinal"): assert r not in m.STOP_AFTER_CHOICES
  ```
- [ ] 跑确认 RED:`uv run --python 3.11 --with PyYAML --with jsonschema --with jinja2 --with requests python -m pytest tests/test_p1_orchestrator_stop_after.py -q`
- [ ] 改 `STOP_AFTER_CHOICES`:移除三者、加 `"report"`。
- [ ] 删 `render_snapshot_html` 调用块 + import;Task7 审计文本去掉 HTML 行。
- [ ] 删整段 Task8b 纵向(longitudinal_risk + render_longitudinal_html 调用 + import + `stop_after=="longitudinal"` guard)。
- [ ] 删 exit-4 halt 块;archive 调用改 `auto_apply=True` 恒定(`--auto-apply-archive` 保留为 no-op 兼容);`longitudinal` 变量移除后,archive_manager 内部 `_read_json(.../longitudinal_risk.json,{})` 自动降级为 `{}`,**archive_manager.py 不需改**。
- [ ] 删 Task9 块(write_manifest/render_index 的 index 路由渲染);留 `# TODO(P1-task2)` 占位 + `stop_after=="report"` guard 占位。(manifest 保留产出见 Task4/OQ-2)
- [ ] 跑确认 GREEN;`grep -n STOP_AFTER_CHOICES scripts/run_formal_analysis.py` 核对。
- [ ] Commit:`feat(p1-task1): wire report checkpoint, retire 4-HTML stop-afters and render calls`

### Task 2 — `report.json` 组装器
**Files:** `scripts/build_report_json.py`(新);`tests/test_p1_build_report_json.py`(新)
- [ ] 写失败测试:读 5 个内部 JSON 产出正确顶层键;缺可选文件优雅降级;`jizaoan_result`/`brca_status` 取自 `answers.json`;原子写 `artifacts/report.json`。(测试代码见规划稿,字段同上 schema)
- [ ] 跑确认 RED。
- [ ] 实现 `build_report_json.py`:`assemble_report_json(*, artifacts, out, answers_path, person_id, run_id, evidence_version)`,纯组装(无数学/LLM),原子写。
- [ ] 跑确认 GREEN。
- [ ] orchestrator 接入(替换 Task1 的 TODO 占位):调用 `assemble_report_json(...)`;并在 CP3 gate 通过后物化 `tumor_markers.json`(OQ-4)。
- [ ] Commit:`feat(p1-task2): add report.json assembler`

### Task 3 — 脚手架 Jinja2 模版 `templates/integrated_report_v14.html`
**Files:** `templates/integrated_report_v14.html`(新);`tests/test_p1_template_structure.py`(新)
- [ ] 写失败测试:StrictUndefined 渲染无 UndefinedError;6 个 section id(`section-header/timeline/clinical-design/liquid-biopsy/package/lifestyle`)存在;person_id 渲染;阴性含"阴性"、阳性含"阳性"。
- [ ] 跑确认 RED。
- [ ] 实现脚手架模版:沿用 temp/-2 的 CSS 调色板(`--primary:#1a5f7a`;`brca_status=="positive"` 切紫/红警示);6 个 section 容器;Jinja 变量引用(person/jizaoan_result/snapshot.cancers|length/health_summary.items/voi/tumor_markers);`{% if jizaoan_result=="positive" %}…{% else %}` 与遗传 `{% if brca_status=="positive" %}` 分支;`{{ disclaimer }}` 页脚。**仅参考 temp 结构/CSS,不照搬静态内容(全保真归 P2)。**
- [ ] 跑确认 GREEN。
- [ ] Commit:`feat(p1-task3): scaffold integrated_report_v14.html`

### Task 4 — 薄渲染器 `scripts/render_report.py` + 接入 orchestrator
**Files:** `scripts/render_report.py`(新);`tests/test_p1_render_report.py`(新);`scripts/run_formal_analysis.py`(接入 + `report` guard);`scripts/write_manifest.py`(reports 键改 `{"report.html":...}`,保留产出—OQ-2)
- [ ] 写失败测试:`render_report(...)` 返回非空 HTML 串;`write_report_html(...)` 写出 `report.html`。
- [ ] 跑确认 RED。
- [ ] 实现 `render_report.py`(Jinja2 薄渲染,无数学/LLM)。
- [ ] 跑确认 GREEN。
- [ ] orchestrator 接入完整 P1 块:`build_report_json` → `render_report.write_report_html` → 写 `module_audits/task_p1_report.md` → `stop_after=="report"` guard;manifest 保留产出(reports 指向 report.html)。
- [ ] 跑全套 `pytest tests/ -q` 无回归。
- [ ] Commit:`feat(p1-task4): thin render_report.py + wire into orchestrator`

### Task 5 — 更新 `SKILL.md`(单报告 workflow,按 skill-creator 指引)
**Files:** `SKILL.md`;`tests/test_p1_skill_md_contract.py`(新)
- [ ] 写失败测试:Output Contract 含 `report.html`、不含旧 4 HTML;Pipeline Stages 含整合报告行;Minimal Workflow 无 `Exit code 4`/人工入档确认。
- [ ] 跑确认 RED。
- [ ] 外科化更新 SKILL.md:frontmatter description(四报告→单一 report.html);Use/Refuse;Pipeline Stages 表(删纵向/index 行,加整合报告行,archive 标 auto);Minimal Workflow step10(自动入档,去 exit-4 块);Non-Negotiables / Archive Contract(自动入档,去纵向前置);Output Contract(report.html + report.json;去 longitudinal_risk.json/manifest 路由);PUA TL;DR CP4;Progressive References(去纵向)。
- [ ] 跑确认 GREEN + 全套无回归。
- [ ] Commit:`docs(p1-task5): update SKILL.md — single-report workflow, auto-archive`

### Task 6 — 集成里程碑:test_1 / test_2 全流程冒烟(design §9 / spec §5)
**非 headless 单测,是实测全流程。** 验收:① test_1(单 PDF)、test_2(多 PDF+图)端到端跑通(问卷首选项/"无");② 产出 `report.html`;③ 输出目录无旧 4 HTML;④ `artifacts/report.json` 合法且 `schema_version=report-v1`;⑤ `docudatabase/<pid>/` 已自动入档;⑥ 无 `longitudinal_risk.json`;⑦ 退出码 0。
- [ ] 跑 test_1 + test_2(命令见规划稿:`run_formal_analysis.py --input ... --analysis-output /tmp/... --person-id ... --answers ...`),逐项核验 PASS。
- [ ] Commit:`test(p1-task6): integration smoke — single report.html, no old HTML deliverables`

### Task 7 — skill-creator 评测 + darwin 迭代触发(design §6 / spec §6)
**P1 合并入 v1.4 后执行。**
- [ ] 用 skill-creator 评测环对更新后的 SKILL.md + 两用例跑评测(with-skill vs baseline,grade,viewer)。
- [ ] 跑一次 darwin 迭代,收集联合评估结果。
- [ ] 把改进项记为 P2/P3 候选(不在 P1 实现)。darwin 接入设计细化归 P5(§11)。

---

## 脚本变更总览
**退役为交付渲染器(留在盘上,orchestrator 不再调用)**:`render_snapshot_html.py`、`render_longitudinal_html.py`、`render_index.py`、`render_health_summary.run_render_phase()`。
**保留但改键**:`write_manifest.py`(reports→report.html,仍产 manifest 作审计)。
**新增**:`scripts/build_report_json.py`、`scripts/render_report.py`、`templates/integrated_report_v14.html`。
**修改**:`scripts/run_formal_analysis.py`、`SKILL.md`。

## Archive 耦合注记
`archive_manager.run_archive_stage()` 内部 `_read_json(artifacts/"longitudinal_risk.json",{})`;P1 该文件不存在 → 返回 `{}` → `longitudinal_summary={}`;`write_baseline_snapshot` 已有 `longitudinal_payload or {}` 守卫。**archive_manager.py 无需改。**

## 后续
P1 合并入 `v1.4` 后 → **P2(模版全保真:字段级对齐 temp/-2/-7、板块内容、三档时间轴、1+X 表、套餐、阳/阴/遗传精确分支)**。
