# Engine Contract Baseline — snapshot_risk.py

**目的:** 记录贝叶斯风险引擎 `scripts/snapshot_risk.py` 当前消费的结构化证据库契约，作为 v1.4 知识库重塑的防回归基准。**重塑后所有标注"不能改动"的字段必须保持完全兼容。**

生成时间: 2026-06-05  
基线来源: `scripts/snapshot_risk.py` 源码 + 实际文件结构扫描

---

## 1. 各文件顶层键（实际扫描结果）

| 文件路径 | 顶层键 |
|---|---|
| `evidence_store/ontology/cancers.json` | `version`, `cancers` |
| `evidence_store/ontology/cancer_age_sex_priors.json` | `schema_version`, `metadata`, `lookup_rule`, `cancers`, `missing_priors` |
| `evidence_store/assertions/risk_assertions.json` | `version`, `assertions` |
| `evidence_store/assertions/risk_assertions_derived.json` | `derived_assertions` |
| `evidence_store/assertions/detection_performance.json` | `tests` |
| `evidence_store/assertions/detection_performance_derived.json` | `derived_detection_performance` |
| `evidence_store/screening/screening_recommendations.json` | `recommendations` |

> `risk_assertions.json` 和 `detection_performance.json` 是源数据文件，引擎**不直接读取**；引擎只读取 `_derived` 版本。

---

## 2. 引擎直接读取的文件与字段（以代码为准）

### 2.1 `evidence_store/ontology/cancers.json`

**读取方式:** `_read_json(evidence_store / "ontology/cancers.json")`  
**索引方式:** 遍历 `payload["cancers"]`

**重塑后不能改动的字段（每条条目）:**

| 字段 | 用途 | 代码引用 |
|---|---|---|
| `cancer_id` | 主键，用于所有跨文件关联 | `cancer["cancer_id"]` |
| `applicable_sex` | 性别过滤；值为 `"all"` / `"male"` / `"female"` | `cancer.get("applicable_sex", "all")` |
| `cancer_name_zh` | 输出报告中的中文癌种名 | `cancer.get("cancer_name_zh")` |

**实际数据样例:**
```json
{
  "cancer_id": "lung_cancer",
  "cancer_name_zh": "肺癌",
  "cancer_name_en": "Lung cancer",
  "applicable_sex": "all"
}
```

---

### 2.2 `evidence_store/assertions/risk_assertions_derived.json`

**读取方式:** `_read_json(evidence_store / "assertions/risk_assertions_derived.json")`  
**索引方式:**
- `_derived_by_assertion_id`: 按 `assertion_id` 建索引 → `payload["derived_assertions"]`
- `_derived_by_factor_level`: 按 `(cancer_id, factor_id, factor_level)` 建索引 → `payload["derived_assertions"]`

**重塑后不能改动的字段（每条条目）:**

| 字段 | 用途 | 代码引用 |
|---|---|---|
| `assertion_id` | 主键，用于去重与索引 | `d["assertion_id"]` |
| `cancer_id` | 关联到 cancers.json | `d.get("cancer_id")` |
| `factor_id` | 关联因子 | `d.get("factor_id")` |
| `factor_level` | 因子水平（如 `present`）| `d.get("factor_level")` |
| `log_odds_delta` | 贝叶斯计算核心值 | `float(derived["log_odds_delta"])` |
| `conversion_status` | 必须为 `"usable"` 才计入计算 | `derived.get("conversion_status") != "usable"` |
| `assertion_key` | 格式 `cancer_id|factor_id|factor_level|assertion_id`，用于输出 | `derived.get("assertion_key")` |
| `effect_type` | 输出字段（如 `"OR"`）| `derived.get("effect_type")` |
| `calculation_value` | 输出字段 | `derived.get("calculation_value")` |
| `approximation` | 近似标志，触发 uncertainty | `bool(derived.get("approximation", False))` |
| `source_id` | 输出引用来源 | `derived.get("source_id")` |

**实际数据样例:**
```json
{
  "assertion_id": "asrt_lung_cancer_smoking_continuous",
  "assertion_key": "lung_cancer|smoking_continuous|present|asrt_lung_cancer_smoking_continuous",
  "cancer_id": "lung_cancer",
  "factor_id": "smoking_continuous",
  "factor_level": "present",
  "effect_type": "OR",
  "calculation_value": 8.43,
  "log_odds_delta": 2.131796772013764,
  "conversion_rule": "ln(OR)",
  "conversion_status": "usable",
  "approximation": false,
  "source_id": "Parkin DM"
}
```

---

### 2.3 `evidence_store/assertions/detection_performance_derived.json`

**读取方式:** `_read_json(evidence_store / "assertions/detection_performance_derived.json")`  
**索引方式:** `_detection_by_cancer_id`: 按 `cancer_id` 建索引，返回 LIST（一个 cancer_id 可有多条，对应多个检测方法）→ `payload["derived_detection_performance"]`

**重塑后不能改动的字段（每条条目）:**

| 字段 | 用途 | 代码引用 |
|---|---|---|
| `cancer_id` | 关联 cancers.json | `d["cancer_id"]` |
| `test_id` | 关联 screening_tests（来自 merged 输入） | `detection.get("test_id")` |
| `negative_log_odds_delta` | 阴性结果的 log odds 贡献（典型值 < 0）| `float(detection["negative_log_odds_delta"])` |
| `positive_log_odds_delta` | 阳性结果的 log odds 贡献（典型值 > 0）| `float(detection["positive_log_odds_delta"])` |
| `lr_negative` | 阴性似然比（输出字段）| `float(detection.get("lr_negative", 0))` |
| `lr_positive` | 阳性似然比（输出字段）| `float(detection.get("lr_positive", 0))` |
| `conversion_status` | 必须为 `"usable"` 才计入计算 | `detection.get("conversion_status") != "usable"` |
| `probability_boundary_adjustment` | 近似标志，触发 uncertainty | `bool(detection.get("probability_boundary_adjustment", False))` |
| `source_id` | 输出引用来源 | `detection.get("source_id")` |

> **关键澄清 — 真实 LR 键名:**  
> 任务描述中预期的键名是 `LR+` / `LR-`，但**代码实际使用的键名是 `lr_positive` / `lr_negative`**（小写，下划线分隔）。  
> 贝叶斯计算本身使用的是预计算好的 `negative_log_odds_delta` / `positive_log_odds_delta`，而非直接用 LR 值计算。`lr_positive` / `lr_negative` 仅作为输出字段写入快照。

**实际数据样例（第一条，jizaoan 多癌筛查）:**
```json
{
  "test_id": "jizaoan_multi_cancer_screening",
  "cancer_id": "lung_cancer",
  "raw_sensitivity": 0.729,
  "raw_specificity": 0.991,
  "sensitivity": 0.729,
  "specificity": 0.991,
  "probability_boundary_adjustment": false,
  "lr_positive": 80.99999999999993,
  "lr_negative": 0.27346115035317864,
  "positive_log_odds_delta": 4.394449154672438,
  "negative_log_odds_delta": -1.296595713450287,
  "conversion_status": "usable",
  "conversion_rule": "LR+/LR- from sensitivity/specificity",
  "unusable_reason": null,
  "source_id": "jizaoan_white_paper_v2026"
}
```

---

### 2.4 `evidence_store/screening/screening_recommendations.json`

**读取方式:** `_read_json(evidence_store / "screening/screening_recommendations.json")`  
**索引方式:** `_screening_by_cancer_id`: 按 `cancer_id` 建索引 → `payload["recommendations"]`

**重塑后不能改动的字段（每条条目）:**

| 字段 | 用途 | 代码引用 |
|---|---|---|
| `cancer_id` | 主键，关联 cancers.json | `r["cancer_id"]` |
| `standard_screening` | 写入 section4 输出 | `screen_entry.get("standard_screening", [])` |

**实际数据样例:**
```json
{
  "cancer_id": "lung_cancer",
  "cancer_name": "肺癌",
  "standard_screening": [
    {
      "method": "低剂量螺旋CT (LDCT)",
      "population": "50-75岁、吸烟≥20包年或戒烟<15年",
      "interval": "每年1次",
      "trigger": "高危人群",
      "source_id": "guideline_uspstf_2021"
    }
  ]
}
```

---

### 2.5 `evidence_store/ontology/cancer_age_sex_priors.json`

**读取方式:** `_read_json(Path(risk_cfg.get("priors_file", evidence_store / "ontology/cancer_age_sex_priors.json")))`  
**使用方式:** 通过 `build_age_sex_priors.resolve_prior(priors_payload, cancer_id, person_sex, person_age)` 查询

**重塑后不能改动的顶层结构:**

| 字段 | 用途 | 代码引用 |
|---|---|---|
| `missing_priors` | 列表，引擎先检查此列表，若 cancer_id 在其中则返回 None（无先验）| `priors_payload.get("missing_priors", [])` |
| `cancers` | 先验记录列表 | `priors_payload.get("cancers", [])` |

**每条 `cancers` 记录必须保留的字段:**

| 字段 | 用途 |
|---|---|
| `cancer_id` | 查询键 |
| `priors` | 该癌种的先验列表 |

**每条 `priors` 记录必须保留的字段:**

| 字段 | 用途 | 代码引用 |
|---|---|---|
| `sex` | 按性别过滤 | `p["sex"] == sex` |
| `age` | 年龄锚点，用于最近下界查找 | `p["age"]` |
| `annual_probability` | 引擎直接使用的先验概率值 | `prior_record["annual_probability"]` |
| `source_id` | 写入输出 `prior_source_id` | `prior_record["source_id"]` |

**`missing_priors` 机制说明:**  
`resolve_prior` 在查找先验之前先检查 `cancer_id` 是否在 `missing_priors` 列表中。若在，直接返回 `None`，引擎将该癌种标记为 `status_reason="no_prior_data"`（或在有影像 PPV 时走 `imaging_ppv_only_no_prior` 路径）。  
重塑后若某癌种暂无先验数据，必须将其 `cancer_id` 列入 `missing_priors`，不能省略此字段。

**实际数据样例:**
```json
{
  "schema_version": "cancer-prior-v1",
  "lookup_rule": {
    "between_anchors": "nearest_lower_anchor",
    "above_max_age": "use_max_age_value",
    "below_min_age": "use_min_age_value"
  },
  "cancers": [
    {
      "cancer_id": "biliary_tract_cancer",
      "cancer_name_zh": "胆道肿瘤",
      "applicable_sex": "all",
      "priors": [
        {
          "sex": "male",
          "age": 30,
          "annual_incidence_per_100000": 0.27,
          "annual_probability": 2.7e-06,
          "source_id": "globocan_2022"
        }
      ]
    }
  ],
  "missing_priors": []
}
```

---

### 2.6 附加文件（非直接证据库文件）

#### `evidence_store/ontology/risk_factors.json`（可选加载）

引擎在 `run_snapshot_stage` 中可选地加载此文件，仅用于为输出结果添加 `factor_name_zh` 显示名：

```python
rf_data = _read_json(rf_path)
for rf in rf_data.get("risk_factors", []):
    fid = rf.get("factor_id")
    if fid and rf.get("factor_name_zh"):
        _factor_zh[fid] = rf["factor_name_zh"]
```

**不能改动的字段:** `factor_id`（关联键）、`factor_name_zh`（显示名）。此文件不影响贝叶斯计算，仅影响输出文本。

#### `config/formal.yaml`

通过 `risk_cfg = config.get("risk_prediction", {})` 读取，控制分层阈值和 section4 过滤参数。不属于 evidence_store，不在本次重塑范围内。

---

## 3. 契约兼容性检查清单

重塑后运行 `scripts/snapshot_risk.py` 前，请逐项确认：

- [ ] `cancers.json` 中每条记录有 `cancer_id`、`applicable_sex`、`cancer_name_zh`
- [ ] `risk_assertions_derived.json` 顶层键为 `derived_assertions`（列表）
- [ ] 每条 derived_assertion 有 `assertion_id`、`cancer_id`、`factor_id`、`factor_level`、`log_odds_delta`、`conversion_status`
- [ ] `detection_performance_derived.json` 顶层键为 `derived_detection_performance`（列表）
- [ ] 每条 detection 有 `cancer_id`、`test_id`、`negative_log_odds_delta`、`positive_log_odds_delta`、`lr_negative`、`lr_positive`、`conversion_status`
- [ ] `screening_recommendations.json` 顶层键为 `recommendations`（列表），每条有 `cancer_id`、`standard_screening`
- [ ] `cancer_age_sex_priors.json` 有 `missing_priors` 和 `cancers` 顶层键
- [ ] 每条 prior 记录有 `sex`、`age`、`annual_probability`、`source_id`
- [ ] 无先验的癌种已列入 `missing_priors`，而非以 0 值记录

---

## 4. 与任务预期描述的差异

| 差异点 | 任务描述 | 代码实际值 | 说明 |
|---|---|---|---|
| `detection_performance_derived.json` 的 LR 键名 | `LR+` / `LR-` | `lr_positive` / `lr_negative` | 代码使用小写下划线格式；贝叶斯计算使用预计算的 `positive_log_odds_delta` / `negative_log_odds_delta`，LR 值仅用于输出 |
| cancers.json 的 name 字段 | `name_zh` | `cancer_name_zh` | 实际字段名带 `cancer_` 前缀 |
