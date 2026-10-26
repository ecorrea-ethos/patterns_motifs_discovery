# Graph Report - ethos_foundation_llm  (2026-10-16)

## Corpus Check
- 110 files · ~178,743 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1695 nodes · 3405 edges · 126 communities (106 shown, 19 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 459 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- d3.v7.min.js (vendored)
- fu() Cluster
- Motif Discovery Engine
- d3 Minified Internals 3
- d3 Minified Internals 4
- Letrozole Script (full)
- Letrozole Script (win12)
- Letrozole Script (win18)
- Letrozole Script (win24)
- d3 Minified Internals 9
- d3 Minified Internals 10
- d3 Minified Internals 11
- Robustness Pipeline (repr_learn)
- Robustness Pipeline (sensitivity)
- d3 Minified Internals 14
- Chest Pain NMF/AHA Handoff
- Day 1 NMF Performance & Glossary
- d3 Minified Internals 17
- d3 Minified Internals 18
- Motif Families & Hybrid (repr_learn)
- Motif Families & Hybrid (sensitivity)
- Chest Pain OMOP Loader
- d3 Minified Internals 22
- AHA Literature Fill Scripts
- PrefixSpan Mining (repr_learn)
- Stability & OOT (repr_learn)
- PrefixSpan Mining (sensitivity)
- Stability & OOT (sensitivity)
- Chest Pain Predicate Engine v3
- Codeset YAML Versions
- Day 3 Robustness Plan
- d3 Minified Internals 31
- Weak Labels & Breast Cancer Codesets
- Breast Cancer OMOP Loader
- d3 Minified Internals 34
- d3 Minified Internals 35
- PubMed Literature Skill
- d3 Minified Internals 37
- Scoring & FWER (repr_learn)
- Scoring & FWER (sensitivity)
- OMOP Loader (variant A)
- Weak Labels & Flow Plot
- Diabetes/Letrozole Predicate Engines
- d3 Minified Internals 43
- Letrozole OMOP Loader
- OMOP Loader (variant B)
- OMOP Loader (variant C)
- Sensitivity OMOP Loader
- OMOP Loader (variant D)
- Cohort Extract (A)
- Cohort Extract (B)
- Cohort Extract (C)
- Mammography OMOP Loader
- Cohort Extract (D)
- Cohort Extract (E)
- Group Loadings (A)
- d3 Minified Internals 56
- d3 Minified Internals 57
- Robustness Config YAMLs
- Group Loadings (B)
- Run Manifest (repr_learn)
- Group Loadings (C)
- Group Loadings (D)
- Run Manifest (sensitivity)
- Letrozole Literature Scripts
- Evidence Store (repr_learn)
- Evidence Store (sensitivity)
- Letrozole Full vs Windowed Summary
- Index Dates & Weak Labels (A)
- Index Dates & Weak Labels (B)
- Letrozole Window Run Logs
- CLMBR Reproduction & Repo Overview
- Chest Pain Literature
- First-Tag-Wins Ordering
- d3 Minified Internals 74
- jm() Cluster
- Tag Events (A)
- Cardiac Workup Outcome
- Tag Events (B)
- Tag Events (C)
- Seq Index Matching (repr_learn)
- Tag Events (D)
- Index Dates (C)
- Tag Events (E)
- Seq Index Matching (sensitivity)
- Sankey Runs
- d3 Minified Internals 86
- d3 Minified Internals 87
- d3 Minified Internals 88
- build_codesets() Cluster
- index_dates() Cluster
- observation_window() Cluster
- build_plain_english_annex.py Cluster
- build_codesets() Cluster
- observation_window() Cluster
- d3 Minified Internals 95
- build_codesets() Cluster
- observation_window() Cluster
- repr_learn_letrozole/motif_robustness/ve Cluster
- build_codesets() Cluster
- observation_window() Cluster
- build_codesets() Cluster
- observation_window() Cluster
- sensitivity_letrozole/motif_robustness/v Cluster
- repr_learn_breastcancer/make_demo_extrac Cluster
- check_codesets.py Cluster
- fetch_abstracts.py Cluster
- repr_learn_chestpain/make_demo_extract.p Cluster
- trajectory_anim.py Cluster
- d3 Minified Internals 109
- d3 Minified Internals 110
- d3 Minified Internals 111
- d3 Minified Internals 112
- d3 Minified Internals 113
- d3 Minified Internals 114
- run_all.sh Cluster
- bag_of_codes() Cluster
- Keep only events at or before each patie Cluster
- repr_learn_chestpain/literature_search/v Cluster
- d3 Minified Internals 119
- d3 Minified Internals 120
- repr_learn_letrozole/literature_search/v Cluster
- repr_learn_mammography/motif_robustness/ Cluster
- run_variant.py Cluster
- requirements.txt Cluster

## God Nodes (most connected - your core abstractions)
1. `n()` - 68 edges
2. `e()` - 59 edges
3. `r()` - 54 edges
4. `o()` - 50 edges
5. `i()` - 48 edges
6. `u()` - 46 edges
7. `a()` - 43 edges
8. `F()` - 35 edges
9. `hv()` - 35 edges
10. `A()` - 33 edges

## Surprising Connections (you probably didn't know these)
- `48 abbreviations glossary` --semantically_similar_to--> `Glossary`  [INFERRED] [semantically similar]
  nb/repr_learn_chestpain/chestpain_plain_labels.yaml → docs/glossary.md
- `UW wording vs data-team wording table` --semantically_similar_to--> `Glossary`  [INFERRED] [semantically similar]
  nb/repr_learn_chestpain/chestpain_plain_labels.yaml → docs/glossary.md
- `Letrozole full-history NMF (k=7) vs windowed +/-18 mo NMF (k=13) summary` --semantically_similar_to--> `Chest pain: three NMF runs compared (sanity check AHA)`  [INFERRED] [semantically similar]
  nb/repr_learn_letrozole/letrozole_full_vs_windowed_summary.pdf → nb/repr_learn_chestpain/sanity_check_AHA.md
- `PMID verification against PubMed esummary` --semantically_similar_to--> `No PMID from memory rule`  [INFERRED] [semantically similar]
  docs/literature-search.md → .claude/skills/pubmed-literature-check/SKILL.md
- `Search basis rule (3 of top-5 entities ANDed or order-of-care steps)` --semantically_similar_to--> `PubMed search rule (entities unordered or order-of-care steps)`  [INFERRED] [semantically similar]
  .claude/skills/pubmed-literature-check/SKILL.md → docs/literature-search.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **PubMed literature check workflow (skill, guide, scripts, final table)** — _claude_skills_pubmed_literature_check_skill, docs_literature_search, _claude_skills_pubmed_literature_check_skill_pubmed_scripts, handoff_final_table_k8_aha, docs_literature_search_pmid_verification [INFERRED 0.85]
- **Chest pain predicate engine v1 / v2 / v3 plus plain-English layer** — nb_repr_learn_chestpain_chestpain_workup_predicate_engine, nb_repr_learn_chestpain_chestpain_workup_predicate_engine_v2, nb_repr_learn_chestpain_chestpain_workup_predicate_engine_v3, nb_repr_learn_chestpain_chestpain_plain_labels, nb_repr_learn_chestpain_diabetes_rx_predicate_engine [INFERRED 0.85]
- **Day 1 NMF pipeline (labels, prevalence floor, sparse sweep, k validation)** — docs_event_labels_fallback_label, docs_event_labels_prevalence_floor, docs_day1_performance_sparse_xs, docs_day1_performance_parallel_sweep, docs_nmf_validation_nmf_kw, docs_nmf_validation_k_sweep [INFERRED 0.85]
- **Letrozole window sensitivity runs (full vs +/-12/18/24 months)** — nb_sensitivity_letrozole_log_full, nb_sensitivity_letrozole_log_win12, nb_sensitivity_letrozole_log_win18, nb_sensitivity_letrozole_log_win24 [EXTRACTED 1.00]
- **Chest pain NMF run comparison (full k5, full k8, AHA k8)** — nb_repr_learn_chestpain_sanity_check_aha_nmf_full_k5, nb_repr_learn_chestpain_sanity_check_aha_nmf_full_k8, nb_repr_learn_chestpain_sanity_check_aha_nmf_aha_k8, nb_repr_learn_chestpain_sanity_check_aha_ed_bundle [EXTRACTED 1.00]
- **Cohort codeset YAMLs sharing the first-tag-wins ordered tag spec** — nb_repr_learn_chestpain_codesets_v2, nb_repr_learn_letrozole_codesets, nb_repr_learn_mammography_codesets, nb_repr_learn_chestpain_codesets [INFERRED 0.85]

## Communities (126 total, 19 thin omitted)

### Community 0 - "d3.v7.min.js (vendored)"
Cohesion: 0.01
Nodes (58): an(), ap(), au(), bl(), ch(), cw(), Dc(), di() (+50 more)

### Community 1 - "fu() Cluster"
Cohesion: 0.07
Nodes (10): fu(), Ia(), ku(), lu(), qu, quadraticCurveTo(), Ru, su() (+2 more)

### Community 2 - "Motif Discovery Engine"
Cohesion: 0.05
Nodes (55): add_heldout(), _bootstrap_lift(), discover(), _mine(), Group-vs-rest ordered-motif discovery with robustness tiers, generic over the…, Motifs for every group id >= 0 in `groups` (one id per patient, aligned with…, Candidate motifs from a group's sequences; a group larger than `mine_cap` is…, Hit matrix [in-group | outside sample] for `cands`, plus the support / lift… (+47 more)

### Community 3 - "d3 Minified Internals 3"
Cohesion: 0.09
Nodes (54): ax(), bd(), a(), C(), Cg(), ct(), draw(), s() (+46 more)

### Community 4 - "d3 Minified Internals 4"
Cohesion: 0.10
Nodes (37): g(), ae(), l(), b(), copy(), d(), w(), g() (+29 more)

### Community 5 - "Letrozole Script (full)"
Cohesion: 0.07
Nodes (28): bootstrap_lift(), _component_job(), component_motifs(), _condense_name(), contains(), discriminative(), dist_to_all(), label() (+20 more)

### Community 6 - "Letrozole Script (win12)"
Cohesion: 0.07
Nodes (28): bootstrap_lift(), _component_job(), component_motifs(), _condense_name(), contains(), discriminative(), dist_to_all(), label() (+20 more)

### Community 7 - "Letrozole Script (win18)"
Cohesion: 0.07
Nodes (28): bootstrap_lift(), _component_job(), component_motifs(), _condense_name(), contains(), discriminative(), dist_to_all(), label() (+20 more)

### Community 8 - "Letrozole Script (win24)"
Cohesion: 0.07
Nodes (28): bootstrap_lift(), _component_job(), component_motifs(), _condense_name(), contains(), discriminative(), dist_to_all(), label() (+20 more)

### Community 9 - "d3 Minified Internals 9"
Cohesion: 0.14
Nodes (26): al(), c(), Bf(), fe(), ft(), gl(), hl(), a() (+18 more)

### Community 10 - "d3 Minified Internals 10"
Cohesion: 0.09
Nodes (31): at(), e(), cp(), dg(), dp(), eo(), fp(), Gm() (+23 more)

### Community 11 - "d3 Minified Internals 11"
Cohesion: 0.14
Nodes (19): A(), bt(), b(), gg(), i(), Gi(), hs(), w() (+11 more)

### Community 12 - "Robustness Pipeline (repr_learn)"
Cohesion: 0.11
Nodes (25): Day 3 v3: motif-robustness pipeline for the letrozole cohort (see…, write_manifest(), load_cfg(), main(), prepare(), Orchestrator for the first three robustness tiers. Run from…, Load once: events, dated patient sequences, component labels (fixed Day 1 v2…, write_outputs() (+17 more)

### Community 13 - "Robustness Pipeline (sensitivity)"
Cohesion: 0.11
Nodes (25): Day 3 v3: motif-robustness pipeline for the letrozole cohort (see…, write_manifest(), load_cfg(), main(), prepare(), Orchestrator for the first three robustness tiers. Run from…, Load once: events, dated patient sequences, component labels (fixed Day 1 v2…, write_outputs() (+17 more)

### Community 14 - "d3 Minified Internals 14"
Cohesion: 0.11
Nodes (28): ar(), brighter(), Ce(), cr(), darker(), de(), displayable(), dr() (+20 more)

### Community 15 - "Chest Pain NMF/AHA Handoff"
Cohesion: 0.12
Nodes (25): NMF bundles describe care delivery, not condition, Chest pain k=8 components reading (c3 acute ED workup), AHA k=8 reference run (c3 acute/ED work-up, 17,250 patients), Chestpain_NMF_PrefixSpan_AHA.ipynb, codesets_v2.yaml (70 tags, AHA/ACC guideline), Group-token and YAML-order gotchas, Plain-English layer (labels yaml -> annex build script), sanity_check_AHA.md (three-run comparison with Sankeys) (+17 more)

### Community 16 - "Day 1 NMF Performance & Glossary"
Cohesion: 0.12
Nodes (24): Day 1 performance: sparse matrix and parallel sweep, Parallel k sweep (joblib), Sparse CSR matrix Xs, Event labels and the prevalence floor, Unique fallback label name__class__concept_id, Prevalence floor (patients per code, KEEP_TAGS), Glossary, ARI (adjusted Rand index; 0.75 solid, 0.60 suggestive) (+16 more)

### Community 17 - "d3 Minified Internals 17"
Cohesion: 0.12
Nodes (15): ad(), bs(), cd(), ed, fd(), T(), ml(), sd() (+7 more)

### Community 18 - "d3 Minified Internals 18"
Cohesion: 0.09
Nodes (22): Av(), bv(), Cv(), Dv(), Ev(), Gv(), hv(), jv() (+14 more)

### Community 19 - "Motif Families & Hybrid (repr_learn)"
Cohesion: 0.18
Nodes (19): cluster_families(), family_any(), Motif families: near-duplicate motifs (same patients, one extra step) are one…, member_matrix: bool (n_motifs, n_eval). Family-level 'found' = any member…, H_in: bool (n_motifs, n_in_patients) coverage of each motif among the…, add_heldout_chestpain(), add_heldout_letrozole(), Held-out pass rate, family clustering, same-day flag and the hybrid verdict,… (+11 more)

### Community 20 - "Motif Families & Hybrid (sensitivity)"
Cohesion: 0.18
Nodes (19): cluster_families(), family_any(), Motif families: near-duplicate motifs (same patients, one extra step) are one…, member_matrix: bool (n_motifs, n_eval). Family-level 'found' = any member…, H_in: bool (n_motifs, n_in_patients) coverage of each motif among the…, add_heldout_chestpain(), add_heldout_letrozole(), Held-out pass rate, family clustering, same-day flag and the hybrid verdict,… (+11 more)

### Community 21 - "Chest Pain OMOP Loader"
Cohesion: 0.15
Nodes (16): expand_descendants(), load_concept(), load_death(), load_events(), load_person(), load_truth(), ethos_omop.py — extract from ETHOS_PRODUCTION.OMOP_54 and load into the shape…, Union the domain tables into one long event stream. Returns person_id,… (+8 more)

### Community 22 - "d3 Minified Internals 22"
Cohesion: 0.11
Nodes (19): Bg(), cf(), l(), Eg(), ff(), hf(), Ig(), Jc() (+11 more)

### Community 23 - "AHA Literature Fill Scripts"
Cohesion: 0.13
Nodes (11): Fill Triage suggestion (M), Supported literature (O) and PMIDs (P) of…, Search definitions for the literature column of…, Round 1 for the AHA k=8 table. Every bundle: all 3-of-5 entity combinations…, run(), Round 2 for the AHA k=8 table. Bundle entities plus the bundle's clinical…, curl(), q(), PubMed (NLM E-utilities) helpers for the literature column of the chest pain… (+3 more)

### Community 24 - "PrefixSpan Mining (repr_learn)"
Cohesion: 0.20
Nodes (16): contains(), mine_candidates(), prefixspan(), PrefixSpan (moved from the v2 notebook) with deterministic ties. v2 iterated…, db: list of token lists. Returns DataFrame(pattern tuple, support, support_pct)…, v2 definition (tie-ordered subsequence)., Top `max_cand` ordered patterns of >= min_len steps present in >= rel_sup of…, run_phase0() (+8 more)

### Community 25 - "Stability & OOT (repr_learn)"
Cohesion: 0.17
Nodes (17): run_core(), holdout_matrix(), _mine_half(), nominated_sets(), oot_eval(), oot_split(), passes(), pre_index_eval() (+9 more)

### Community 26 - "PrefixSpan Mining (sensitivity)"
Cohesion: 0.20
Nodes (16): contains(), mine_candidates(), prefixspan(), PrefixSpan (moved from the v2 notebook) with deterministic ties. v2 iterated…, db: list of token lists. Returns DataFrame(pattern tuple, support, support_pct)…, v2 definition (tie-ordered subsequence)., Top `max_cand` ordered patterns of >= min_len steps present in >= rel_sup of…, run_phase0() (+8 more)

### Community 27 - "Stability & OOT (sensitivity)"
Cohesion: 0.17
Nodes (17): run_core(), holdout_matrix(), _mine_half(), nominated_sets(), oot_eval(), oot_split(), passes(), pre_index_eval() (+9 more)

### Community 28 - "Chest Pain Predicate Engine v3"
Cohesion: 0.12
Nodes (17): ASD-STE100 check by script, not certified, Open item: nothing measured on real patients, UW wording vs data-team wording table, composite_c3_manual_ruw flag rule, Lipase, IV push, CMP, CBC are not chest-pain specific, Work-up sequences A, B, C (4-step chest pain ... CMP/CBC), Work-up service in window (1 day, symmetric, uncalibrated), Chest Pain Work-up Predicate Engine v3 (short UW page, ASD-STE100) (+9 more)

### Community 29 - "Codeset YAML Versions"
Cohesion: 0.15
Nodes (16): Chest pain codesets.yaml (v4), chest_pain anchor tag (chest pain, precordial pain, intercostal space), ethos_omop_taxonomy_crosswalk.csv, Name-resolution over literal concept_ids (portable codesets), psych_eval_therapy / psych_screen tags (literal concept_ids, pending review), Chest pain codesets_v2.yaml (v5, AHA/ACC guideline rewrite), Cardiac and noncardiac cause tags (acs_mi, angina, old_mi, GERD, etc.), check_codesets.py (codeset validation script) (+8 more)

### Community 30 - "Day 3 Robustness Plan"
Cohesion: 0.18
Nodes (15): Day 3 v3 motif robustness implementation plan, Day-block permutation null (order test), Determinism and run manifest, Duplicate-coding detection (same-day rate, review-only), Effect sizes, FDR and label-permutation FWER, Evidence plots and per-motif evidence cards, Known unknowns (order-type column, decision date, thresholds), Record-length confounding (Mantel-Haenszel OR, SMD) (+7 more)

### Community 31 - "d3 Minified Internals 31"
Cohesion: 0.20
Nodes (12): M(), dd(), e(), m(), v(), y(), F(), gd() (+4 more)

### Community 32 - "Weak Labels & Breast Cancer Codesets"
Cohesion: 0.16
Nodes (14): Criterion validity (c5 vs confirmed breast cancer), Weak label (co-evidence probe label), chest_pain_labels() psych vs cardiac co-evidence, breast cancer codesets.yaml (v1-v6 bitacora), Aromatase inhibitor tags (letrozole, anastrozole, exemestane, tamoxifen), breast_cancer v5 over-match fix (dropped 'neoplasm of breast'), Patterns are unanchored substring regex via resolve(), Breast cancer course README (5-day pattern discovery) (+6 more)

### Community 33 - "Breast Cancer OMOP Loader"
Cohesion: 0.14
Nodes (10): bag_of_codes(), ethos_omop.py — extract from ETHOS_PRODUCTION.OMOP_54 and load into the shape…, Patient x code matrix. The representation we are trying to beat., person_id -> ordered token list. Two decisions, both arbitrary and both written…, Keep only events at or before each patient's index_date. Prevents leakage., Rule-based PROBE labels for the letrozole indication, from corroborating co-…, # NOTE: breast_cancer is deliberately NOT oncology evidence. A fertility, sequences() (+2 more)

### Community 34 - "d3 Minified Internals 34"
Cohesion: 0.15
Nodes (14): Ai(), ao(), Ci(), co(), fo(), Hi(), ji(), ki() (+6 more)

### Community 35 - "d3 Minified Internals 35"
Cohesion: 0.14
Nodes (14): bp(), e(), Fx(), gp(), Ip(), ix(), jx(), Kx() (+6 more)

### Community 36 - "PubMed Literature Skill"
Cohesion: 0.21
Nodes (13): pubmed-literature-check skill, curl instead of Python HTTPS (corporate TLS proxy), Final table columns M/O/P (triage, literature, PMIDs), No PMID from memory rule, literature_search scripts (pubmed.py, search_entities_patterns.py, search_setting.py, verify_pmids.py), Search basis rule (3 of top-5 entities ANDed or order-of-care steps), Literature column and triage guide, final_table_letrozole_k7_full.xlsx (worked example) (+5 more)

### Community 37 - "d3 Minified Internals 37"
Cohesion: 0.18
Nodes (13): a(), Df(), dl(), ds(), el(), gs(), Ks(), ps() (+5 more)

### Community 38 - "Scoring & FWER (repr_learn)"
Cohesion: 0.22
Nodes (12): fisher_greater(), label_permutation_fwer(), log_or(), newcombe_diff(), Effect sizes with CIs, multiple-testing control. All from 2x2 tables: in/out…, Newcombe (method 10) CI for p1 - p2 from Wilson intervals., Haldane-Anscombe (+0.5) log odds ratio and Woolf SE. a, c = motif hits in /…, One-sided (enrichment in the component) Fisher exact p-values. (+4 more)

### Community 39 - "Scoring & FWER (sensitivity)"
Cohesion: 0.22
Nodes (12): fisher_greater(), label_permutation_fwer(), log_or(), newcombe_diff(), Effect sizes with CIs, multiple-testing control. All from 2x2 tables: in/out…, Newcombe (method 10) CI for p1 - p2 from Wilson intervals., Haldane-Anscombe (+0.5) log odds ratio and Woolf SE. a, c = motif hits in /…, One-sided (enrichment in the component) Fisher exact p-values. (+4 more)

### Community 40 - "OMOP Loader (variant A)"
Cohesion: 0.20
Nodes (12): expand_descendants(), load_concept(), load_death(), load_events(), load_person(), load_truth(), Union the domain tables into one long event stream. Returns person_id,…, Roll a code set down through concept_ancestor (ingredient -> all products). (+4 more)

### Community 41 - "Weak Labels & Flow Plot"
Cohesion: 0.18
Nodes (8): chest_pain_labels(), Events of group/tag `tag`: every group the concept is in (col=None) or an…, Rule-based PROBE labels for the letrozole indication, from corroborating co-…, Rule-based PROBE labels for the dx_9487 chest-pain triage question, from…, _select(), weak_labels(), Draw the decision flow of the chest pain c3 pattern for the UW team. usage…, tag()

### Community 42 - "Diabetes/Letrozole Predicate Engines"
Cohesion: 0.17
Nodes (12): predicates_v3.md (empty file), Diabetes Rx Predicate Engine, Atomic predicates and composites pattern, GLP-1 indication resolution by brand (diabetes vs obesity), Diabetes regimen ladder (oral classes, basal/bolus/premixed insulin), Letrozole Rx Predicate Engine, Entity registry (OMOP concepts for letrozole predicates), 74-day late threshold (median offset in c5) (+4 more)

### Community 43 - "d3 Minified Internals 43"
Cohesion: 0.17
Nodes (12): bw(), dw(), fv(), M(), i(), Ka(), lv(), ou() (+4 more)

### Community 44 - "Letrozole OMOP Loader"
Cohesion: 0.17
Nodes (8): bag_of_codes(), ethos_omop.py — extract from ETHOS_PRODUCTION.OMOP_54 and load into the shape…, Patient x code matrix. The representation we are trying to beat., person_id -> ordered token list. Two decisions, both arbitrary and both written…, Keep only events at or before each patient's index_date. Prevents leakage., # NOTE: breast_cancer is deliberately NOT oncology evidence. A fertility, sequences(), truncate_at()

### Community 45 - "OMOP Loader (variant B)"
Cohesion: 0.20
Nodes (12): expand_descendants(), load_concept(), load_death(), load_events(), load_person(), load_truth(), Union the domain tables into one long event stream. Returns person_id,…, Roll a code set down through concept_ancestor (ingredient -> all products). (+4 more)

### Community 46 - "OMOP Loader (variant C)"
Cohesion: 0.20
Nodes (12): expand_descendants(), load_concept(), load_death(), load_events(), load_person(), load_truth(), Union the domain tables into one long event stream. Returns person_id,…, Roll a code set down through concept_ancestor (ingredient -> all products). (+4 more)

### Community 47 - "Sensitivity OMOP Loader"
Cohesion: 0.17
Nodes (8): bag_of_codes(), ethos_omop.py — extract from ETHOS_PRODUCTION.OMOP_54 and load into the shape…, Patient x code matrix. The representation we are trying to beat., person_id -> ordered token list. Two decisions, both arbitrary and both written…, Keep only events at or before each patient's index_date. Prevents leakage., # NOTE: breast_cancer is deliberately NOT oncology evidence. A fertility, sequences(), truncate_at()

### Community 48 - "OMOP Loader (variant D)"
Cohesion: 0.20
Nodes (12): expand_descendants(), load_concept(), load_death(), load_events(), load_person(), load_truth(), Union the domain tables into one long event stream. Returns person_id,…, Roll a code set down through concept_ancestor (ingredient -> all products). (+4 more)

### Community 49 - "Cohort Extract (A)"
Cohesion: 0.20
Nodes (11): connect(), _dip_exclusion_clause(), _dump_core(), extract_cohort(), extract_omop(), Accept either a raw SQL string or a path to a .sql file. A path-looking string…, Dump CORE_TABLES filtered to `pids` (dip-excluded per domain), plus a…, Dump a random patient sample to CSV. slim_concept restrict concept.csv to… (+3 more)

### Community 50 - "Cohort Extract (B)"
Cohesion: 0.20
Nodes (11): connect(), _dip_exclusion_clause(), _dump_core(), extract_cohort(), extract_omop(), Accept either a raw SQL string or a path to a .sql file. A path-looking string…, Dump CORE_TABLES filtered to `pids` (dip-excluded per domain), plus a…, Dump a random patient sample to CSV. slim_concept restrict concept.csv to… (+3 more)

### Community 51 - "Cohort Extract (C)"
Cohesion: 0.20
Nodes (11): connect(), _dip_exclusion_clause(), _dump_core(), extract_cohort(), extract_omop(), Accept either a raw SQL string or a path to a .sql file. A path-looking string…, Dump CORE_TABLES filtered to `pids` (dip-excluded per domain), plus a…, Dump a random patient sample to CSV. slim_concept restrict concept.csv to… (+3 more)

### Community 52 - "Mammography OMOP Loader"
Cohesion: 0.18
Nodes (7): bag_of_codes(), ethos_omop.py — extract from ETHOS_PRODUCTION.OMOP_54 and load into the shape…, Patient x code matrix. The representation we are trying to beat., person_id -> ordered token list. Two decisions, both arbitrary and both written…, Keep only events at or before each patient's index_date. Prevents leakage., sequences(), truncate_at()

### Community 53 - "Cohort Extract (D)"
Cohesion: 0.20
Nodes (11): connect(), _dip_exclusion_clause(), _dump_core(), extract_cohort(), extract_omop(), Accept either a raw SQL string or a path to a .sql file. A path-looking string…, Dump CORE_TABLES filtered to `pids` (dip-excluded per domain), plus a…, Dump a random patient sample to CSV. slim_concept restrict concept.csv to… (+3 more)

### Community 54 - "Cohort Extract (E)"
Cohesion: 0.20
Nodes (11): connect(), _dip_exclusion_clause(), _dump_core(), extract_cohort(), extract_omop(), Accept either a raw SQL string or a path to a .sql file. A path-looking string…, Dump CORE_TABLES filtered to `pids` (dip-excluded per domain), plus a…, Dump a random patient sample to CSV. slim_concept restrict concept.csv to… (+3 more)

### Community 55 - "Group Loadings (A)"
Cohesion: 0.20
Nodes (10): _gcol(), group_loadings(), group_mask(), group_tokens(), Column that holds curated group names: `group` when tag_events wrote it, else…, Boolean mask of events whose concept is in ANY of the curated group(s) `names`…, The `tag` tokens (columns of a bag-of-codes / NMF) that belong to curated group…, components x tokens matrix -> components x curated groups: a group's loading is… (+2 more)

### Community 56 - "d3 Minified Internals 56"
Cohesion: 0.20
Nodes (10): Be(), clamp(), formatHsl(), hn(), jn(), pn(), toString(), Ve() (+2 more)

### Community 57 - "d3 Minified Internals 57"
Cohesion: 0.20
Nodes (8): cl(), fl(), ll(), ol(), e(), ql(), sl(), ul()

### Community 58 - "Robustness Config YAMLs"
Cohesion: 0.22
Nodes (10): Letrozole robustness.yaml (Day 3 v3 motif robustness config), PrefixSpan mining parameters (rel_sup 0.15, max_len 4, min_len 3), Split-half stability and out-of-time validation settings, Mammography codesets.yaml (v1), mammography cohort anchor (Procedure-domain only), Port of oncology side, removal of fertility tags from letrozole codeset, Mammography robustness.yaml (NMF + PrefixSpan parameters), Held-out family pass rate (downgrades solid to suggestive) (+2 more)

### Community 59 - "Group Loadings (B)"
Cohesion: 0.20
Nodes (10): _gcol(), group_loadings(), group_mask(), group_tokens(), Column that holds curated group names: `group` when tag_events wrote it, else…, Boolean mask of events whose concept is in ANY of the curated group(s) `names`…, The `tag` tokens (columns of a bag-of-codes / NMF) that belong to curated group…, components x tokens matrix -> components x curated groups: a group's loading is… (+2 more)

### Community 60 - "Run Manifest (repr_learn)"
Cohesion: 0.27
Nodes (7): build_manifest(), config_hash(), git_commit(), Run manifest: everything needed to say what produced a CSV (config hash, input…, Per-phase wall time: `with timer.phase('name'): ...`, sha256_file(), Timer

### Community 61 - "Group Loadings (C)"
Cohesion: 0.20
Nodes (10): _gcol(), group_loadings(), group_mask(), group_tokens(), Column that holds curated group names: `group` when tag_events wrote it, else…, Boolean mask of events whose concept is in ANY of the curated group(s) `names`…, The `tag` tokens (columns of a bag-of-codes / NMF) that belong to curated group…, components x tokens matrix -> components x curated groups: a group's loading is… (+2 more)

### Community 62 - "Group Loadings (D)"
Cohesion: 0.20
Nodes (10): _gcol(), group_loadings(), group_mask(), group_tokens(), Column that holds curated group names: `group` when tag_events wrote it, else…, Boolean mask of events whose concept is in ANY of the curated group(s) `names`…, The `tag` tokens (columns of a bag-of-codes / NMF) that belong to curated group…, components x tokens matrix -> components x curated groups: a group's loading is… (+2 more)

### Community 63 - "Run Manifest (sensitivity)"
Cohesion: 0.27
Nodes (7): build_manifest(), config_hash(), git_commit(), Run manifest: everything needed to say what produced a CSV (config hash, input…, Per-phase wall time: `with timer.phase('name'): ...`, sha256_file(), Timer

### Community 64 - "Letrozole Literature Scripts"
Cohesion: 0.28
Nodes (6): curl(), q(), PubMed (NLM E-utilities) helpers for the letrozole literature column of the…, Round 1. For every bundle: all 3-of-5 entity combinations (unordered), the 3…, run(), Round 2. Bundle entities (>=3, unordered) plus the bundle's clinical setting,…

### Community 67 - "Letrozole Full vs Windowed Summary"
Cohesion: 0.25
Nodes (8): Grouping codes matters more than codeset content, Letrozole full-history NMF (k=7) vs windowed +/-18 mo NMF (k=13) summary, Infection-Rx bundle is a null in both runs (lift 1.0-1.5, 0/5 re-tests), Lift is not reliability (high-lift unstable outliers, e.g. win c5 anesthesia), Patient-level partition agreement (ARI 0.28, NMI 0.30), Strongest result: win c3 letrozole -> US -> live birth (11.2x, 5/5), Window +/-18 months run log (k=13, 301s), script_win18.py

### Community 68 - "Index Dates & Weak Labels (A)"
Cohesion: 0.25
Nodes (8): index_dates(), Events of group/tag `tag`: every group the concept is in (col=None) or an…, First occurrence of group/tag `tag` per patient — the point-in-time anchor., Days from first tag_a to first tag_b, per patient. Negative = b came first., Rule-based PROBE labels for the letrozole indication, from corroborating co-…, _select(), signed_gap(), weak_labels()

### Community 69 - "Index Dates & Weak Labels (B)"
Cohesion: 0.25
Nodes (8): index_dates(), Events of group/tag `tag`: every group the concept is in (col=None) or an…, First occurrence of group/tag `tag` per patient — the point-in-time anchor., Days from first tag_a to first tag_b, per patient. Negative = b came first., Rule-based PROBE labels for the letrozole indication, from corroborating co-…, _select(), signed_gap(), weak_labels()

### Community 70 - "Letrozole Window Run Logs"
Cohesion: 0.25
Nodes (8): Full-history run log (k=7, 817s, 7 bundles), Oncology evidence timing lanes (70 confirmed dx, 79% coverage in full run), script_full.py, Window +/-12 months run log (k=12, 199s), Windowed runs produce no fertility-labelled components (all background), script_win12.py, Window +/-24 months run log (k=9, 294s), script_win24.py

### Community 71 - "CLMBR Reproduction & Repo Overview"
Cohesion: 0.29
Nodes (7): clmbr_paper_reproduction.ipynb (Stages 1-6), README.md (repo overview), CLMBR reproduction (Steinberg 2021) thread, External reference material (femr, hf_ehr, MEDS tutorial), OMOP -> MEDS -> meds_reader pipeline, Inconsistent notebook path convention (repo root vs own directory), repr_learn 5-day pattern-discovery courses

### Community 72 - "Chest Pain Literature"
Cohesion: 0.29
Nodes (7): 2021 AHA/ACC Chest Pain Guideline (Gulati et al.), Chest pain references (APA, 14 items with PMIDs), ACS and acute chest pain literature (Fanaroff, Basu, Stopyra, Mockel, Reamy), Gulati et al. 2021 AHA/ACC chest pain guideline (Circulation), Jordan et al. 2022/2023 unattributed chest pain EHR studies, Non-cardiac / musculoskeletal chest pain literature (Burgstaller, Chambers, Ayloo, Sturm), verify_pmids.py (PMID verification)

### Community 73 - "First-Tag-Wins Ordering"
Cohesion: 0.29
Nodes (7): First-tag-wins ordering in tag_events (fine-grained first, umbrella last), Letrozole codesets.yaml (v5), breast_cancer over-match fix (dropped 'neoplasm of breast', split DCIS), tag_events first-tag-wins ordering (setdefault), letrozole aromatase inhibitor tag, Unanchored substring regex pattern matching (resolve()), Sensitivity letrozole codesets.yaml (identical copy)

### Community 74 - "d3 Minified Internals 74"
Cohesion: 0.29
Nodes (6): Ag(), mg(), Sg(), xg(), Xr(), Yr()

### Community 76 - "Tag Events (A)"
Cohesion: 0.33
Nodes (6): _clean(), _fallback_label(), Lower-case, fold accents, drop everything that is not a-z/0-9/space, spaces ->…, Unique label for an event with no codeset tag: <name20>__<class>__<concept_id>.…, Add a `tag` column collapsing many concept_ids to one clinical label. This is…, tag_events()

### Community 77 - "Cardiac Workup Outcome"
Cohesion: 0.33
Nodes (6): cardiac_workup_outcome(), index_dates(), First occurrence of group/tag `tag` per patient — the point-in-time anchor., Days from first tag_a to first tag_b, per patient. Negative = b came first., Day 5 proxy outcome for dx_9487 triage: did a real cardiac workup happen AFTER…, signed_gap()

### Community 78 - "Tag Events (B)"
Cohesion: 0.33
Nodes (6): _clean(), _fallback_label(), Lower-case, fold accents, drop everything that is not a-z/0-9/space, spaces ->…, Unique label for an event with no codeset tag: <name20>__<class>__<concept_id>.…, Add a `tag` column (the token sequences / bag-of-codes / NMF are built from)…, tag_events()

### Community 79 - "Tag Events (C)"
Cohesion: 0.33
Nodes (6): _clean(), _fallback_label(), Lower-case, fold accents, drop everything that is not a-z/0-9/space, spaces ->…, Unique label for an event with no codeset tag: <name20>__<class>__<concept_id>.…, Add a `tag` column (the token sequences / bag-of-codes / NMF are built from)…, tag_events()

### Community 80 - "Seq Index Matching (repr_learn)"
Cohesion: 0.53
Nodes (5): match_strict(), match_tie(), match_windowed(), matches(), Fast, date-aware subsequence matching. Three semantics (all deterministic, all…

### Community 81 - "Tag Events (D)"
Cohesion: 0.33
Nodes (6): _clean(), _fallback_label(), Lower-case, fold accents, drop everything that is not a-z/0-9/space, spaces ->…, Unique label for an event with no codeset tag: <name20>__<class>__<concept_id>.…, Add a `tag` column (the token sequences / bag-of-codes / NMF are built from)…, tag_events()

### Community 82 - "Index Dates (C)"
Cohesion: 0.33
Nodes (6): index_dates(), Events of group/tag `tag`: every group the concept is in (col=None) or an…, First occurrence of group/tag `tag` per patient — the point-in-time anchor., Days from first tag_a to first tag_b, per patient. Negative = b came first., _select(), signed_gap()

### Community 83 - "Tag Events (E)"
Cohesion: 0.33
Nodes (6): _clean(), _fallback_label(), Lower-case, fold accents, drop everything that is not a-z/0-9/space, spaces ->…, Unique label for an event with no codeset tag: <name20>__<class>__<concept_id>.…, Add a `tag` column (the token sequences / bag-of-codes / NMF are built from)…, tag_events()

### Community 84 - "Seq Index Matching (sensitivity)"
Cohesion: 0.53
Nodes (5): match_strict(), match_tie(), match_windowed(), matches(), Fast, date-aware subsequence matching. Three semantics (all deterministic, all…

### Community 85 - "Sankey Runs"
Cohesion: 0.50
Nodes (3): Sankey of patient flow between the bundles of two NMF runs (same cohort, same…, sankey(), smooth()

### Community 86 - "d3 Minified Internals 86"
Cohesion: 0.40
Nodes (5): bezierCurveTo(), Bx(), ow(), rx(), Vx()

### Community 87 - "d3 Minified Internals 87"
Cohesion: 0.40
Nodes (5): Dh(), Ih(), Ph(), qh(), uh()

### Community 88 - "d3 Minified Internals 88"
Cohesion: 0.40
Nodes (4): Li(), o(), u(), Ni()

### Community 89 - "build_codesets() Cluster"
Cohesion: 0.50
Nodes (4): build_codesets(), Find concept_ids by name pattern. Returns a DataFrame for eyeballing — ALWAYS…, Resolve CODESETS to concept_id sets. Returns dict tag -> set(concept_id). Each…, resolve()

### Community 90 - "index_dates() Cluster"
Cohesion: 0.50
Nodes (4): index_dates(), First occurrence of `tag` per patient — the point-in-time anchor., Days from first tag_a to first tag_b, per patient. Negative = b came first., signed_gap()

### Community 91 - "observation_window() Cluster"
Cohesion: 0.50
Nodes (4): observation_window(), Proxy enrolment window from first/last observed event. The extract does not…, time-to-event frame for Day 5, anchored at each patient's first event. Real…, survival_frame()

### Community 93 - "build_codesets() Cluster"
Cohesion: 0.50
Nodes (4): build_codesets(), Find concept_ids by name pattern. Returns a DataFrame for eyeballing — ALWAYS…, Resolve CODESETS to concept_id sets. Returns dict tag -> set(concept_id). Each…, resolve()

### Community 94 - "observation_window() Cluster"
Cohesion: 0.50
Nodes (4): observation_window(), Proxy enrolment window from first/last observed event. The extract does not…, time-to-event frame for Day 5, anchored at each patient's first event. Real…, survival_frame()

### Community 95 - "d3 Minified Internals 95"
Cohesion: 0.50
Nodes (4): Ac(), bc(), mc(), xc()

### Community 96 - "build_codesets() Cluster"
Cohesion: 0.50
Nodes (4): build_codesets(), Find concept_ids by name pattern. Returns a DataFrame for eyeballing — ALWAYS…, Resolve CODESETS to concept_id sets. Returns dict tag -> set(concept_id). Each…, resolve()

### Community 97 - "observation_window() Cluster"
Cohesion: 0.50
Nodes (4): observation_window(), Proxy enrolment window from first/last observed event. The extract does not…, time-to-event frame for Day 5, anchored at each patient's first event. Real…, survival_frame()

### Community 98 - "repr_learn_letrozole/motif_robustness/ve Cluster"
Cohesion: 0.50
Nodes (3): provisional_status(), PROVISIONAL tiering using only the checks built so far (effect + FDR/FWER,…, row: dict-like with q_fisher, p_fwer, log_or_lo, fam_holdout_rate_lo,…

### Community 99 - "build_codesets() Cluster"
Cohesion: 0.50
Nodes (4): build_codesets(), Find concept_ids by name pattern. Returns a DataFrame for eyeballing — ALWAYS…, Resolve CODESETS to concept_id sets. Returns dict tag -> set(concept_id). Each…, resolve()

### Community 100 - "observation_window() Cluster"
Cohesion: 0.50
Nodes (4): observation_window(), Proxy enrolment window from first/last observed event. The extract does not…, time-to-event frame for Day 5, anchored at each patient's first event. Real…, survival_frame()

### Community 101 - "build_codesets() Cluster"
Cohesion: 0.50
Nodes (4): build_codesets(), Find concept_ids by name pattern. Returns a DataFrame for eyeballing — ALWAYS…, Resolve CODESETS to concept_id sets. Returns dict tag -> set(concept_id). Each…, resolve()

### Community 102 - "observation_window() Cluster"
Cohesion: 0.50
Nodes (4): observation_window(), Proxy enrolment window from first/last observed event. The extract does not…, time-to-event frame for Day 5, anchored at each patient's first event. Real…, survival_frame()

### Community 103 - "sensitivity_letrozole/motif_robustness/v Cluster"
Cohesion: 0.50
Nodes (3): provisional_status(), PROVISIONAL tiering using only the checks built so far (effect + FDR/FWER,…, row: dict-like with q_fisher, p_fwer, log_or_lo, fam_holdout_rate_lo,…

### Community 109 - "d3 Minified Internals 109"
Cohesion: 0.67
Nodes (3): ca(), ua(), g()

### Community 110 - "d3 Minified Internals 110"
Cohesion: 0.67
Nodes (3): cu(), u(), uu()

### Community 111 - "d3 Minified Internals 111"
Cohesion: 0.67
Nodes (3): ja(), nu(), tu()

### Community 112 - "d3 Minified Internals 112"
Cohesion: 1.00
Nodes (3): kd(), o(), Nd()

### Community 113 - "d3 Minified Internals 113"
Cohesion: 0.67
Nodes (3): nf(), Wc(), zc()

### Community 114 - "d3 Minified Internals 114"
Cohesion: 0.67
Nodes (3): Vm(), Wm(), zm()

## Knowledge Gaps
- **55 isolated node(s):** `run_all.sh script`, `MPLBACKEND`, `Final table columns M/O/P (triage, literature, PMIDs)`, `sanity_check_AHA.md (three-run comparison with Sankeys)`, `Trajectory animation HTML with GIF export` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 615 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `qu` connect `fu() Cluster` to `d3.v7.min.js (vendored)`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `build_patient_seqs()` connect `Robustness Pipeline (sensitivity)` to `Letrozole Script (win24)`, `Letrozole Script (full)`, `Letrozole Script (win12)`, `Letrozole Script (win18)`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `jm()` connect `jm() Cluster` to `d3.v7.min.js (vendored)`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `n()` (e.g. with `C()` and `M()`) actually correct?**
  _`n()` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `e()` (e.g. with `A()` and `C()`) actually correct?**
  _`e()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `r()` (e.g. with `A()` and `g()`) actually correct?**
  _`r()` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `o()` (e.g. with `A()` and `al()`) actually correct?**
  _`o()` has 28 INFERRED edges - model-reasoned connections that need verification._