# Handoff

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
