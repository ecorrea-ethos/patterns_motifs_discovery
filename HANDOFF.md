# Handoff

## Update 2026-10-14: chest pain literature, predicate engine, AHA codeset v2, k=8 comparison

All paths below are under `nb/repr_learn_chestpain/` unless stated. Conda env for scripts and notebooks: `ethos_llm` (pandas, sklearn, nbformat, openpyxl). `omop_local` has matplotlib; the system python has no numpy.

**Next step (yours): in `Chestpain_NMF_PrefixSpan_AHA.ipynb` run section "5 · Member table" (code cell 63), then re-run the final-table cell (65, now section 6).** The member cell writes `token_members_k8_chestpain_AHA.csv`: one row per concept with its group token, so a group-level entity becomes `concept_id IN (...)` for the predicate engine. The final-table cell reads that table and adds columns Q and R (members of the group tokens in the entities / in the pattern) to `final_table_chestpain_k8_AHA.xlsx`; it raises a NameError telling you to run the member cell first. Needs the Part B state (`K`, `H`, `hyb`): same kernel, or Run All. Both cells were tested on synthetic events at both token levels, not on the real extract. Then check the printed "group tokens among the top-5 loadings" list: those are the entities an engine on AHA c3 would be built from. Caution: re-running cell 65 overwrites the xlsx, so any Triage / Literature / PMIDs typed into `final_table_chestpain_k8_AHA.xlsx` by hand would be lost; save a copy first if you filled it.

**Done earlier (kept for the method): `Chestpain_NMF_PrefixSpan_full_k8.ipynb` was run and compared (see `sanity_check_AHA.md`).**
- It is a copy of `..._full` with `K_OVERRIDE = 8`, `VARIANT = 'full_k8'`, outputs cleared, same `codesets.yaml`, **concept-level tokens**. It writes `nmf_k8_chestpain_full_k8.npz`, `..._components.json`, `nmf_components_chestpain_k8_full_k8.xlsx`, `final_table_chestpain_k8_full_k8.xlsx`. About 25 min (PrefixSpan cell 50 is most of it).
- First run gives auto-names. The k=5 `DESCR` is skipped by the `DESCR_K = 5` guard in cell 43. Send the printed bundle list and write a `DESCR` block, then set `DESCR_K = 8` and re-run cell 43.
- Comparisons to make: `full_k8` vs AHA (same k: isolates codeset v2 + group tokens); `full_k8` vs `k5_full` (isolates k); `full_k8` vs `nmf_k8_chestpain_v2.npz` (older k=8 run). Method used so far: load both `.npz` (`pids`, `labels`), align on pids, `pd.crosstab`, ARI / NMI from sklearn; stability from the sweep table (cell 32) and bootstrap (cell 42); patterns from the final-table xlsx (columns 4-14).

**What exists now**
- `final_table_chestpain_k5_full.xlsx`: columns M (triage), O (literature), P (PMIDs) filled; Notes line A28 rewritten. Triage (draft): c0 Manual RUW, c1/c2/c4 Routine, c3 Unclear. Literature: `Partly` for 13 of 15 rows, `None` for r7 and r11 (`none found`), never `Yes` (no paper tests order). Titles only were read; a clinician should confirm each `Partly`. `final_table_chestpain_k5_full_literature_verified.csv` holds the 13 verified PMIDs. Searches and logs: `literature_search/`. APA reference list with PMIDs (it was only in chat before): `literature_search/references_apa.md`.
- `Chestpain_Workup_Predicate_Engine.md` + `chestpain_c0_flag_flow.png`: predicate/composite engine in the letrozole format. Target is **k=5 c0 (acute/ED, 25,953 patients)**; flag = chest pain + at least 3 of 4 services (ECG, troponin, chest X-ray, IV push) within 1 day of a chest pain event + one of three chest pain → X-ray/ECG → troponin sequences. The 1-day window is a draft, not calibrated. Evaluation protocol is defined, not run. **It does not map to k=8** (ED bundle is AHA c3, n=17,250); re-derive if k=8 becomes the reference.
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
1. Reference k for chest pain (5 vs 8) once `full_k8` is compared; then re-derive the predicate engine, flow image and literature ratings on the chosen run's ED bundle.
2. Group labels for AHA c4, c5, c7 (see above).
3. Same-k codeset test: AHA at k=5 vs full k=5 (not run; AHA sweep row k=5 has ARI 0.935).
4. Clinical review of the `Partly` ratings and of the 1-day window / 3-of-4 threshold in the engine.

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
