
TUMOR_MARKERS = {
    "AFP": {
        "cancer": "肝癌",
        "unit": "ng/mL",
        "normal_upper": 20,
        "evidence": "灵敏度60-70%，肝癌筛查核心标志物(IA级证据)",
        "levels": {
            0: {"range": "<7", "OR": 0.5, "label": "正常"},
            1: {"range": "7-20", "OR": 1.5, "label": "轻度升高"},
            2: {"range": "20-200", "OR": 20, "label": "中度升高", "note": "肝癌风险显著增加"},
            3: {"range": ">200", "OR": 100, "label": "显著升高", "note": "高度怀疑肝癌"}
        }
    },
    "CEA": {
        "cancer": "结直肠癌",
        "unit": "ng/mL",
        "normal_upper": 5,
        "evidence": "结直肠癌灵敏度30-40%，胃癌辅助(IIA级证据)",
        "levels": {
            0: {"range": "<2.5", "OR": 0.5, "label": "正常"},
            1: {"range": "2.5-5", "OR": 1.5, "label": "轻度升高"},
            2: {"range": "5-20", "OR": 20, "label": "中度升高", "note": "建议肠镜检查"},
            3: {"range": ">20", "OR": 100, "label": "显著升高", "note": "高度怀疑消化道肿瘤"}
        }
    },
    "CA19-9": {
        "cancer": "胰腺癌/胆道肿瘤",
        "unit": "U/mL",
        "normal_upper": 37,
        "evidence": "胰腺癌灵敏度70-80%，胆道癌灵敏度50-70%(IIA级证据)",
        "levels": {
            0: {"range": "<37", "OR": 0.5, "label": "正常"},
            1: {"range": "37-100", "OR": 5, "label": "轻度升高"},
            2: {"range": "100-500", "OR": 20, "label": "中度升高", "note": "建议影像学检查"},
            3: {"range": ">500", "OR": 100, "label": "显著升高", "note": "高度怀疑胰胆肿瘤"}
        }
    },
    "CA125": {
        "cancer": "卵巢癌",
        "unit": "U/mL",
        "normal_upper": 35,
        "evidence": "卵巢癌灵敏度50-80%，早期灵敏度40-50%(IA级证据)",
        "levels": {
            0: {"range": "<35", "OR": 0.5, "label": "正常"},
            1: {"range": "35-100", "OR": 5, "label": "轻度升高", "note": "建议阴道超声"},
            2: {"range": "100-500", "OR": 20, "label": "中度升高", "note": "卵巢癌风险增加"},
            3: {"range": ">500", "OR": 100, "label": "显著升高", "note": "高度怀疑卵巢癌"}
        }
    },
    "PSA": {
        "cancer": "前列腺癌",
        "unit": "ng/mL",
        "normal_upper": 4,
        "evidence": "前列腺癌灵敏度70-80%，f-PSA/t-PSA<0.15可提高特异性(IA级证据)",
        "levels": {
            0: {"range": "<1", "OR": 0.5, "label": "极低风险"},
            1: {"range": "1-4", "OR": 1, "label": "灰区", "note": "建议f-PSA比值"},
            2: {"range": "4-10", "OR": 20, "label": "轻度升高", "note": "建议前列腺穿刺"},
            3: {"range": ">10", "OR": 100, "label": "显著升高", "note": "高度怀疑前列腺癌"}
        }
    },
    "CYFRA21-1": {
        "cancer": "肺癌",
        "unit": "ng/mL",
        "normal_upper": 3.3,
        "evidence": "肺鳞癌灵敏度50-60%，腺癌30-40%(IIA级证据)",
        "levels": {
            0: {"range": "<3.3", "OR": 0.5, "label": "正常"},
            1: {"range": "3.3-10", "OR": 5, "label": "轻度升高", "note": "建议LDCT"},
            2: {"range": "10-30", "OR": 20, "label": "中度升高", "note": "肺癌风险增加"},
            3: {"range": ">30", "OR": 100, "label": "显著升高", "note": "高度怀疑肺癌"}
        }
    },
    "CA72-4": {
        "cancer": "胃癌",
        "unit": "U/mL",
        "normal_upper": 6.9,
        "evidence": "胃癌灵敏度30-40%，联合CEA可提高至50-60%(IIB级证据)",
        "levels": {
            0: {"range": "<6.9", "OR": 0.5, "label": "正常"},
            1: {"range": "6.9-20", "OR": 2, "label": "轻度升高"},
            2: {"range": "20-50", "OR": 20, "label": "中度升高", "note": "建议胃镜检查"},
            3: {"range": ">50", "OR": 100, "label": "显著升高", "note": "高度怀疑胃癌"}
        }
    },
    "CA15-3": {
        "cancer": "乳腺癌",
        "unit": "U/mL",
        "normal_upper": 25,
        "evidence": "乳腺癌灵敏度30-40%，主要用于疗效监测(IIB级证据)",
        "levels": {
            0: {"range": "<25", "OR": 0.5, "label": "正常"},
            1: {"range": "25-50", "OR": 2, "label": "轻度升高"},
            2: {"range": "50-100", "OR": 20, "label": "中度升高", "note": "建议乳腺检查"},
            3: {"range": ">100", "OR": 100, "label": "显著升高", "note": "高度怀疑乳腺癌"}
        }
    },
    "SCC": {
        "cancer": "宫颈癌/食管癌/头颈肿瘤",
        "unit": "ng/mL",
        "normal_upper": 1.5,
        "evidence": "宫颈鳞癌50-60%，食管鳞癌40-50%，头颈癌30-40%(IIA级证据)",
        "levels": {
            0: {"range": "<1.5", "OR": 0.5, "label": "正常"},
            1: {"range": "1.5-5", "OR": 2, "label": "轻度升高"},
            2: {"range": "5-15", "OR": 20, "label": "中度升高", "note": "建议TCT/内镜检查"},
            3: {"range": ">15", "OR": 100, "label": "显著升高", "note": "高度怀疑鳞癌"}
        }
    },
    "NMP22": {
        "cancer": "膀胱癌",
        "unit": "U/mL",
        "normal_upper": 10,
        "evidence": "膀胱癌灵敏度50-70%，高分级70-80%(IIB级证据)",
        "levels": {
            0: {"range": "<10", "OR": 0.5, "label": "正常"},
            1: {"range": "10-20", "OR": 2, "label": "轻度升高"},
            2: {"range": "20-50", "OR": 20, "label": "中度升高", "note": "建议膀胱镜检查"},
            3: {"range": ">50", "OR": 100, "label": "显著升高", "note": "高度怀疑膀胱癌"}
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
        "evidence": "肾脏小占位多为良性，但>4cm需警惕",
        "levels": {
            0: {"description": "无", "OR": 0.5},
            1: {"description": "≤1cm", "OR": 2, "note": "建议随访"},
            2: {"description": "1-4cm", "OR": 10, "note": "建议进一步评估"},
            3: {"description": ">4cm", "OR": 100, "note": "高度怀疑恶性"}
        }
    },
    "pancreas_mass": {
        "cancer": "胰腺癌",
        "description": "胰腺占位影像学评估",
        "evidence": "胰腺占位需高度警惕，早期症状隐匿",
        "levels": {
            0: {"description": "无", "OR": 0.5},
            1: {"description": "异常信号", "OR": 10, "note": "建议EUS评估"},
            2: {"description": "≤2cm", "OR": 20, "note": "可切除性高"},
            3: {"description": ">2cm", "OR": 100, "note": "高度警惕胰腺癌"}
        }
    },
    "ovarian_mass": {
        "cancer": "卵巢癌",
        "description": "卵巢占位影像学评估",
        "evidence": "绝经后卵巢肿物需警惕，>7cm复杂性需重视",
        "levels": {
            0: {"description": "无", "OR": 0.5},
            1: {"description": "≤3cm单纯性", "OR": 2, "note": "随访观察"},
            2: {"description": "3-7cm/复杂性", "OR": 20, "note": "建议CA125+超声"},
            3: {"description": ">7cm/腹水", "OR": 100, "note": "高度怀疑恶性"}
        }
    },
    "prostate_mri": {
        "cancer": "前列腺癌",
        "description": "前列腺MRI PI-RADS评分",
        "evidence": "PI-RADS 5级前列腺癌风险>90%",
        "levels": {
            0: {"description": "1-2级", "OR": 0.5, "note": "可能性极低"},
            1: {"description": "3级", "OR": 5, "note": "建议活检"},
            2: {"description": "4级", "OR": 20, "note": "中高度怀疑"},
            3: {"description": "5级", "OR": 100, "note": "高度怀疑，建议活检"}
        }
    }
}

# 胃肠镜结果赋分（根据中国早诊早治专家共识）
ENDOSCOPY_RESULTS = {
    "gastric_mirror": {
        "cancer": "胃癌",
        "description": "胃镜病理（胃癌早诊共识2019）",
        "evidence": "萎缩性胃炎癌变风险2-6倍，肠化3-5倍，高级别瘤变60-80%",
        "levels": {
            0: {"description": "正常/浅表性胃炎", "OR": 0.5, "note": "基线风险"},
            1: {"description": "萎缩性胃炎/肠上皮化生", "OR": 4, "note": "癌变风险2-6倍"},
            2: {"description": "轻度上皮内瘤变", "OR": 4.5, "note": "癌变风险4-5倍"},
            3: {"description": "中重度上皮内瘤变", "OR": 100, "note": "高度怀疑癌变，需切除"}
        }
    },
    "esophageal_mirror": {
        "cancer": "食管癌",
        "description": "食管镜病理（食管癌早诊共识2019）",
        "evidence": "中国90%为鳞癌，Barrett食管主要见于西方",
        "levels": {
            0: {"description": "正常", "OR": 0.5, "note": "基线风险"},
            1: {"description": "轻度不典型增生", "OR": 4, "note": "需密切随访"},
            2: {"description": "中度上皮内瘤变", "OR": 20, "note": "癌变风险增加"},
            3: {"description": "重度上皮内瘤变/原位癌", "OR": 100, "note": "高度怀疑癌变"}
        }
    },
    "colorectal_mirror": {
        "cancer": "结直肠癌",
        "description": "肠镜病理（结直肠癌筛查共识2023）",
        "evidence": "腺瘤癌变风险3-5倍，多发腺瘤5-7倍，高级别瘤变25-50%",
        "levels": {
            0: {"description": "正常/增生性息肉", "OR": 0.5, "note": "基线风险"},
            1: {"description": "1-2个腺瘤<1cm", "OR": 2.5, "note": "癌变风险2-3倍"},
            2: {"description": "≥3个或>1cm或高级别", "OR": 7.5, "note": "癌变风险5-10倍"},
            3: {"description": "癌变/高度上皮内瘤变", "OR": 100, "note": "需切除治疗"}
        }
    }
}

# 病理结果赋分（根据WHO分类和TBS分类）
PATHOLOGY_RESULTS = {
    "cervical_tct": {
        "cancer": "宫颈癌",
        "description": "宫颈TCT（TBS 2014分类）",
        "evidence": "CIN2+为癌前病变，5年进展风险>20%",
        "levels": {
            0: {"description": "正常/NILM", "OR": 0.5, "note": "基线风险"},
            1: {"description": "ASCUS/LSIL", "OR": 2, "note": "低级别病变"},
            2: {"description": "HSIL", "OR": 20, "note": "高级别病变，建议阴道镜"},
            3: {"description": "CIN2/3", "OR": 100, "note": "癌前病变，需锥切"}
        }
    },
    "cervical_hpv": {
        "cancer": "宫颈癌",
        "description": "HPV分型（WHO 2020指南）",
        "evidence": "HPV16/18致癌性最强，持续感染5年CIN3风险>40%",
        "levels": {
            0: {"description": "阴性", "OR": 0.5, "note": "基线风险"},
            1: {"description": "低危型", "OR": 2, "note": "低致癌风险"},
            2: {"description": "高危型16/18", "OR": 20, "note": "高致癌风险"},
            3: {"description": "高危型持续感染", "OR": 100, "note": "需阴道镜+ECC"}
        }
    },
    "urine_cytology": {
        "cancer": "膀胱癌",
        "description": "尿细胞学",
        "evidence": "阳性预测值>90%，但灵敏度较低",
        "levels": {
            0: {"description": "阴性", "OR": 0.5, "note": "基线风险"},
            1: {"description": "atypia", "OR": 5, "note": "需复查"},
            2: {"description": "suspicious", "OR": 20, "note": "建议膀胱镜"},
            3: {"description": "positive", "OR": 100, "note": "高度怀疑，需活检"}
        }
    },
    "breast_biopsy": {
        "cancer": "乳腺癌",
        "description": "乳腺活检病理（WHO 2019）",
        "evidence": "不典型增生癌变风险4-5倍，原位癌100%治愈",
        "levels": {
            0: {"description": "正常", "OR": 0.5, "note": "基线风险"},
            1: {"description": "纤维腺瘤/增生", "OR": 2, "note": "癌变风险略增"},
            2: {"description": "不典型增生", "OR": 4.5, "note": "癌变风险4-5倍"},
            3: {"description": "原位癌/早期浸润", "OR": 10000, "note": "需手术切除"}
        }
    }
}

# 生化指标赋分
BIOCHEMISTRY_RESULTS = {
    "HBsAg": {
        "cancer": "肝癌",
        "levels": {
            0: {"description": "阴性", "OR": 0.5},
            1: {"description": "仅HBsAb阳性", "OR": 1.5},
            2: {"description": "HBsAg+HBeAb阳性", "OR": 5},
            3: {"description": "HBsAg+高病毒载量", "OR": 20}
        }
    },
    "HCV_Ab": {
        "cancer": "肝癌",
        "levels": {
            0: {"description": "阴性", "OR": 0.5},
            1: {"description": "阴性但有暴露史", "OR": 1.5},
            2: {"description": "抗HCV阳性", "OR": 5},
            3: {"description": "高病毒载量", "OR": 20}
        }
    },
    "ALT_AST": {
        "cancer": "肝癌",
        "levels": {
            0: {"description": "正常", "OR": 1},
            1: {"description": "1-2倍", "OR": 1.5},
            2: {"description": "2-5倍", "OR": 2.5},
            3: {"description": ">5倍", "OR": 5}
        }
    },
    "eGFR": {
        "cancer": "肾癌",
        "levels": {
            0: {"description": "≥90", "OR": 1},
            1: {"description": "60-89", "OR": 1.5},
            2: {"description": "30-59", "OR": 2.5},
            3: {"description": "<30", "OR": 5}
        }
    },
    "hematuria": {
        "cancer": "肾癌/膀胱癌",
        "levels": {
            0: {"description": "无", "OR": 1},
            1: {"description": "镜下血尿", "OR": 2},
            2: {"description": "肉眼血尿", "OR": 5},
            3: {"description": "持续肉眼血尿", "OR": 10}
        }
    },
    "EBV_DNA": {
        "cancer": "鼻咽癌",
        "levels": {
            0: {"description": "阴性", "OR": 0.5},
            1: {"description": "低水平", "OR": 1.5},
            2: {"description": "中等水平", "OR": 5},
            3: {"description": "高水平/持续", "OR": 10}
        }
    },
    "bilirubin_ALP_GGT": {
        "cancer": "胆道肿瘤",
        "levels": {
            0: {"description": "正常", "OR": 1},
            1: {"description": "单项轻度", "OR": 1.5},
            2: {"description": "多项或中度", "OR": 5},
            3: {"description": "显著升高", "OR": 10}
        }
    }
}


