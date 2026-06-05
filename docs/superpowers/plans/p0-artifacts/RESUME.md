# P0 续作指引（RESUME）—— 新会话从这里接续

**最后更新:** 2026-06-05

## ✅ P0 已全部完成（T1–T8，18 测试全绿，已推送 origin/v1.4-p0-knowledge-db）
- 产物:`evidence_store_v14/`(引擎兼容,15 癌种,含 Lynch 8 断言、吉早安 8 癌种性能含胰腺、甲状腺/胰腺风险因子、screening 含 NPC/肾/胆道决策)、`evidence_store_v14/kb/` + `index.json`(15 癌种+6 专题按需加载)、3 套测试、`scripts/patch_evidence_store_v14.py`、`env_check.py` 已校验 v14。
- **下一步**:① 对 P0 整体做一次独立 code review;② 把 `v1.4-p0-knowledge-db` 合并/PR 回 `v1.4`;③ 开 **P1(管线改造为单报告)** 计划。建议新会话进行。
- 进入改 skill 结构(P1/P2)时:严格用 `skill-creator`;每轮后 `skill-creator`+`darwin-skill` 联合迭代(spec §6)。

---
## (以下为 P0 执行期参考,已完成)

## 现在在哪
- 仓库：`cancerrisk-skill`，远程 `git@github.com:zhongxianyu-wy/cancerrisk-skill.git`。
- 开发分支：**`v1.4`**（基于远程 `v1.3`）。P0 工作分支：**`v1.4-p0-knowledge-db`**（已 push）。
- Worktree（请在此继续）：`/Volumes/exp/project/cancerrisk_beta_v3/cancerrisk-skill/.claude/worktrees/v1.4-p0-knowledge-db`
- 设计：`docs/superpowers/specs/2026-06-05-cancerrisk-v1.4-design.md`
- P0 计划：`docs/superpowers/plans/2026-06-05-cancerrisk-v1.4-P0-knowledge-db.md`（8 个任务）

## 已完成（已提交+推送）
- **T1** 引擎契约基线 `engine_contract_baseline.md`（`8a07472`）
- **T2** 需求矩阵 `knowledge_need_matrix.md`（`41eefed`）
- **T3** 差集分析 `gap_analysis.md`（`08101cb`）
- **T4** 缺口调研 `research_findings.md`（`23ef31a`/`7d4dc0b`）

## 剩余：T5 → T8（用 subagent-driven-development 接续）
T5 重建 `evidence_store_v14`（最重）→ T6 引擎加载冒烟 → T7 MD KB + index → T8 env_check + P0 验收。

## ⚠️ 对 P0 计划的关键修正（务必带入 T5）
1. **引擎契约真实字段名**（计划原文写错，以此为准）：
   - `cancers.json` → `cancers[]`，字段是 **`cancer_name_zh`**（不是 `name_zh`）、`cancer_id`、`applicable_sex`。
   - `risk_assertions_derived.json` → `derived_assertions[]`：`assertion_id`、`cancer_id`、`factor_id`、`factor_level`、`log_odds_delta`、`conversion_status`。
   - `detection_performance_derived.json` → `derived_detection_performance[]`：`cancer_id`、`test_id`、`positive_log_odds_delta`、`negative_log_odds_delta`、`lr_positive`、`lr_negative`、`conversion_status`（贝叶斯用 *_log_odds_delta，lr_* 仅参考）。
   - `screening_recommendations.json` → `recommendations[]`：`cancer_id`、`standard_screening`。
   - `cancer_age_sex_priors.json` → 必须有顶层 `missing_priors`；prior 含 `sex`/`age`/`annual_probability`/`source_id`。
   - **T5 的契约测试必须用以上真实字段名**（计划里 `name_zh` 是错的，改成 `cancer_name_zh`）。

## ⚠️ T5 建模决策（用户 2026-06-05 拍板）
1. **吉早安性能**：采用**原数据库的 81.9% 灵敏度**作为基准；**不要**采用 77.2%（用户判定为过时）。research_findings.md 里的 77.2%/74.9% 不作为 T5 落库值。
2. **head_neck_cancer**：保留通用癌种 ID；筛查推荐补"鼻咽癌(NPC)在中国南方高发区 EBV 抗体筛查(30–69 岁)"；口腔/喉无推荐。
3. **肾癌 / 胆道癌**：一般人群不推荐筛查（如实记录）；胆道癌 PSC 高危 → 年度 MRI/MRCP。
4. **待定项**（肾癌高危间隔、口腔/喉筛查、中国糖尿病 meta 全文 OR）：**不编造**，留空待后续。
5. **Lynch**：OR 值已在 `database_new/.../md/09-遗传性高危基因证据.md`，T5 直接**落库**即可，无需再调研。

## 非协商约束（贯穿）
- 任何入库数值必须有来源（MD 字面或 research_findings 的来源行）；无来源不入库、不编造。
- 不重写贝叶斯引擎；`evidence_store_v14` 必须保住上面 5 个契约文件与字段。
- 严格按 skill-creator 改 skill 结构（进入 P1/P2 时）；每轮完成后用 skill-creator + darwin-skill 联合评估迭代（spec §6）。

## 如何起步（新会话）
1. `cd` 到上面 worktree 路径，确认 `git branch --show-current` = `v1.4-p0-knowledge-db`。
2. 读本文件 + P0 计划 Task 5–8 + 4 个 p0-artifacts。
3. 用 `superpowers:subagent-driven-development`，从 Task 5 起逐任务派子代理（实现→spec复查→质量复查→提交）。
4. T8 跑通三套测试即 P0 完成；再开 P1 计划。
