# Evidence Store Changelog


## evidence-v0002 — 2026-05-13T18:54:26Z

- Translated v2 flat evidence store into the v3 lightweight JSON ontology layout.
- 13 cancers, 101 risk factors, 111 risk assertions, 7 Jizaoan detection-performance entries, 13 screening recommendations.
- Source: v2 evidence_store + oncoRAG raw ontology/references.

## evidence-v0002 patch — 2026-05-17

- Added `ontology/cancer_age_sex_priors.json` built from oncoRAG GLOBOCAN
  `incidence_rates.json` (6 cancers covered: lung, liver, gastric, colorectal,
  breast, prostate). Anchor ages 30…75 with 5-year step.
- Lookup contract: age clamped to [min,max] then nearest lower anchor.
- Missing-prior cancers (snapshot_risk surfaces them with
  `status_reason=no_prior_data`, omitted from posterior calc):
  esophageal_cancer, cervical_cancer, ovarian_cancer, bladder_cancer,
  kidney_cancer, head_neck_cancer, biliary_tract_cancer.
- TODO (vendor data missing): pancreatic_cancer is not in the v3 ontology
  because the upstream Jizaoan multi-cancer panel data does not include
  pancreatic. Re-evaluate when the vendor publishes the eighth-cancer
  sensitivity / specificity together with a matching incidence-rate row.
