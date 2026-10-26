# Handoff

## Update 2026-10-23 (colonoscopy): Triage / Supported literature / PMIDs filled in the k=7 final table

`nb/repr_learn_colonoscopy/outputs/final_table_colonoscopy_k7_v1.xlsx`, filled with the `pubmed-literature-check` rule (copied from mammography into new `nb/repr_learn_colonoscopy/literature_search/`: `pubmed.py` T / ENT / PAT, `round1.py`, `round2.py`, `steps.py`, `fetch_abstracts.py`, `fill_literature.py` with `--check`, `verify_pmids.py`; logs `round1.log`, `round2.log`, `abstracts.json`). Backup of the empty table: `literature_search/final_table_colonoscopy_k7_v1.empty_cols_2026-10-23.xlsx`. Audit files next to the table: `_literature_evidence.csv`, `_literature_search_log.csv`, `_literature_verified.csv` (28 PMIDs, all confirmed in PubMed; all returned by a search of this run, none from memory). Network steps need the sandbox off.
- **Triage (draft, bundle level; mine, unreviewed):** c0 Manual RUW, c1 Routine, c2 Routine, c3 Routine, c4 Routine, **c5 Unclear**, c6 Routine. Judgment calls: c0 (enriched, OR 2.7, owns ostomy, colectomy, chemotherapy; but its top-5 entities are acute-care codes), c5 (the underwriting note asks for polyp size, number and histology, which codes do not show), c6 (iron studies and the CEA tumor marker load on it; I called it Routine like the mammography endocrine bundle).
- **Literature:** 14 rows `Partly`, 7 rows `None` (rows 2-4 = c0, 8-10 = c2, 13 = c3), none `Yes`. A row keeps a paper only if the title fits the setting and the title or abstract names at least min(2, steps) of the row's steps (regexes in `steps.py`). All titles read, 28 abstracts used. A clinician must confirm each `Partly`.
- **Why the None rows:** c0, the 5-fluorouracil / capecitabine / oxaliplatin cardiotoxicity papers name the ECG but no chemistry or blood-count step; c2, no paper names a PPI / H2 blocker together with the antibiotic; c3 row 13, none names the preventive visit with the pelvic exam. Papers that fit a bundle's setting but not its steps (e.g. iron deficiency and colorectal cancer screening, 37516515) are not on any row.
- **Weak points:** PT rows (c4) rest on general musculoskeletal papers (ankle sprain, TMD, neck pain, knee and hip osteoarthritis), not on colorectal patients. The older 2012 US Multi-Society Task Force paper was retrieved, the 2020 update cited in the codeset header was not, so it is not cited. Re-running cell 48 overwrites M / O / P; if patterns change, update PAT, re-run both rounds, `fetch_abstracts.py`, rebuild KEEP.
- **Not done:** the page does not list these PMIDs yet (see item 3 below).

## Update 2026-10-23 (colonoscopy): one-file page, abbreviation rule

**Colonoscopy page.** `nb/repr_learn_colonoscopy/outputs/colonoscopy_all_patterns.md` (504 lines, 7 care patterns c0-c6, 21 sequences) from `colonoscopy_page.yaml`; lint 0 issues. Source: `final_table_colonoscopy_k7_v1.xlsx` (211,291 patients, both sexes, variant v1). Same rules and same `sequence_rule` as mammography (patterns mined on the full history, no gap limit).

**Abbreviation rule (new, from the user).** Write the full term first and the abbreviation after it in brackets, everywhere. The tool now enforces it: config key `abbreviations` prints a glossary before any other use, and `lint_page.py` fails on any abbreviation whose first use is not the bracketed one. The build also replaced two abbreviations in its own text: "d" became "days" in the coverage tables, and "code ID" became "concept identifier". The mammography page was rebuilt to follow the rule (lint 0). **The chest pain page was not touched**: its file and `chest_pain_page.yaml` still have abbreviation-first wording (13 lint issues: ED, GERD, SNOMED, CPT4, CMP, CBC, HbA1c, STI, DNA, RNA, ECG, PPI, and the old "ID"; the old "d" for days is not a lint hit). Fix the YAML and rebuild before it is sent again; rebuilt to a scratch file it differs from the delivered page only by the "days" and "identifier" wording.

**Facts for the reader / open.**
1. Window fit: 6 of 7 care patterns have all 5 entities more than 1 day from the first colonoscopy (medians 17 to 529 days **before**, so the entity rule is rarely met as written). Only c5 (colonoscopy procedure episode) sits on day 0: colonoscopy with polyp removal is itself a colonoscopy event and the other 4 entities have a median of 0 days (stated in the page).
2. 4 of 21 sequences fail the re-test: c0-A (0 of 5), c0-C (2), c1-A (3, Suggestive), c4-A (0). The page says so.
3. The page lists only the two guidelines from the `codesets.yaml` header (USPSTF 2021 colorectal screening, USMSTF 2020 follow-up); citations copied, not re-checked online. The final table now has PMIDs (entry above this one); add `files.literature: outputs/final_table_colonoscopy_k7_v1_literature_verified.csv` to `colonoscopy_page.yaml` and rebuild to put them in the page. Not done yet.
4. In-situ: the `in_situ` tag has only 38 patients and no row in the NMF loadings, so no bundle holds it; the page has no in-situ sentence.
5. Entity wording and the 7 care pattern names (from the `DESCR` names in cell 30, which are mine and unreviewed) need a clinical read; c0 "acute care work-up, bowel complications, and colorectal cancer treatment" is the longest and most mixed.
6. The anchor `colonoscopy` includes polypectomy and biopsy colonoscopies, so those two code groups are anchor events, not separate care.

## Update 2026-10-23 (mammography): one-file page, and the `bundle-predicate-page` skill

**Skill.** `.claude/skills/bundle-predicate-page/` (`SKILL.md`, `scripts/build_page.py`, `scripts/lint_page.py`, `references/config_format.md`) builds the one-file page of a use case from its final table plus a YAML config. Run with env `ethos_llm` (base python has no numpy): `python .claude/skills/bundle-predicate-page/scripts/build_page.py nb/repr_learn_<uc>/<uc>_page.yaml`, then `lint_page.py <page>`. The chest pain config `nb/repr_learn_chestpain/chest_pain_page.yaml` reproduces `outputs/chest_pain_all_patterns.md` byte for byte (checked). `make_chest_pain_all_patterns.py` and `make_bundle_engine_docs.py` are now redundant for the one-file page; kept, not deleted.

**Mammography page.** `nb/repr_learn_mammography/outputs/mammography_all_patterns.md` (574 lines, 8 care patterns, 46 predicates: the anchor and 45 entities, 24 sequences) from `mammography_page.yaml`; lint 0 issues (script check, not ASD-STE100 certified). Same format as chest pain, no triage, no manual-review wording.

**Rules that differ from chest pain (decide before it goes to Zack).**
- **Sequences have no time limit between steps** (`sequence_rule` in the YAML). The mammography patterns were mined on the full history with no gap limit and most contain no mammography step, so the chest pain rule "last step within 1 day of the anchor" has nothing to apply to. The page states the rule that matches the measured shares.
- **Entity window kept at 1 day, 3 entities** (draft, no calibration). Window-fit table: 4 or 5 of 5 entities per care pattern sit more than 1 day from the first mammography (medians 7 to 443 d), so the entity rule is rarely met as written. c0 is the exception: screening mammography is a mammography event and tomosynthesis is billed the same day, so 2 of its 5 entities are in the window by construction (stated in the page).

**Open.**
1. Entity wording, the 8 care pattern names (from the DESCR names; c3 "women's health and breast-imaging work-up" and c6 "peri-operative care and breast surgery" most need a clinician read) and the DCIS / LCIS sentence are mine, unreviewed.
2. 4 of 24 sequences fail the re-test (c0 all three: 0 of 5; c5-B: 3 of 5). The page says so.
3. References: the 2 guideline lines (USPSTF 2024, ASCO 2026) are copied from the header of `codesets_v2.yaml`, not re-checked online. The PMID list is the final table's (many rated Partly, a clinician should confirm).
4. Predicates that look alike differ from chest pain on purpose (`complete_blood_count` is the 5-code group, chest pain `cbc` is one code; `troponin_quantitative` vs the troponin group; ECG, cervical screening). A shared predicate library would remove this drift; not built.
5. ~~Colonoscopy has no page yet~~: built the same day, see the entry above.

## Update 2026-10-21 (chest pain): Zack's feedback, one consolidated page

Source: `transcripts/Esteban : Zack - Touch Base 2026-10-21.txt` (auto-captioned; "Chesapeake" = chest pain, "IREX" probably the existing rules system).

**What Zack asked for.**
- **One document per use case, not eight.** He wants all predicates in one section, then all composites, as the single page for the underwriters; predicates like chest pain and ECG repeat across patterns, so defining them 8 times is redundant and can drift apart.
- **No cardiac versus non-cardiac compaction**; just one document.
- **No underwriting or product decisions in the document** (accept, decline, manual review): it must stay an independent clinical grouping of codes so it does not bias the underwriters. Chest-pain-only scope is by design; people without chest pain are handled by the existing rules.
- **Hand-offs:** Esteban sends the chest pain document "tomorrow" (Oct 22); mammography follows in the same format if approved; colonoscopy is already run (about 20 million records) and gets the same format; Zack forwards to Dr. Z and some underwriters. Esteban also owes Zack a slide deck from the conference (OMOP best practices, snapshot-based code set drift, Atlas for transportability, OMOP 5.5, source values kept as the Milliman JSON) and the skill files (the condition-definition refiner demo).

**Done.** `outputs/chest_pain_all_patterns.md` (541 lines) from `python make_chest_pain_all_patterns.py`: overview and pattern table, 39 predicates once (grouped by diagnoses, lab tests, procedures and visits, drugs; each says which care patterns use it as an entity or a step), the window rule, then the four composites of every care pattern c0-c7 (c3 included, same names as the v3 page: `composite_ed_workup_pattern`), window-fit, entity-rate and sequence-rate tables, references. No triage, no "Manual RUW", no routing wording. Same ASD-STE100 style and script check as the per-pattern pages (0 issues; not certified).
- The 7 per-pattern pages in `outputs/bundle_engines/` and the c3 page `Chestpain_Workup_Predicate_Engine_v3.md` are **kept, not deleted**; the consolidated page supersedes them for delivery. Those pages still carry a "draft triage" line, which Zack does not want in what the underwriters read.
- `make_bundle_engine_docs.py` gained the c3 entities (`ENT`, `NOUN`, `BUNDLES["c3"]`); the 7 pages regenerate unchanged (c3 has no per-pattern page).

**Open / not done.**
1. Zack has not read the consolidated page; the length (about 540 lines, 39 predicates, 24 sequences) may still be too much for the underwriters. A shorter version would drop the entity-rate table or move the predicates into a table.
2. The same one-document format for mammography and colonoscopy is not built: it needs their final tables and engine definitions (mammography v2 k8 table exists; colonoscopy k7 table exists; neither has predicates and composites yet).
3. The 1-day window does not fit most care patterns (see the window-fit table in the page); no rate is measured. Triage, if it is ever needed, stays in the final tables.

## Update 2026-10-20 (chest pain): `outputs/` folder, one engine page per care pattern

Paths under `nb/repr_learn_chestpain/`. Env `ethos_llm`.

- **`outputs/` created.** Moved there: every `.xlsx` (final tables, NMF component tables, triage tables), every `.png` (flag flows, Sankeys), the engine / sanity `.md` (`Chestpain_Workup_Predicate_Engine*.md`, `Diabetes_Rx_Predicate_Engine.md`, `sanity_check_AHA.md`, the empty `predicates_v3.md`) and the literature audit csv files that sit next to a final table (`final_table_*_literature_*.csv`). **Left in the folder**: `.npz`, `.json`, the member / map csv files, `.html`, yaml, code, notebooks, `README_repr_learn.md`. Two stale Excel lock files (`~$...xlsx`, dated Oct 9 and Oct 13) are still there; delete them if Excel is closed.
- **Paths updated** so nothing breaks: the 9 notebooks that save an xlsx now write to `outputs/` (AHA, `full_k5`, `full_k8`, `windowed`: cells 38 and 63 / 65; `Day1_nmf_v3` cell 36; `Day3_prefixspan_v3_concept` cells 31 and 33; `Day3_prefixspan_v3_hybrid` cell 27), plus `make_c3_flag_flow.py`, `sankey_runs.py`, `build_plain_english_annex.py` (edits `outputs/..._v2.md`), `literature_search/aha_k8/fill_literature_AHA.py` (`--check` still passes: 24 rows, 25 PMIDs), the README and two path strings in the v1 / v2 engine pages. Image links inside the md pages still resolve (md and png moved together). Not run after the move: the notebooks, `make_c3_flag_flow.py`, `build_plain_english_annex.py`, `sankey_runs.py`.
- **Git.** `.gitignore` ignores `*.xlsx`, `*.png`, `*.csv`; only the `.md` files were tracked, and `nb/repr_learn_chestpain/outputs/` is not ignored, so they stay tracked (as moves). Do not add that folder to `.gitignore`: the engine pages would drop out of the repo.
- **New: one compact ASD-STE100 page per care pattern** of the AHA k=8 run, `outputs/bundle_engines/Chestpain_c{0,1,2,4,5,6,7}_Predicate_Engine.md` (c3 = the v3 page), from `python make_bundle_engine_docs.py`. Same rules as v3 (chest pain, 3 or more of the 5 top entities within 1 day, one of the 3 highest-lift sequences). Nothing is measured; every number comes from the AHA final table. Where an entity table lists two codes of one test (STI chlamydia + gonorrhea, 97110 + 97112, rapid antigen 87880 + 87804), the engine counts them as one entity.
  - **The 1-day window does not fit most care patterns.** Median first-event timing is 97-193 d before the first chest pain in c2, 115 d before to 133 d after in c5; only c6 has an entity on the same day. Every page says the window needs calibration. Sequences with chest pain in the middle (c1, c2, c7) allow no limit before the chest pain step and 1 day after.
  - **c0 and c2 sequences are weak**: held-out pass rate 0 to 50% (c2: 0% for all 3; c2's steps are generic blood draws, not its top entities). c4, c5, c6, c7 are `Solid` (c4 sequence B is `Suggestive`); c1 is `Suggestive`.
  - ASD-STE100 was checked by a script (sentence <= 25 words, paragraph <= 6 sentences, no modal / passive / perfect tense / contraction hits), not certified. The check script is not in the project. Triage per care pattern is the draft of the AHA table (c3 Manual RUW, c0 / c1 Unclear, the rest Routine).

## Update 2026-10-20 (colonoscopy): notebook, Snowflake extract, k=7 run, DESCR

Paths under `nb/repr_learn_colonoscopy/` unless stated. Env `ethos_llm`. Run by the user; I did not run the notebook on the real data.

| What | File | State |
|---|---|---|
| Notebook = clone of `Mammography_NMF_PrefixSpan_v2.ipynb` with all its later changes (parquet, text loadings, ledger F0-F8, `DROP_INSITU_ONLY`, bundles-only final table, member table) | `Colonoscopy_NMF_PrefixSpan_v1.ipynb` | Run end to end by the user |
| Support files copied from mammography | `ethos_omop.py`, `csv_to_parquet.py`, `motif_robustness/`, `config/robustness.yaml` (paths point to `colonoscopy_cohort`) | Done |
| Cohort SQL (anchor: CPT 45378-45398, 44388-44408, HCPCS G0105 / G0121, SNOMED 4249893 + 40480729 and descendants; same Ethos-person and dx-evidence gates as mammography) | `sql/colonoscopy_cohort.sql` | Run; cohort size below |
| Extract + parquet | `inputs/colonoscopy_cohort/` (master tables 1.5-3.8 GB each) | Done |
| Run outputs (k=7) | `outputs/nmf_k7_colonoscopy_v1.npz`, `_components.json`, `nmf_components_colonoscopy_k7_v1.xlsx`, `final_table_colonoscopy_k7_v1.xlsx` (7 bundles x 3 patterns), `loadings_k7_colonoscopy_v1.csv`, `token_members_k7_colonoscopy_v1.csv`, `filter_ledger_colonoscopy_v1.csv` | Done |
| `DESCR` for the 7 bundles | cell 30 | Written by me 2026-10-20, needs a clinical read |

**Differences from the mammography notebook.**
- Anchor `colonoscopy` (umbrella); `ANCHOR_GROUPS` (cell 2) lists the finer colonoscopy tags first, then the umbrella.
- Label `colorectal_cancer`: ICD-10 `C18\d?|C19|C20`, ICD-9 `153\d?|154[01]`, the name-matched codeset, and personal history `Z850[34]\d?|V100[56]`; all source codes matched whole (`fullmatch`). **C18.1 (appendix) is inside C18**, so appendix cancer counts as a case. Anal cancer (C21, 154.2-154.3) is not.
- `in_situ` = D01.0-D01.2 / 230.3-230.4. `LABEL_PROXY_TAGS` = in_situ, colectomy, ostomy, chemotherapy, antineoplastic_drug, radiation_therapy, metastasis, tumor_marker.
- **F8 female-only is a switch, `FEMALE_ONLY`, off by default** (colonoscopy is for both sexes; the mammography notebooks are always female-only). Variant suffix `_female` when on.
- Cell 5 builds the parquet files right after a fresh extract. Cell 11 prints the tags that have no concept in the extract. Cell 13 (Table 1) reports screening and polypectomy colonoscopies instead of diagnostic mammography.

**Extract problems met (fixed in the colonoscopy copy of `ethos_omop.py` only).**
- Snowflake rejects an `IN` list of more than 200,000 expressions; this cohort seeded 210,620 persons (mammography: 145k, under the limit). `_dump_core` now sends person ids and concept ids in chunks of `PID_CHUNK` = 100,000 (one SELECT per chunk, rows appended to one CSV, header once). The chunk size is set in cell 5 (`eo.PID_CHUNK`) and read at call time. **The mammography and chest pain copies still have the 200,000 limit.**
- Two network errors, not code: (1) `390422 IP not allowed` = off the approved VPN / network, (2) `NameResolutionError` for the Snowflake S3 result stage = DNS dropped mid-pull. The pull is not resumable (every table restarts) and `extract_cohort` leaves a half-written folder: **delete `inputs/colonoscopy_cohort/` before a re-run or cell 5 skips the pull**. A retry / skip-written-tables step in `_dump_core` is not written.

**Run facts (k=7, all 7 components reported stable by the user).**
- 211,291 patients, F1 events 87,366,218 to 67,073,801, F2 to 67,062,902, F7 to 66,362,109 (no patient lost by F2 or F7). F3, F8, F4-F6 off.
- **700 cases (0.33%)**, so the label is very rare; the control group is 99.7%.
- Bundles (n, cases, cancer %, OR): c0 21,216, 161, 0.76%, OR 2.69 **cancer-enriched**; c1 59,585, 187, 0.31%, 0.93; c2 31,949, 53, 0.17%, OR 0.46 **no-cancer-enriched**; c3 32,048, 85, 0.27%, 0.78; c4 22,560, 62, 0.27%, 0.82; c5 30,080, 112, 0.37%, 1.15; c6 13,853, 40, 0.29%, 0.87 (the rest `mixed`).
- `DESCR`: c0 acute-care workup, GI complications and colorectal cancer treatment (owns ostomy 100, colectomy 82, chemotherapy 53, radiation 51, post-procedural complication 91, upper endoscopy 67, capsule endoscopy 61, GI bleeding 42); c1 preventive check-up and screening labs (screening colonoscopy 49, T2DM 51, FIT 33, PSA in the top tokens); c2 acute-illness prescriptions and bowel prep (PPI / H2 81, bowel prep 72, `antineoplastic_drug` 58 and `ibd_drug` 58, likely non-cancer uses); c3 women's preventive care; c4 physical therapy and musculoskeletal pain (no codeset at 30% or more); c5 colonoscopy procedure episode (polypectomy 100, polyp 98, benign neoplasm 97, biopsy 72, pathology 58); c6 endocrine / nutrient / iron labs (iron studies 81, tumor marker 58).
- c0 mixes two things (acute-care codes and cancer-treatment proxies): do not triage it as plain routine. Not read by me: the printouts of cells 11, 13, 15 (codesets with no concept, Table 1 criteria counts, F7 floor and sub-floor codesets), the sweep, the motifs and the final table.

**Open / to check later**
1. **Why only 0.33% cases?** Read Table 1 (cell 13): how many patients meet each of the four label criteria. The history criterion (Z85.03x / Z85.04x, V10.05 / V10.06) and the ICD-9 criterion may be empty if those codes are not in `condition_source_value` (or live only in Observation, which is not loaded). If so, survivors are controls.
2. Run `python check_codesets.py` on the real extract: the 7 tags that were empty on the other cohorts' concept tables (`colonoscopy_high_risk_screening`, `advanced_adenoma_histology`, `adenomatous_polyp`, `polyp_history`, `personal_history_crc`, `occult_blood_positive`, `colon_mass_or_abnormal_imaging`) and the Observation-domain tags are still unchecked. Cell 11 of the notebook prints which tags are empty.
3. `in_situ`, `metastasis`, `ct_colonography` were not in the loadings printout (probably under the F7 floor); check the "codesets with fewer patients than the floor" line. If `in_situ` is under the floor, `DROP_INSITU_ONLY` has no effect on the bundles.
4. Final table `final_table_colonoscopy_k7_v1.xlsx`: Triage / Literature / PMIDs columns are empty. `pubmed-literature-check` needs a `literature_search/` folder written for these bundles (copy the mammography one and change `ENT`, `PAT`, the setting queries); not started.
5. `papers/colonoscopy/colonoscopy_asg_endoscopy.pdf` is the GERD guideline, not a colonoscopy document (see the 2026-10-19 update). The upper-GI tags come from it.
6. Cohort SQL: confirm the person count against the dx-evidence list (the first pull returned 210,620 seeded ids, the run has 211,291 patients; the SQL was run twice on different days, not compared).
7. Clinical review of the 7 `DESCR` names; `FEMALE_ONLY = True` run for comparison with mammography.

## Update 2026-10-19 (mammography + colonoscopy): parquet, text loadings, bundles-only table, female-only filter, in-situ switch, v2 table filled, colonoscopy codeset

Paths under `nb/repr_learn_mammography/` unless stated. Env `ethos_llm`. The notebook edits are saved in both `Mammography_NMF_PrefixSpan_v2.ipynb` and `..._full.ipynb` (JSON round-trip checked lossless). The saved outputs of `_v2` are the user's own female-only run; `_full` was edited but **not re-run**.

| What | Where | State |
|---|---|---|
| Parquet loading (the two items of the 2026-10-17 to-do below) | `csv_to_parquet.py` (new); `ethos_omop.py`: `_fresh_parquet`, `_read`, `load_events`, `describe_extract`; cell 8 (reads through `eo._read`) and cell 4 (note) in both notebooks | Done, checked equal to the CSV load |
| Loadings as text | cell 25 of both notebooks: `print(loadings.round(0).astype(int).to_string())`, "where each codeset sits (owner bundle, share >= 30%)", `loadings_k{K}_{TAG}.csv` in `RES_DIR` | Done; v2 ran it |
| Final table = NMF bundles only | cells 47 / 48 of both notebooks (`BLOCKS`, one block per bundle, no label blocks, no stability filter, same as chest pain AHA) | Done; cell 48 of v2 was run by the user, the `_full` one only compile-checked |
| F8 female only; F3 on / off switch | cells 1, 2, 8, 9, 10 of both notebooks | Done (below) |
| `DESCR` of the 8 v2 bundles, rewritten for the female-only run | cell 30 of `_v2` | Done, needs a clinical read |
| `final_table_mammography_k8_v2.xlsx` columns M / O / P | `literature_search/` | Filled (below) |
| Colonoscopy codeset | `../repr_learn_colonoscopy/codesets.yaml`, `check_codesets.py` | Done; notebook, extract and k=7 run followed on 2026-10-20 (update above) |

**Parquet.** `csv_to_parquet.py` (pyarrow streaming CSV to zstd parquet, default dir `../../inputs/mammography_cohort/`) wrote a `.parquet` next to each of the 9 tables. The 5 `master_*` parquets keep only `person_id`, the concept id and the date (plus `condition_source_value` for conditions; dates stay strings so `pd.to_datetime` behaves as before): about 370 MB against about 10.5 GB of CSV. `_read` uses the parquet only if it is not older than the CSV **and** holds every requested column (all CSV header columns when `columns=None`); otherwise it reads the CSV, so nothing breaks when a column is missing or the extract is regenerated (rebuild with `python csv_to_parquet.py`). Measured: `load_events` 97 s to 61 s (the CSVs were already fast), `describe_extract` 9.9 s (row counts from the parquet footer). Equality checked on dtypes, frames and hashes. RAM saving on the full pipeline was **not** measured. During testing I touched the mtime of `master_condition_occurrence.csv`; it is reset to 2026-10-12 17:18, and all tables count as fresh. Chest pain has no parquet.

**Filters (F1-F8 ledger), cells 9 / 10.**
- **F8 (new)**: keep female patients only (`person.gender` = FEMALE), applied with the patient filters F1-F3, before tagging.
- **F3 is now a switch**: `DROP_INSITU_ONLY = False` (cell 2, default). When False, patients with in-situ breast disease only (DCIS / LCIS, no invasive criterion) are kept and **labelled "no breast cancer"** in the binary label; when True they are dropped as before. The VARIANT gets the suffix `_dropinsitu` when True, so files do not collide.
- **Why**: in-situ is pre-cancer, carries some risk, needs manual review (underwriting view). NMF is label-blind, so it does not form an in-situ group by itself: in the v2 run `in_situ` loads 63% on c6 (peri-operative + breast-cancer surgery) and 37% on c7 (colorectal / pathology / breast MRI and biopsy).
- **Rule for later**: bundle cancer % and ORs count in-situ-only patients as controls. Say so when quoting them. A three-class label (no cancer / in-situ / invasive) is **not built**; if it is, drop the `in_situ` concepts as features for the in-situ group (same leakage reason as F2). The note is in cell 30, in the final table Notes line and in the Claude memory file `mammography-insitu-handling.md`.
- **Outputs before 2026-10-19 are not comparable** (they used F3 on and all sexes). That includes the comparison table of the 2026-10-16 update below and every number for `_full` k9.

**v2 re-run (the user's, female-only, F3 off)**: 145,170 patients before F8 to 142,583 after (962 cases, 141,621 controls); 207 in-situ-only patients kept. Events 66,107,290, F1 50,514,305, F2 50,493,881, F8 49,595,708, F7 49,151,469; F7 floor 36 patients, 9,050 of 25,829 codes kept. `metastasis` (4), `cdk46_inhibitor` (10), `her2_targeted` (32) are below the floor. k=8, all 8 components `solid` (cosine 0.996-0.999), bootstrap ARI mean 0.845 (three refits at 0.63-0.66), NMI(bundle, label) 0.001, 3 of 8 bundles cancer-enriched. Bundle sizes: c0 32,587 (22.9%), c1 17,936, c2 26,265, c3 17,587, c4 10,978, c5 9,908, c6 8,500 (6.0%), c7 18,822. Loadings: `chemotherapy` and `bone_scan_pet` 41% on c1 (odd, see open items), `endocrine_therapy` 59% c3 / 35% c2, `menopausal_hormone_therapy` 73% c2.

**`final_table_mammography_k8_v2.xlsx` (24 pattern rows, Excel rows 2-25, bundles c0-c7 only).** Filled with the `pubmed-literature-check` skill, redone after the user re-ran cell 48 and the patterns changed.
- Triage (draft, bundle level): c0 Routine, c1 Unclear, c2 Routine, c3 Routine, c4 Routine, c5 Routine, **c6 Manual RUW**, c7 Unclear.
- Literature: 21 rows `Partly`, 3 `None` (rows 8-10 = c2), none `Yes` (PubMed cannot test order). 30 distinct PMIDs, each returned by a search in `round1.log` / `round2.log`, kept only if the title fits the setting and the title or abstract names at least `min(2, steps)` of the row's steps (regexes in `steps.py`), confirmed in PubMed by `verify_pmids.py`. A clinician must confirm each `Partly`.
- The Notes lines state the rule and the in-situ note. Drop-down on O2:O25 kept, merged M blocks kept. Audit files next to it: `_literature_evidence.csv`, `_literature_search_log.csv`, `_literature_verified.csv`.
- **Scripts: `literature_search/`**: `pubmed.py` (T clauses, ENT c0-c7, PAT keyed by table rows 2-25), `round1.py`, `round2.py` (setting queries), `fetch_abstracts.py`, `steps.py`, `fill_literature.py` (KEEP, TRIAGE; `--check`, `--out`; asserts the three columns are empty and A2 / A23 start with `c0 ` / `c7 `), `verify_pmids.py`. Network steps need the sandbox off (`/usr/bin/curl`); never turn TLS checks off; no PMID from memory.
- **Re-running cell 48 overwrites M / O / P.** If the patterns change: update `PAT`, re-run both rounds, `fetch_abstracts.py`, rebuild `KEEP`, then `fill_literature.py`. Backups in `literature_search/`: `final_table_mammography_k8_v2.before_literature.xlsx`, `..._with_label_groups_filled.xlsx` (older pre-F8 fill with label rows), `..._empty_cols_2026-10-19_1349.xlsx` (regenerated table before the final fill). Close the workbook in Excel before any script writes (a `~$` lock file means it is open).
- The `_full` k9 final table is **not** literature-filled. The label groups (cancer / no cancer) still exist in the mining sections of both notebooks; only the final table dropped them.

**Colonoscopy codeset (`nb/repr_learn_colonoscopy/`, asked 2026-10-19, "continue later").**
- `codesets.yaml`: 66 tags, 59 with `source:`, built from `papers/colonoscopy/` (UW docx, USPSTF 2021 CRC screening, USMSTF 2020 post-polypectomy surveillance, the ASGE file). Names follow the other cohorts: anchor `colonoscopy` (umbrella, last of its group), label `colorectal_cancer`, `in_situ` (D01.0-D01.2, anus excluded, listed before `colorectal_cancer`). Sections: procedures (screening / high-risk / polypectomy / biopsy / other, sigmoidoscopy, CT colonography, stool DNA, FOBT, bowel prep, sedation, pathology), CPT II / HCPCS quality codes, findings, risk context, cancer and treatment, indications and harms, upper GI, utilisation.
- `check_codesets.py` (pandas + pyyaml, replicates `resolve()`): per-tag counts, EMPTY flags, examples, overlaps; exit 1 on unexpected overlaps (umbrellas `colonoscopy`, `antineoplastic_drug` are allowed). Concept table: `inputs/colonoscopy_cohort/concept.csv` if present, else the union of `inputs/*/concept.csv`.
- Validated only against the union of the other cohorts' `concept.csv` (about 757 distinct concepts): exit 0, **7 tags empty there**: `colonoscopy_high_risk_screening`, `advanced_adenoma_histology`, `adenomatous_polyp`, `polyp_history`, `personal_history_crc`, `occult_blood_positive`, `colon_mass_or_abnormal_imaging`. Re-check on the real colonoscopy extract.
- **Wrong PDF**: `papers/colonoscopy/colonoscopy_asg_endoscopy.pdf` is the ASGE **GERD** guideline, not a colonoscopy document. The UW note cites "Quality Indicators for Colonoscopy" (Am J Gastroenterol 2024;119:1754), which is not in the folder. The upper-GI tags (`upper_endoscopy`, `gerd`, `barrett_esophagus`, `hiatal_hernia_antireflux`, `ppi_h2`) come from that GERD file. Add the right paper and revisit.
- **Observation caveat**: family history, personal history of CRC, polyp history and weight loss are Observation-domain concepts; the tags stay empty or thin until Observation is loaded. The CRC drugs in `antineoplastic_drug` are clinical convention, not from the papers.
- ~~Not done: cohort SQL, extract, `ethos_omop.py` copy, notebook~~ All done on 2026-10-20, see the update above. `check_codesets.py` has still not been run on the real extract.

**Open / to check later**
1. Clinical review of the 8 `DESCR` names, the triage, and each `Partly` rating.
2. `chemotherapy` and `bone_scan_pet` load 41% on c1 (the cardiac / chest-pain bundle), not on the treatment bundle c6. Not looked into (my guess: PET / bone scan and chemo-related labs ordered in the ED).
3. Optional three-class label (no cancer / in-situ / invasive), with the `in_situ` leakage rule above.
4. Older item 1 of the 2026-10-16 list still open: `K_OVERRIDE = 9` and `TOKEN_LEVEL='concept'` comparison runs; redo them under F8 / F3-off so they are comparable to the new v2 run.
5. `_full` notebook: edits (parquet, loadings, F8, F3 switch, bundles-only table) are untested; run it before comparing with v2.
6. The final table of a re-run changes whenever the patterns change: repeat the literature steps above.
7. `HANDOFF.md` and `graphify-out/` show as modified in git; nothing was committed.

## Update 2026-10-16 (mammography): codesets v2 run, compared with the k9 full run; open: why the breast-diagnostic bundle vanished

All paths under `nb/repr_learn_mammography/`. Env `ethos_llm`. Same pattern as chest pain AHA; v1 files (`codesets.yaml`, `Mammography_NMF_PrefixSpan_full.ipynb`, `outputs/*_full*`) are untouched.

| What | File |
|---|---|
| v2 codeset: 46 tags (v1 36), from USPSTF 2024 screening + ASCO 2026 surveillance (`papers/mammography/`); every changed / new tag has a `source:` key | `codesets_v2.yaml` |
| Checker: matched names per tag, empties, overlaps, v1 diff, invariants; `--md` writes the before / after report | `check_codesets.py`, `codesets_v1_vs_v2.md` (generated, do not edit) |
| Notebook = clone of `_full`, `CODESETS_FILE='codesets_v2.yaml'`, `TOKEN_LEVEL='group'`, files labelled `v2` | `Mammography_NMF_PrefixSpan_v2.ipynb` (outputs cleared; cells 2, 6, 10, 14, 29, 30, 44, 48 + member table at the end differ) |

Invariant: `mammography`, `breast_cancer`, `in_situ` have the same concept ids as v1 (checker exits 1 otherwise), so cohort, label and filters are identical (144,963 patients, 985 cases in both runs) and a v1 / v2 difference is only feature grouping. Checked: 0 empty tags, 0 unexpected overlaps (v1 had 3).

**Run by the user on 2026-10-16**: `outputs/nmf_k8_mammography_v2.npz` + `_components.json` (k=8, chosen by the sweep), `nmf_components_mammography_k8_v2.xlsx`, `final_table_mammography_k8_v2.xlsx`, `token_members_k8_mammography_v2.csv` (member table, last notebook cell). `DESCR` for the 8 bundles was written by me from the top-10 tokens and the codeset-loadings table, and is pasted in cell 30 (a saved name is kept only while the bundle's top-5 tokens match). Bundles: c0 preventive check-up / screening, c1 cardiac / chest-pain work-up, c2 acute-illness prescriptions, c3 women's health + breast-imaging work-up, c4 endocrine / nutrient labs, c5 physical therapy, c6 peri-operative + breast-cancer surgical treatment (owns all the label-proxy tags), c7 colorectal screening / surgical pathology / dermatology (+ breast MRI, density, findings, biopsy).

**Notebook edits after the run** (made in place on the saved copy, other outputs kept): cell 34 builds `COMP` as saved name else auto-name, then a non-empty `DESCR` entry wins (reads `DESCR` directly, no dependency on re-running cell 30); cells 44 / 46 colour the trajectory-graph nodes by the owning NMF bundle (largest summed loading over the step's tokens, legend with `COMP` names, gold outline = mammography anchor, printout of steps per bundle). **Cell 46's output was cleared: re-run 34, then 45, 46** (and 38 / 41 if the names changed). Tested on synthetic data only; the patch script was in the session scratchpad and is not in the project.

### Comparison v2 k8 vs full k9 (same 144,963 patients)

| | full k9 | v2 k8 |
|---|---|---|
| events with a codeset tag | 6.1% | 8.0% |
| NMF columns | 9,243 | 9,042 (38 group tokens) |
| k chosen by the sweep | 9 | 8 (v2 at k=9: 1 of 5 splits solid, 1 unstable component) |
| sweep ARI at k=8 | 0.907 | 0.858 |
| bootstrap ARI at the chosen k | 0.910 (sd 0.017) | 0.845 (sd 0.131; 3 of 10 refits about 0.63-0.66, every component cosine >= 0.99) |
| NMI bundle vs label | 0.0017 | 0.0012 |
| cancer cases in cancer-enriched bundles | 595 of 985 (60%), 28% of patients | 581 (59%), 32% of patients |
| max bundle OR | 3.3 | 3.5 |
| solid / suggestive / unstable motifs, cancer group | 0 / 18 / 82 | 1 / 8 / 91 |

- **Same structure.** Partition agreement ARI 0.72, NMI 0.71. 8 of the 9 full bundles land 82-96% inside one v2 bundle (f0 to c0, f1 to c1, f2 to c2, f3 to c3, f4 to c4, f5 to c5, f6 to c6, f7 to c7). Treatment bundle: c6 8,561 patients (f6 8,981), 2.04% cancer, OR 3.5.
- **Lost: the breast-diagnostic bundle.** Full f8 (13,595 patients, 246 cases = 25%, 1.81% cancer, OR 3.26) has no v2 counterpart; its patients spread over c7 21%, c0 21%, c3 20%, c2 19%. Breast imaging now splits between c3 (diagnostic mammography, ultrasound, symptoms, BRCA testing) and c7 (MRI, density, findings, biopsy); c7 became cancer-enriched (OR 1.7; f7 was mixed) because it absorbed part of f8.
- **Gained: one solid motif.** Cancer group: `mammography diagnostic -> chemistry panel -> CBC`, support 57.7% vs 13.0% outside, lift 4.2 (3.6-4.8), 5 of 5 splits, no proxy, not a same-day bundle. In the full run the same idea was spread over CBC / CMP concept variants (best lift 2.1, suggestive). The new `cbc` and `chemistry_panel` tags (87,724 and 99,676 patients) sit in 187 and 340 motifs. No-cancer group: still 0 solid in both runs.
- **New tags.** Small and motif-free: `breast_density` 2,109 patients (c7), `genetic_counseling` 1,035 and `brca_testing` 2,309 (c3), `tumor_marker` 1,278 (c6), `bone_scan_pet` 1,098 (c1), `germline_susceptibility` 62. `cdk46_inhibitor` (10 patients) and `her2_targeted` (32) are below the F7 floor of 37, so they reach neither the NMF nor the motifs (each of their concepts was smaller in the full run too).
- **Reading.** v2 relabels the same care bundles, does not separate cancer better (NMI about 0.001 in both), is a little less stable, and trades the dedicated breast-diagnostic bundle for one clean lab motif. Not a clear win yet.

**Open / to check later**
1. **k or tokens?** It is not known whether f8 vanished because k went 9 to 8 or because of group tokens. Two runs (about 25 min each): (a) v2 with `K_OVERRIDE = 9`, does a breast-workup bundle come back and is it stable; (b) `CODESETS_FILE='codesets_v2.yaml'` with `TOKEN_LEVEL='concept'` (labelled `v2_concept`), which isolates grouping from the codeset change.
2. Hypothesis, not tested: the breast-workup mass sits between c3 and c7 (diagnostic mammography 39% / 33%, ultrasound 41% / 37% of loading) and the argmax assignment flips in the bad bootstrap refits.
3. What the `diagnostic mammography -> chemistry panel -> CBC` labs are (diagnosis work-up, treatment monitoring, or ASCO 2.1 post-treatment surveillance) is untested; a timing check against the first diagnosis / first treatment or a `PRE_DX_ONLY` run would tell.
4. `cdk46_inhibitor` / `her2_targeted` below the floor: keep as curation-only, merge back into `antineoplastic_drug`, or lower the floor.
5. `endocrine_therapy` sits in c3 (59%) and c2 (37%), not in c6, so it is a weak cancer proxy. My guess (not checked): letrozole for fertility and tamoxifen / anastrozole co-prescribed with gyn care.
6. ~~Triage / Literature / PMIDs columns empty~~ Filled on 2026-10-19 (see the update above; the table has since been regenerated bundles-only and refilled). The `_full` k9 final table is still not filled. Bundle names (`DESCR`) and the plain wording need a clinical read.

**To do (asked 2026-10-17): DONE 2026-10-19, see the update above.** Original plan kept for the record:
- **Move the data loading to parquet.** The notebook reads the 1-3 GB `master_*.csv` of `inputs/mammography_cohort/` every run (`eo.load_events` through `ethos_omop._read`, line 266, plus cell 8 re-reads `master_condition_occurrence.csv` with `usecols`). `pyarrow` 25.0.1 is already in `ethos_llm`. Plan: one-off CSV to `.parquet` conversion next to the CSVs (chunked, the files do not fit comfortably in memory as one frame), make `_read` prefer `<table>.parquet` and fall back to the CSV, use `columns=` instead of `usecols=` in cell 8. Check that the event table and the sort order `load_events` guarantees are identical after the switch (compare row counts and a hash of a sorted sample against a CSV load), and do it in `ethos_omop.py` of both `repr_learn_mammography` and `repr_learn_chestpain` if the other cohorts should benefit.
- **Print the loadings in text as well as the heatmap.** Cell 25 (codeset loadings, `loadings` DataFrame) only shows a styled table, which is an image for anyone reading the saved notebook through text. Add a `print(loadings.round(0).astype(int).to_string())` (share of each codeset's loading per component c0..c{K-1}, plus `owner` and `rank_in_owner`) after the styled display, and the one-line list "codeset: owner bundle (share)" sorted by tag, so the where-does-it-sit read does not need the picture.

Known limits: contrast-enhanced mammography, family history (Observation), ctDNA, atypical hyperplasia have no concepts in this extract; `metastasis` stays at 1 concept; plain CT / brain MRI are not tagged on purpose; `breast_absence` was added to `LABEL_PROXY_TAGS` (v2 only).

## Update 2026-10-16: engine v2 / v3 on AHA k=8 (care pattern c3), plain-English layer, final table filled

All paths under `nb/repr_learn_chestpain/`. Conda envs: `ethos_llm` (pandas, openpyxl, pyyaml, sklearn), `omop_local` (matplotlib). Reference run for chest pain is now **AHA k=8, c3 = acute / ED work-up, 17,250 of 139,416 patients (12.4%)**; k=5 stays as the fallback.

**What exists now (all done and checked against the source files; nothing scored on real patient data)**

| What | File | Rebuild |
|---|---|---|
| Long engine (flag rule, checklist, compared-against table, evaluation protocol, limits, Annex A / B) | `Chestpain_Workup_Predicate_Engine_v2.md`, image `chestpain_c3_flag_flow.png` | `python make_c3_flag_flow.py` (`omop_local`) |
| **Short UW page for Zack's comment** (shaped like `Diabetes_Rx_Predicate_Engine.md`, ASD-STE100 wording, no CPT / flag-rule / evaluation text), embeds the neutral image as base64 | `Chestpain_Workup_Predicate_Engine_v3.md`, image `chestpain_c3_pattern_flow.png` | `python make_c3_flag_flow.py --neutral`; re-embed the PNG in the `[image1]:` line by hand |
| Plain-English layer: 48 abbreviations, UW wording vs data wording, one label per code list, every code with OMOP ID | `chestpain_plain_labels.yaml` -> `build_plain_english_annex.py` (`ethos_llm`) -> `chestpain_plain_english_omop_map.csv` (878 rows) and the registry table + Annex A / B inside v2 (between the `REGISTRY` / `ANNEX` markers) | edit the yaml, re-run the script; never edit the generated tables by hand; it stops if the labels and `codesets_v2.yaml` differ |
| AHA final table, **columns M / O / P filled** with the `pubmed-literature-check` skill; audit files next to it: `_literature_evidence.csv`, `_literature_verified.csv`, `_literature_search_log.csv` | `final_table_chestpain_k8_AHA.xlsx`; scripts and logs in `literature_search/aha_k8/` | `python fill_literature_AHA.py --check` re-tests the decisions; the search and `../verify_pmids.py` need the sandbox off (NCBI via `/usr/bin/curl`) |
| Old k=5 engine, banner points to v2 | `Chestpain_Workup_Predicate_Engine.md` | not updated |

**Engine design (same in v2 and v3, only the wording differs)**: chest pain + at least 3 of 4 services (troponin, chest X-ray, lipase, IV push) each within 1 day of a chest pain event + one of three 4-step sequences as mined for c3 (A chest pain, chest X-ray, troponin, CMP; B chest pain, ECG, troponin, CMP; C chest pain, troponin, CMP, CBC), last step within 1 day. ECG is not a counted service. Same-day order = date, then domain, then OMOP ID (so troponin < CMP < CBC on one day is a rule, not clock time). **Key renames in v3**: `workup_entity_count` -> `workup_service_count`, `composite_workup_bundle` -> `composite_workup_services`, `composite_c3_manual_ruw` -> `composite_ed_workup_pattern`; the two ablation composites are dropped.

**Final table k=8 AHA**: triage (bundle level, draft from entities and names) c0 Unclear, c1 Unclear, c2 Routine, **c3 Manual RUW**, c4 to c7 Routine; all 24 rows `Partly`, none `Yes` (PubMed cannot test order), none `None`; 25 PMIDs, each returned by a search of that run, read as title + abstract, kept only if the title or abstract names at least 2 of the row's steps (the 2021 AHA/ACC guideline 34709879 and the 2022 ACC ED pathway 36241466 are kept on their titles), confirmed in PubMed by `verify_pmids.py`. Weak spots: no abstract names the CMP step, so the c3 CMP / CBC steps are only partly covered; c2 and c6 rows rest on generic blood-test or risk-factor papers; a clinician should confirm each `Partly`. **Re-running notebook cell 65 overwrites these three columns**; the copy from before the fill was not kept in the project. Close the workbook in Excel before any script writes to it (a `~$` lock file means it is open).

**Open / not done**
1. **Nothing is measured on real patients.** No rate for any predicate or composite; the evaluation protocol of v2 (confusion table against the c3 label, per care pattern, window calibration at 0 / 1 / 3 / 7 days, `tie_ordered` vs strict-date match, forward outcome `cardiac_workup_outcome()` without troponin) is defined, not run.
2. Draft values with no calibration: the 1-day window and the 3-of-4 rule. The 4-step sequences versus a 3-step core (chest pain, X-ray or ECG, troponin) is a question for clinical review.
3. The draft triage, the plain labels and the UW-vs-data wording need review by the UW team and an underwriter.
4. **ASD-STE100 is not certified**: the official dictionary and Specification are not on this machine. The check was by script (sentence <= 25 words, paragraph <= 6 sentences, no modal / passive / perfect tense / contraction hits) plus a hand read of the vocabulary. The scripts (`verify_v3.py`, `ste_check.py`) lived in the session scratchpad and are not in the project.
5. v3 links a Drive file ("full list of codes") that you uploaded; I did not open it. Re-upload it after any change of the yaml or the CSV.
6. Note line A28 of the AHA final table says "NMF k=8 on concept-level tokens" but the AHA run uses group tokens; the text comes from the notebook, fix it there if wanted.
7. Housekeeping: `.claude/launch.json` (project root) is a temporary preview-server config the sandbox could not delete; `nb/repr_learn_chestpain/outputs/predicates_v3.md` is an empty file (0 bytes) that I did not create.

## Update 2026-10-14: chest pain literature, predicate engine, AHA codeset v2, k=8 comparison

All paths below are under `nb/repr_learn_chestpain/` unless stated. Conda env for scripts and notebooks: `ethos_llm` (pandas, sklearn, nbformat, openpyxl). `omop_local` has matplotlib; the system python has no numpy.

**Done (run by the user on 2026-10-15): member table, final table with Members columns Q-R, trajectory animation and GIF.** `token_members_k8_chestpain_AHA.csv` (cells 62-63) gives, for every group token, its OMOP concepts, so a group-level entity becomes `concept_id IN (...)`; the final-table cell (65) adds columns Q and R. The last two cells (67) write `trajectory_k8_chestpain_AHA.json` and `trajectory_k8_chestpain_AHA_animation.html` (d3 inlined, no network, **Export GIF** button: 12 s, 12 fps, up to 1000 px). Rebuild the HTML after a template change without the notebook: `python trajectory_anim.py trajectory_k8_chestpain_AHA.json`. Caveats: dots are Normal(median, SD) samples (real timings are skewed); the graph's entity list is the hard-coded v1 `FOCUS` set, so v2-only tags are not in it; the Claude preview browser crashes on the GIF export and paints polygons wrongly, so use installed Chrome. If the kernel restarted, `patseqs` is gone and Parts A-B must be re-run first.

**Done earlier (kept for the method): `Chestpain_NMF_PrefixSpan_full_k8.ipynb` was run and compared (see `sanity_check_AHA.md`).**
- It is a copy of `..._full` with `K_OVERRIDE = 8`, `VARIANT = 'full_k8'`, outputs cleared, same `codesets.yaml`, **concept-level tokens**. It writes `nmf_k8_chestpain_full_k8.npz`, `..._components.json`, `nmf_components_chestpain_k8_full_k8.xlsx`, `final_table_chestpain_k8_full_k8.xlsx`. About 25 min (PrefixSpan cell 50 is most of it).
- First run gives auto-names. The k=5 `DESCR` is skipped by the `DESCR_K = 5` guard in cell 43. Send the printed bundle list and write a `DESCR` block, then set `DESCR_K = 8` and re-run cell 43.
- Comparisons to make: `full_k8` vs AHA (same k: isolates codeset v2 + group tokens); `full_k8` vs `k5_full` (isolates k); `full_k8` vs `nmf_k8_chestpain_v2.npz` (older k=8 run). Method used so far: load both `.npz` (`pids`, `labels`), align on pids, `pd.crosstab`, ARI / NMI from sklearn; stability from the sweep table (cell 32) and bootstrap (cell 42); patterns from the final-table xlsx (columns 4-14).

**What exists now**
- `final_table_chestpain_k5_full.xlsx`: columns M (triage), O (literature), P (PMIDs) filled; Notes line A28 rewritten. Triage (draft): c0 Manual RUW, c1/c2/c4 Routine, c3 Unclear. Literature: `Partly` for 13 of 15 rows, `None` for r7 and r11 (`none found`), never `Yes` (no paper tests order). Titles only were read; a clinician should confirm each `Partly`. `final_table_chestpain_k5_full_literature_verified.csv` holds the 13 verified PMIDs. Searches and logs: `literature_search/`. APA reference list with PMIDs (it was only in chat before): `literature_search/references_apa.md`.
- `Chestpain_Workup_Predicate_Engine.md` + `chestpain_c0_flag_flow.png`: predicate/composite engine in the letrozole format. Target is **k=5 c0 (acute/ED, 25,953 patients)**; flag = chest pain + at least 3 of 4 services (ECG, troponin, chest X-ray, IV push) within 1 day of a chest pain event + one of three chest pain → X-ray/ECG → troponin sequences. The 1-day window is a draft, not calibrated. Evaluation protocol is defined, not run. **It does not map to k=8**; the k=8 version is `Chestpain_Workup_Predicate_Engine_v2.md` (see the 2026-10-16 update above).
- `codesets_v2.yaml` (70 tags, from Gulati et al., Circulation 2021;144:e368, read from the PDF pp. 1-48), `check_codesets.py` (prints matched names per tag, empties, overlaps, diff vs v4; 0 unexpected overlaps), README section. `codesets.yaml` and `ethos_omop.py` untouched; the 16 tests in `tests/` pass.
- `Chestpain_NMF_PrefixSpan_AHA.ipynb`: clone of `..._full` with `VARIANT='AHA'`, `CODESETS_FILE='codesets_v2.yaml'`, `TOKEN_LEVEL='group'`; only cells 0, 1, 2, 7, 38, 43 differ. **Already run at k=8** (files `*_AHA*`). Its `DESCR` block (names, groups) was written by me from the k=8 top tokens: c0 outpatient cardiometabolic + elective cardiac testing, c1 prescriptions, c2 women's health, **c3 acute/ED workup**, c4 GI + cancer screening, c5 MSK/PT, c6 nutrition/endocrine labs, c7 acute respiratory infection. c4 and c7 are labelled `non-cardiac explanation`, c5 stays `background` (my choice, open).
- `Chestpain_NMF_PrefixSpan_full.ipynb` shows as modified in git: it was already modified before this session; I did not edit it. `.gitignore` and `README.md` also were.

**One-page UW summary of the three runs (full k=5, full k=8, AHA k=8, all run): `sanity_check_AHA.md`.** Conclusion there: full k=8 is unstable (do not use); AHA k=8 is the draft working reference, k=5 the fallback. It now embeds two Sankey diagrams (AHA k=8 → full k=8, AHA k=8 → full k=5; made by `sankey_runs.py`): the ED bundle is the only structure all runs share (91% of AHA c3 sits in k=5 c0, 58% in k=8 c0); the rest is how finely background care is split.

**Findings: full k=5 (concept tokens) vs AHA k=8 (group tokens)** (the two differ in codeset, token level and k, so not all of it is the codeset)
- Same 139,416 patients / 46,525,784 events. Tag coverage 9.2% → 16.0%; NMF columns 9,542 → 9,155. Label agreement between runs: ARI 0.40, NMI 0.44 (mostly k).
- Stability at the same k favours AHA: k=5 ARI 0.861 → 0.935; k=8 ARI 0.712 (2/5 splits solid) → 0.851 (5/5). Bootstrap mean ARI 0.765 → 0.880. AHA's sweep rule picks k=8, full's picks 5.
- ED bundle: full c0 (25,953) → AHA c3 (17,250); 91% of AHA c3 comes from full c0; troponin loads 60% there. ECG is no longer a top token (46% of `ekg` loads on the outpatient bundle). The old 39% outpatient bundle (full c2) splits into outpatient, GI/screening, PT, nutrition, respiratory.
- AHA k=8 is almost the older Day 1 k=8 run (`nmf_k8_chestpain_v2.npz`, concept tokens, v4 codeset): ARI 0.907, sizes within about 1%. So at k=8 v2 mostly relabels existing bundles.
- Outliers: `ppi_h2 → ppi_h2 → ppi_h2` is a top-lift motif in the prescriptions bundle (refills collapsed into one token); `methylprednisolone → chest pain → ECG` (lift 4.3, `Suggestive`) is new; bootstrap 5 of AHA k=8 has ARI 0.567; psych-vs-troponin timing is unchanged (57.2% psych first, median 108 d in both).

**Gotchas for the next person**
- `..._full` is concept-level (`token_level="concept"`, cell 7): codeset tags there only label events (anchor, weak labels, loadings table), they are not NMF tokens. To make a codeset change the bundles you need `TOKEN_LEVEL='group'`.
- YAML order is load-bearing at group level (first matching tag wins the token); `stress_test` and `cad` are umbrellas and must stay last. Chest pain tag must stay `{77670, 134159, 42539051, 4168213}` (4168213 = R07.1 is in the tag, not in the cohort SQL; removing it changes NMF columns).
- Cells 38/43/63 re-set `COHORT = 'chestpain'`, so changing `COHORT` in cell 2 does not rename the xlsx; change `VARIANT`. Cell 43 attaches `DESCR` by component index when `k == DESCR_K` with no signature check.
- Group tokens have no concept_id or code in the components json / final table (`[code group]`); the member list is in `token_members_k{K}_{TAG}.csv` (AHA notebook, section 5) and in the final table's columns Q-R; the components json and the nmf components xlsx still do not show it. The `FOCUS` lists in cells 23/56/58 are hard-coded, so v2's new tags do not appear in the trajectory graph.
- PubMed (`eutils.ncbi.nlm.nih.gov`) is blocked in the Claude sandbox and Python's TLS fails behind the corporate proxy; the scripts use `/usr/bin/curl` and need the sandbox off. Never switch certificate checks off. No PMID from memory.
- The triage categories (Manual RUW / Routine / Unclear) in the skill are written for letrozole; for chest pain I mapped Manual RUW = acute/ED cardiac work-up bundle. Needs underwriter confirmation (earlier k=8 triage `chestpain_v2_bundles_triage.xlsx` also sent the acute/ED bundle to manual review).

**Open decisions**
1. Reference k for chest pain: AHA k=8 is the working reference (engine v2 / v3 and the literature ratings are built on its c3); k=5 is the fallback. The UW team still has to confirm the choice.
2. Group labels for AHA c4, c5, c7 (see above).
3. Same-k codeset test: AHA at k=5 vs full k=5 (not run; AHA sweep row k=5 has ARI 0.935).
4. Clinical review of the `Partly` ratings and of the 1-day window / 3-of-4 threshold in the engine; UW review of the plain labels (see the 2026-10-16 update).

## Update 2026-10-01 (evening): Day 1 results for three cohorts; next is Day 3 MVP

**Next session: Day 3 MVP (PrefixSpan / SPADE) for letrozole and chest pain.**
- `nb/repr_learn_chestpain/Day3_Sequence_Mining.ipynb` already has hand-written `prefixspan()` and `spade()` cells plus closed patterns, discriminative mining and a timeline graph. First step: run it end to end on the current Day 1 outputs.
- `nb/repr_learn_letrozole/` has no Day 3 notebook (only Day 1 and Day 2). Create it from the chest pain one. What must change: the anchor/index code (`letrozole`), probe labels from `weak_labels()` (fertility vs oncology) instead of `chest_pain_labels()`, and the signed-gap pair (e.g. letrozole vs `breast_cancer`).
- Check first: Days 2-5 still use `bag_of_codes(events, min_count=20)` without the prevalence floor (see open step 3 below). Decide whether Day 3 should use the floor before comparing results with Day 1.

**Day 1 results (k-sweep, five split seeds, `N_BOOT_K = 10`, rule: ARI >= 0.75 on 4+ of 5 splits and no unstable component):**

| Cohort | Largest passing k | Splits solid | Note |
|---|---|---|---|
| Chest pain (139k patients) | 8 | 4/5 | k=9 is the cliff (1 solid split); k=7 is a dip (3 solid, 1 unstable); k=5 is the safest (5/5). Replaces the older "solid on both splits" claim, which came from the two-split run. |
| Letrozole (5,238 patients, female-only v0.5 SQL) | 8 | 5/5 | Flat plateau at k=4-8, cliff at k=9. At k=8 every component is solid (cosine 0.988-0.997, bootstrap ARI 0.899, SD 0.026). |
| Breast cancer | 4 | 4/5 | One split misses at 0.747; nothing above k=4 is even suggestive. Sweep screenshot was the older column format (`ari_min`). |

**Chest pain k=8 reading (loadings check):** bundles reflect care delivery, not condition. Cardiac evidence splits into an acute workup bundle (troponin 62%, rank 1) and an outpatient bundle (stress test, EKG, diabetes, lipids). GERD loads on the GI/screening bundle (51%); costochondritis on the acute-respiratory bundle (43%, needs Zack's confirmation). Anxiety is diffuse (max 23%); SSRI/benzodiazepine sit in generic pharmacy with beta-blockers and statins, so they are not a psych signal. No psych bundle exists at k=5 or k=8.

**Letrozole k=8 reading:** fertility is four bundles (treatment c2, carrier screening c4, prenatal labs c7, pregnancy outcome c0; 37.5% of patients). Oncology is one bundle (c5, 7.2%): its top-10 codes look procedural, but breast_cancer, chemotherapy and mastectomy load there at 79-100% with low ranks (400-1,300). Oral aromatase inhibitors also load on the pharmacy bundle (c1), so c5's n=379 is a lower bound. c1, c3 and c6 (55%) are background care with no letrozole signal. Triage and pathway columns are draft inference and need review by Zack or an underwriter.

**Done this session in `nb/repr_learn_letrozole/Day1_Extract_and_Representation.ipynb`** (ported from chest pain, edited via script, not yet run end to end): prevalence-floor cells, sparse `Xs` replacing `X_nmf`/`Xv`, five-seed parallel sweep with the 4-of-5 rule, loadings check (fertility / oncology / other codesets; `K_CHECK` follows the last NMF fit), shorter markdown in the cells touched. Not ported: the k list in the NMF printout cell (`[5, 12]`; set it to `[8]` so stability and loadings use the k=8 fit), Table 1 component names. Breast cancer notebook was not touched by this port.

**To do next, besides Day 3:**
1. Letrozole: rerun Day 1 from the top; run the `breast_cancer` x `infertility` cross-tab by dominant component (counts patients with both histories and shows how many breast-cancer patients sit outside c5).
2. Chest pain: per-component stability at the chosen k; rewrite Table 1 `COMPONENT_GROUPS` and the "reading the output" notes (still written for k=11).
3. Update `docs/nmf-validation.md` with the five-seed chest pain table and the letrozole and breast cancer tables.

The 2026-10-01 morning entry follows. Its item 4 (port to breast cancer and letrozole) is done for letrozole as described above.

## Update 2026-10-01: pattern-discovery Day 1 (bag of codes + NMF)

Details are in `docs/` (start at `docs/README.md`). Summary for the next person:

**Done in `nb/repr_learn_chestpain/` Day 1 (reference version):**
- New unique fallback labels `<name20>__<class>__<concept_id>` in all three `ethos_omop.py` copies (`docs/event-labels.md`). Class and id are never cut; accents folded, non-alphanumerics removed.
- Prevalence-floor cell: floor of 35 patients (`KEEP_TAGS`); `X` is rebuilt from kept codes with `min_count=1`.
- One shared `NMF_KW = dict(init='nndsvd', random_state=0, max_iter=2000, tol=1e-4)` for every NMF fit (an earlier base/refit mismatch was fixed).
- One k-sweep cell: k = 3..14, five split seeds `(1, 2, 3, 4, 5)` (was two; the k=8 numbers below are from the two-split run and need refreshing), `N_BOOT_K = 10`, pass rule "4 of 5 splits", t-based intervals, run in parallel on a sparse matrix `Xs`. `X_nmf` and the dense `Xv` were removed. Verified equal to the old dense serial code on synthetic data (`docs/day1-performance.md`).
- Loadings-check cell built from `codesets.yaml` (psych / cardiac / other codesets).

**Chest pain results (latest run):** k=8 is the largest k that is solid on both splits (worst-split ARI 0.822, cosine 0.991, nothing unstable); k=9 is bad; k>=10 is only suggestive. The earlier k=11 (old labels) is not supported. NMF bundles reflect care delivery (pharmacy, acute workup, preventive), not condition: SSRI/benzodiazepine load on the pharmacy bundle; no psych bundle exists. Full tables in `docs/nmf-validation.md`.

**Open decisions / next steps:**
1. Pick the final k for chest pain (statistics favour 8) and rewrite Table 1's `COMPONENT_GROUPS` and the "Reading the k=.. output" notes; they are still hand-written for an older k and older labels.
2. Cardiac risk factors (hypertension, hyperlipidemia, obesity) are not in `codesets.yaml`, so the loadings check cannot see them. Adding them would pool their concepts and change the whole matrix; decision on hold.
3. Rerun Days 2-5 for chest pain: they still use `bag_of_codes(events, min_count=20)` (no patient floor) and do not drop the anchor before SVD, unlike Day 1. A `min_patients=` argument on `bag_of_codes()` would let all notebooks share the floor.
4. **Port to breast cancer and letrozole tomorrow, after their cohort SQL (`sql/breast_cancer_cohort.sql`, `sql/letrozole_cohort.sql`) has been reviewed.** Cohort sizes (1,704 and 6,103 patients) may change. What those two have today: the new labels, `NMF_KW`, and a serial dense k-sweep with the same cell order as chest pain. What they lack: the prevalence-floor cell, sparse `Xs` + parallel sweep, `X_nmf` removal, loadings check. Their sweep split sizes were fixed to scale with cohort size (a fixed 20,000/10,000 would have left no held-out patients).
5. The chest pain anchor code is 100% prevalent by construction (it defines the cohort); it is dropped only for the SVD/NMF matrix.

**Gotchas:** three separate copies of `ethos_omop.py` must be edited together; run the `nmf_stability` definition cell before the k sweep; the parallel sweep needs multiprocessing (blocked in restricted sandboxes, fine in Jupyter); Day 1 notebooks get large after a run, so edit the JSON with a script if an editor tool refuses to read them. All Day 1 results computed before the label change are not comparable and must be rerun.

## State

`nb/repr_clmbr/clmbr_paper_reproduction.ipynb` runs end to end (Stages 1–6): Snowflake OMOP sample → MEDS → `meds_reader` extract → small vocab → per-day code sets → tiny CLMBR-replica model (EmbeddingBag + GRU), trained loss goes down over 20 epochs.

Repo reorganized since the last handoff:
- Notebooks moved under `nb/`: the original CLMBR repro + MEDS tutorial are now `nb/repr_clmbr/`, alongside two new 5-day pattern-discovery courses, `nb/repr_learn_chestpain/` (dx_9487 triage) and `nb/repr_learn_letrozole/`.
- New `sql/` (Snowflake extract queries), `data_input/` (their OMOP CSV extract, gitignored), and `docs/` (design specs, e.g. the chest-pain-triage design doc) directories.
- `graphify-out/` added — generated knowledge-graph artifacts from the `/graphify` skill, regeneratable, not hand-maintained.
- `output/`, `data_input/`, `omop_extract/`, `meds_reader_extract/` are now all gitignored (previously only `omop_extract/`/`meds_reader_extract/` were tracked — see caveat below, now resolved).

Recent changes to the CLMBR notebook itself:
- **Stage 1** excludes `ethos_dip` (custom disclosure vocabulary) rows: the `concept` dump filters `vocabulary_id`, and all `master_*` domain tables filter out rows whose concept_id resolves to `ethos_dip`, so disclosure data never enters the pipeline.
- **Stage 6** model fixed after a day-features shape mismatch (`num_day_features` wasn't updated when a 5th feature — raw `gap_days` — was added to `day_features`).
- Final cell now inspects CLMBR representations for **3 patients** (not just 1), printing shapes and pairwise cosine similarity as a sanity check that the model differentiates patients rather than collapsing to a population average.

See `README.md` for what each file/folder is and how to run each notebook.

## Known caveats

- Everything after Stage 1 of `clmbr_paper_reproduction.ipynb` is not independently re-verifiable here — needs a live Snowflake session (SSO browser auth) to actually pull data and execute.
- This is a small-scale sanity-check reproduction (64 patients, ~256-token vocab, 20 epochs), not a paper-scale result — loss trending down is the only claim being made.
- **Path convention is inconsistent across notebook groups.** `nb/repr_clmbr/*.ipynb` reference data dirs (`omop_extract/`, `meds_output/`, `meds_reader_extract/`) as root-relative — they must be launched with the **repo root** as the Jupyter working directory even though the files live under `nb/repr_clmbr/`. `nb/repr_learn_*/` notebooks instead resolve `../data_input/`, `../sql/` relative to their own directory. Easy to break by launching Jupyter from the wrong place — not yet fixed to be launch-location-independent.
- `docs/` and `graphify-out/` are currently untracked but **not** gitignored — no decision made yet on whether to commit them or ignore them.

## Next steps (suggested, not started)

- Decide whether `docs/` (design specs) should be committed, and whether `graphify-out/` (regeneratable) should be gitignored instead.
- Consider making notebook data paths independent of Jupyter's launch directory (e.g. resolve relative to the notebook's own file location) so the two conventions in `nb/repr_clmbr/` vs `nb/repr_learn_*/` stop being a footgun.
- If pursuing paper-scale results, `hf_ehr/` already has the training infra for that — `nb/repr_clmbr/clmbr_paper_reproduction.ipynb` is a from-scratch minimal version for understanding, not meant to replace it.
