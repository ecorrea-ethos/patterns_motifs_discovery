# Handoff

## Update 2026-10-01: pattern-discovery Day 1 (bag of codes + NMF)

Details are in `docs/` (start at `docs/README.md`). Summary for the next person:

**Done in `nb/repr_learn_chestpain/` Day 1 (reference version):**
- New unique fallback labels `<name20>__<class>__<concept_id>` in all three `ethos_omop.py` copies (`docs/event-labels.md`). Class and id are never cut; accents folded, non-alphanumerics removed.
- Prevalence-floor cell: floor of 35 patients (`KEEP_TAGS`); `X` is rebuilt from kept codes with `min_count=1`.
- One shared `NMF_KW = dict(init='nndsvd', random_state=0, max_iter=2000, tol=1e-4)` for every NMF fit (an earlier base/refit mismatch was fixed).
- One k-sweep cell: k = 3..14, two split seeds `(1, 2)`, `N_BOOT_K = 10`, t-based intervals, run in parallel on a sparse matrix `Xs`. `X_nmf` and the dense `Xv` were removed. Verified equal to the old dense serial code on synthetic data (`docs/day1-performance.md`).
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
