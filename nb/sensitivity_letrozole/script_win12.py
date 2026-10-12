import matplotlib; matplotlib.use('Agg')

from IPython.display import display

import time as _t; _T0=_t.time()

print('### CELL 2  t=%.0fs' % (_t.time()-_T0), flush=True)
VARIANT       = 'win12'
WINDOW_MONTHS = 12
K_OVERRIDE    = None       # None = the k chosen by the stability sweep; set an int (e.g. 7) to force it
ANCHOR        = 'letrozole'
COHORT        = 'letrozole'
TAG           = f"{COHORT}_{VARIANT}"      # used in every cache / json / xlsx file name


print('### CELL 5  t=%.0fs' % (_t.time()-_T0), flush=True)
# One-time export from Snowflake into local CSV files. Safe to re-run: it
# checks OUT_DIR first and skips the (slow) Snowflake pull if the files are
# already there, so you won't accidentally re-download everything every time
# you restart the notebook.
import os
import ethos_omop as eo

OUT_DIR     = "../../inputs/letrozole_cohort/"      # extract_cohort() output, relative to this notebook's dir
COHORT_SQL  = "../../sql/letrozole_cohort.sql"     # relative to this notebook's cwd

# Runs once: if OUT_DIR is already populated, notebooks load from disk and never
# re-hit Snowflake. Delete OUT_DIR (or pick a different one) to force a re-pull.
if not os.path.isdir(OUT_DIR):
    eo.extract_cohort(COHORT_SQL, out_dir=OUT_DIR)
else:
    print(f"{OUT_DIR}/ already populated -- skipping extract_cohort(). "
          f"Delete it to re-pull from Snowflake.")


print('### CELL 7  t=%.0fs' % (_t.time()-_T0), flush=True)
# Load everything from disk into memory as one big table of "events":
# one row per visit / diagnosis / procedure / drug / lab result, for every
# patient in the cohort. `codesets` translates raw medical codes into the
# readable clinical labels (letrozole, breast_cancer, mastectomy, ...) used
# throughout the rest of the notebook.
import numpy as np, pandas as pd, matplotlib.pyplot as plt
pd.set_option('display.width', 150); pd.set_option('display.max_columns', 40)

DOMAINS = ['Visit', 'Condition', 'Drug', 'Procedure', 'Measurement']   # Visit stays in the load so we can show before vs after

concept  = eo.load_concept(OUT_DIR)
codesets = eo.build_codesets(concept, verbose=False)
raw      = eo.load_events(OUT_DIR, domains=DOMAINS)
person   = eo.load_person(OUT_DIR)
truth    = eo.load_truth(OUT_DIR)                   # None against real data


# v2: drop every visit event BEFORE tagging (care-driven bias). A visit row is any row whose
# domain OR vocabulary is "visit"; pharmacy / office / ED visits otherwise dominate the bundles.
is_visit = (raw['domain'].astype(str).str.lower().eq('visit')
            | raw['vocabulary_id'].astype(str).str.lower().eq('visit'))
visits   = raw[is_visit]
events   = eo.tag_events(raw[~is_visit].reset_index(drop=True), codesets, token_level="concept", multi_group=True)

# ---- before / after pruning
tbl = (pd.DataFrame({'before': raw['domain'].value_counts(), 'after': events['domain'].value_counts()})
         .fillna(0).astype(int))
tbl.loc['TOTAL'] = [len(raw), len(events)]
tbl['removed_%'] = ((1 - tbl['after'] / tbl['before']) * 100).round(1)
print("events per domain, BEFORE vs AFTER visit pruning")
print(tbl.to_string())
print(f"\npatients:               {raw.person_id.nunique():>10,} -> {events.person_id.nunique():,}")
print(f"distinct concepts:      {raw.concept_id.nunique():>10,} -> {events.concept_id.nunique():,}")
print(f"median events/patient:  {raw.groupby('person_id').size().median():>10,.0f} -> "
      f"{events.groupby('person_id').size().median():,.0f}")
print("\nremoved rows by vocabulary:")
print(visits['vocabulary_id'].value_counts().head(10).to_string())
print("\ntop removed visit concepts:")
print(visits['concept_name'].value_counts().head(10).to_string())

visit_ids = set(visits['concept_id'])
lost      = sorted(t for t, ids in codesets.items() if set(ids) & visit_ids)
print("\ncurated codeset tags that sit on visit concepts (their events are gone):", lost or "none")
vanished  = set(raw['person_id']) - set(events['person_id'])
if vanished:
    print(f"WARNING: {len(vanished):,} patients had only visit events and are no longer in `events`")
if not eo.group_mask(events, 'letrozole').any():
    print("WARNING: the cohort anchor `letrozole` has no events after pruning")
del raw, visits                                      # free memory; `events` is the pruned stream from here on

print(f"events {events.shape}   patients {events.person_id.nunique()}")
print(f"codeset coverage: {events.in_codeset.mean():.1%} of events carry a clinical tag")
print(f"truth labels: {'present (DEMO extract)' if truth is not None else 'ABSENT (real data)'}")
events.head(6)

print('### CELL 8  t=%.0fs' % (_t.time()-_T0), flush=True)
if WINDOW_MONTHS:
    _n0, _p0 = len(events), events.person_id.nunique()
    events = eo.window_around_anchor(events, ANCHOR, months=WINDOW_MONTHS)
    print(f"windowed to +/- {WINDOW_MONTHS} months around any {ANCHOR} event, merged per patient, exact duplicates dropped:")
    print(f"  events   {_n0:,} -> {len(events):,}")
    print(f"  patients {_p0:,} -> {events.person_id.nunique():,}")
    print(f"  median events per patient: {events.groupby('person_id').size().median():.0f}")
else:
    print(f"full variant: every event of each patient ({len(events):,} events, {events.person_id.nunique():,} patients)")


print('### CELL 9  t=%.0fs' % (_t.time()-_T0), flush=True)
# Sanity check: how big is what we just loaded? Useful to know before you
# wait on a slow cell later, and a quick way to notice if an extract came
# back suspiciously empty or huge.
print(eo.describe_extract(OUT_DIR).to_string(index=False))

print('### CELL 11  t=%.0fs' % (_t.time()-_T0), flush=True)
# How much history do we actually have per patient? (See point 4 above --
# this is the proxy lookback window, not a true observation period.) The
# 2-year line is a common minimum bar for "long enough history to trust an
# absence of a code."
win = eo.observation_window(events)
print(win.lookback_days.describe().round(0).to_string())

plt.figure(figsize=(7, 3))
plt.hist(win.lookback_days / 365.25, bins=40, color='#2C5F6F')
plt.axvline(2, ls='--', c='firebrick', label='2-year minimum')
plt.xlabel('observed history (years)'); plt.ylabel('patients')
plt.title('proxy lookback -- left truncation is real'); plt.legend()
plt.tight_layout(); plt.show()

SHORT = win.loc[win.lookback_days < 730, 'person_id']
print(f"\n{len(SHORT)} patients ({len(SHORT)/len(win):.1%}) have under 2 years of history.")
print("Exclude them from any analysis that depends on the ABSENCE of a code.")

print('### CELL 13  t=%.0fs' % (_t.time()-_T0), flush=True)
# Eyeball it: what did the "letrozole" pattern actually match? One row here
# means one specific product code -- exactly what you want to see before
# trusting anything downstream.
eo.resolve(concept, ['letrozole'], vocabularies=['RxNorm', 'RxNorm Extension'])

print('### CELL 14  t=%.0fs' % (_t.time()-_T0), flush=True)
# Medical coding systems are hierarchical: a drug "ingredient" (letrozole)
# can have several branded/dosed "products" under it, and a diagnosis can
# have several more specific children. `concept_ancestor` lets us walk that
# hierarchy in either direction.

# On real data, roll a drug ingredient DOWN to all its products via concept_ancestor.
lz = codesets['letrozole']
print("letrozole concepts, direct:      ", len(lz))
print("letrozole concepts, + descendants:", len(eo.expand_descendants(lz)))

# And roll an unspecified diagnosis UP to its parents -- e.g. `breast_cancer`,
# the comorbidity marker that distinguishes this cohort's oncology-indication
# subgroup (letrozole is the anchor here, not breast_cancer -- see Table 1).
bc = codesets['breast_cancer']
print("breast cancer parents, 1 level up:  ", len(eo.roll_up(bc, levels=1)))

print('### CELL 15  t=%.0fs' % (_t.time()-_T0), flush=True)
# `tag` collapses many concept_ids into one readable clinical label.
# Untagged events fall back to a slug of concept_name so sequences stay legible.
# What are the most common tags overall, and what fraction of all events
# actually got one of our curated labels versus falling back to a raw name?
print(events.tag.value_counts().head(15).to_string())
print(f"\ntagged into a codeset: {events.in_codeset.mean():.1%}")

print('### CELL 17  t=%.0fs' % (_t.time()-_T0), flush=True)
# The "bag of codes": one row per patient, one column per code, 1 if the
# patient ever had that code and 0 if not. This throws away *when* things
# happened and *how many times* -- it's the simplest representation there
# is, and the one we're about to show fails.
X = eo.bag_of_codes(events, min_count=20)
print(X.shape)
X.iloc[:5, :8]

print('### CELL 19  t=%.0fs' % (_t.time()-_T0), flush=True)
# How common is each code across the whole cohort? (Just column-wise
# averages of the 0/1 matrix above -- no modelling yet.)
prevalence = X.mean().sort_values(ascending=False)
print(f"{len(prevalence)} codes, prevalence range "
      f"{prevalence.min():.3%} - {prevalence.max():.3%}")
display(prevalence.head(20).to_frame('prevalence').style.format('{:.1%}'))

plt.figure(figsize=(7, 5))
prevalence.head(30).iloc[::-1].plot.barh(color='#2C5F6F')
plt.xlabel('fraction of cohort'); plt.title('Top 30 codes by direct prevalence')
plt.tight_layout(); plt.show()

print('### CELL 21  t=%.0fs' % (_t.time()-_T0), flush=True)
import math

MIN_TRAIN_PATIENTS = 5            # a code should appear in >= this many patients of a training split
n_pat   = events.person_id.nunique()
N_TRAIN = min(20_000, int(0.6 * n_pat))      # training-split size used by the k-sweep cells

# patients per code, and events per code (what bag_of_codes' min_count counts)
code, tags = pd.factorize(events['tag'])
key        = events['person_id'].to_numpy(np.int64) * len(tags) + code
prev_pat   = pd.Series(np.bincount(np.unique(key) % len(tags), minlength=len(tags)), index=tags)
ev_cnt     = pd.Series(np.bincount(code, minlength=len(tags)), index=tags)
all_pairs  = int(prev_pat.sum())             # distinct (patient, code) pairs = ones in the full 0/1 matrix

def summarize(mask):
    return {'columns': int(mask.sum()),
            'pairs_kept_%': round(100 * prev_pat[mask].sum() / all_pairs, 2)}

rows = [{'rule': f'>= {p} patients', 'prevalence_%': round(100 * p / n_pat, 4), **summarize(prev_pat >= p)}
        for p in [1, 2, 5, 10, 20, 35, 50, 100, 200, 500]]
rows.append({'rule': 'current min_count=20 (events)', 'prevalence_%': np.nan, **summarize(ev_cnt >= 20)})
rule_tbl = pd.DataFrame(rows).set_index('rule')

MIN_PATIENTS = math.ceil(MIN_TRAIN_PATIENTS * n_pat / N_TRAIN)
KEEP_TAGS    = prev_pat.index[prev_pat >= MIN_PATIENTS]
display(rule_tbl)

# the clinical (codeset) tags are the ones the analysis is about -- do any fall below the floor?
codeset_tags = [t for t in codesets if t in prev_pat.index]
lost = prev_pat[codeset_tags][lambda s: s < MIN_PATIENTS]
print(f"cohort {n_pat} patients, training split {N_TRAIN}")
print(f"suggested floor: {MIN_PATIENTS} patients ({100 * MIN_PATIENTS / n_pat:.3f}% prevalence) -> "
      f"{len(KEEP_TAGS)} of {len(prev_pat)} columns, "
      f"{100 * prev_pat[KEEP_TAGS].sum() / all_pairs:.1f}% of patient-code pairs kept")
print("codeset tags below the floor:", lost.to_dict() if len(lost) else "none")

fig, ax = plt.subplots(figsize=(7, 3.2))
ps = np.unique(np.round(np.geomspace(1, max(2, prev_pat.max() / 5), 40)).astype(int))
ax.plot(ps, [(prev_pat >= p).sum() for p in ps], color='C0')
ax.set_xscale('log'); ax.set_xlabel('minimum patients per code'); ax.set_ylabel('columns kept', color='C0')
ax2 = ax.twinx()
ax2.plot(ps, [100 * prev_pat[prev_pat >= p].sum() / all_pairs for p in ps], color='C1')
ax2.set_ylabel('% of patient-code pairs kept', color='C1')
ax.axvline(MIN_PATIENTS, ls='--', c='grey')
ax.set_title('what each prevalence floor costs')
plt.tight_layout(); plt.show()

print("\nTo apply it, build X from the kept codes only (min_count=1 on pre-filtered events):")
print("    X = eo.bag_of_codes(events[events.tag.isin(KEEP_TAGS)], min_count=1)")

print('### CELL 22  t=%.0fs' % (_t.time()-_T0), flush=True)
X = eo.bag_of_codes(events[events.tag.isin(KEEP_TAGS)], min_count=1)
print(X.shape)

print('### CELL 23  t=%.0fs' % (_t.time()-_T0), flush=True)
# The punchline of the whole notebook: find one letrozole+breast_cancer
# patient labelled "fertility" and one labelled "oncology" by the rule-based
# check below, then show that the bag-of-codes view (X) can't tell them
# apart at all, even though their real timelines obviously can.
weak = eo.weak_labels(events)                      # rule-based probe labels
lab  = weak.set_index('person_id').weak_label

_eg = events[events.groups.notna()]
Xg = eo.bag_of_codes(_eg.assign(group=_eg.groups.astype(str).str.split('|')).explode('group').reset_index(drop=True), col='group', min_count=1)   # group-level checklist (a concept counts in EVERY group it is in), demo only
both = [p for p in X.index
        if Xg.loc[p].get('letrozole', 0) == 1
        and Xg.loc[p].get('breast_cancer', 0) == 1
        and p in lab.index]

a = next((p for p in both if lab[p] == 'fertility'), None)
b = next((p for p in both if lab[p] == 'oncology'),  None)
assert a and b, ("No identical-bag pair found in this sample. Increase the extract "
                 "size, or inspect `both` to see which side is missing.")

# Same view, plus a few randomly-picked columns where they DO differ -- shown
# side by side so it's clear these two patients aren't identical everywhere,
# just on the two columns that matter for the fertility-vs-oncology question.
diff_cols_all = X.columns[X.loc[a] != X.loc[b]]
diff_cols = list(pd.Index(diff_cols_all).to_series()
                  .sample(n=min(3, len(diff_cols_all)), random_state=0))
print("bag-of-codes view -- identical on letrozole/breast_cancer, "
      f"differs on {diff_cols}:")
display(pd.concat([Xg, X], axis=1).loc[[a, b], ['letrozole', 'breast_cancer'] + diff_cols])

print("\nactual timelines -- obviously different:")
# FOCUS = eo.FERTILITY_TAGS / eo.ONCOLOGY_TAGS -- the same constants
# weak_labels() used to build `lab` -- plus the exposure/anchor tags, so this
# timeline shows the full evidence base behind the label instead of a
# hand-picked subset that can drift from it. Tags that never occurred for a
# given patient simply produce no row below, so this costs nothing visually.
FOCUS = ['letrozole', 'breast_cancer'] + eo.FERTILITY_TAGS + eo.ONCOLOGY_TAGS
for pid in (a, b):
    s = events[(events.person_id == pid) & eo.group_mask(events, FOCUS)]
    print(f"\n  person_id {pid}  ({lab[pid]})")
    print(s[['event_date', 'groups', 'tag']].drop_duplicates('tag').to_string(index=False))

print('### CELL 25  t=%.0fs' % (_t.time()-_T0), flush=True)
from sklearn.metrics import pairwise_distances
import scipy.sparse as sp

# letrozole is the cohort anchor here -- 100% prevalence (confirmed below), so
# it's a constant column that carries no discriminative signal and would just
# eat a component. Drop it before any distance/SVD/NMF fit; X itself (with
# the column) stays untouched for the two-patient demo above.
# Everything downstream works on a SPARSE copy (Xs): same values as the dense matrix without the
# anchor column, a fraction of the memory, and faster NMF / SVD.
nmf_cols = X.columns[~X.columns.isin(events.loc[eo.group_mask(events, 'letrozole'), 'tag'])]                   # code names for the components
n_pat    = X.shape[0]
Xs = sp.csr_matrix(X.to_numpy())[:, X.columns.get_indexer(nmf_cols)].astype(float).tocsr()
print(f"Xs {Xs.shape}, density {Xs.nnz / (Xs.shape[0] * Xs.shape[1]):.3%}")

def dist_to_all(row, M, metric, chunk=10_000):
    """Distances from one row to every row of sparse M, densifying only `chunk` rows at a time."""
    return np.concatenate([pairwise_distances(row, M[i:i + chunk].toarray(), metric=metric)[0]
                           for i in range(0, M.shape[0], chunk)])

# First: pick 400 random patients and measure how "far apart" every pair is,
# under two different definitions of distance. If cosine and jaccard disagree
# on how spread out the cohort is, that's a sign the metric matters, not just
# the data.
sub = Xs[:400].toarray()
for m in [#'euclidean', 
          'cosine', 'jaccard']:
    D  = pairwise_distances(sub, metric=m)
    iu = np.triu_indices(len(sub), 1)
    print(f"{m:10s} mean={D[iu].mean():.3f}  sd={D[iu].std():.3f}")

# Second: for one specific patient (`a`, our fertility case from the demo
# above), who are their 5 nearest neighbours under each metric, and what
# weak label do those neighbours carry? Also report the direct a<->b
# distance, since b (the oncology case) is exactly the contrast we want.
posa = list(X.index).index(a)
posb = list(X.index).index(b)
print()
for m in [#'euclidean', 
          'cosine', 'jaccard']:
    D  = dist_to_all(Xs[posa:posa+1].toarray(), Xs, m)
    nn = [X.index[i] for i in np.argsort(D)[1:6]]
    print(f"{m:10s} neighbours of {a}: {[lab.get(p, '?') for p in nn]}")
    print(f"{m:10s} distance({a}, {b}) = {D[posb]:.3f}")

print('### CELL 27  t=%.0fs' % (_t.time()-_T0), flush=True)
# Not our data -- pure demonstration. Make random sparse 0/1 tables (2% of
# cells "on", like real code data) of increasing width, and watch the ratio
# of the closest pair's distance to the farthest pair's distance collapse
# toward 1 as width grows. That's the curse of dimensionality happening in
# front of you, independent of anything about breast cancer or letrozole.
rng = np.random.default_rng(0)
print(f"{'dims':>6} {'min/max distance ratio':>24}")
for d in [10, 50, 200, 1000, 5000]:
    Zr = (rng.random((200, d)) < 0.02).astype(float)     # sparse, like code data
    D  = pairwise_distances(Zr)
    iu = np.triu_indices(200, 1)
    print(f"{d:>6} {D[iu].min() / D[iu].max():>24.3f}")
print("\nRatio -> 1 means every patient is equally far from every other.")

print('### CELL 29  t=%.0fs' % (_t.time()-_T0), flush=True)
from sklearn.decomposition import TruncatedSVD, NMF
from sklearn.preprocessing import normalize

# SVD finds the directions that explain the most variation in the data --
# similar in spirit to PCA. Its components can be positive or negative and
# don't have a clean "these codes belong to this theme" reading, but they're
# a solid general-purpose compression. Normalize first so this lines up with
# the cosine geometry we already decided was the right one for this data.
Xn  = normalize(Xs)                                  # cosine geometry, done properly
svd = TruncatedSVD(n_components=min(200, Xs.shape[1] - 1), random_state=0).fit(Xn)
Z   = svd.transform(Xn)

# How many components until we've captured most of the signal? The scree
# plot below answers that -- steep rise then flattening out means most of
# what matters is in the first handful of components.
plt.figure(figsize=(7, 3))
plt.plot(np.cumsum(svd.explained_variance_ratio_), marker='o', ms=3)
plt.axhline(0.8, ls='--', c='grey')
plt.xlabel('components'); plt.ylabel('cumulative variance')
plt.title('SVD scree -- where to truncate'); plt.tight_layout(); plt.show()

print('### CELL 31  t=%.0fs' % (_t.time()-_T0), flush=True)
import time
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import adjusted_rand_score

# one place for the NMF fit settings, used by every NMF fit in this section
NMF_KW = dict(init='nndsvd', random_state=0, max_iter=2000, tol=1e-4)

N_BOOT        = 10        # refits; each is a full NMF fit, raise once you know the runtime
N_BOOT_SAMPLE = 20_000    # patients per resample (capped at the cohort size)
N_EVAL        = 20_000    # fixed patients used to compare argmax labels (capped)

def _unit(M):
    return M / np.linalg.norm(M, axis=1, keepdims=True)

def nmf_stability(nmf_base, Xv, n_boot=N_BOOT, n_sample=N_BOOT_SAMPLE,
                  n_eval=N_EVAL, seed=0):
    """Bootstrap-refit NMF; return per-component matched cosine and per-boot ARI.

    Component order is arbitrary between fits (label switching), so each refit's
    components are matched to the base fit's by cosine similarity (Hungarian
    algorithm). ARI compares argmax patient partitions, which needs no matching.
    """
    k    = nmf_base.n_components_
    Hb   = _unit(nmf_base.components_)
    rng  = np.random.default_rng(seed)
    ev   = rng.choice(Xv.shape[0], min(n_eval, Xv.shape[0]), replace=False)
    lab0 = nmf_base.transform(Xv[ev]).argmax(1)
    cos, ari = [], []
    for b in range(n_boot):
        t0  = time.perf_counter()
        idx = rng.choice(Xv.shape[0], min(n_sample, Xv.shape[0]), replace=True)
        m   = NMF(n_components=k, **NMF_KW).fit(Xv[idx])
        S        = Hb @ _unit(m.components_).T         # base x refit cosine
        rows, cols = linear_sum_assignment(-S)          # rows come back sorted 0..k-1
        cos.append(S[rows, cols])                       # cos[b][j] = base component j
        ari.append(adjusted_rand_score(lab0, m.transform(Xv[ev]).argmax(1)))
        print(f"  boot {b + 1}/{n_boot}  {time.perf_counter() - t0:.0f}s  "
              f"ARI {ari[-1]:.3f}")
    return np.array(cos), np.array(ari)


print('### CELL 32  t=%.0fs' % (_t.time()-_T0), flush=True)
import time
import io, contextlib
import os, math
import scipy.sparse as sp
from joblib import Parallel, delayed
from sklearn.metrics import silhouette_score
from scipy import stats

K_GRID      = list(range(3, 25))
SPLIT_SEEDS = (1, 2, 3, 4, 5)   # independent train / held-out splits of the cohort
N_SWEEP     = min(20_000, int(0.6 * Xs.shape[0]))   # train patients every k is fit on (scales with the cohort)
N_HELD      = min(10_000, Xs.shape[0] - N_SWEEP)    # disjoint held-out patients for error / silhouette
N_BOOT_K    = 10          # bootstrap refits per k and split (reuses nmf_stability above)
NC_SIL      = min(24, Z.shape[1])   # SVD dims Day 2 scored KMeans silhouette in
MIN_SPLITS_OK = math.ceil(1.0 * len(SPLIT_SEEDS))   # a k must pass on this many splits (4 of 5)
N_JOBS      = max(1, (os.cpu_count() or 2) - 2)   # sklearn's NMF is single-threaded: one fit per core

def rel_err(X, W, H):
    """||X - W H||_F / ||X||_F without building the dense W @ H (X may be sparse)."""
    x2    = X.multiply(X).sum() if sp.issparse(X) else (X ** 2).sum()
    cross = np.sum((X @ H.T) * W)
    quad  = np.sum((W.T @ W) * (H @ H.T))
    return float(np.sqrt(max(x2 - 2 * cross + quad, 0.0) / x2))

def sweep_job(split_seed, k, Xtr, Xho, Zho, n_boot):
    """All metrics for one (split, k): one base fit plus n_boot bootstrap refits."""
    t0 = time.perf_counter()
    m  = NMF(n_components=k, **NMF_KW).fit(Xtr)
    Wh = m.transform(Xho)
    lab_ho = Wh.argmax(1)
    with contextlib.redirect_stdout(io.StringIO()):          # silence per-boot prints
        cos, ari = nmf_stability(m, Xtr, n_boot=n_boot, n_sample=Xtr.shape[0],
                                 n_eval=Xtr.shape[0], seed=k)
    share = np.bincount(lab_ho, minlength=k) / len(lab_ho)
    return {'split': split_seed, 'k': k,
            'held_out_err': rel_err(Xho, Wh, m.components_),
            'silhouette': silhouette_score(Zho, lab_ho) if len(set(lab_ho)) > 1 else np.nan,
            'ari_mean': ari.mean(), 'ari_sd': ari.std(ddof=1),
            'ari_se': ari.std(ddof=1) / np.sqrt(n_boot),
            'cos_mean': cos.mean(), 'n_unstable': int((cos.mean(0) < .75).sum()),
            'n_used': int((share >= .01).sum()), 'secs': time.perf_counter() - t0}

def make_split(split_seed):                                   # sliced once here, so workers get small inputs
    perm   = np.random.default_rng(split_seed).permutation(Xs.shape[0])
    tr, ho = perm[:N_SWEEP], perm[N_SWEEP:N_SWEEP + N_HELD]
    return Xs[tr], Xs[ho], Z[ho, :NC_SIL]                     # Z rows align with Xs rows

splits  = {s: make_split(s) for s in SPLIT_SEEDS}
jobs    = [(s, k) for k in sorted(K_GRID, reverse=True) for s in SPLIT_SEEDS]   # slow (large k) first
results = Parallel(n_jobs=N_JOBS, verbose=5)(
              delayed(sweep_job)(s, k, *splits[s], N_BOOT_K) for s, k in jobs)
res       = pd.DataFrame(results)
per_split = {s: res[res.split == s].drop(columns=['split', 'secs']).set_index('k').sort_index()
             for s in SPLIT_SEEDS}
print(f"{len(jobs)} jobs on {N_JOBS} workers; summed fit time {res.secs.sum() / 60:.1f} CPU-min")

# one row per k, summarised over splits
g     = pd.concat(per_split, names=['split']).groupby('k')
sweep = pd.DataFrame({'held_out_err': g.held_out_err.mean(), 'silhouette': g.silhouette.mean(),
                      'ari_mean': g.ari_mean.mean(), 'ari_sd_splits': g.ari_mean.std(),
                      'n_splits_solid': g.ari_mean.apply(lambda a: int((a >= .75).sum())),
                      'n_splits_sugg':  g.ari_mean.apply(lambda a: int((a >= .60).sum())),
                      'cos_mean': g.cos_mean.mean(), 'n_unstable': g.n_unstable.median(),
                      'n_used': g.n_used.min()})
display(sweep.round(3))

t_crit = stats.t.ppf(0.975, N_BOOT_K - 1)    # few refits -> t interval, not 1.96
fig, ax = plt.subplots(1, 3, figsize=(13, 3.2))
ax[0].plot(sweep.index, sweep.held_out_err, marker='o')
ax[0].set_title('held-out relative error (look for the elbow)')
ax[1].plot(sweep.index, sweep.silhouette, marker='o', color='C1')
ax[1].set_title('silhouette of argmax groups (SVD space)')
for i, s in enumerate(SPLIT_SEEDS):                          # small x-offset so splits do not overlap
    d = per_split[s]
    ax[2].errorbar(d.index + (i - (len(SPLIT_SEEDS) - 1) / 2) * 0.1, d.ari_mean,
                   yerr=t_crit * d.ari_se, fmt='o', ms=3, capsize=2, alpha=.6, label=f'split {s}')
ax[2].plot(sweep.index, sweep.ari_mean, 'k-', lw=2, label='mean of splits')
ax[2].axhline(0.75, ls='--', c='green');  ax[2].axhline(0.60, ls='--', c='orange')
ax[2].set_title('bootstrap ARI per split (95% CI)'); ax[2].legend(fontsize=7, ncol=2)
for a in ax: a.set_xlabel('k'); a.set_xticks(sweep.index)
plt.tight_layout(); plt.show()

ok     = sweep[(sweep.n_splits_sugg >= MIN_SPLITS_OK) & (sweep.cos_mean >= .75)]
strong = sweep[(sweep.n_splits_solid >= MIN_SPLITS_OK) & (sweep.n_unstable == 0)]
print(f"largest k with ARI >= 0.60 on {MIN_SPLITS_OK}+ of {len(SPLIT_SEEDS)} splits and mean cos >= 0.75:",
      int(ok.index.max()) if len(ok) else "none")
print(f"largest k with ARI >= 0.75 on {MIN_SPLITS_OK}+ of {len(SPLIT_SEEDS)} splits and no unstable component (median):",
      int(strong.index.max()) if len(strong) else "none")

print('### CELL 36  t=%.0fs' % (_t.time()-_T0), flush=True)
int(strong.index.max()) 

print('### CELL 37  t=%.0fs' % (_t.time()-_T0), flush=True)
# NMF factorises into non-negative PARTS, so each component reads as a set of
# co-occurring codes. Unlike SVD components you can name them.
#
# In plain terms: NMF is only allowed to add codes together, never subtract
# them, so each component ends up looking like "a bundle of codes that tend
# to show up together" -- e.g. "chemotherapy + antineoplastic drug" reads
# as an actual clinical bundle, not an abstract direction in space. That's
# why we print the top-5 codes per component below: it's how you check
# whether a component actually means something clinically, or is noise.
#
# We fit twice, at k=5 and k=12, to see how the story changes with more
# components allowed (see the annotated discussion two cells down). Each
# component is also sized -- by dominant-component count and % of the
# cohort -- and each top code is shown with its % share of that component's
# total loading, so you can see at a glance both which bundles are large
# populations and which codes actually drive each one.
# for k in [3, 5, 8, 12]:
for k in [K_OVERRIDE or int(strong.index.max())]:
    nmf = NMF(n_components=k, **NMF_KW).fit(Xs)
    H   = pd.DataFrame(nmf.components_, columns=nmf_cols)
    lab_k = nmf.transform(Xs).argmax(axis=1)
    dom = pd.Series(lab_k).value_counts().sort_index()
    # save the fit for reuse (Day 3 loads it instead of refitting); the tag keeps cohorts apart
    np.savez(f"nmf_k{k}_{TAG}.npz", H=H.to_numpy(), cols=np.array(H.columns, dtype=str),
             pids=X.index.to_numpy(), labels=lab_k)
    print (f"\nNMF with {k} components:")
    for c in range(k):
        n    = int(dom.get(c, 0))
        row  = H.iloc[c]
        top  = row.sort_values(ascending=False).head(10)
        share = (top / row.sum() * 100).round(1)
        codes = [f"{name} ({pct}%)" for name, pct in share.items()]
        print(f"component {c} (n={n}, {n / n_pat * 100:.1f}%): {codes}")

print('### CELL 40  t=%.0fs' % (_t.time()-_T0), flush=True)
K_CHECK = nmf.n_components_      # the last fit above
H8 = pd.DataFrame(nmf.components_, columns=nmf_cols)
# v3: columns of H8 are concept tokens; a codeset's loading is the SUM over the tokens it groups (a token counts in EVERY codeset it is in)
H8g = eo.group_loadings(H8, events)

# watch list comes from codesets.yaml (via eo), not hand-typed; the cohort anchor is excluded
WATCH = {
    'fertility':      eo.FERTILITY_TAGS,
    'oncology':       eo.ONCOLOGY_TAGS,
    'other codesets': [t for t in eo.CODESETS
                       if t not in eo.FERTILITY_TAGS + eo.ONCOLOGY_TAGS and t != 'letrozole'],
}

rows, missing = [], []
for group, tags in WATCH.items():
    for tag in tags:
        if tag not in H8g.columns or H8g[tag].sum() == 0:
            missing.append(tag); continue
        share = H8g[tag] / H8g[tag].sum() * 100                       # this code's split across components
        own   = int(share.values.argmax())
        rows.append({'group': group, 'code': tag, **{f'c{i}': share.iloc[i] for i in range(K_CHECK)},
                     'owner': own, 'rank_in_owner': int((H8.iloc[own] > H8.iloc[own][H8.columns.intersection(list(eo.group_tokens(events, tag)))].max()).sum() + 1)})

loadings = pd.DataFrame(rows).set_index(['group', 'code'])
comp_cols = [f'c{i}' for i in range(K_CHECK)]
display(loadings.style.format({c: '{:.0f}' for c in comp_cols}).background_gradient(
        axis=1, cmap='Blues', subset=comp_cols))
print("components (n, top code):",
      {i: (int((nmf.transform(Xs).argmax(1) == i).sum()), H8.iloc[i].idxmax()[:28]) for i in range(K_CHECK)})
print("codeset tags with no column (dropped by the prevalence floor, or never occur):", missing or "none")

print('### CELL 41  t=%.0fs' % (_t.time()-_T0), flush=True)
print(f"base fit: NMF k={nmf.n_components_}  (the `nmf` from the cell above)")
cos, ari = nmf_stability(nmf, Xs)

dom_n = pd.Series(nmf.transform(Xs).argmax(1)).value_counts().reindex(range(nmf.n_components_), fill_value=0)
top3  = [', '.join(pd.Series(nmf.components_[c], index=nmf_cols)
                   .nlargest(3).index) for c in range(nmf.n_components_)]
stab = pd.DataFrame({'n': dom_n.values, 'top_codes': top3,
                     'cos_mean': cos.mean(0).round(3), 'cos_sd': cos.std(0).round(3),
                     'cos_min': cos.min(0).round(3)})
stab['verdict'] = np.select([stab.cos_mean >= .90, stab.cos_mean >= .75],
                            ['solid', 'suggestive'], 'unstable')
display(stab)
print(f"\nbootstrap ARI of argmax labels: mean {ari.mean():.3f}  sd {ari.std():.3f}  "
      f"(Day 2 cut-offs: >=0.75 solid, >=0.60 suggestive)")

plt.figure(figsize=(7, 3))
plt.errorbar(stab.index, stab.cos_mean, yerr=stab.cos_sd, fmt='o', capsize=4)
plt.axhline(0.90, ls='--', c='green',  label='solid')
plt.axhline(0.75, ls='--', c='orange', label='suggestive')
plt.xlabel('NMF component'); plt.ylabel('matched cosine vs base')
plt.xticks(stab.index); plt.legend(fontsize=8)
plt.title('NMF component stability under bootstrap refit')
plt.tight_layout(); plt.show()

print('### CELL 43  t=%.0fs' % (_t.time()-_T0), flush=True)
COHORT = 'letrozole'
# Export the NMF components as a table to review with the underwriters: one row per bundle, the last two columns are left empty to fill in.
import re
try:
    import openpyxl
except ImportError as e:
    raise ImportError("pip install openpyxl in this kernel's environment, then rerun this cell") from e
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RANK_BY = 'loading'        # 'loading' = codes that define the bundle (NMF loading); 'prevalence' = codes most patients of the bundle have
TOP_N   = 5
k_exp   = nmf.n_components_
XLSX_NMF = f"nmf_components_{COHORT}_k{k_exp}_{VARIANT}.xlsx"

lab_e  = nmf.transform(Xs).argmax(1)                                   # dominant component per patient (same rule as the sizes above)
Hc     = pd.DataFrame(nmf.components_, columns=nmf_cols)
meta   = events.drop_duplicates('tag').set_index('tag')

def entity(tok, prev):
    r = meta.loc[tok]
    name = re.split(r' \(|;| This ', str(r.concept_name))[0].strip()
    name = name if len(name) >= 8 else str(r.concept_name)          # packs like '{6 (azithromycin ...) } Pack [Z-PAK]' would be cut to '{6'
    name = name if len(name) <= 60 else name[:60].rsplit(' ', 1)[0] + '…'
    return f"{name} [{r.vocabulary_id} {r.concept_code}] (concept_id {int(r.concept_id)}; {prev:.0%} of bundle)"

rows_e = []
for c in range(k_exp):
    members = np.flatnonzero(lab_e == c)
    prev  = pd.Series(np.asarray(Xs[members].mean(axis=0)).ravel(), index=nmf_cols)     # share of the bundle's patients with each code
    score = Hc.iloc[c] if RANK_BY == 'loading' else prev
    top   = score.nlargest(TOP_N).index
    rows_e.append({'Group': f"c{c}",
                   'n (%)': f"{len(members):,} ({len(members) / len(lab_e):.1%})",
                   'Most frequently OMOP clinical entities found': "\n".join(f"{i}. {entity(t, prev[t])}" for i, t in enumerate(top, 1)),
                   'Suggested Clinical Pathway': '',
                   'UW suggestion': ''})
nmf_table = pd.DataFrame(rows_e)

F = lambda **kw: Font(name='Arial', size=10, **kw)
thin = Side(style='thin', color='D0D5DB')
wb = openpyxl.Workbook(); ws = wb.active; ws.title = f'NMF k={k_exp}'
ws.append(list(nmf_table.columns))
for j in range(1, ws.max_column + 1):
    h = ws.cell(1, j); h.font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
    h.fill = PatternFill('solid', fgColor='334E68'); h.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
ws.row_dimensions[1].height = 30
for row in nmf_table.itertuples(index=False):
    ws.append(list(row))
for i in range(2, len(nmf_table) + 2):
    ws.row_dimensions[i].height = 15 * TOP_N + 6
    for j in range(1, ws.max_column + 1):
        c_ = ws.cell(i, j); c_.font = F(bold=(j == 1)); c_.border = Border(bottom=thin)
        c_.alignment = Alignment(wrap_text=True, vertical='top', horizontal='center' if j in (1, 2) else 'left')
for j, w in enumerate([14, 16, 95, 40, 40], 1):
    ws.column_dimensions[get_column_letter(j)].width = w
ws.freeze_panes = 'B2'
ws.cell(len(nmf_table) + 3, 1, f"Source: Day 1 v3 {COHORT}, NMF k={k_exp} on concept-level tokens ({len(lab_e):,} patients). n (%) = patients whose dominant component is the bundle. "
        f"Entities ranked by {'NMF loading in the bundle' if RANK_BY == 'loading' else 'share of the bundle patients having the code'}; "
        "the percentage is the share of the bundle's patients with that code. The last two columns are left empty on purpose.").font = F(italic=True)
wb.save(XLSX_NMF)
print(f"wrote {os.path.abspath(XLSX_NMF)} ({k_exp} bundles)")
nmf_table


print('### CELL 44  t=%.0fs' % (_t.time()-_T0), flush=True)
COHORT = 'letrozole'
# Persist the NMF components next to the .npz: n, top tokens with concept ids, a signature, and the names you give them.
# Part B of this notebook loads this file (COMP_JSON) for the component names. Workflow: run once -> copy the printed DESCR block
# (or paste names from Claude) into DESCR below -> run again. Components not listed in DESCR keep the names already saved
# in the file, as long as their top-5 tokens are unchanged.
import json, hashlib, os
FERT, ONCO, BG = 'fertility', 'oncology', 'background'
MANUAL, EXPLAINED, UNCLEAR = ('manual UW review (stage, treatment status, adjuvant letrozole)',
                              'routine (letrozole explained by fertility)',
                              'routine, indication unclear (use other evidence)')
DESCR = {}      # windowed run: names are not carried over from the full run; fill this after reading the printed top tokens

k_j       = nmf.n_components_
NPZ_J     = f"nmf_k{k_j}_{TAG}.npz"
JSON_PATH = f"nmf_k{k_j}_{TAG}_components.json"
TOP_J     = 10

Hj     = pd.DataFrame(nmf.components_, columns=nmf_cols)
lab_j  = nmf.transform(Xs).argmax(1)
meta_j = events.drop_duplicates('tag').set_index('tag')
old    = json.load(open(JSON_PATH))['components'] if os.path.exists(JSON_PATH) else {}

comps = {}
for c in range(k_j):
    row = Hj.iloc[c]
    sig = list(row.nlargest(5).index)
    toks = []
    for t, v in row.nlargest(TOP_J).items():
        m = meta_j.loc[t]
        toks.append(dict(token=t, concept_id=int(m.concept_id) if pd.notna(m.concept_id) else None,
                         concept_name=str(m.concept_name), vocabulary_id=str(m.vocabulary_id), concept_code=str(m.concept_code),
                         loading=round(float(v), 6), share_pct=round(float(v / row.sum() * 100), 1)))
    n    = int((lab_j == c).sum())
    keep = old.get(str(c), {})
    keep = keep if set(keep.get('signature', [])) == set(sig) else {}            # saved names only survive if the component is unchanged
    d    = DESCR.get(c, {})
    comps[str(c)] = dict(n=n, pct=round(n / len(lab_j) * 100, 2), signature=sig,
                         name=d.get('name', keep.get('name')), group=d.get('group', keep.get('group')),
                         status=d.get('status', keep.get('status')), top_tokens=toks)

out = dict(cohort=COHORT, k=int(k_j), npz=NPZ_J,
           npz_sha256=hashlib.sha256(open(NPZ_J, 'rb').read()).hexdigest() if os.path.exists(NPZ_J) else None,
           n_patients=int(len(lab_j)), components=comps)
with open(JSON_PATH, 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"saved {JSON_PATH}  (k={k_j}, {len(lab_j):,} patients)\n")

print(f"{'comp':>4} {'n':>6} {'%':>5}  name  |  top tokens")
for c, d in comps.items():
    print(f"{c:>4} {d['n']:>6} {d['pct']:5.1f}  {d['name'] or '(unnamed)'}  |  " + ', '.join(t['token'].split('__')[0] for t in d['top_tokens'][:4]))
print("\n# paste-ready DESCR (edit name / group / status, then re-run this cell):")
print("DESCR = {")
for c, d in comps.items():
    extra = f", status={d['status']!r}" if d['status'] else ''
    print(f"    {c}: dict(name={d['name']!r}, group={d['group']!r}{extra}),")
print("}")


print('### CELL 47  t=%.0fs' % (_t.time()-_T0), flush=True)
cond = pd.read_csv(os.path.join(OUT_DIR, 'master_condition_occurrence.csv'),
                   usecols=['person_id', 'condition_concept_id', 'condition_source_value', 'condition_start_date'],
                   dtype={'condition_source_value': str}, parse_dates=['condition_start_date'])
src  = cond.condition_source_value.fillna('').str.upper().str.replace('.', '', regex=False)   # 'C50.911' -> 'C50911'
crit = {'ICD-9 174.x':     src.str.startswith('174'),
        'ICD-10 C50.x':    src.str.startswith('C50'),
        'SNOMED 4162253':  cond.condition_concept_id.eq(4162253)}

cohort_ids = set(events.person_id)
case_mask  = np.logical_or.reduce(list(crit.values()))
case_ids   = set(cond.person_id[case_mask]) & cohort_ids
groups = {'Overall': cohort_ids,
          'No breast cancer dx': cohort_ids - case_ids,
          'Confirmed breast cancer dx': case_ids}

lz        = eo.index_dates(events, 'letrozole').set_index('person_id')['index_date']
age_yrs   = (lz - person.set_index('person_id')['birth_date'].reindex(lz.index)).dt.days / 365.25
female    = set(person.loc[person.gender.astype(str).str.upper().eq('FEMALE'), 'person_id'])
first_dx  = cond[case_mask].groupby('person_id').condition_start_date.min()       # first confirmed dx per patient
crit_ids  = {k: set(cond.person_id[m]) & cohort_ids for k, m in crit.items()}

# diagnosis-related rows: curated codesets whose events are conditions
ev_c      = events[events.group.notna()]
tag_dom   = ev_c.assign(g=ev_c.groups.astype(str).str.split('|')).explode('g').groupby('g').domain.agg(lambda s: s.mode().iat[0])
DX_TAGS   = sorted(tag_dom.index[tag_dom == 'Condition'])
has       = {t: set(ev_c.loc[eo.group_mask(ev_c, t), 'person_id']) for t in DX_TAGS}

def describe(name, ids):
    n   = len(ids)
    npc = lambda k: f"{k} ({k / n:.1%})" if n else "0"
    a   = age_yrs.reindex(list(ids))
    row = {'N (% of cohort)': f"{n} ({n / len(cohort_ids):.1%})",
           'Age at first letrozole, mean (SD)': f"{a.mean():.1f} ({a.std():.1f})" if n else '-',
           'Female, n (%)': npc(len(ids & female))}
    for k, s in crit_ids.items():
        row[f'Meets {k}, n (%)'] = npc(len(ids & s))
    before = [first_dx.get(p) is not None and first_dx[p] < lz[p] for p in ids]
    row['Dx recorded before first letrozole, n (%)'] = npc(sum(before)) if name == 'Confirmed breast cancer dx' else '-'
    for t in DX_TAGS:
        row[f'{t}, n (%)'] = npc(len(ids & has[t]))
    return row

table1 = pd.DataFrame({name: describe(name, ids) for name, ids in groups.items()})
display(table1)
print("curated diagnosis codesets shown:", DX_TAGS)

print('### CELL 48  t=%.0fs' % (_t.time()-_T0), flush=True)
seqs = eo.sequences(events, col='tag', dedup_same_day=True, collapse_repeats=True)
pids = sorted(seqs)
db   = [seqs[p] for p in pids]

print("example timeline:")
print(' -> '.join(db[1][:12]))
print("\nmedian sequence length:", int(np.median([len(s) for s in db])))

print('### CELL 50  t=%.0fs' % (_t.time()-_T0), flush=True)
import collections

def prefixspan(db, min_sup, max_len=4):
    """Minimal PrefixSpan over single-item sequences.

    db      : list of lists of tokens
    min_sup : minimum number of sequences containing the pattern
    returns : DataFrame of (pattern, support, support_pct)
    """
    n, results = len(db), []

    def scan(projected, prefix):
        counts = collections.Counter()
        for seq in projected:
            for item in sorted(set(seq)):                   # count each sequence once
                counts[item] += 1
        for item, c in counts.items():
            if c < min_sup:
                continue
            new_prefix = prefix + [item]
            results.append((tuple(new_prefix), c))
            if len(new_prefix) >= max_len:
                continue
            # project: keep the suffix after the FIRST occurrence of item
            nxt = [seq[seq.index(item) + 1:] for seq in projected if item in seq]
            if nxt:
                scan(nxt, new_prefix)

    scan([list(s) for s in db], [])
    return (pd.DataFrame(results, columns=['pattern', 'support'])
              .assign(support_pct=lambda d: (d.support / n * 100).round(1)))

print('### CELL 52  t=%.0fs' % (_t.time()-_T0), flush=True)
# Part B starts from the NMF fitted in Part A (same events, same prevalence floor, same anchor drop): no refit, no cache file.
K    = nmf.n_components_
H    = pd.DataFrame(nmf.components_, columns=nmf_cols)
lab  = pd.Series(nmf.transform(Xs).argmax(1), index=X.index)
comp = lab.reindex(pids).fillna(-1).astype(int).to_numpy()   # aligned with db / pids

# DRAFT triage labels -- need underwriter review.
FERT, ONCO, BG = 'fertility', 'oncology', 'background'
MANUAL, EXPLAINED, UNCLEAR = ('manual UW review (stage, treatment status, adjuvant letrozole)',
                              'routine (letrozole explained by fertility)',
                              'routine, indication unclear (use other evidence)')
COMP = {}                                                     # auto-names from the top tokens; real names come from the components JSON below
for c in range(K):
    top = H.iloc[c].idxmax()
    COMP[c] = (top[:20], f'c{c}: ' + ', '.join(H.iloc[c].nlargest(3).index.str.split('__').str[0]), BG, UNCLEAR)
# Names from the components JSON written by the last cell of Part A: override COMP for every component whose top-5 tokens still match
# (>= 4 of 5); otherwise the auto-name is kept and a warning is printed. Point COMP_JSON at another file to reuse it.
import json
COMP_JSON = f"nmf_k{K}_{TAG}_components.json"
if os.path.exists(COMP_JSON):
    J = json.load(open(COMP_JSON))['components']
    for c in range(K):
        j = J.get(str(c))
        if not j or not j.get('name'):
            continue
        if len(set(j['signature']) & set(H.iloc[c].nlargest(5).index)) < 4:
            print(f"WARNING c{c}: top tokens in {COMP_JSON} differ from this NMF, its name is ignored")
            continue
        COMP[c] = (COMP[c][0], j['name'], j.get('group') or COMP[c][2]) + ((j.get('status') or COMP[c][3],) if len(COMP[c]) > 3 else ())
    print(f"component names loaded from {COMP_JSON}")
else:
    print(f"{COMP_JSON} not found: components are auto-named (name them in DESCR in the last cell of Part A)")
print("top tokens per component:")
for c in range(K):
    print(f"  c{c}:", ', '.join(H.iloc[c].nlargest(4).index.str.slice(0, 32)))

print(f"{'comp':>4} {'n':>6} {'%':>5}  {'group':<24} name")
for c, v in COMP.items():
    n = int((comp == c).sum())
    print(f"{c:>4} {n:>6} {n / len(comp) * 100:5.1f}  {v[2]:<24} {v[1]}")


print('### CELL 53  t=%.0fs' % (_t.time()-_T0), flush=True)
from joblib import Parallel, delayed

def contains(seq, pat):
    it = iter(seq)
    return all(x in it for x in pat)

def discriminative(mask, candidates, sequences_db=None, min_in=0.12):
    sdb = sequences_db if sequences_db is not None else db
    out = []
    for p in candidates:
        h = np.array([contains(s, p) for s in sdb])
        si, so = h[mask].mean(), h[~mask].mean()
        if si >= min_in:
            out.append({'pattern': ' -> '.join(p), 'sup_in': round(si, 3),
                        'sup_out': round(so, 3), 'lift': round((si + .01) / (so + .01), 1)})
    if not out:
        return pd.DataFrame(columns=['pattern', 'sup_in', 'sup_out', 'lift'])
    return pd.DataFrame(out).sort_values(['lift', 'pattern'], ascending=[False, True]).reset_index(drop=True)

def _component_job(sdb_in, sdb_out, rel_sup, max_cand):
    """One component: LOCAL mining on its own patients, then lift vs the out-sample.
    Takes only its own slices, so it ships cheaply to a worker process."""
    pats_c = prefixspan(sdb_in, max(3, int(rel_sup * len(sdb_in))), max_len=4)
    pats_c = pats_c[pats_c.pattern.map(len) >= 3].sort_values(['support', 'pattern'], ascending=[False, True]).head(max_cand)
    sdb    = sdb_in + sdb_out
    mask   = np.arange(len(sdb)) < len(sdb_in)
    return discriminative(mask, [tuple(p) for p in pats_c.pattern], sequences_db=sdb, min_in=rel_sup)

def component_motifs(rel_sup=0.15, max_cand=100, n_out=1500, seed=0, n_jobs=None):
    """All components in parallel (they are independent), like Day 1's k-sweep."""
    n_jobs = n_jobs or min(len(COMP), max(1, (os.cpu_count() or 2) - 2))   # leave 2 cores free
    jobs = []
    for c in COMP:
        idx_in  = np.flatnonzero(comp == c)
        idx_out = np.flatnonzero(comp != c)
        idx_out = np.random.default_rng(seed).choice(idx_out, min(n_out, len(idx_out)), replace=False)
        jobs.append(delayed(_component_job)([db[i] for i in idx_in], [db[i] for i in idx_out],
                                            rel_sup, max_cand))
    return dict(zip(COMP, Parallel(n_jobs=n_jobs, verbose=5)(jobs)))

# the local mining is the point: a global 4% floor would bury the 5% components entirely
motifs = component_motifs()
for c, (_, name, grp, triage) in COMP.items():
    d = motifs[c]
    print(f"\n===== component {c} [{grp}]: {name}  (n={(comp == c).sum()})")
    print(f"      draft triage: {triage}")
    if len(d):
        display(d.head(4))
    else:
        print("  no ordered pattern of length >= 3 reaches the in-component support floor")

print('### CELL 55  t=%.0fs' % (_t.time()-_T0), flush=True)
weak = eo.weak_labels(events)
wl   = weak.set_index('person_id').weak_label

# Every patient here has letrozole by cohort construction, so no filtering needed. Still use
# LOCAL mining: a global 4% threshold is tuned for the full mixed cohort, and the smaller
# indication subgroup would be buried under it.
y_lz = np.array([wl.get(p, 'unlabelled') for p in pids])
print("letrozole patients:", len(db),
      "  labelled:", int((y_lz != 'unlabelled').sum()),
      "  ", dict(zip(*np.unique(y_lz, return_counts=True))))

pats_lz = prefixspan(db, max(3, int(0.08 * len(db))), max_len=4)
C_lz = [tuple(p) for p in pats_lz[pats_lz.pattern.map(len) >= 3]
        .sort_values(['support', 'pattern'], ascending=[False, True]).head(60).pattern]

for g in ['fertility', 'oncology']:
    print(f"\n=== {g} indication")
    display(discriminative(y_lz == g, C_lz, sequences_db=db, min_in=0.10).head(4))

print('### CELL 57  t=%.0fs' % (_t.time()-_T0), flush=True)
import collections, time

MIN_LIFT      = 2                       # a motif must be at least this specific to its component
MIN_SPLITS_OK = 4                       # of the 5 split seeds, as in Day 1
REL_SUP, N_OUT, SEED = 0.15, 1500, 0    # the values component_motifs() used above (same candidates, same outside sample)

# Hit matrix, built once and shared by the bootstrap: hits[c][i, j] = does motif i occur in patient j?
# Columns are [in-component patients | the same random outside sample component_motifs() drew].
hits, n_in = {}, {}
for c in COMP:
    cand    = [tuple(p.split(' -> ')) for p in motifs[c].pattern]
    idx_in  = np.flatnonzero(comp == c)
    idx_out = np.flatnonzero(comp != c)
    idx_out = np.random.default_rng(SEED).choice(idx_out, min(N_OUT, len(idx_out)), replace=False)
    sdb     = [db[i] for i in np.concatenate([idx_in, idx_out])]
    hits[c] = np.array([[contains(s, p) for s in sdb] for p in cand], dtype=bool).reshape(len(cand), len(sdb))
    n_in[c] = len(idx_in)
print({c: hits[c].shape for c in COMP})

print('### CELL 58  t=%.0fs' % (_t.time()-_T0), flush=True)
B = 1000   # bootstrap draws

def bootstrap_lift(H, n_in, B=B, seed=0):
    """Lift of every motif (rows of H) on B resamples with replacement of the in / out patients."""
    rng        = np.random.default_rng(seed)
    Hin, Hout  = H[:, :n_in], H[:, n_in:]
    n_out      = Hout.shape[1]
    lifts      = np.empty((B, H.shape[0]))
    for b in range(B):
        si = Hin[:,  rng.integers(0, n_in,  n_in)].mean(1)
        so = Hout[:, rng.integers(0, n_out, n_out)].mean(1)
        lifts[b] = (si + .01) / (so + .01)
    return lifts

boot = {}
for c in COMP:
    d = motifs[c].copy()
    if len(d):
        L = bootstrap_lift(hits[c], n_in[c])
        d['lift_lo'], d['lift_hi'] = np.percentile(L, [2.5, 97.5], axis=0).round(1)
        d['p_lift_ok'] = (L >= MIN_LIFT).mean(0).round(2)     # share of draws where lift >= MIN_LIFT
    boot[c] = d
print("bootstrap done:", {c: len(d) for c, d in boot.items()}, "motifs per component")

print('### CELL 59  t=%.0fs' % (_t.time()-_T0), flush=True)
SPLIT_SEEDS = (1, 2, 3, 4, 5)   # independent 50 / 50 splits of each component, as in Day 1
MAX_CAND    = 100                # same candidate budget as component_motifs()

def _split_job(sdb_tr, sdb_ho, sdb_out, rel_sup, max_cand):
    """One (component, seed): nominate candidates by mining the TRAIN half, score them on the HELD-OUT half
    against a seed-specific outside sample. discriminative() already drops motifs below the support floor."""
    pats = prefixspan(sdb_tr, max(3, int(rel_sup * len(sdb_tr))), max_len=4)
    pats = pats[pats.pattern.map(len) >= 3].sort_values(['support', 'pattern'], ascending=[False, True]).head(max_cand)
    sdb  = sdb_ho + sdb_out
    mask = np.arange(len(sdb)) < len(sdb_ho)
    return discriminative(mask, [tuple(p) for p in pats.pattern], sequences_db=sdb, min_in=rel_sup)

def split_stability(n_out=N_OUT, n_jobs=None):
    """All (component, seed) jobs in parallel, largest component first so no big job starts last."""
    n_jobs = n_jobs or max(1, (os.cpu_count() or 2) - 2)
    keys, jobs = [], []
    for c in sorted(COMP, key=lambda c: -int((comp == c).sum())):
        idx_in, idx_out = np.flatnonzero(comp == c), np.flatnonzero(comp != c)
        for s in SPLIT_SEEDS:
            rng  = np.random.default_rng(s)
            perm = rng.permutation(idx_in)
            tr, ho = perm[:len(perm) // 2], perm[len(perm) // 2:]
            out  = rng.choice(idx_out, min(n_out, len(idx_out)), replace=False)
            keys.append((c, s))
            jobs.append(delayed(_split_job)([db[i] for i in tr], [db[i] for i in ho],
                                            [db[i] for i in out], REL_SUP, MAX_CAND))
    return dict(zip(keys, Parallel(n_jobs=n_jobs, verbose=5)(jobs)))

t0 = time.perf_counter()
splits = split_stability()
print(f"split-seed mining: {(time.perf_counter() - t0) / 60:.1f} min")

print('### CELL 60  t=%.0fs' % (_t.time()-_T0), flush=True)
rows, summ = {}, []
for c, (_, name, grp, _) in COMP.items():
    d = boot[c].copy()
    if len(d):
        found = collections.Counter(p for s in SPLIT_SEEDS
                                    for p in splits[(c, s)].loc[splits[(c, s)].lift >= MIN_LIFT, 'pattern'])
        d['splits_found'] = d.pattern.map(lambda p: found.get(p, 0))
        d['verdict'] = np.select([(d.splits_found >= MIN_SPLITS_OK) & (d.lift_lo >= MIN_LIFT),
                                  d.splits_found >= MIN_SPLITS_OK - 1],
                                 ['solid', 'suggestive'], 'unstable')
    rows[c] = d
    v = d.verdict.value_counts() if len(d) else pd.Series(dtype=int)
    summ.append({'comp': c, 'group': grp, 'motifs': len(d), 'solid': int(v.get('solid', 0)),
                 'suggestive': int(v.get('suggestive', 0)), 'unstable': int(v.get('unstable', 0))})
display(pd.DataFrame(summ).set_index('comp'))

SHOW = ['pattern', 'sup_in', 'sup_out', 'lift', 'lift_lo', 'lift_hi', 'splits_found', 'verdict']
with pd.option_context('display.max_colwidth', 110):
    for c, (_, name, grp, _) in COMP.items():
        print(f"\n===== component {c} [{grp}]: {name}  (n={n_in[c]})")
        if len(rows[c]):
            display(rows[c][SHOW].head(4))
        else:
            print("  no motif reached the support floor on the full run")

print('### CELL 63  t=%.0fs' % (_t.time()-_T0), flush=True)
# Held-out pass rate, family clustering, same-day flag and the hybrid verdict (the table below reads them). Computed in motif_robustness/hybrid.py, nothing is shown here.
import time
from motif_robustness.preprocess import build_patient_seqs
from motif_robustness.hybrid import add_heldout_letrozole

HO_SEEDS       = tuple(range(101, 121))   # 20 splits; both directions are scored -> 40 runs
HO_MIN_OR      = 2.0                      # lower 95% bound of the odds ratio on the held-out half
HO_MIN_RATE_LO = 0.70                     # family pass rate (lower Wilson bound) needed to stay `solid`
FAM_DIST       = 0.2                      # Jaccard distance below which motifs are one family
SAME_DAY_RATIO = 0.5                      # strict-date support / tie-ordered support below this = same-day bundle

_p, _ps = build_patient_seqs(events)      # same dedup / collapse rules as eo.sequences, but keeps the dates
assert _p == pids and all(_ps[p].tokens == s for p, s in zip(pids, db)), "dated sequences differ from db"
patseqs = [_ps[p] for p in pids]

t0 = time.perf_counter()
hyb, ho_runs = add_heldout_letrozole(rows, comp, patseqs, hits, n_in, rel_sup=REL_SUP, ho_seeds=HO_SEEDS, ho_min_or=HO_MIN_OR,
                                     ho_min_rate_lo=HO_MIN_RATE_LO, fam_dist=FAM_DIST, same_day_ratio=SAME_DAY_RATIO, min_lift=MIN_LIFT)
print(f"held-out pass rate: {(time.perf_counter() - t0):.0f} s")


print('### CELL 65  t=%.0fs' % (_t.time()-_T0), flush=True)
# One colour per component group, used by 3b and the trajectory graphs. The group of each component comes from COMP.
GCOL   = {FERT: '#2f855a', ONCO: '#c05621', BG: '#718096'}
grp_of = pd.Series(comp, index=pids).map(lambda c: COMP[c][2] if c in COMP else np.nan)
lanes  = [FERT, ONCO, BG]


print('### CELL 67  t=%.0fs' % (_t.time()-_T0), flush=True)
LANE_NAME = {FERT: 'fertility comps, no dx', ONCO: 'oncology: confirmed dx', BG: 'other comps, no dx'}
onc_first = events[eo.group_mask(events, eo.ONCOLOGY_TAGS)].groupby('person_id').event_date.min()
gap2      = (onc_first - lz).dt.days.dropna()                      # patients with letrozole AND oncology evidence

by_grp = lambda grp: set(grp_of.index[grp_of == grp]) - case_ids
pools  = {FERT: by_grp(FERT), ONCO: case_ids, BG: by_grp(BG)}      # comparison lanes exclude every confirmed-dx patient
have   = {k: sorted(set(gap2.index) & p) for k, p in pools.items()}
N_PLOT = len(have[ONCO])                                           # match the oncology lane's plotted n
rng    = np.random.default_rng(0)
samp   = {k: (have[k] if k == ONCO else sorted(rng.choice(have[k], min(N_PLOT, len(have[k])), replace=False)))
          for k in lanes}

fig, ax = plt.subplots(figsize=(10.5, 3.2))
for y, k in enumerate(lanes):
    d = gap2.loc[samp[k]]
    ax.scatter(d, y + rng.normal(0, .06, len(d)), s=44, color=GCOL[k], edgecolor='white', linewidth=.6)
    ax.text(1.01, y, f"plotted n={len(d)}   median {d.median():.0f} d   {(d < 0).mean():.0%} evidence first\n"
                     f"coverage {len(have[k])} of {len(pools[k])} ({len(have[k]) / max(len(pools[k]), 1):.0%}) have oncology evidence",
            transform=ax.get_yaxis_transform(), va='center', fontsize=7.5)
ax.axvline(0, c='k', lw=1)
ax.set_yticks(range(len(lanes))); ax.set_yticklabels([LANE_NAME[k] for k in lanes]); ax.set_ylim(-.6, len(lanes) - .4)
ax.set_xlabel('days from first letrozole to first oncology evidence   (negative = evidence first)')
ax.set_title(f'letrozole -> first oncology evidence, matched samples of {N_PLOT}')
fig.subplots_adjust(left=.22, right=.64, bottom=.2); plt.show()

rows = []
for k in lanes:
    d = gap2.loc[samp[k]]
    rows.append({'lane': LANE_NAME[k], 'patients in group': len(pools[k]), 'with oncology evidence': len(have[k]),
                 'coverage %': round(len(have[k]) / max(len(pools[k]), 1) * 100, 1), 'plotted n': len(d),
                 'median days': d.median(), 'p25': d.quantile(.25), 'p75': d.quantile(.75),
                 'evidence first %': round((d < 0).mean() * 100, 1)})
display(pd.DataFrame(rows).set_index('lane').round(0))

print('### CELL 69  t=%.0fs' % (_t.time()-_T0), flush=True)
import networkx as nx

# every curated codeset tag (codesets.yaml via eo); the raw per-product codes would swamp the graph
FOCUS = set(eo.CODESETS)

# the graph is about curated clinical steps: relabel each concept token by its group, drop uncurated ones, collapse repeats
import itertools
_tg = events.drop_duplicates('tag').dropna(subset=['groups']).set_index('tag')['groups'].astype(str).str.split('|').to_dict()   # token -> ALL its groups
gseqs = {p: [g for g, _ in itertools.groupby(g for t in seqs[p] for g in _tg.get(t, ()))] for p in pids}
Hg = eo.group_loadings(H, events)       # a group's NMF loading = sum over its concept tokens (a token counts in every group it is in)
db_lz_g = [[c for c in gseqs[p] if c in FOCUS] for p in pids if 'letrozole' in gseqs[p]]
print(f"{len(db_lz_g)} letrozole patients")

cnt = collections.Counter()
for s in db_lz_g:
    for u, v in zip(s, s[1:]):
        cnt[(u, v)] += 1
G = nx.DiGraph()
for (u, v), w in cnt.items():
    if w >= max(5, int(0.02 * len(db_lz_g))):
        G.add_edge(u, v, weight=w)
print(G.number_of_nodes(), "nodes,", G.number_of_edges(), "edges")

# Fill colour = the component group that owns the tag's NMF loading (its share of the tag's total
# loading; fertility is summed over its 4 components). letrozole is the cohort anchor, so it is not in
# the NMF; tags dropped by the prevalence floor are not in H either.
grp_comps = {g: [k for k, v in COMP.items() if v[2] == g] for g in GCOL}
def owner_group(tag):
    if tag == 'letrozole':
        return 'anchor'
    if tag not in Hg.columns or Hg[tag].sum() == 0:
        return 'not in NMF'
    share = {g: Hg.loc[ks, tag].sum() / Hg[tag].sum() for g, ks in grp_comps.items()}
    return max(share, key=share.get)
NODE_COL = {**GCOL, 'anchor': '#f6e05e', 'not in NMF': '#e2e8f0'}
node_grp = {n: owner_group(n) for n in G.nodes()}
print("nodes per group:", dict(collections.Counter(node_grp.values())))


print('### CELL 71  t=%.0fs' % (_t.time()-_T0), flush=True)
# Trajectory graph on a time axis: x = median days from the patient's first letrozole to the first time the patient has that group
# (log-compressed, 0 = letrozole), y = the component group that owns the tag's NMF loading. Nodes in one lane are staggered by x, so labels cannot overlap.
# Edges are the transitions in G (cell above). Needs the graph cell above and the dated sequences (patseqs) from the hybrid section.
ANCHOR      = 'letrozole'
ANCHOR_NAME = ANCHOR.replace('_', ' ')
MIN_N       = 20                                                   # fewer patients with both -> no timing, node parked at the right edge
SLOT, LABEL_IN = 1.0, 1.15                                          # vertical stagger step (y units), room one label needs on the x axis (inches)

_nodes  = set(G.nodes())
_have   = [i for i, p in enumerate(pids) if ANCHOR in gseqs[p]]     # the cohort of the graph
_first  = {n: [] for n in _nodes}
_a_tok  = {t for t, gs in _tg.items() if ANCHOR in gs}
for i in _have:
    ps = patseqs[i]
    a0 = min((ps.dpos[t][0] for t in _a_tok if t in ps.dpos), default=None)
    if a0 is None:
        continue
    best = {}
    for t, dl in ps.dpos.items():
        for g in _tg.get(t, ()):
            if g in _nodes and (g not in best or dl[0] < best[g]):
                best[g] = dl[0]
    for g, d in best.items():
        _first[g].append(d - a0)
med = {g: float(np.median(v)) for g, v in _first.items() if len(v) >= MIN_N}
med[ANCHOR] = 0.0

Hg_    = Hg if 'Hg' in globals() else eo.group_loadings(H, events)
comps_ = list(dict.fromkeys(v[2] for v in COMP.values()))           # component groups, in COMP order
def owner_lane(g):
    if g == ANCHOR:
        return 'anchor'
    if g not in Hg_.columns or Hg_[g].sum() == 0:
        return 'not in NMF'
    share = {l: Hg_.loc[[k for k, v in COMP.items() if v[2] == l], g].sum() / Hg_[g].sum() for l in comps_}
    return max(share, key=share.get)
lane_of  = {n: owner_lane(n) for n in _nodes}
LANES    = [l for l in comps_ + ['anchor', 'not in NMF'] if l in set(lane_of.values())]
_pal     = ['#2f855a', '#c05621', '#718096', '#2b6cb0', '#b83280', '#b7791f']
LANE_COL = {**{l: _pal[i % len(_pal)] for i, l in enumerate(comps_)}, 'anchor': '#d69e2e', 'not in NMF': '#a0aec0', **globals().get('GCOL', {})}

tf = lambda d: np.sign(d) * np.log1p(np.abs(d) / 30)                # days -> compressed axis, 0 stays 0
xs = {g: tf(m) for g, m in med.items() if g in _nodes}
x_park = (max(xs.values()) if xs else 0) + 1.4
_all_x = list(xs.values()) + ([x_park] if any(n not in xs for n in _nodes) else [])
MIN_DX = LABEL_IN * (max(_all_x) - min(_all_x) + 1) / 12.0           # x units that fit one label on a 14 in wide figure
order  = [0] + [s * k for k in range(1, 13) for s in (1, -1)]
slot_of, lane_k = {}, {}
for l in LANES:
    members = sorted((n for n in _nodes if lane_of[n] == l), key=lambda n: (xs.get(n, x_park), n))
    last = {}                                                      # slot -> x of the last node placed there
    for n in members:
        x = xs.get(n, x_park)
        k = next(k for k in order if x - last.get(k, -1e9) >= MIN_DX)
        last[k] = x; slot_of[n] = (l, k, x)
    lane_k[l] = max((abs(k) for (ll, k, _) in slot_of.values() if ll == l), default=0)
heights = {l: 2 * lane_k[l] * SLOT + 1.8 for l in LANES}            # a lane is as tall as its stagger needs
centers, y_top = {}, 0.0
for l in LANES:
    centers[l] = y_top - heights[l] / 2; y_top -= heights[l]
pos_t = {n: (x, centers[l] + k * SLOT) for n, (l, k, x) in slot_of.items()}

fig, ax = plt.subplots(figsize=(14, max(5, 0.6 * (-y_top) + 1.8)))
for l in LANES:
    ax.axhspan(centers[l] - heights[l] / 2, centers[l] + heights[l] / 2, color=LANE_COL.get(l, '#e2e8f0'), alpha=.08, lw=0)
    ax.text(-0.01, centers[l], l, transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=9, fontweight='bold')
w = np.array([G[u][v]['weight'] for u, v in G.edges()], dtype=float)
nx.draw_networkx_edges(G, pos_t, ax=ax, width=1 + 4 * w / w.max(), alpha=.3, arrowsize=14, node_size=700, connectionstyle='arc3,rad=0.15')
nx.draw_networkx_nodes(G, pos_t, ax=ax, node_size=700, node_color=[LANE_COL.get(lane_of[n], '#e2e8f0') for n in G.nodes()], edgecolors='#4a5568', linewidths=.8)
nx.draw_networkx_labels(G, {n: (x, y - 0.42) for n, (x, y) in pos_t.items()}, ax=ax, font_size=8,
                        bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=.85))
ax.tick_params(axis='x', bottom=True, labelbottom=True)              # networkx hides the ticks
tick_d = [-365, -90, -30, 0, 30, 90, 365, 730]
ax.set_xticks([tf(d) for d in tick_d]); ax.set_xticklabels([f"{d:+d} d" if d else ANCHOR_NAME for d in tick_d], fontsize=8)
ax.axvline(0, color='#d69e2e', lw=1, ls='--', alpha=.7)
if any(n not in xs for n in _nodes):
    ax.text(x_park, 0.3, f'timing n<{MIN_N}', ha='center', fontsize=8, color='#718096')
ax.set_yticks([]); ax.spines[['left', 'right', 'top']].set_visible(False)
ax.set_xlabel(f"median days from first {ANCHOR_NAME} to first occurrence of the group (log-compressed)")
ax.set_title(f'{ANCHOR_NAME} trajectory graph on a time axis -- lanes = owning component group')
plt.margins(x=.06); plt.tight_layout(); plt.show()
print({l: int(sum(1 for n in _nodes if lane_of[n] == l)) for l in LANES}, "nodes per lane;", sum(1 for n in _nodes if n not in xs), "without timing")


print('### CELL 74  t=%.0fs' % (_t.time()-_T0), flush=True)
COHORT = 'letrozole'
# ANCHOR-FOCUSED view of the final table (additional; the table above is untouched): per bundle, the top-TOPK_ANCHOR scored ordered patterns that contain a letrozole step,
# with the position of that step (k of n). Same scores / verdicts as the table above (post-filter of hyb, no re-mining). Own xlsx file; Triage / literature / PMIDs left empty.
import re, itertools, collections
try:
    import openpyxl
except ImportError as e:
    raise ImportError("pip install openpyxl in this kernel's environment, then rerun this cell") from e
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

TOPK, TOP_ENT = 3, 5            # patterns per bundle (highest lift first) / entities per bundle
RANK_BY = 'loading'             # entities ranked by NMF loading ('loading') or by share of the bundle's patients having the code ('prevalence')
XLSX_FINAL = f"final_table_{COHORT}_k{K}_{VARIANT}.xlsx"
cdx = concept.drop_duplicates('concept_id').set_index('concept_id')

ANCHOR      = 'letrozole'                                                    # cohort anchor group (codesets.yaml)
ANCHOR_NAME = ANCHOR.replace('_', ' ')
ANCHOR_TOK  = set(events.loc[eo.group_mask(events, ANCHOR), 'tag'])    # every concept-level token that belongs to the anchor group
TOPK_ANCHOR = 3                                                       # anchor patterns per bundle (highest lift first)

def has_anchor(pattern):
    return any(t in ANCHOR_TOK for t in pattern.split(' -> '))

_a0 = {}
def offset_text(c, members, t, min_n=20):
    """Median days from each patient's first {ANCHOR} step to their first occurrence of token t (negative = t came first), over the bundle's patients who have both."""
    if c not in _a0:                                                       # first anchor day per member, computed once per bundle
        _a0[c] = np.array([min((patseqs[i].dpos[x][0] for x in ANCHOR_TOK if x in patseqs[i].dpos), default=np.nan) for i in members])
    td = np.array([patseqs[i].dpos[t][0] if t in patseqs[i].dpos else np.nan for i in members])
    g  = (td - _a0[c])[~np.isnan(td - _a0[c])]
    if len(g) < min_n:
        return f"\n    vs first {ANCHOR_NAME}: too few patients with both (n={len(g)})"
    med = int(np.median(g))
    when = "same day as" if med == 0 else f"{abs(med):,} d {'before' if med < 0 else 'after'}"
    return f"\n    median {when} first {ANCHOR_NAME} ({(g < 0).mean():.0%} of them before)"

def _condense_name(n, limit=38):
    s = re.split(r' \(|;| This ', n)[0].strip()
    s = s if len(s) >= 8 else n                                      # packs like '{6 (azithromycin ...) } Pack' would be cut to '{6'
    return s if len(s) <= limit else s[:limit].rsplit(' ', 1)[0] + '…'

def label(token):
    m = re.search(r'__(\d+)$', token)
    if m and int(m.group(1)) in cdx.index:
        r = cdx.loc[int(m.group(1))]
        return f"{_condense_name(r.concept_name)} [{r.vocabulary_id} {r.concept_code}]"
    return f"{token.replace('_', ' ')} [code group]"

def pattern_text(pattern):
    parts = []
    for t, g in itertools.groupby(pattern.split(' -> ')):
        n = len(list(g)); parts.append(label(t) + (f" ×{n}" if n > 1 else ""))
    return ' → '.join(parts)

HEAD = ['Group (bundle)', 'n (%)', 'Most frequently OMOP clinical entities found', 'Rank (by lift)', 'Typical order of care (condensed names, vocabulary + code)', "Position in the bundle's scored top patterns (by lift · by support)", 'Share of group with pattern', 'Share of everyone else with pattern', 'Re-tests found (of 5)', 'Holds up on re-test?', 'Times as common (lift)', 'Final verdict', 'Triage suggestion', 'Order shown by dates?', 'Supported literature (Yes / Partly / None)', 'PMIDs']
BUNDLE_COLS = (1, 2, 3, 13)                   # merged down the rows of a bundle

table = []                                                          # list of (bundle number, row values)
for c in sorted(COMP):
    members = np.flatnonzero(comp == c)
    cnt   = collections.Counter(t for i in members for t in set(db[i]))
    share = lambda t: cnt.get(t, 0) / max(len(members), 1)
    score = H.iloc[c] if RANK_BY == 'loading' else pd.Series({t: share(t) for t in H.columns})
    ents  = "\n".join(f"{i}. {label(t)} ({share(t):.0%} of bundle){offset_text(c, members, t)}" for i, t in enumerate(score.nlargest(TOP_ENT).index, 1))
    head  = [f"c{c} · {COMP[c][1]}", f"{len(members):,} ({len(members) / len(comp):.1%})", ents]
    pool  = hyb.get(c)
    pool  = pool if pool is not None and len(pool) else None
    if pool is not None:
        pool = pool.assign(rk_lift=np.arange(1, len(pool) + 1), rk_sup=pool.sup_in.rank(ascending=False, method='min').astype(int))   # hyb[c] is lift-sorted
        has  = pool.pattern.map(has_anchor)
    d     = pool[has].head(TOPK_ANCHOR) if pool is not None else None
    head[1] += f"\n{int(has.sum()) if pool is not None else 0} of {len(pool) if pool is not None else 0} scored patterns contain {ANCHOR_NAME}"
    if d is None or not len(d):
        table.append((c, head + ['', f"no scored pattern contains {ANCHOR_NAME} (bundle has {len(pool) if pool is not None else 0} scored patterns)"] + [''] * (len(HEAD) - 5)))
        continue
    for rk, (_, r) in enumerate(d.iterrows(), 1):
        holds = 'Yes' if r.splits_found >= 4 else 'Partly' if r.splits_found == 3 else 'No'
        row = (head if rk == 1 else ['', '', '']) + [rk, pattern_text(r.pattern), f"{int(r.rk_lift)} of {len(pool)} by lift · {int(r.rk_sup)} of {len(pool)} by support", float(r.sup_in), float(r.sup_out), int(r.splits_found), holds,
                                                     float(r.lift), r.hybrid_verdict.capitalize(), '', 'Same-day bundle' if r.same_day_bundle else 'Yes', '', '']
        table.append((c, row))

FILL = {'Yes': 'D6F0DE', 'Partly': 'FBEFC9', 'No': 'F8D7D7', 'Solid': 'D6F0DE', 'Suggestive': 'FBEFC9', 'Unstable': 'F8D7D7', 'Same-day bundle': 'FBEFC9'}
F = lambda **kw: Font(name='Arial', size=10, **kw)
thin = Side(style='thin', color='D0D5DB')
wb = openpyxl.Workbook(); ws = wb.active; ws.title = f'{COHORT} k={K}'
ws.append(HEAD)
for j in range(1, len(HEAD) + 1):
    h = ws.cell(1, j); h.font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
    h.fill = PatternFill('solid', fgColor='334E68'); h.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
ws.row_dimensions[1].height = 44
for _, row in table:
    ws.append(row)
dv = DataValidation(type='list', formula1='"Yes,Partly,None"', allow_blank=True); ws.add_data_validation(dv)
LEFT = {1, 3, 5, 13}
for i in range(2, len(table) + 2):
    ws.row_dimensions[i].height = 64
    for j in range(1, len(HEAD) + 1):
        c_ = ws.cell(i, j); c_.font = F(bold=(j == 1)); c_.border = Border(bottom=thin)
        c_.alignment = Alignment(wrap_text=True, vertical='top', horizontal='left' if j in LEFT else 'center')
    for j in (7, 8): ws.cell(i, j).number_format = '0.0%'
    ws.cell(i, 11).number_format = '0.0'
    for j in (10, 12, 14):
        v = ws.cell(i, j).value
        if v in FILL: ws.cell(i, j).fill = PatternFill('solid', fgColor=FILL[v]); ws.cell(i, j).font = F(bold=True)
    dv.add(ws.cell(i, 15))
r0 = 2
for c, grp in itertools.groupby([b for b, _ in table]):               # one merged block per bundle
    n = len(list(grp)); r1 = r0 + n - 1
    if n > 1:
        for j in BUNDLE_COLS: ws.merge_cells(start_row=r0, end_row=r1, start_column=j, end_column=j)
    r0 = r1 + 1
for j, w in enumerate([30, 22, 70, 8, 80, 22, 12, 13, 11, 11, 11, 12, 34, 14, 16, 16], 1):
    ws.column_dimensions[get_column_letter(j)].width = w
ws.freeze_panes = 'B2'
notes = [
    "Notes",
    f"Source: fused Day 1 + Day 3 notebook, letrozole run ({VARIANT}{', +/- ' + str(WINDOW_MONTHS) + ' months around any letrozole event' if WINDOW_MONTHS else ''}), NMF k={K} on concept-level tokens, {len(db):,} patients. Bundles are the NMF components in order c0, c1, ...; n (%) = patients whose dominant component is the bundle.",
    f"Entities: the top {TOP_ENT} OMOP concepts of the bundle ranked by {'NMF loading' if RANK_BY == 'loading' else 'share of the bundle patients having the code'}; the % is the share of the bundle's patients with that code.",
    f"Patterns: the {TOPK_ANCHOR} highest-lift scored ordered patterns of each bundle that contain a {ANCHOR_NAME} step (any {ANCHOR_NAME} concept), from the same candidates as the main table (ordered patterns of 3+ steps, each present in >={REL_SUP:.0%} of the bundle). The second line of each n (%) cell says how many of the bundle's scored patterns contain {ANCHOR_NAME}.",
    f"Entities: under each entity, the median number of days from the patient's first {ANCHOR_NAME} step to their FIRST occurrence of that entity (before / after), over the bundle patients who have both, and the share of them for whom it came first. Repeated entities (labs, drugs) are read at their first occurrence.",
    "Position among the bundle's scored top patterns: each bundle's candidates are its 100 most frequent ordered patterns (3+ steps) that pass the support floor, scored for lift; the pattern's place in that list by lift (1 = most specific to the bundle) and by support (1 = most frequent), out of the N patterns scored. A bundle with no such pattern is shown as such, not filled.",
    "Times as common = (share inside bundle + 0.01) / (share outside + 0.01). Outside = random sample of 1,500 patients from other bundles.",
    "Re-tests: each bundle split in half at random, 5 times; patterns found on one half and checked on the other. Yes = found in 4-5 of 5, Partly = 3, No = 0-2.",
    f"Final verdict = the hybrid verdict: Solid = re-found in >=4 of 5 re-tests with lift range low >= {MIN_LIFT}, downgraded to Suggestive when the family held-out pass rate lower bound is below {HO_MIN_RATE_LO:.0%} ({len(HO_SEEDS)} splits x 2 directions); Suggestive = found in 3 of 5; Unstable otherwise.",
    f"Order shown by dates? 'Same-day bundle' = with every step required on a strictly later day, support falls below {SAME_DAY_RATIO:.0%} of its table value: the steps mostly occur together on one day, so the order is a tie-break, not evidence.",
    "Triage suggestion, Supported literature (Yes / Partly / None, drop-down) and PMIDs are left empty for the review.",
    "'×N' = the same concept appears N times in a row. '[code group]' = a curated group of several codes.",
]
for k_, t in enumerate(notes):
    ws.cell(len(table) + 3 + k_, 1, t).font = F(bold=(k_ == 0))
wb.save(XLSX_FINAL)
print(f"wrote {os.path.abspath(XLSX_FINAL)}  ({len(COMP)} bundles, {len(table)} rows)")
pd.DataFrame([r for _, r in table], columns=HEAD).iloc[:, :12]

print('### DONE', flush=True)
