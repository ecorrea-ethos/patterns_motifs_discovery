# Choosing and validating k for the NMF (Day 1)

## What this covers
Day 1 factorises the patient-by-code table with NMF into a handful of "bundles" of codes that
tend to occur together. This doc explains how the number of bundles (k) is chosen and checked,
and what the chest pain run found. Terms (NMF, ARI, cosine, silhouette, bag of codes):
see [glossary.md](glossary.md). Labels: [event-labels.md](event-labels.md).

## The pieces, in notebook order
All three Day 1 notebooks use this order (the chest pain one is the reference):

| Step | Cell | Purpose |
|---|---|---|
| 1 | SVD | Compress patients to 30 numbers; used for KMeans and for the silhouette |
| 2 | `nmf_stability` definition | Defines `NMF_KW` (the one place with the NMF settings) and the bootstrap check |
| 3 | k sweep | Fits k = 3..14 on two train/held-out splits and reports every metric |
| 4 | Reading notes | How to read the sweep and the stability table |
| 5 | Main NMF fit | The chosen k; prints the top codes per component |
| 6 | Loadings check (chest pain only so far) | Shows where each codeset tag sits across components |
| 7 | Stability call | Per-component stability of the main fit |

Run them top to bottom except that step 2 must run before step 3 (it defines what step 3 uses).

## Settings
`NMF_KW = dict(init='nndsvd', random_state=0, max_iter=2000, tol=1e-4)`, used by **every** NMF
fit (base fits, bootstrap refits, the main fit). Why one object: an earlier version fit the
base model at `2000 / 1e-4` but the refits at `1500 / 1e-3`. Refits that are less converged than the
base lower the measured stability, and the mistake was invisible. Do not hand-type NMF
settings in new cells.

## What the sweep measures (per k, per split)
- **Held-out error:** how well the model explains patients it was not fit on. Always falls with
  k; look for an elbow (none has appeared).
- **Silhouette** of the `argmax` groups in SVD space: how separated the groups are. Low in
  absolute terms (about 0.05) and falls with k; read the shape only.
- **Bootstrap ARI:** refit on resampled patients and compare the resulting patient groups with
  the base fit's. 1 = identical. Cut-offs follow Day 2: 0.75 solid, 0.60 suggestive.
- **Mean cosine** between each bundle and its best-matching bundle in each refit (components
  are matched, because their numbering is arbitrary). 1 = the same code bundle comes back.
- **`n_unstable`:** components whose matched cosine is below 0.75. **`n_used`:** components that
  are dominant for at least 1% of held-out patients.

Settings in the sweep cell: `SPLIT_SEEDS = (1, 2)` (two independent splits of the cohort),
`N_BOOT_K = 10` refits per k and split, `K_GRID = 3..14`. The error bars use a t interval
(`stats.t.ppf(0.975, N_BOOT_K - 1)`), because a 1.96 interval is too narrow for few refits.
`ari_min` (the worst split) is what the pass lines use.

Why two splits: with one split, a k can look stable or unstable depending on which patients
were drawn. On the chest pain data one earlier run gave ARI 0.49 for k=13 on one split and
0.73 on another. More refits only reduce noise within a split; they cannot show that.

Split sizes scale with the cohort: `N_SWEEP = min(20_000, 60% of cohort)` and
`N_HELD = min(10_000, the rest)`. (Chest pain: 139,416 patients; breast cancer: 1,704; letrozole:
6,103.)

## Chest pain findings (new labels, 35-patient floor, `NMF_KW`, 10 refits, 2 splits)
ARI of the worse split (`ari_min`), mean cosine, unstable components:

| k | ari_min | cos | unstable |
|---|---|---|---|
| 3-5 | 0.88-0.93 | 0.997-0.998 | 0 |
| 6 | 0.745 | 0.919 | 1 |
| 7 | 0.784 | 0.953 | 1 |
| **8** | **0.822** | **0.991** | **0** |
| 9 | 0.564 | 0.890 | 3 |
| 10 | 0.687 | 0.944 | 1 |
| 11-14 | 0.57-0.61 | 0.909-0.959 | 1-2 |

- **k=8 is the largest k that is solid on both splits.** k=9 is clearly bad. From k=10 up, ARI is
  in the suggestive range on at least one split.
- The earlier choice of k=11 (made on the old, merged labels) is **not supported** under the new labels.
- Held-out error falls in a straight line (0.890 to 0.853), so it does not pick k.

### What the components are at k=8
| # | Share | Reading |
|---|---|---|
| 0 | 22% | Preventive / annual physical with labs (EKG lands here) |
| 1 | 23% | Acute infection pharmacy (steroids, antibiotics, `pharmacy` visit) |
| 2 | 11% | Women's health plus infectious and pregnancy testing |
| 3 | 11% | Acute ED-style workup (troponin, imaging, lipase, injections) |
| 4 | 6% | GI endoscopy / colonoscopy workup (GERD) |
| 5 | 13% | Physical therapy / MSK |
| 6 | 7% | Fatigue / anemia / thyroid lab panel |
| 7 | 7% | Acute respiratory infection |

Compared with k=10, k=8 merges PT with chiropractic and merges mammography screening into
component 2. Neither affects the chest pain question.

### Where the clinical codes sit (loadings check)
- **Psych:** SSRI (90%) and benzodiazepine (74%) sit in the pharmacy bundle (1). Anxiety and panic
  attack are spread thinly (largest share 23% and 29%, both in component 7). No bundle is
  psychiatric.
- **Cardiac:** troponin defines component 3 (62%, rank 1). Stress test, CAD and angiography split
  roughly 45/55 between the preventive bundle (0) and the acute workup (3).
- **GERD** defines component 4 (51%, rank 5). **T2DM and HbA1c** sit in component 0.
- `ed_visit` shows 100% in component 3, but its rank there is 733, so its total loading is tiny.
  Shares are normalised per code, so a small concentrated loading looks like 100%.

**Takeaway:** NMF bundles describe how care is delivered (pharmacy, acute workup, preventive
visits) more than the condition behind it. Use them to describe the cohort (Table 1). The
psych versus cardiac distinction has to come from the weak labels and the ordered patterns on
Day 3, not from NMF.

## Caveats
- Stability is not meaning. A stable bundle can still be a utilisation artefact.
- `argmax` groups throw away how much of each bundle a patient has. If ARI is low but cosine is
  high, prefer the soft loadings (`nmf.transform`) over hard groups.
- Table 1's `COMPONENT_GROUPS` and the "Reading the k=.. output" notes are hand-written for one k.
  They must be rewritten whenever k or the labels change. They have **not** yet been updated for k=8.
- Conditions such as hypertension, hyperlipidemia and obesity are not in `codesets.yaml`, so the
  loadings check does not cover them. Adding them would pool their concepts into tags and change
  the whole matrix; that decision is open.
