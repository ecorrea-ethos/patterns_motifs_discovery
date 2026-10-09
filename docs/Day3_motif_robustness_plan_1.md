# Day 3 v3 — Motif robustness upgrade: implementation plan

**For:** Claude Code
**Input notebook:** `Day3_prefixspan_v2.ipynb` (letrozole cohort, 8 visit-pruned NMF components, PrefixSpan motifs)
**Goal:** each motif proposed for the underwriting rule catalog must survive tests for:
- ordering artifacts
- duplicate coding
- record-length confounding
- component-label uncertainty
- selection bias and multiple testing
- time shift
- pre-decision truncation

Every downgrade must carry a written, auditable reason.

---

## 0. How to work (read first)

1. **Do not change v2 results silently.** Build the new code in a module plus a new notebook. Leave `Day3_prefixspan_v2.ipynb` untouched.
2. **Do not modify `ethos_omop.py` behaviour.** If you need new loaders, add *new* functions (e.g. `sequences_with_dates`) and keep the existing ones working. Do not edit `codesets.yaml` (v5). Its file load order is load-bearing.
3. **Work phase by phase.** For each phase:
   - implement it;
   - run that phase's unit tests on synthetic data;
   - run it on the real extract;
   - print a short v2-vs-v3 diff.

   Do not start the next phase while a test is failing.
4. **Stop and ask the user (do not guess) when:**
   - a column or table needed for a phase does not exist in the extract. Known unknowns are listed in §11.
   - a threshold choice changes which motifs pass.
5. **Be deterministic.** Every random step takes an explicit seed from the config. Two runs with the same config must produce byte-identical CSVs. There is a test for this.
6. **Benchmark before scaling.** Each phase has a rough compute estimate. These are guesses. Time a small run first, then pick B and seed counts that fit, and record what you chose in the run manifest.

---

## 1. Deliverables

```
motif_robustness/
    __init__.py
    seqindex.py        # fast + date-aware subsequence matching
    preprocess.py      # dated sequences, duplicate-coding detection, truncation
    mining.py          # PrefixSpan (moved from notebook, deterministic ties)
    scoring.py         # hit matrices, effect sizes, CIs, FDR, permutation nulls
    order_tests.py     # day-block permutation null, strict-date matching
    families.py        # motif families (Jaccard clustering)
    stability.py       # bootstrap, split-seeds, out-of-time, pre-index, NMF-refit
    confounding.py     # length / span covariates, Mantel-Haenszel OR
    verdict.py         # final tiering with reasons
    manifest.py        # config hash, data hash, git hash, seeds, timings
    evidence_store.py  # saves/loads per-motif arrays that the plots read (§14)
    style.py           # palette, fonts, sizes, file naming for figures
    plots.py           # evidence cards, forest, checklist, attrition, funnels, timelines
config/robustness.yaml
tests/test_motif_robustness.py      # synthetic planted-signal tests
notebooks/Day3_prefixspan_v3.ipynb  # thin: calls the module, shows tables/plots
outputs/day3_v3/
    motif_robustness.csv            # one row per (component, motif)
    motif_families.csv              # one row per (component, family)
    duplicate_coding_candidates.csv
    null_distributions.npz
    motif_evidence.npz              # per-motif arrays behind every plot (§14)
    run_manifest.json
    Day3_v3_top_patterns_table.xlsx # see §13
    figures/
        figures_manifest.csv        # file -> component, family, verdict, figure type
        summary/                    # forest, checklist, attrition, semantics slope charts
        c{comp}/                    # per-motif evidence cards, gaps, timing, funnels
        timelines/                  # OPT-IN only, de-identified (§14.8)
```

---

## 2. Phase 0 — Baseline reproduction and determinism

**Purpose:** prove the v2 numbers can be reproduced exactly before anything changes.

**Tasks**
- Move `prefixspan`, `contains`, `discriminative`, `component_motifs` and the 2b cells into `mining.py` / `stability.py` with the same defaults:
  - `rel_sup=0.15`, `max_len=4`, `max_cand=100`, `n_out=1500`
  - `MIN_LIFT=2`, `B=1000`, `SPLIT_SEEDS=(1..5)`
- Fix tie nondeterminism. Every "top-N by support" sort becomes:
  ```python
  pats.sort_values(['support', 'pattern'], ascending=[False, True]).head(max_cand)
  ```
  The `Counter` over `set(seq)` inside `prefixspan` inserts in hash order. That is why v2 notes say results vary between runs. The secondary sort key removes the dependence.
- Add `manifest.py`. It writes the following to `run_manifest.json`:
  - config dict and its SHA-256
  - SHA-256 of each input CSV
  - git commit
  - Python and package versions
  - `PYTHONHASHSEED`
  - all seeds
  - per-phase wall time

**Acceptance (regression check against v2 outputs)**
- Component sizes: `{0:622, 1:1600, 2:641, 3:760, 4:269, 5:406, 6:349, 7:591}`.
- `motifs` per component: `{0:100, 1:21, 2:100, 3:100, 4:100, 5:100, 6:100, 7:100}`.
- v2 "solid" counts: `{0:76, 1:0, 2:34, 3:39, 4:37, 5:76, 6:69, 7:80}`. With deterministic ties these may shift slightly. Report any difference and the motifs involved. Do not hide it.
- Test: running the pipeline twice yields identical CSVs (hash compare).

---

## 3. Phase 1 — Fast, date-aware matching (`seqindex.py`)

Everything downstream calls containment millions of times. The current `contains()` is a Python iterator scan.

**Build per patient:**
- `tokens: list[str]`
- `dates: np.ndarray[int]` (days since epoch, non-decreasing)
- `pos: dict[str, np.ndarray[int]]` (sorted positions of each token)

**Three matching semantics.** All must be implemented, tested and reported side by side.

| name | rule | why |
|---|---|---|
| `tie_ordered` | greedy earliest match, same as v2 `contains` | baseline, reproduces v2 |
| `strict_date` | each step must be on a **strictly later date** than the previous step | removes `DOMAIN_ORDER` tie-break artifacts |
| `windowed(max_span_days)` | `strict_date` + last step within `max_span_days` of the first step | removes "A eight years before B" matches; makes rules readable |

**Implementation notes**
- `tie_ordered`: loop over pattern tokens; `k = bisect_right(pos[t], cur)`; fail if `k == len`.
- `strict_date`: same idea on dates. Find the first occurrence of `t` whose date is greater than `cur_date`. Use a per-token date array and `bisect_right`.
- `windowed`: for each occurrence of `pat[0]` as the start, run the greedy `strict_date` match forward. Greedy gives the minimal end for a fixed start, so the check `dates[end] - dates[start] <= max_span` is exact. Return True on the first success.
- Dated sequences need a new loader, `preprocess.sequences_with_dates(events, ...)`. It must apply the same dedup / `collapse_repeats` rules as `eo.sequences`. When collapsing a run of repeats, keep the **first** date of the run. Verify on 200 random patients that its token lists equal `eo.sequences` output exactly.

**Tests**
- `tie_ordered` equals the old `contains` on 10,000 random (sequence, pattern) pairs from the real data.
- Hand-built cases for each semantics, including:
  - same-day A and B (strict fails, tie-ordered may pass)
  - repeated tokens
  - window boundary exactly equal to `max_span`
- Benchmark: report µs per call before and after.

---

## 4. Phase 2 — Duplicate coding and same-day structure (`preprocess.py`)

**2a. Detect cross-vocabulary duplicates (data-first, review-only)**
- For every token pair (A, B) with both prevalences ≥ 1% of the cohort, compute:
  - `same_day_rate(A→B)` = share of A's dates on which B also occurs, and the reverse.
- Flag the pair as a duplicate-coding candidate if:
  - both directions are ≥ `dup_same_day_min` (default 0.9), and
  - the pair spans different vocabularies or domains (e.g. CPT4 vs SNOMED).
- Write the flags to `duplicate_coding_candidates.csv` with columns:
  - A, B, both rates
  - vocabularies, concept names
  - number of patients
- **Do not auto-merge.** The user reviews this list. Approved pairs go into `config/robustness.yaml` under `equivalent_tokens:` and are merged in a re-run, with the merge recorded in the manifest.
- Expected example to sanity-check (inference, verify on real data): `immunization_adminis__cpt4__2213418` with `active_or_passive_im__procedure__4132855`.

**2b. Per-motif same-day share**
- For each motif, take patients where it matches under `tie_ordered`. Compute the share of matches in which any two consecutive steps fall on the same date.
- Report the result as column `same_day_step_share`.

**Tests**
- Synthetic: plant B on the same day as A in 95% of A's occurrences. The pair must be flagged.
- Unrelated tokens with 30% same-day overlap must not be flagged.

---

## 5. Phase 3 — Does order matter? (`order_tests.py`)

The components were built from bag-of-codes NMF. High lift for a motif made of a component's own codes is therefore partly built in. This phase separates **"these codes co-occur"** from **"they occur in this order."**

**Day-block permutation null**
- Represent each patient as a list of day blocks: the tokens on each date, kept as one unit.
- Null draw: randomly permute the **order of the day blocks** and re-assign dates in the original sorted order. This keeps:
  - the bag of codes
  - same-day bundles
  - the number of active days

  It destroys only between-day order.
- For a motif `pat`, set `pool` = in-component patients that contain all of `set(pat)` (unordered). Then compute:
  - `p_obs` = share of `pool` matching under `strict_date`
  - `p_null` = mean over `B_order` draws of the same share on permuted patients
  - `order_ratio = p_obs / p_null`
  - `p_order` = empirical one-sided p-value, `(1 + #{null ≥ obs}) / (1 + B_order)`
  - `order_ratio_lo` / `order_ratio_hi` = bootstrap CI over patients in `pool`
- **Cost control:**
  - generate the B_order permuted versions of each patient **once per component** and reuse them across all motifs;
  - run only on motifs that passed the Phase 5 pre-filter (default top 30 per component by log OR);
  - parallelise over components with joblib.
  - Default `B_order = 200`. Benchmark first.

**Interpretation, written into the verdict**
- `order_ratio_lo > 1` and `p_order` FDR-significant: catalog it as an **ordered rule**.
- Otherwise, if the motif passes everything else: catalog it as an **unordered co-occurrence rule** ("A and B and C present"). Do not discard it.

**Tests**
- Synthetic, two planted cases:
  - **Order planted:** A always precedes B by ≥ 7 days. Expect `order_ratio` well above 1 and a small p.
  - **No order planted:** A and B co-occur in random order. Expect `order_ratio` ≈ 1 and p > 0.2.

---

## 6. Phase 4 — Motif families (`families.py`)

Near-duplicate motifs split the stability vote. For example, pregnancy rank 1 is "unstable" (2/5) while rank 2, nearly identical, is "solid" (5/5).

**Steps**
- Per component, cluster motifs on the Jaccard distance of their **in-component patient coverage**: rows of the hit matrix, `strict_date` semantics.
  ```python
  from scipy.cluster.hierarchy import linkage, fcluster
  from scipy.spatial.distance import pdist
  fam = fcluster(linkage(pdist(H_in, 'jaccard'), 'average'),
                 t=cfg.family_jaccard_dist, criterion='distance')   # default 0.2
  ```
- Family representative: the shortest motif; break ties by highest log OR, then lexical order.
- Family-level stability: a family is "found" in a split / draw if **any** member is found.
- Report stability at both motif level and family level. The verdict (Phase 10) uses the **family** level, and the catalog lists one representative per family with its member list.

**Tests**
- Synthetic: three variants of one planted pathway form one family.
- A distinct planted pathway forms its own family.

---

## 7. Phase 5 — Effect sizes, outside sample, multiple testing (`scoring.py`)

**7a. Hit matrix on all patients**
- `hits_all[c]` is a boolean matrix of shape `(n_candidates_c, 5238)`, one per semantics.
- Use **all non-component patients** as the outside group, replacing the fixed 1,500 sample. It removes one source of variance at no cost.
- Report the old and new `sup_out` side by side for the regression diff.

**7b. Effect measures (replace the `+0.01` lift as the primary metric)**
- Per motif, from the 2×2 table (in/out × has/has-not):

| column | definition |
|---|---|
| `sup_in`, `sup_out` | proportions, with Wilson 95% CIs |
| `risk_diff` | `sup_in - sup_out`, with Newcombe CI |
| `log_or` | log odds ratio with Haldane–Anscombe +0.5 correction |
| `log_or_lo`, `log_or_hi` | Woolf CI |
| `ppv_for_component` | `P(in component \| motif)` |
| `sens_for_component` | `P(motif \| in component)` |
| `fisher_p` | Fisher exact p-value |

- Keep the v2 `lift` column for continuity, but do not use it in the verdict. Note in the notebook why: c4's lift of ~60 is mostly the pseudo-count, because `sup_out` ≈ 0.005.

**7c. Multiple testing**
- Apply Benjamini–Hochberg over **all** (component × motif) tests in a run, giving `q_fisher`.
- **Label-permutation null for max effect, per component:**
  - permute component labels while keeping group sizes, `B_perm = 1000`;
  - compute `log_or` for all candidates with matrix ops (`hits_all @ indicator_matrix`);
  - record the max per draw;
  - `p_fwer` = share of draws whose max ≥ the observed value.
- Document the limitation: candidates stay fixed, so this does not re-mine under the null. As an optional check (`perm_remine: true`), run 20 draws that re-mine on permuted labels and report the max log OR distribution.

**Tests**
- Random labels on synthetic data: about 5% of motifs have `q < 0.05` at most (FDR control sanity check).
- `p_fwer` is roughly uniform.

---

## 8. Phase 6 — Stability (`stability.py`)

Run every tier under `strict_date` semantics as the primary. Run `tie_ordered` as a secondary for comparison with v2.

**8a. Selection-aware bootstrap (cheap)**
- Keep the v2 patient-resampling bootstrap on fixed candidates, `B = 1000`, but resample the in-group and the **full** outside group.
- Add `p_top3` and `p_top10`: the share of draws in which the motif ranks in its component's top 3 / top 10 by log OR.
- Add `p_logor_ok`: the share of draws with `log_or ≥ log(min_or)`.
- Use percentile CIs on the log scale. Add BCa CIs if `scipy.stats.bootstrap` handles it in reasonable time.

**8b. Nested bootstrap (expensive, optional, `nested_bootstrap: true`)**
- `B_nested = 50` draws. In each, resample the component's patients and **re-mine** candidates, then score.
- Report `nested_found_rate` per family. This is the honest version of "would we find it again". Benchmark one draw first. Expect roughly a few minutes per draw for all 8 components on 8–12 cores; this is an estimate.

**8c. Repeated split-half validation (replaces the 5 seeds)**
- `SPLIT_SEEDS = 1..20`. In each seed, use both directions (train A → test B, and train B → test A), giving 40 evaluations.
- Record two separate outcomes per evaluation:
  - `rediscovered`: the motif or family is nominated in the train half's top `max_cand` **and** passes on the test half (v2 definition).
  - `holds_out`: the **full-run** motif scored directly on the test half passes the support floor and `log_or_lo ≥ log(min_or)`. This removes the dependence on the candidate cutoff.
- Report `rediscovery_rate` and `holdout_rate` with Wilson CIs, at motif level and family level.
- Flag small components: when the half size is below 200 (c4 = 135), set `small_component = True` and note it in the verdict reasons.

**8d. Component-label uncertainty (NMF refits)**
- `B_label = 50` draws. In each:
  - bootstrap-resample patients;
  - refit NMF k=8 with the Day 1 v2 settings (same prevalence floor, `nmf_cols`, `init='nndsvd'`, `max_iter=2000`, `tol=1e-4`);
  - align components to the reference H by Hungarian matching on row cosine similarity;
  - if a component's best cosine < 0.8, mark it unmatched for that draw;
  - assign **all** 5,238 patients with `transform().argmax(1)`;
  - recompute metrics with `hits_all`. No re-mining is needed.
- Report:
  - `p_logor_ok_nmf`: share of matched draws passing
  - `component_match_rate`: share of draws in which the component was matched
- **Soft-membership variant (no refits):** weighted `sup_in = Σ_j w_jc·h_ij / Σ_j w_jc`, using row-normalised W from the reference fit. Report `log_or_soft`.

**8e. Out-of-time validation**
- Use the index year of first letrozole (`eo.index_dates(events, 'letrozole')`).
- Train = patients with index date ≤ the 60th-percentile date; test = the rest.
- Mine on the train patients per component and score on the test patients.
- Report `oot_holds` (bool), plus `oot_log_or` with CI.
- Also print the index-year distribution per component. A component concentrated in a few years is a warning sign for Day 5.

**8f. Pre-index truncation (decision-time realism)**
- Truncate each sequence to events **strictly before** the letrozole index date. This is a proxy for "what is known at decision time"; see §11 for the true application date.
- Re-mine and score per component. Report `pre_index_holds` and `pre_index_log_or`.
- Expected (from earlier findings, verify): many fertility motifs are mostly post-index, while cancer-workup motifs are pre-index. Surface this explicitly. It decides which motifs can become underwriting rules at all.

**Tests**
- A planted stable pathway gets `holdout_rate ≥ 0.9`.
- A noise motif nominated by chance gets `holdout_rate ≤ 0.2`.
- Hungarian alignment recovers a known permutation of components.

---

## 9. Phase 7 — Confounding by record length (`confounding.py`)

**Patient covariates**
- `n_tokens` (after preprocessing)
- `n_active_days`
- `span_days` (last event − first event)
- `index_year`

Lookback is proxied from first/last event because there is no `observation_period` in the extract. Repeat the existing left-truncation warning in the notebook.

**Checks**
- Per component: standardised mean difference (SMD) of each covariate, in vs out. Flag components with |SMD| > 0.25.
- Per motif: Mantel–Haenszel odds ratio across **deciles of `n_active_days`**, with a Robins–Breslow–Greenland CI. Report `mh_log_or`, `mh_log_or_lo`.
- Flag `length_driven = True` when the crude `log_or_lo` passes but `mh_log_or_lo < log(min_or)`.
- Sensitivity variant: repeat the Phase 5 metrics with a **length-matched outside sample** (sample the outside group to match the in-group's `n_active_days` decile distribution, seed from config).

**Tests**
- Synthetic: the component has 3× longer random sequences and no planted signal. Crude OR > 2, but the MH OR CI covers 1, so `length_driven = True`.

---

## 10. Phase 8 — Criterion validity

**c5 (oncology) against confirmed breast cancer**
- Case definition: reuse the mini Table 1 rule, ICD-10 `C50.x` from `condition_source_value` or SNOMED `4162253`. ICD-9 `174.x` currently finds nobody; keep it in the rule anyway.
- For each c5 family representative, over the **whole cohort** (c5 is a lower bound, so cases sit in other components too), compute:
  - sensitivity, specificity, PPV and NPV for confirmed dx
  - exact Clopper–Pearson CIs
- Also compute the same with pre-index truncation.

**Fertility components against the weak fertility label**
- Compute the same metrics against `eo.weak_labels` fertility labels.
- Mark the result `circular = True` whenever the motif contains a tag from `FERTILITY_TAGS`, because the label rule partly rediscovers itself.

**Report:** n = 70 confirmed cases, so CIs will be wide. Print them; do not suppress them.

---

## 11. Known unknowns — ask the user before implementing

1. **Order-type / data-source column (DX vs BOLS vs neither).** This is needed for funnel-stratified replication: run 8c within each source and report `holds_by_source`. It is not in the events schema seen so far. Ask where it lives (possibly a schema like `AIRFLOW_UW_EVIDENCE`) and how it joins to `person_id`.
2. **Application / decision date.** This is needed for true decision-time truncation. Until it is available, §8f uses the letrozole index date as a proxy and labels it that way everywhere.
3. **Thresholds** in §12. The defaults are proposals. Confirm them with the user (and Zack) before treating verdicts as final.
4. **Equivalent-token merges** from Phase 2a need user approval.
5. **Plot palette hex values and fonts** (§14.3), and whether example timelines (§14.8) may be generated or shared.

---

## 12. Phase 9 — Final verdict (`verdict.py`)

One row per **family representative**. Every rule below is a config value. Each failed check appends a short reason string to `reasons`, e.g. `"length_driven: MH OR lo 1.6 < 2"`.

```text
catalog_robust  (all must hold)
    q_fisher < 0.05 and p_fwer < 0.05
    log_or_lo >= log(min_or)                     # strict_date semantics, full outside group
    family holdout_rate_lo (Wilson) >= 0.70
    p_top10 >= 0.80
    p_logor_ok_nmf >= 0.90 and component_match_rate >= 0.90
    not length_driven
    oot_holds
    same_day_step_share < 0.50  OR  motif still passes under strict_date
    pre_index_holds      -> sets usable_at_decision = True/False (reported, not a gate)

rule_form
    'ordered'    if order_ratio_lo > 1 and q_order < 0.05
    'unordered'  otherwise

catalog_candidate   = passes all but at most one of: oot_holds, p_top10, small_component
exploratory_lead    = q_fisher < 0.05 but fails two or more stability checks
reject              = otherwise
```

Proposed defaults (config): `min_or: 2.0`, `max_span_days: 365`, `family_jaccard_dist: 0.2`, `dup_same_day_min: 0.9`, `rel_sup: 0.15`, `max_len: 4`, `max_cand: 100`.

---

## 13. Phase 10 — Outputs and reporting

**`motif_robustness.csv` columns** (one row per component × motif):
- identity: `component, family_id, is_representative, pattern, pattern_len`
- matching: `semantics_primary, same_day_step_share`
- support: `sup_in, sup_in_lo, sup_in_hi, sup_out, sup_out_lo, sup_out_hi`
- effect: `risk_diff (+CI), log_or, log_or_lo, log_or_hi, lift_v2, ppv_for_component, sens_for_component`
- testing: `fisher_p, q_fisher, p_fwer`
- order: `order_ratio, order_ratio_lo, order_ratio_hi, p_order, q_order`
- bootstrap: `p_logor_ok, p_top3, p_top10, nested_found_rate`
- splits: `rediscovery_rate (+CI), holdout_rate (+CI)`
- labels: `p_logor_ok_nmf, component_match_rate, log_or_soft`
- confounding: `mh_log_or, mh_log_or_lo, length_driven`
- validation: `oot_holds, oot_log_or, pre_index_holds, pre_index_log_or`
- criterion: `criterion_sens, criterion_ppv` (with CIs, where applicable)
- verdict: `small_component, rule_form, usable_at_decision, verdict, reasons`

**Notebook `Day3_prefixspan_v3.ipynb` sections**
1. Setup and manifest.
2. Baseline regression vs v2 (Phase 0 diff).
3. Duplicate-coding candidates (for review).
4. Matching semantics comparison: how many v2 "solid" motifs survive `strict_date` and `windowed`.
5. Order test results, with a plot of `order_ratio` and CI per family.
6. Families.
7. Stability tiers, with a plot of the family `holdout_rate` CI per component.
8. Label uncertainty.
9. Length confounding, with the SMD table and crude vs MH OR plot.
10. Out-of-time and pre-index results.
11. Criterion validity for c5.
12. Final catalog table, with verdict counts per component and the full reasons column.
13. Evidence plots (§14): attrition chart and checklist matrix first, then forest plots, then one evidence card per catalog motif.

Keep the plain-language reading notes under each table, as in v2. Avoid black-box framing: every number must trace back to a 2×2 table or a resampling procedure.

**Excel deliverable `Day3_v3_top_patterns_table.xlsx`**
- Keep the v2 table layout and the existing literature columns (N–P: support level, summary, PMIDs), carried over by matching on pattern string. Mark rows where the pattern changed.
- Add new columns: `rule_form`, `holdout_rate (CI)`, `log OR (CI)`, `order_ratio (CI)`, `length_driven`, `pre_index_holds`, `verdict`, `reasons`.
- Same fonts and header style as the existing sheet (Arial, header fill `334E68`, white bold header text). Same colour coding for verdicts: green `D6F0DE`, amber `FBEFC9`, red `F8D7D7`.

---

## 14. Phase 11 — Evidence plots (`evidence_store.py`, `style.py`, `plots.py`)

**Purpose:** every motif that reaches the catalog gets a figure a non-technical reviewer (Zack, underwriters) can read without the code. Each figure must answer "why should I believe this rule?" with numbers that trace back to a 2×2 table or a resampling procedure.

### 14.1 Ground rules
- **Plots never recompute statistics.** They read only `motif_robustness.csv` and `motif_evidence.npz`. If a number on a plot cannot be found in those files, that is a bug.
- **Every figure ships with its data.** Save `<figure>.csv` next to each `<figure>.png`, holding exactly the values drawn.
- **Every figure ships with a caption.** Save `<figure>.txt`: an auto-filled 2–3 sentence plain-language caption, e.g. "48% of the 622 patients in this group follow this path vs 6% of everyone else (odds ratio 14, 95% CI 11–18). The path held up in 38 of 40 held-out checks." The captions are ready to paste into slides.
- **Readable labels.** Never show raw tokens such as `immunization_adminis__cpt4__2213418`. Add `pretty_token(token, concept)`:
  - format: `"Immunization administration [CPT4 90471]"`, matching the Excel column E style;
  - truncate at 45 characters with "…";
  - keep the full name in the CSV.
- **Scope.** Generate per-motif figures for verdicts `catalog_robust` and `catalog_candidate`, family representatives only. Summary figures include all families.
- **Deterministic.** Use fixed seeds for any sampling or jitter. Save with `metadata={'Software': None}` so repeated runs give identical bytes where matplotlib allows.

### 14.2 Data contract — what earlier phases must persist (`evidence_store.py`)
Add saving calls to the phases below. Key every array by `(component, family_id)` and store it in `motif_evidence.npz` (or a folder of `.npy` files if that is too large).

| key | shape / content | written by |
|---|---|---|
| `boot_log_or` | (B,) bootstrap log OR draws | Phase 6a |
| `nmf_log_or` | (B_label,) log OR per NMF refit, NaN if component unmatched | Phase 6d |
| `holdout_pass`, `rediscovered` | (20, 2) bool, seed × direction | Phase 6c |
| `order_null` | (B_order,) null `p_null` draws; plus scalar `p_obs` | Phase 3 |
| `step_gaps_days` | list of arrays, one per consecutive step pair, over matching in-group patients | Phase 2b |
| `step_days_from_index` | list of arrays, one per step: days from first letrozole | Phase 8f |
| `funnel_counts` | in-group and out-group counts reaching step 1, 1→2, 1→2→3, … (`strict_date`) | Phase 5 |
| `semantics_log_or` | log OR + CI under `tie_ordered`, `strict_date`, `windowed` | Phase 1/5 |
| `checks` | dict of check name → pass / fail / NA, mirroring the verdict rules | Phase 9 |

Test: `evidence_store` round-trips (save then load gives identical arrays) on synthetic data.

### 14.3 Style (`style.py`)
- Palette: navy / teal / amber, matching the existing decks.
  - Default hexes: navy `334E68` (Excel header), teal `2A9D8F`, amber `E9A23B`.
  - **Confirm the exact hex values with the user**, then put them in config.
- Verdict colours: same as the Excel sheet (green `D6F0DE`, amber `FBEFC9`, red `F8D7D7`), with darker edge versions for visibility on white.
- Fonts: Calibri for plot text, falling back to Carlito, then Arial. Log a warning if falling back.
- No background images, light grid only.
- Sizes:
  - evidence cards: 13.33 × 7.5 in (16:9 slide)
  - single charts: 10 × 5.6 in
  - 200 dpi PNG; optional SVG
- File naming: `c{comp}/fam{fid:03d}_{slug}_{figtype}.png`, where `slug` is the first 3 pretty tokens joined with `_`, lowercase, max 60 characters.
- Write every saved figure as a row in `figures_manifest.csv`.

### 14.4 Summary figures (`figures/summary/`)
1. **Attrition chart.** Horizontal bars showing how many v2 "solid" motifs and families survive each check, in this order:
   - `strict_date`
   - duplicate-coding merge
   - FDR
   - held-out replication
   - NMF-label stability
   - length adjustment
   - out-of-time

   End with final verdict counts. One panel per component group (fertility / oncology / background). *This is the one-slide answer to "how robust is this?"*
2. **Checklist matrix.** Rows = family representatives (grouped by component); columns = each verdict check; cells = pass (green) / fail (red) / not applicable (grey). Right margin: verdict and `rule_form`. This makes the verdict logic auditable at a glance.
3. **Forest plot.**
   - One plot per component, plus one for the final catalog.
   - Each family: log OR with 95% CI.
   - Marker: ● ordered rule, ◆ unordered rule. Colour by verdict.
   - Reference lines at OR = 1 and OR = `min_or`. Axis ticks show the OR (not the log).
   - Right-hand text: `holdout_rate` (CI) and `sup_in` / `sup_out`.
4. **Matching-semantics slope chart.** For each v2 "solid" motif: log OR under `tie_ordered` → `strict_date` → `windowed`, as lines. Highlight motifs that drop below `min_or`. This shows same-day artifacts disappearing.
5. **Length confounding scatter.** Crude log OR vs Mantel–Haenszel log OR, with the diagonal, and `length_driven` motifs highlighted. (The same plot as Phase 7 — move it here so all figures come from one module.)

### 14.5 Per-motif evidence card (`figures/c{comp}/…_card.png`)
One 16:9 figure per catalog motif with a 2 × 3 grid.

**Header**
- pretty pattern (steps joined by "→")
- component name and n
- family size ("+N variants")
- verdict badge and `rule_form`
- up to 3 reasons, if not `catalog_robust`

**Panels**

| # | panel | content |
|---|---|---|
| 1 | Who has it | in-group vs out-group support bars with Wilson CIs, the 2×2 counts as text, PPV and sensitivity |
| 2 | Is the effect steady? | histogram of `boot_log_or` with 95% CI shaded and a line at `log(min_or)`; overlay `nmf_log_or` as a second distribution; annotate `p_logor_ok` and `p_logor_ok_nmf` |
| 3 | Does it replicate? | 20 × 2 dot grid of `holdout_pass` (filled = pass), second row for `rediscovered`; text: holdout rate with Wilson CI |
| 4 | Does order matter? | histogram of `order_null` with the observed `p_obs` line; text: `order_ratio` (CI), `p_order`, and the resulting rule form |
| 5 | How far apart are the steps? | per consecutive step pair, a strip/box plot of days on a symlog axis; mark the same-day share and the `max_span_days` line |
| 6 | When does it happen vs letrozole? | per step, violin of days from first letrozole, line at 0; text: share of steps before index and `usable_at_decision` |

**Footer:** run ID, config hash, data hash (short), date.

### 14.6 Step funnel (`…_funnel.png`)
- Paired horizontal bars, in-group vs out-group: share of patients reaching step 1, then 1→2, then 1→2→3 (`strict_date`). This shows *where* the motif separates the groups.
- Optional (`sankey_html: true`): an interactive Plotly Sankey as HTML. Plotly is an extra dependency, so check whether it is installed and ask before adding it.

### 14.7 Gap and timing details (`…_gaps.png`, `…_timing.png`)
Larger stand-alone versions of card panels 5 and 6, for motifs where the timing is the point (e.g. cancer workup before letrozole). Generate them only when `same_day_step_share > 0.2` or `usable_at_decision` differs between family members.

### 14.8 Example timelines — OPT-IN, de-identified (`figures/timelines/`)
Off by default (`example_timelines: false`). When on:
- Per catalog motif, sample (fixed seed):
  - 5 in-group patients who match the motif;
  - 5 in-group patients who have at least one step but do not match (near-misses).
- Swimmer plot:
  - x-axis = days from first letrozole;
  - motif steps drawn as large labelled markers;
  - other events as small grey ticks.
- **Privacy:**
  - no `person_id`, birth dates or calendar dates;
  - relative days only, with random jitter of ±3 days;
  - suppress the figure if fewer than `min_cell` (default 11) patients match;
  - write a `README.txt` in the folder stating the figures contain patient-level data and are for internal review only.
- Confirm with the user whether these may be shared outside the analytics team before enabling.

### 14.9 Tests
- **Data matches the CSV:** each plot function has a pure `_data()` companion returning the DataFrame it draws. The tests assert those values equal `motif_robustness.csv` / `motif_evidence.npz`.
- **Smoke test:** generate every figure type from the synthetic evidence store. Assert that each PNG, CSV and TXT exists, is non-empty, and is listed in `figures_manifest.csv`.
- **Labels:** `pretty_token` never returns a raw token string when a concept name exists.
- **Privacy:** with `example_timelines: false`, no file is written under `figures/timelines/`. With it true and fewer than `min_cell` matches, the figure is suppressed and the suppression is logged.

---

## 15. Suggested run order and rough budget (estimates; benchmark first)

| phase | content | rough cost |
|---|---|---|
| 0 | baseline + determinism | ≈ v2 runtime (~5 min) |
| 1 | seqindex | minutes; should cut later phases a lot |
| 2 | duplicate coding | minutes |
| 5 | scoring, FDR, label-permutation null | minutes (matrix ops) |
| 4 | families | seconds |
| 3 | order null, B_order=200, top 30/component | benchmark; likely tens of minutes |
| 6a/6c | bootstrap + 20×2 splits | ~10–20 min |
| 6d | NMF refits, B_label=50 | benchmark one refit; likely tens of minutes |
| 6e/6f | out-of-time, pre-index | ~2× one mining run |
| 7 | MH OR + matched outside sample | minutes |
| 8 | criterion | seconds |
| 6b | nested bootstrap (optional) | longest; run overnight if enabled |
| 11 | evidence plots | minutes (reads saved artifacts only); run last, re-run alone after styling tweaks |

Run Phase 5 before Phase 3, because the order test uses Phase 5's pre-filter.

---

## 16. Definition of done

- All synthetic planted-signal tests pass:
  - order vs no-order
  - duplicate coding
  - length confound
  - stable vs noise motif
  - FDR sanity
  - Hungarian alignment
- Two identical runs produce identical output hashes.
- Phase 0 regression diff is explained line by line.
- Every motif in the catalog has a verdict and, if not `catalog_robust`, at least one reason.
- The §11 unknowns are either resolved with the user or clearly labelled as proxies in every output.
- Every `catalog_robust` / `catalog_candidate` family has an evidence card. Every figure has its data CSV and caption TXT and is listed in `figures_manifest.csv`.
- Example timelines are off unless the user enabled them; if enabled, the privacy rules in §14.8 hold.
