
TUMOR_MARKERS = {
    "AFP": {
        "cancer": "肝癌",
        "unit": "ng/mL",
        "normal_upper": 20,
        "evidence": "AFP用于肝癌诊断的Meta分析：20-100 ng/mL灵敏度约0.61、特异性约0.86，DOR约9.6；200 ng/mL灵敏度约0.49、特异性约0.98，DOR约47.1",
        "levels": {
            0: {"range": "<7", "OR": 0.5, "label": "正常"},
            1: {"range": "7-20", "OR": 0.8, "label": "轻度升高/未达诊断阈值"},
            2: {"range": "20-200", "OR": 9.6, "label": "中度升高", "note": "AFP 20-100 ng/mL Meta分析DOR约9.6；101-200 ng/mL LR+约6.9"},
            3: {"range": ">200", "OR": 47.1, "label": "显著升高", "note": "AFP≥200 ng/mL特异性约98%，Meta分析DOR约47"}
        }
    },
    "CEA": {
        "cancer": "结直肠癌",
        "unit": "ng/mL",
        "normal_upper": 5,
        "evidence": "CEA诊断结直肠癌Meta分析：cutoff约2.4-10 ng/mL时 pooled sensitivity约46.1%、specificity约89.2%，DOR约7.1；5 ng/mL研究约43%/90%，DOR约6.8；复发监测5 µg/L DOR约17.9、10 µg/L DOR约68.7",
        "levels": {
            0: {"range": "<2.5", "OR": 0.5, "label": "正常"},
            1: {"range": "2.5-5", "OR": 2.0, "label": "轻度升高", "note": "低阈值敏感性提高但特异性下降，单独筛查价值有限"},
            2: {"range": "5-20", "OR": 7.1, "label": "中度升高", "note": "原发CRC诊断Meta分析DOR约7；建议结合FIT/肠镜"},
            3: {"range": ">20", "OR": 20, "label": "显著升高", "note": "提示肿瘤负荷或转移可能，但缺少普通筛查场景直接OR证据"}
        }
    },
    "CA19-9": {
        "cancer": "胰腺癌/胆道肿瘤",
        "unit": "U/mL",
        "normal_upper": 37,
        "evidence": "CA19-9诊断胰腺癌：37-40 U/mL阈值灵敏度约79-81%、特异性约82-90%，DOR约17-38；胰腺癌vs慢性胰腺炎Meta分析DOR 19.31；100 U/mL阈值灵敏度约68%、特异性约98%，DOR约104；胆管癌≥100 U/mL DOR约18.1",
        "levels": {
            0: {"range": "<37", "OR": 0.5, "label": "正常"},
            1: {"range": "37-100", "OR": 19.3, "label": "轻度升高", "note": "胰腺癌 vs 慢性胰腺炎Meta分析DOR约19.3；胆道炎症/梗阻可假阳性"},
            2: {"range": "100-500", "OR": 104, "label": "中度升高", "note": "胰腺癌100 U/mL阈值特异性约98%，DOR约104；胆管癌≥100 U/mL DOR约18.1"},
            3: {"range": ">500", "OR": 200, "label": "显著升高", "note": "高阈值特异性进一步升高；1000 U/mL特异性约99.8%，DOR约347，500阈值为保守外推"}
        }
    },
    "CA125": {
        "cancer": "卵巢癌",
        "unit": "U/mL",
        "normal_upper": 35,
        "evidence": "CA125用于疑似附件包块鉴别：35 U/mL阈值Meta分析灵敏度约78-80%、特异性约75-78%，DOR约12-13；100 U/mL时恶性概率受绝经状态影响明显，绝经前约21%、绝经后约74%；普通人群筛查敏感性有限且不降低死亡率",
        "levels": {
            0: {"range": "<35", "OR": 0.5, "label": "正常"},
            1: {"range": "35-100", "OR": 12.5, "label": "轻度升高", "note": "附件包块Meta分析DOR约12-13；普通筛查敏感性有限，建议结合阴道超声"},
            2: {"range": "100-500", "OR": 50, "label": "中度升高", "note": "CA125 100 U/mL时恶性概率强烈受绝经状态影响：绝经前约21%，绝经后约74%"},
            3: {"range": ">500", "OR": 100, "label": "显著升高", "note": "高度提示卵巢恶性或肿瘤负荷，但需排除内异症、炎症、腹水等假阳性并结合超声/RMI"}
        }
    },
    "PSA": {
        "cancer": "前列腺癌",
        "unit": "ng/mL",
        "normal_upper": 4,
        "evidence": "PSA筛查/活检风险分层：4-10 ng/mL约25%活检阳性，>10 ng/mL超过50%；PSA>4 ng/mL总体PPV约30%；4-10灰区需结合f/t PSA、PSA density、MRI和年龄等因素",
        "levels": {
            0: {"range": "<1", "OR": 0.4, "label": "极低风险", "note": "低PSA不完全排除前列腺癌，但总体风险较低"},
            1: {"range": "1-4", "OR": 1, "label": "灰区", "note": "低于4 ng/mL仍可能检出癌，建议结合年龄/家族史/趋势"},
            2: {"range": "4-10", "OR": 2.5, "label": "轻度升高", "note": "约1/4活检阳性；需结合f-PSA比值、PSA density或MRI决定是否穿刺"},
            3: {"range": ">10", "OR": 6, "label": "显著升高", "note": "活检阳性概率通常>50%，但仍受前列腺炎/BPH等影响"}
        }
    },
    "CYFRA21-1": {
        "cancer": "肺癌",
        "unit": "ng/mL",
        "normal_upper": 3.3,
        "evidence": "CYFRA21-1诊断NSCLC Meta分析：总体灵敏度0.60、特异性0.90、DOR 16.17；肺鳞癌灵敏度0.72、特异性0.94、DOR 27.30，较腺癌更适用",
        "levels": {
            0: {"range": "<3.3", "OR": 0.5, "label": "正常"},
            1: {"range": "3.3-10", "OR": 16.2, "label": "轻度升高", "note": "NSCLC总体Meta分析DOR约16；建议结合LDCT"},
            2: {"range": "10-30", "OR": 27.3, "label": "中度升高", "note": "肺鳞癌Meta分析DOR约27；高水平阈值为保守分层"},
            3: {"range": ">30", "OR": 40, "label": "显著升高", "note": "显著升高提示肿瘤负荷/肺鳞癌可能，但缺少>30 ng/mL直接DOR证据"}
        }
    },
    "CA72-4": {
        "cancer": "胃癌",
        "unit": "U/mL",
        "normal_upper": 6.9,
        "evidence": "CA72-4诊断胃癌Meta分析：单项灵敏度约0.58、特异性约0.86、DOR约8；联合CEA+CA19-9+CA72-4灵敏度约0.67、特异性约0.89、DOR约16；中国人群Meta分析报告CA72-4与胃癌OR约32.9",
        "levels": {
            0: {"range": "<6.9", "OR": 0.5, "label": "正常"},
            1: {"range": "6.9-20", "OR": 8, "label": "轻度升高", "note": "CA72-4单项诊断胃癌Meta分析DOR约8，筛查PPV有限"},
            2: {"range": "20-50", "OR": 16, "label": "中度升高", "note": "联合CEA/CA19-9/CA72-4 Meta分析DOR约16；建议胃镜检查"},
            3: {"range": ">50", "OR": 32.9, "label": "显著升高", "note": "中国人群Meta分析OR约32.9；高阈值分层缺少直接DOR证据，需胃镜确认"}
        }
    },
    "CA15-3": {
        "cancer": "乳腺癌",
        "unit": "U/mL",
        "normal_upper": 25,
        "evidence": "CA15-3不推荐用于乳腺癌筛查/初诊；多中心评估显示初诊时敏感性随分期由I期约7%至IV期约78%(95%特异性)，复发监测灵敏度/特异性约90%/71%(DOR约22)，更适用于转移/复发和疗效监测",
        "levels": {
            0: {"range": "<25", "OR": 0.5, "label": "正常"},
            1: {"range": "25-50", "OR": 2, "label": "轻度升高", "note": "轻度升高特异性有限，不适合作为独立筛查依据"},
            2: {"range": "50-100", "OR": 10, "label": "中度升高", "note": "更提示复发/转移或肿瘤负荷，建议乳腺影像和既往病史联判"},
            3: {"range": ">100", "OR": 22, "label": "显著升高", "note": "复发监测DOR约22；晚期/转移场景价值高于初诊筛查"}
        }
    },
    "SCC": {
        "cancer": "宫颈癌/食管癌/头颈肿瘤",
        "unit": "ng/mL",
        "normal_upper": 1.5,
        "evidence": "SCC-Ag用于鳞癌辅助评估：宫颈高级别病变/鳞癌研究灵敏度约78.6-81.2%、特异性约74-100%，DOR约10-40；食管鳞癌血清SCC-Ag阳性约8倍富集，更多用于辅助诊断、复发和预后监测",
        "levels": {
            0: {"range": "<1.5", "OR": 0.5, "label": "正常"},
            1: {"range": "1.5-5", "OR": 10, "label": "轻度升高", "note": "鳞癌辅助标志物，轻度升高需结合TCT/HPV或内镜"},
            2: {"range": "5-15", "OR": 20, "label": "中度升高", "note": "中高水平提示宫颈/食管/头颈鳞癌可能，建议定位检查"},
            3: {"range": ">15", "OR": 40, "label": "显著升高", "note": "显著升高更偏向肿瘤负荷/复发监测；缺少统一>15 ng/mL诊断DOR"}
        }
    },
    "NMP22": {
        "cancer": "膀胱癌",
        "unit": "U/mL",
        "normal_upper": 10,
        "evidence": "尿NMP22诊断膀胱癌Meta分析：BladderChek pooled sensitivity约56%、specificity约88%、DOR 9.29；定量NMP22约10 U/mL阈值DOR约9，高分级/高分期肿瘤敏感性更高但特异性低于尿细胞学",
        "levels": {
            0: {"range": "<10", "OR": 0.5, "label": "正常"},
            1: {"range": "10-20", "OR": 9.3, "label": "轻度升高", "note": "10 U/mL阈值Meta分析DOR约9；需结合血尿/感染/膀胱镜"},
            2: {"range": "20-50", "OR": 15, "label": "中度升高", "note": "高分级/高分期敏感性较高；建议膀胱镜检查"},
            3: {"range": ">50", "OR": 20, "label": "显著升高", "note": "显著升高提示较高风险，但缺少>50 U/mL直接DOR证据"}
        }
    }
}

# ============================================================================
# 第三部分：影像学结果赋分
# ============================================================================

# 影像学结果赋分（根据Fleischner Society/NCCN指南调整）
IMAGING_RESULTS = {
    "lung_nodule": {
        "cancer": "肺癌",
        "description": "肺结节（Fleischner指南2017）",
        "evidence": "结节>8mm恶性风险>15%，需密切随访",
        "levels": {
            0: {"description": "无结节", "score": 0},
            1: {"description": "≤5mm", "score": 1, "note": "恶性风险<1%"},
            2: {"description": "5-8mm", "score": 2, "note": "恶性风险1-15%"},
            3: {"description": ">8mm或增大", "score": 3, "note": "恶性风险>15%，建议进一步检查"}
        }
    },
    "thyroid_nodule": {
        "cancer": "甲状腺癌",
        "description": "甲状腺结节TI-RADS（Kwak 2011）",
        "evidence": "TI-RADS 4级恶性风险5-50%，5级>90%",
        "levels": {
            0: {"description": "无/1-2级", "score": 0, "note": "恶性风险0.1%"},
            1: {"description": "3级", "score": 1, "note": "恶性风险0.5%"},
            2: {"description": "4a/4b级", "score": 2, "note": "恶性风险5-50%"},
            3: {"description": "4c/5级", "score": 3, "note": "恶性风险>50%，建议穿刺"}
        }
    },
    "breast_nodule": {
        "cancer": "乳腺癌",
        "description": "乳腺结节BI-RADS分级",
        "evidence": "BI-RADS 4级恶性风险2-95%，5级>95%",
        "levels": {
            0: {"description": "无/1-2级", "score": 0, "note": "恶性风险≈0%"},
            1: {"description": "3级", "score": 1, "note": "恶性风险0.5%"},
            2: {"description": "4a/4b级", "score": 2, "note": "恶性风险10-50%"},
            3: {"description": "4c/5级", "score": 3, "note": "恶性风险>50%，建议活检"}
        }
    },
    "kidney_mass": {
        "cancer": "肾癌",
        "description": "肾脏占位影像学评估",
        "evidence": "实性肾脏占位恶性概率随大小增加：<1 cm约46.3%为良性(恶性约53.7%，odds约1.2)，1-4 cm约20%为良性(恶性约80%，odds约4)，>4 cm良性约8%(恶性约92%，odds约11.5)；高分级风险每增加1 cm约上升13%",
        "levels": {
            0: {"description": "无", "OR": 0.5},
            1: {"description": "≤1cm", "OR": 1.2, "note": "小实性肾占位约46%可为良性，建议随访/进一步定性"},
            2: {"description": "1-4cm", "OR": 4, "note": "1-4 cm实性占位约80%为恶性，但多为低级别"},
            3: {"description": ">4cm", "OR": 12, "note": ">4 cm恶性概率约90%以上，建议泌尿专科评估"}
        }
    },
    "pancreas_mass": {
        "cancer": "胰腺癌",
        "description": "胰腺占位影像学评估",
        "evidence": "胰腺偶发实性病灶需高度警惕：实性PI约占31-65%，常见诊断包括PDAC约31-34%、pNET约23-42%、实性假乳头状肿瘤3-15%和局灶慢性胰腺炎0-11%；≤15 mm小实性病灶中PDAC亦约37%，需EUS/病理定性",
        "levels": {
            0: {"description": "无", "OR": 0.5},
            1: {"description": "异常信号", "OR": 5, "note": "非特异异常建议胰腺增强MRI/CT或EUS评估"},
            2: {"description": "≤2cm", "OR": 10, "note": "小实性病灶仍可为PDAC或pNET，建议EUS-FNA/专科评估"},
            3: {"description": ">2cm", "OR": 25, "note": "较大实性胰腺占位恶性/交界性概率高，但需病理确认"}
        }
    },
    "ovarian_mass": {
        "cancer": "卵巢癌",
        "description": "卵巢占位影像学评估",
        "evidence": "卵巢/附件占位可参考O-RADS：O-RADS 2恶性风险<1%，O-RADS 3为1-<10%，O-RADS 4为10-<50%，O-RADS 5为≥50%；腹水/腹膜结节等进入高风险类别",
        "levels": {
            0: {"description": "无", "OR": 0.5},
            1: {"description": "≤3cm单纯性", "OR": 1, "note": "近似O-RADS 2，恶性风险<1%，通常随访"},
            2: {"description": "3-7cm/复杂性", "OR": 10, "note": "对应O-RADS 3-4范围，恶性风险约1-<50%，建议CA125+专科超声"},
            3: {"description": ">7cm/腹水", "OR": 100, "note": "腹水/腹膜结节等接近O-RADS 5，恶性风险≥50%"}
        }
    },
    "prostate_mri": {
        "cancer": "前列腺癌",
        "description": "前列腺MRI PI-RADS评分",
        "evidence": "PI-RADS v2.1 Meta分析：临床显著前列腺癌检出率约PI-RADS 1为6%、2为9%、3为16%、4为59%、5为85%；≥4阈值灵敏度约81%、特异性约82%",
        "levels": {
            0: {"description": "1-2级", "OR": 0.5, "note": "csPCa检出率约6-9%"},
            1: {"description": "3级", "OR": 2, "note": "csPCa检出率约16%，需结合PSA density决定活检"},
            2: {"description": "4级", "OR": 15, "note": "csPCa检出率约59%，建议靶向活检"},
            3: {"description": "5级", "OR": 57, "note": "csPCa检出率约85%，高度怀疑，建议靶向活检"}
        }
    }
}

# 胃肠镜结果赋分（根据中国早诊早治专家共识）
ENDOSCOPY_RESULTS = {
    "gastric_mirror": {
        "cancer": "胃癌",
        "description": "胃镜病理（胃癌早诊共识2019）",
        "evidence": "胃癌前病变系统综述/Meta分析：胃萎缩和肠上皮化生为Correa级联癌前阶段，胃肠化可使胃癌风险最高约6倍；不完全肠化较完全肠化风险约5倍；低级别异型增生年进展约0.6%，高级别上皮内瘤变隐匿癌/进展风险高",
        "levels": {
            0: {"description": "正常/浅表性胃炎", "OR": 0.5, "note": "未见癌前病变，按低于人群基线处理"},
            1: {"description": "萎缩性胃炎/肠上皮化生", "OR": 4, "note": "癌前级联病变，风险约3-6倍，需结合范围和OLGA/OLGIM分期"},
            2: {"description": "轻度上皮内瘤变", "OR": 5, "note": "低级别异型增生，风险高于单纯萎缩/肠化，建议规范随访或内镜评估"},
            3: {"description": "中重度上皮内瘤变", "OR": 50, "note": "高级别病变接近癌前/早癌诊断场景，应优先内镜切除或病理复核"}
        }
    },
    "esophageal_mirror": {
        "cancer": "食管癌",
        "description": "食管镜病理（食管癌早诊共识2019）",
        "evidence": "中国Linxian高发区前瞻性随访显示，鳞状上皮轻/中/重度异型增生后续食管鳞癌风险呈梯度升高，约为3倍、10倍、28倍量级；重度异型增生/原位癌属近诊断状态",
        "levels": {
            0: {"description": "正常", "OR": 0.5, "note": "未见癌前病变"},
            1: {"description": "轻度不典型增生", "OR": 3, "note": "Linxian随访轻度异型增生风险约3倍"},
            2: {"description": "中度上皮内瘤变", "OR": 10, "note": "Linxian随访中度异型增生风险约10倍，建议短期复查/内镜治疗评估"},
            3: {"description": "重度上皮内瘤变/原位癌", "OR": 30, "note": "Linxian随访重度异型增生风险约28倍；原位癌按诊断性病变处理"}
        }
    },
    "colorectal_mirror": {
        "cancer": "结直肠癌",
        "description": "肠镜病理（结直肠癌筛查共识2023）",
        "evidence": "息肉切除后队列/Meta分析显示，低风险腺瘤后续结直肠癌风险接近或略高于人群基线，高风险/进展期腺瘤风险约2-4倍；高级别上皮内瘤变或癌变属需治疗的近诊断病变",
        "levels": {
            0: {"description": "正常/增生性息肉", "OR": 0.5, "note": "未见腺瘤性癌前病变"},
            1: {"description": "1-2个腺瘤<1cm", "OR": 1.3, "note": "低风险腺瘤，随访后CRC风险接近人群基线"},
            2: {"description": "≥3个或>1cm或高级别", "OR": 4, "note": "高风险/进展期腺瘤，需按指南缩短肠镜随访间隔"},
            3: {"description": "癌变/高度上皮内瘤变", "OR": 50, "note": "已接近诊断性病变，应以切除病理和分期为准，不宜与筛查OR简单叠加"}
        }
    }
}

# 病理结果赋分（根据WHO分类和TBS分类）
PATHOLOGY_RESULTS = {
    "cervical_tct": {
        "cancer": "宫颈癌",
        "description": "宫颈TCT（TBS 2014分类）",
        "evidence": "ASCCP/KPNC风险模型显示，ASC-US/LSIL多为低级别风险；HSIL即时CIN3+风险常约28-60%；CIN2/3为组织学癌前病变，需按诊疗路径处理",
        "levels": {
            0: {"description": "正常/NILM", "OR": 0.5, "note": "阴性细胞学，需结合HPV状态"},
            1: {"description": "ASCUS/LSIL", "OR": 3, "note": "低级别异常，HPV阳性时CIN3+风险上升，建议按ASCCP风险分层"},
            2: {"description": "HSIL", "OR": 30, "note": "HSIL即时CIN3+风险可达约28-60%，建议阴道镜/治疗评估"},
            3: {"description": "CIN2/3", "OR": 50, "note": "组织学癌前病变，按锥切/治疗和随访路径处理"}
        }
    },
    "cervical_hpv": {
        "cancer": "宫颈癌",
        "description": "HPV分型（WHO 2020指南）",
        "evidence": "持续高危HPV是宫颈癌必要风险因素；HPV16/18风险最高，持续感染多年CIN3+累积风险可超过40%，低危型不作为宫颈癌主要致癌型处理",
        "levels": {
            0: {"description": "阴性", "OR": 0.5, "note": "高危HPV阴性提示短期宫颈癌/癌前风险低"},
            1: {"description": "低危型", "OR": 1, "note": "低危型主要相关疣状病变，宫颈癌风险按基线处理"},
            2: {"description": "高危型16/18", "OR": 20, "note": "HPV16/18为最高风险基因型，建议阴道镜或按指南分流"},
            3: {"description": "高危型持续感染", "OR": 50, "note": "持续高危感染提示CIN3+风险显著升高，需结合TCT/阴道镜"}
        }
    },
    "urine_cytology": {
        "cancer": "膀胱癌",
        "description": "尿细胞学",
        "evidence": "Paris System文献显示尿细胞学主要识别高级别尿路上皮癌：AUC高级别恶性风险约8-35%，SHGUC约50-90%，HGUC/positive通常>90%；灵敏度有限但特异性高",
        "levels": {
            0: {"description": "阴性", "OR": 0.5, "note": "阴性不能完全排除低级别肿瘤，需结合血尿和膀胱镜指征"},
            1: {"description": "atypia", "OR": 5, "note": "AUC类别风险中等，建议复查或结合膀胱镜"},
            2: {"description": "suspicious", "OR": 20, "note": "SHGUC高级别恶性风险常约50-90%，建议膀胱镜/上尿路评估"},
            3: {"description": "positive", "OR": 50, "note": "HGUC/positive特异性和阳性预测值高，需活检确认"}
        }
    },
    "breast_biopsy": {
        "cancer": "乳腺癌",
        "description": "乳腺活检病理（WHO 2019）",
        "evidence": "良性乳腺病变Meta分析：非增生性/纤维腺瘤总体风险接近基线或轻度升高，增生性无不典型约1.5-2倍，不典型增生约4-5倍；原位癌/早期浸润已属诊断性病理",
        "levels": {
            0: {"description": "正常", "OR": 0.5, "note": "未见高危病理"},
            1: {"description": "纤维腺瘤/增生", "OR": 1.5, "note": "多数良性病变风险轻度升高，需结合是否复杂性/增生性"},
            2: {"description": "不典型增生", "OR": 4.5, "note": "不典型导管/小叶增生长期乳腺癌风险约4-5倍"},
            3: {"description": "原位癌/早期浸润", "OR": 100, "note": "已属癌或近癌诊断场景，不应作为普通筛查风险倍数叠加"}
        }
    }
}

# 生化指标赋分
BIOCHEMISTRY_RESULTS = {
    "HBsAg": {
        "cancer": "肝癌",
        "evidence": "HBV是肝细胞癌主要病因；REVEAL-HBV等队列显示HBsAg阳性、HBeAg阳性和HBV DNA高载量与HCC风险呈剂量反应关系，高病毒载量可达数十倍风险；仅HBsAb阳性多提示免疫/接种，不作为增风险证据",
        "levels": {
            0: {"description": "阴性", "OR": 0.5, "note": "无HBV感染证据，低于HBV携带者风险"},
            1: {"description": "仅HBsAb阳性", "OR": 0.7, "note": "多提示既往免疫或接种，不应赋增风险"},
            2: {"description": "HBsAg+HBeAb阳性", "OR": 15, "note": "慢性HBV感染/携带者HCC风险显著升高，需结合年龄、肝硬化和AFP/超声"},
            3: {"description": "HBsAg+高病毒载量", "OR": 60, "note": "HBV DNA高载量为强风险因素，按REVEAL-HBV剂量反应取保守高风险倍数"}
        }
    },
    "HCV_Ab": {
        "cancer": "肝癌",
        "evidence": "慢性HCV感染显著增加HCC风险，抗HCV阳性需用HCV RNA区分既往暴露与活动感染；病毒持续复制、肝纤维化/肝硬化时风险最高，抗病毒达到SVR后风险下降但不归零",
        "levels": {
            0: {"description": "阴性", "OR": 0.5, "note": "无HCV感染证据"},
            1: {"description": "阴性但有暴露史", "OR": 1.2, "note": "仅暴露史证据弱，建议复查抗体/RNA而非高权重赋分"},
            2: {"description": "抗HCV阳性", "OR": 10, "note": "提示既往或当前感染，需HCV RNA确认活动感染"},
            3: {"description": "高病毒载量", "OR": 20, "note": "活动性慢性HCV感染，若合并肝硬化风险进一步升高"}
        }
    },
    "ALT_AST": {
        "cancer": "肝癌",
        "evidence": "ALT/AST升高提示肝细胞损伤或炎症，队列研究显示转氨酶升高与HCC风险相关，但其本身非肿瘤特异指标，风险主要由HBV/HCV、酒精、脂肪肝、纤维化/肝硬化等病因驱动",
        "levels": {
            0: {"description": "正常", "OR": 1, "note": "按基线处理"},
            1: {"description": "1-2倍", "OR": 1.5, "note": "轻度肝损伤信号，需复查和病因评估"},
            2: {"description": "2-5倍", "OR": 3, "note": "中度异常，建议结合病毒、脂肪肝、酒精和肝纤维化指标"},
            3: {"description": ">5倍", "OR": 5, "note": "明显异常更提示活动性肝损伤，非HCC特异证据"}
        }
    },
    "eGFR": {
        "cancer": "肾癌",
        "evidence": "CKD与肾癌/尿路上皮癌风险相关，个体参与者Meta分析提示低eGFR和蛋白尿与泌尿系统癌症风险升高有关；轻度eGFR下降证据较弱，重度CKD/透析人群风险更高",
        "levels": {
            0: {"description": "≥90", "OR": 1, "note": "按基线处理"},
            1: {"description": "60-89", "OR": 1.2, "note": "轻度下降，单独作为癌症证据较弱"},
            2: {"description": "30-59", "OR": 1.8, "note": "中度CKD，泌尿系统癌风险轻中度升高"},
            3: {"description": "<30", "OR": 3, "note": "重度CKD/接近ESRD风险较高，需结合透析史、囊性肾病和影像"}
        }
    },
    "hematuria": {
        "cancer": "肾癌/膀胱癌",
        "evidence": "血尿是膀胱癌和肾/上尿路肿瘤常见首发表现；综述与指南提示镜下血尿泌尿系肿瘤检出率通常为低个位数，肉眼血尿膀胱癌检出率可达约20%量级，风险受年龄、性别、吸烟和持续性影响",
        "levels": {
            0: {"description": "无", "OR": 1, "note": "按基线处理"},
            1: {"description": "镜下血尿", "OR": 3, "note": "需按AUA/泌尿外科风险分层，排除结石/感染/肾小球来源"},
            2: {"description": "肉眼血尿", "OR": 10, "note": "可见血尿提示较高泌尿系肿瘤检出概率，建议膀胱镜+上尿路影像"},
            3: {"description": "持续肉眼血尿", "OR": 20, "note": "持续或复发肉眼血尿为强警示信号，需尽快专科评估"}
        }
    },
    "EBV_DNA": {
        "cancer": "鼻咽癌",
        "evidence": "EBV DNA用于鼻咽癌筛查/诊断的Meta分析显示灵敏度约0.76、特异性约0.96、DOR约84；中国南方等高发区前瞻性研究支持EBV抗体/DNA分层筛查，但低水平阳性仍需复测和鼻咽镜/MRI确认",
        "levels": {
            0: {"description": "阴性", "OR": 0.5, "note": "阴性提示短期NPC风险较低"},
            1: {"description": "低水平", "OR": 10, "note": "低水平阳性需复测；单次低拷贝可能假阳性"},
            2: {"description": "中等水平", "OR": 40, "note": "中等水平阳性建议鼻咽镜/影像分流"},
            3: {"description": "高水平/持续", "OR": 84, "note": "持续或高水平EBV DNA接近Meta分析诊断DOR量级，需专科评估"}
        }
    },
    "bilirubin_ALP_GGT": {
        "cancer": "胆道肿瘤",
        "evidence": "胆红素、ALP、GGT升高提示胆汁淤积/胆道梗阻，但对胆道肿瘤缺乏单独诊断特异性；胆管癌诊断仍需影像、CA19-9/CEA和病理，单纯生化异常应保守赋分",
        "levels": {
            0: {"description": "正常", "OR": 1, "note": "按基线处理"},
            1: {"description": "单项轻度", "OR": 1.2, "note": "非特异，常见于炎症、药物、脂肪肝或短暂胆汁淤积"},
            2: {"description": "多项或中度", "OR": 2, "note": "胆汁淤积模式，建议结合腹部超声/CT/MRCP和CA19-9"},
            3: {"description": "显著升高", "OR": 5, "note": "明显梗阻性黄疸需排查胆道/胰头肿瘤，但单独生化证据不宜给过高OR"}
        }
    }
}


