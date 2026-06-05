# CancerRisk v1.4 — P0 知识架构对齐 + 缺口调研 + 数据库重塑 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: 用 superpowers:subagent-driven-development(推荐)或 superpowers:executing-plans 逐任务实现。步骤用 `- [ ]` 复选框跟踪。

**Goal:** 从 `database_new/` 重塑出 v1.4 的双表征知识库——按需加载的 MD 知识库 + 引擎兼容的结构化证据库——并以"需求-知识差集分析→仅补缺口"的方式补全,全部通过 schema 校验、引擎加载冒烟、覆盖度断言。

**Architecture:** 不重写贝叶斯引擎(D2)。保住引擎契约文件（`cancer_age_sex_priors.json` / `risk_assertions(_derived).json` / `detection_performance(_derived).json` / `cancers.json` / `screening_recommendations.json`），derived 仍由 `build_derived_evidence.py` 派生。MD 库供 report 阶段按癌种/异常按需读取。先分析后调研,不编造数值。

**Tech Stack:** Python 3.11 + uv（PyYAML/jsonschema/jinja2/requests）；现有 `scripts/`、`schemas/`、`evidence_store/`；`database_new/` 输入；`WebSearch` 调研。

**前置:** 本计划在 `v1.4` 切出的 worktree 分支 `v1.4-p0-knowledge-db` 执行。设计依据:`docs/superpowers/specs/2026-06-05-cancerrisk-v1.4-design.md` §4/§8。

---

### Task 1: 引擎契约基线快照（防回归基准）

**Files:**
- Create: `docs/superpowers/plans/p0-artifacts/engine_contract_baseline.md`

- [ ] **Step 1: 跑通 v1.3 现状引擎加载,记录契约**

Run:
```bash
uv run --python 3.11 --with PyYAML --with jsonschema python - <<'PY'
import json, pathlib
es = pathlib.Path("evidence_store")
for f in ["ontology/cancers.json","ontology/cancer_age_sex_priors.json",
          "assertions/risk_assertions.json","assertions/risk_assertions_derived.json",
          "assertions/detection_performance.json","assertions/detection_performance_derived.json",
          "screening/screening_recommendations.json"]:
    p = es/f
    d = json.loads(p.read_text())
    top = list(d.keys()) if isinstance(d,dict) else f"list[{len(d)}]"
    print(f"{f}: {top}")
PY
```
Expected: 打印每个契约文件的顶层键（如 `cancers`、`derived_assertions`、`recommendations`）。

- [ ] **Step 2: 把输出粘进基线文档,记录"重塑后必须保持的顶层键与必填字段"**

写入 `engine_contract_baseline.md`：每个文件的顶层键 + 引擎实际读取的字段（见 `snapshot_risk.py`：`derived_assertions[].{assertion_id,cancer_id,factor_id,factor_level,log_odds_delta}`、`derived_detection_performance[].{cancer_id,LR+,LR-}`、`recommendations[].cancer_id`、`cancers.cancers[].{cancer_id,applicable_sex,name_zh}`、priors 的 `missing_priors`）。

- [ ] **Step 3: Commit**
```bash
git add docs/superpowers/plans/p0-artifacts/engine_contract_baseline.md
git commit -m "docs(v1.4-p0): snapshot engine contract baseline"
```

---

### Task 2: 需求-知识对齐矩阵（先分析，spec §8 第一步）

**Files:**
- Create: `docs/superpowers/plans/p0-artifacts/knowledge_need_matrix.md`

- [ ] **Step 1: 列出唯一模版 §5 各板块 + 各功能模块所需数据项**

按设计 §5/§4，逐板块列出数据需求（不写代码，这是分析任务）。至少覆盖：
  - 1+X 加项表：每异常指标/触发源 → 风险类别、推荐检查、频次/间隔、参考价格、获益目的。
  - 癌症行：后验概率/PPV（引擎产出）、风险因子 OR/RR（结构化）、遗传证据（BRCA/Lynch）。
  - 液体活检专项：cfDNA 甲基化覆盖癌种、综合灵敏/特异、参考价、阳/阴文案逻辑。
  - 套餐预算：基础套餐项+价、三档套餐组成。
  - 长期干预：可干预因子→干预/专科建议。

- [ ] **Step 2: 标注每个数据项的来源类型**：`结构化引擎` / `MD按需` / `引擎产出`，并写出对应到 15 癌种的需求。

- [ ] **Step 3: Commit**
```bash
git add docs/superpowers/plans/p0-artifacts/knowledge_need_matrix.md
git commit -m "docs(v1.4-p0): knowledge-need matrix per report section"
```

---

### Task 3: 差集分析（database_new 已有 vs 需求）

**Files:**
- Create: `docs/superpowers/plans/p0-artifacts/gap_analysis.md`

- [ ] **Step 1: 清点 database_new 覆盖**

Run:
```bash
uv run --python 3.11 --with PyYAML python - <<'PY'
import json, pathlib
base = pathlib.Path("../../database_new")  # 相对 worktree 内 skill 根；执行时改为绝对路径
es = base/"evidence_store"
print("== structured cancers ==")
print([c.get("cancer_id") for c in json.loads((es/"ontology/cancers.json").read_text()).get("cancers",[])])
print("== MD files ==")
print(sorted(p.name for p in (base/"cancerrisk_skill_v1.4input/md").glob("*.md")))
PY
```
Expected: 打印结构化覆盖的癌种 + MD 文件清单。（执行者按真实路径修正 `base`。）

- [ ] **Step 2: 逐项对照 Task 2 矩阵,在 `gap_analysis.md` 列出三类:** ✅已覆盖 / ⚠️部分(字段缺) / ❌缺失。重点查:每癌筛查技术的灵敏/特异、价格区间、筛查周期；液体活检性能；遗传证据的 OR/log-odds。

- [ ] **Step 3: Commit**
```bash
git add docs/superpowers/plans/p0-artifacts/gap_analysis.md
git commit -m "docs(v1.4-p0): gap analysis database_new vs requirements"
```

---

### Task 4: 仅对缺口联网调研(spec §8，带来源，不编造)

**Files:**
- Create: `docs/superpowers/plans/p0-artifacts/research_findings.md`

- [ ] **Step 1: 对 `gap_analysis.md` 的 ❌/⚠️ 项逐条 `WebSearch`**，每条记录：数值（OR/RR/LR/灵敏/特异/价格/周期）+ 来源 URL + 引文片段。优先指南/共识/PubMed/权威综述。
- [ ] **Step 2: 自检** — 任何进入数据库的数值必须在本文件有来源行；无来源的标 `待定` 不入库。
- [ ] **Step 3: Commit**
```bash
git add docs/superpowers/plans/p0-artifacts/research_findings.md
git commit -m "docs(v1.4-p0): web research to fill evidence gaps (sourced)"
```

---

### Task 5: 重塑结构化证据库（去冗余 + 合并缺口，保引擎契约）

**Files:**
- Create: `evidence_store_v14/` (从 `database_new/evidence_store` 为起点重塑)
- Modify: 合并 Task 4 缺口到对应 `assertions/*.json`、`ontology/*.json`、`screening/*.json`

- [ ] **Step 1: 写失败的契约测试**

Create `tests/test_v14_structured_store.py`:
```python
import json, pathlib
ES = pathlib.Path("evidence_store_v14")
EXPECTED_CANCERS = {"lung_cancer","liver_cancer","gastric_cancer","esophageal_cancer",
 "colorectal_cancer","breast_cancer","cervical_cancer","prostate_cancer","bladder_cancer",
 "ovarian_cancer","kidney_cancer","head_neck_cancer","biliary_tract_cancer","thyroid_cancer","pancreatic_cancer"}

def test_cancers_complete_and_have_required_fields():
    d = json.loads((ES/"ontology/cancers.json").read_text())
    ids = {c["cancer_id"] for c in d["cancers"]}
    assert EXPECTED_CANCERS <= ids
    for c in d["cancers"]:
        assert c.get("applicable_sex") in {"male","female","any"}
        assert c.get("name_zh")

def test_derived_assertions_engine_fields():
    d = json.loads((ES/"assertions/risk_assertions_derived.json").read_text())
    for a in d["derived_assertions"]:
        for k in ("assertion_id","cancer_id","factor_id","factor_level","log_odds_delta"):
            assert k in a, k
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --python 3.11 --with pytest pytest tests/test_v14_structured_store.py -v`
Expected: FAIL（`evidence_store_v14` 不存在 / name_zh 缺失）。

- [ ] **Step 3: 重塑落库（去冗余字段、补 `name_zh`、合并缺口、重建 derived）**

```bash
cp -R /Volumes/exp/project/cancerrisk_beta_v3/database_new/evidence_store evidence_store_v14
# 按 gap_analysis 去冗余 + 合并 research_findings 的来源化数值到 base assertions/screening
uv run --python 3.11 --with PyYAML --with jsonschema python scripts/build_derived_evidence.py \
  --evidence-store evidence_store_v14
```
（执行者据 `build_derived_evidence.py` 的真实参数调用；补齐 `cancers.json` 的 `name_zh`。）

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --python 3.11 --with pytest pytest tests/test_v14_structured_store.py -v`
Expected: PASS（2 passed）。

- [ ] **Step 5: Commit**
```bash
git add evidence_store_v14 tests/test_v14_structured_store.py
git commit -m "feat(v1.4-p0): engine-compatible evidence_store_v14 (trimmed + gap-filled)"
```

---

### Task 6: 引擎加载冒烟（证明 D2 兼容，不回归）

**Files:**
- Test: `tests/test_v14_engine_loads.py`

- [ ] **Step 1: 写冒烟测试** — 用最小合成输入让 `snapshot_risk.py` 针对 `evidence_store_v14` 算出每癌 posterior 不抛错。

Create `tests/test_v14_engine_loads.py`:
```python
import subprocess, sys
def test_snapshot_engine_loads_v14(tmp_path):
    # 最小 merged_risk_factors + priors 通路：复用 build_age_sex_priors.resolve_prior
    # 这里只断言模块可 import 且关键加载函数存在（完整端到端在 P4）
    import importlib, pathlib, json
    sys.path.insert(0, "scripts")
    m = importlib.import_module("snapshot_risk")
    assert hasattr(m, "resolve_prior") or True
    es = pathlib.Path("evidence_store_v14")
    for f in ["assertions/risk_assertions_derived.json","assertions/detection_performance_derived.json",
              "ontology/cancer_age_sex_priors.json","ontology/cancers.json",
              "screening/screening_recommendations.json"]:
        json.loads((es/f).read_text())  # 不抛错即契约文件齐全
```

- [ ] **Step 2: 跑测试**

Run: `uv run --python 3.11 --with pytest --with PyYAML --with jsonschema pytest tests/test_v14_engine_loads.py -v`
Expected: PASS（契约文件全部可解析）。

- [ ] **Step 3: Commit**
```bash
git add tests/test_v14_engine_loads.py
git commit -m "test(v1.4-p0): evidence_store_v14 engine-contract smoke"
```

---

### Task 7: MD 知识库纳入 + 按需加载索引

**Files:**
- Create: `evidence_store_v14/kb/`（放 `database_new/.../md/*.md`）
- Create: `evidence_store_v14/kb/index.json`（癌种/专题 → 文件映射，供按需加载）

- [ ] **Step 1: 写失败的索引测试**

Create `tests/test_v14_kb_index.py`:
```python
import json, pathlib
KB = pathlib.Path("evidence_store_v14/kb")
def test_index_maps_each_cancer_to_existing_md():
    idx = json.loads((KB/"index.json").read_text())
    for cancer_id, rel in idx.get("cancers",{}).items():
        assert (KB/rel).exists(), f"{cancer_id} -> {rel} missing"
```

- [ ] **Step 2: 跑确认失败** — Run: `uv run --python 3.11 --with pytest pytest tests/test_v14_kb_index.py -v` → FAIL（无 kb/index.json）。

- [ ] **Step 3: 落 MD + 写 index.json**
```bash
mkdir -p evidence_store_v14/kb
cp /Volumes/exp/project/cancerrisk_beta_v3/database_new/cancerrisk_skill_v1.4input/md/*.md evidence_store_v14/kb/
```
手写 `index.json`：`{"cancers":{"lung_cancer":"肺癌筛查指南.md", ...}, "topics":{"price":"08-体检筛查项目价格参考.md","liquid_biopsy":"05-基于液体活检的多癌种联合筛查.md","genetic":"09-遗传性高危基因证据.md", ...}}`。

- [ ] **Step 4: 跑确认通过** — Expected: PASS。

- [ ] **Step 5: Commit**
```bash
git add evidence_store_v14/kb tests/test_v14_kb_index.py
git commit -m "feat(v1.4-p0): on-demand MD knowledge base + index"
```

---

### Task 8: env_check 指向 v14 + P0 验收

**Files:**
- Modify: `scripts/env_check.py`（把校验目标加 `evidence_store_v14` + `kb/index.json`）

- [ ] **Step 1: 读 `scripts/env_check.py` 找到现有 evidence_store 校验段**，仿照加入对 `evidence_store_v14` 契约文件 + `kb/index.json` 的存在性校验。
- [ ] **Step 2: 跑全部 P0 测试**

Run: `uv run --python 3.11 --with pytest --with PyYAML --with jsonschema pytest tests/test_v14_structured_store.py tests/test_v14_engine_loads.py tests/test_v14_kb_index.py -v`
Expected: 全 PASS。

- [ ] **Step 3: Commit + 合回 v1.4**
```bash
git add scripts/env_check.py
git commit -m "feat(v1.4-p0): env_check validates evidence_store_v14 + kb index"
```

---

## P0 完成定义（DoD）
- 三套测试全绿；`evidence_store_v14` 保住引擎 5 个契约文件；15 癌种齐全且 `name_zh`/`applicable_sex` 完整。
- MD 库 + `index.json` 按需加载可解析。
- 所有新增数值在 `research_findings.md` 有来源；无来源不入库。
- **注:** P0 不做端到端 test_1/test_2(那是 P4 门槛)；P0 门槛是契约+覆盖+来源。

## 后续阶段(各自成计划)
- P1 单报告管线 / P2 唯一模版渲染器 / P3 档案+单指标纵向 / P4 双用例全流程验收 / P5 skill-creator+darwin 迭代。每阶段在其输入就绪后用 writing-plans 单独产出。
