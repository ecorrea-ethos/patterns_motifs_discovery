"""Group-vs-rest ordered-motif discovery with robustness tiers, generic over the grouping.

`discover()` takes one group id per patient (NMF argmax components, or the breast-cancer label) and, for every group:

  1. mines candidate motifs inside the group (PrefixSpan, local support floor),
  2. scores them against a random sample of the other patients (support in / out, lift),
  3. bootstraps the lift (does the number hold on re-draws of the patients?),
  4. repeats the nomination on random 50 / 50 splits (would the motif be found again?) -> `verdict`,
  5. runs the held-out odds-ratio pass rate per motif family -> `hybrid_verdict`.

Nothing here is fitted to a label: groups are inputs, motifs are patterns, the verdicts are about reproducibility.
"""
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from .families import cluster_families, family_any
from .mining import mine_candidates
from .scoring import bh_fdr, or_ci, score_hits
from .seqindex import hit_matrix
from .stability import rate_ci, split_halves


def _mine(token_lists, rel_sup, max_len, max_cand, min_len, mine_cap, seed):
    """Candidate motifs from a group's sequences; a group larger than `mine_cap` is mined on a random sample of that size.

    The cap bounds PrefixSpan's runtime only. Candidates are always scored on every patient of the group.
    """
    if len(token_lists) > mine_cap:
        keep = np.sort(np.random.default_rng(seed).choice(len(token_lists), mine_cap, replace=False))
        token_lists = [token_lists[i] for i in keep]
    return [p for p, _ in mine_candidates(token_lists, rel_sup, max_len, max_cand, min_len)]


def _score(patseqs, idx_in, idx_out, cands, min_in):
    """Hit matrix [in-group | outside sample] for `cands`, plus the support / lift table (motifs with sup_in >= min_in, lift-sorted).

    Returns (table, H) with the rows of H in table order (`_i` = index into `cands`). Matching is tie_ordered (same-day steps ordered by DOMAIN_ORDER).
    """
    cols = ['pattern', 'sup_in', 'sup_out', 'lift', '_i']
    if not cands:
        return pd.DataFrame(columns=cols), np.zeros((0, len(idx_in) + len(idx_out)), bool)
    H  = hit_matrix([patseqs[i] for i in np.concatenate([idx_in, idx_out])], cands, 'tie_ordered')
    si = H[:, :len(idx_in)].mean(1)
    so = H[:, len(idx_in):].mean(1) if len(idx_out) else np.zeros(len(cands))
    d  = pd.DataFrame({'pattern': [' -> '.join(p) for p in cands], 'sup_in': si.round(3), 'sup_out': so.round(3),
                       'lift': np.round((si + .01) / (so + .01), 1), '_i': np.arange(len(cands))})
    d  = d[si >= min_in].sort_values(['lift', 'pattern'], ascending=[False, True]).reset_index(drop=True)
    return d[cols], H[d['_i'].to_numpy()]


def _bootstrap_lift(H, n_in, n_boot, seed=0):
    """Lift of every motif (rows of H = [in | out]) on n_boot resamples with replacement of the in / out patients."""
    rng       = np.random.default_rng(seed)
    Hin, Hout = H[:, :n_in], H[:, n_in:]
    lifts     = np.empty((n_boot, H.shape[0]))
    for b in range(n_boot):
        si = Hin[:,  rng.integers(0, n_in,            n_in)].mean(1)
        so = Hout[:, rng.integers(0, Hout.shape[1], Hout.shape[1])].mean(1)
        lifts[b] = (si + .01) / (so + .01)
    return lifts


def add_heldout(rows, groups, patseqs, *, rel_sup, ho_seeds, ho_min_or, ho_min_rate_lo, fam_dist, same_day_ratio):
    """Held-out pass rate per motif family, same-day flag, Fisher q and the hybrid verdict. Mutates and returns `rows`.

    A motif passes on a held-out half when its support there is >= rel_sup and the lower 95% bound of its odds ratio against ALL
    outside patients is >= ho_min_or. Near-duplicate motifs form a family that passes when any member does.
    """
    _fisher = []
    for c in rows:
        d = rows[c]
        if not len(d):
            continue
        pats    = [tuple(p.split(' -> ')) for p in d.pattern]
        in_idx  = np.flatnonzero(groups == c)
        out_idx = np.flatnonzero(groups != c)
        Ht      = hit_matrix(patseqs, pats, 'tie_ordered')                       # all patients x motifs
        assert np.allclose(Ht[:, in_idx].mean(1), d.sup_in.to_numpy(), atol=1e-3), "hit matrix disagrees with sup_in"
        sc      = score_hits(Ht, groups == c)
        fam, reps, _ = cluster_families(Ht[:, in_idx], pats, sc.log_or.to_numpy(), fam_dist)

        # (a) held-out pass: lower OR bound >= ho_min_or vs ALL outside patients, on the half not used
        a_all = np.zeros((len(pats), len(ho_seeds), 2), bool)
        for si, s in enumerate(ho_seeds):
            A, B = split_halves(in_idx, s)
            for k, test in enumerate((B, A)):
                hit_in, hit_out = Ht[:, test].sum(1), Ht[:, out_idx].sum(1)
                _, lo, _ = or_ci(hit_in, len(test), hit_out, len(out_idx))
                a_all[:, si, k] = (hit_in / len(test) >= rel_sup) & (lo >= np.log(ho_min_or))
        fa      = a_all.reshape(len(pats), -1)
        fam_a   = family_any(fa, fam)
        r,  lo,  hi  = rate_ci(fa)
        fr, flo, fhi = rate_ci(fam_a)
        Hs = hit_matrix([patseqs[i] for i in in_idx], pats, 'strict_date')       # strictly later dates, in-group only
        d['holdout_rate'], d['holdout_rate_lo'], d['holdout_rate_hi'] = r.round(3), lo.round(3), hi.round(3)
        d['fam_id']            = fam
        d['fam_holdout_rate']  = fr.round(3); d['fam_holdout_rate_lo'] = flo.round(3); d['fam_holdout_rate_hi'] = fhi.round(3)
        d['sup_in_strict']     = Hs.mean(1).round(3)
        d['same_day_bundle']   = d.sup_in_strict < same_day_ratio * d.sup_in
        d['log_or']            = sc.log_or.round(2).to_numpy()
        d['fisher_p']          = sc.fisher_p.to_numpy()
        d['is_family_rep']     = [reps[int(f)] == i for i, f in enumerate(fam)]
        _fisher.append(d.fisher_p.to_numpy())
    q = bh_fdr(np.concatenate(_fisher)) if _fisher else np.array([]); k = 0
    for c in rows:
        if len(rows[c]):
            d = rows[c]
            d['q_fisher'] = q[k:k + len(d)].round(4); k += len(d)
            d['hybrid_verdict'] = np.where((d.verdict == 'solid') & (d.fam_holdout_rate_lo < ho_min_rate_lo), 'suggestive', d.verdict)
    return rows


def discover(patseqs, groups, *, rel_sup, max_len, max_cand, min_len, mine_cap, n_out, min_lift, n_boot, split_seeds,
             min_splits_ok, ho_seeds, ho_min_or, ho_min_rate_lo, fam_dist, same_day_ratio, min_group_n, seed=0, n_jobs=1):
    """Motifs for every group id >= 0 in `groups` (one id per patient, aligned with `patseqs`). Returns dict group -> DataFrame.

    Columns: pattern, sup_in, sup_out, lift (full-run), lift_lo / lift_hi / p_lift_ok (bootstrap), splits_found, verdict
    (solid / suggestive / unstable), then the held-out columns from add_heldout() ending in hybrid_verdict.
    Groups with fewer than `min_group_n` patients are skipped (a floor of 3 patients is no pattern).
    """
    groups = np.asarray(groups)
    ids    = [int(g) for g in np.unique(groups) if g >= 0 and (groups == g).sum() >= min_group_n]
    idx_in = {g: np.flatnonzero(groups == g) for g in ids}
    idx_ot = {g: np.flatnonzero(groups != g) for g in ids}
    toks   = lambda idx: [patseqs[i].tokens for i in idx]

    # 1. candidates: local mining inside each group (a global floor would bury the small groups)
    order = sorted(ids, key=lambda g: -len(idx_in[g]))                       # largest first, so no big job starts last
    cand  = dict(zip(order, Parallel(n_jobs=n_jobs, verbose=5)(
                delayed(_mine)(toks(idx_in[g]), rel_sup, max_len, max_cand, min_len, mine_cap, seed) for g in order)))

    # 2. score on every in-group patient vs a fixed random outside sample; 3. bootstrap the lift
    rows = {}
    for g in ids:
        out = np.random.default_rng(seed).choice(idx_ot[g], min(n_out, len(idx_ot[g])), replace=False)
        d, H = _score(patseqs, idx_in[g], out, cand[g], rel_sup)
        d = d.drop(columns='_i')            # H rows follow d's order
        if len(d):
            L = _bootstrap_lift(H, len(idx_in[g]), n_boot, seed)
            d['lift_lo'], d['lift_hi'] = np.percentile(L, [2.5, 97.5], axis=0).round(1)
            d['p_lift_ok'] = (L >= min_lift).mean(0).round(2)
        rows[g] = d

    # 4. split seeds: nominate on one half, score on the other (and against a seed-specific outside sample)
    keys, halves = [], {}
    for g in order:
        for s in split_seeds:
            rng  = np.random.default_rng(s)
            perm = rng.permutation(idx_in[g])
            tr, ho = perm[:len(perm) // 2], perm[len(perm) // 2:]
            halves[(g, s)] = (ho, rng.choice(idx_ot[g], min(n_out, len(idx_ot[g])), replace=False))
            keys.append((g, s, tr))
    cs = Parallel(n_jobs=n_jobs, verbose=5)(
            delayed(_mine)(toks(tr), rel_sup, max_len, max_cand, min_len, mine_cap, s) for g, s, tr in keys)
    found = {g: {} for g in ids}
    for (g, s, _), cands in zip(keys, cs):
        t, _ = _score(patseqs, *halves[(g, s)], cands, rel_sup)
        for p in t.loc[t.lift >= min_lift, 'pattern']:
            found[g][p] = found[g].get(p, 0) + 1
    for g in ids:
        d = rows[g]
        if len(d):
            d['splits_found'] = d.pattern.map(lambda p: found[g].get(p, 0))
            d['verdict'] = np.select([(d.splits_found >= min_splits_ok) & (d.lift_lo >= min_lift), d.splits_found >= min_splits_ok - 1],
                                     ['solid', 'suggestive'], 'unstable')

    # 5. held-out pass rate per motif family
    return add_heldout(rows, groups, patseqs, rel_sup=rel_sup, ho_seeds=ho_seeds, ho_min_or=ho_min_or,
                       ho_min_rate_lo=ho_min_rate_lo, fam_dist=fam_dist, same_day_ratio=same_day_ratio)
