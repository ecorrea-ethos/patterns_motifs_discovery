"""Phase 0: faithful port of the v2 notebook pipeline (mining cell + 2b cells), to prove v3 starts from v2's numbers.

Differences from the v2 notebook: deterministic tie-breaking (see mining.py). Everything else (seeds, sampling order, rounding of
lift to 1 decimal, MIN_LIFT, thresholds) is kept so any difference in counts is attributable to tie order.
"""
import collections

import numpy as np
import pandas as pd

from .mining import contains, mine_candidates


def v2_discriminative(mask, candidates, sdb, min_in):
    out = []
    for p in candidates:
        h = np.array([contains(s, p) for s in sdb])
        si, so = h[mask].mean(), h[~mask].mean()
        if si >= min_in:
            out.append({"pattern": " -> ".join(p), "sup_in": round(si, 3), "sup_out": round(so, 3),
                        "lift": round((si + .01) / (so + .01), 1)})
    cols = ["pattern", "sup_in", "sup_out", "lift"]
    if not out:
        return pd.DataFrame(columns=cols)
    # v2 sorted by lift only (unstable on ties); pattern as secondary key makes it deterministic
    return pd.DataFrame(out).sort_values(["lift", "pattern"], ascending=[False, True]).reset_index(drop=True)


def _component_job(sdb_in, sdb_out, rel_sup, max_len, max_cand, min_len):
    cands = [p for p, _ in mine_candidates(sdb_in, rel_sup, max_len, max_cand, min_len)]
    sdb = sdb_in + sdb_out
    mask = np.arange(len(sdb)) < len(sdb_in)
    return v2_discriminative(mask, cands, sdb, rel_sup)


def v2_component_motifs(db, comp, comps, cfg, n_jobs=1, seed=0, n_out=1500):
    from joblib import Parallel, delayed
    m = cfg["mining"]
    jobs = []
    for c in comps:
        idx_in = np.flatnonzero(comp == c)
        idx_out = np.flatnonzero(comp != c)
        idx_out = np.random.default_rng(seed).choice(idx_out, min(n_out, len(idx_out)), replace=False)
        jobs.append(delayed(_component_job)([db[i] for i in idx_in], [db[i] for i in idx_out],
                                            m["rel_sup"], m["max_len"], m["max_cand"], m["min_len"]))
    return dict(zip(comps, Parallel(n_jobs=n_jobs)(jobs)))


def _bootstrap_lift(H, n_in, B, seed=0):
    rng = np.random.default_rng(seed)
    Hin, Hout = H[:, :n_in], H[:, n_in:]
    n_out = Hout.shape[1]
    lifts = np.empty((B, H.shape[0]))
    for b in range(B):
        si = Hin[:, rng.integers(0, n_in, n_in)].mean(1)
        so = Hout[:, rng.integers(0, n_out, n_out)].mean(1)
        lifts[b] = (si + .01) / (so + .01)
    return lifts


def _split_job(sdb_tr, sdb_ho, sdb_out, rel_sup, max_len, max_cand, min_len):
    cands = [p for p, _ in mine_candidates(sdb_tr, rel_sup, max_len, max_cand, min_len)]
    sdb = sdb_ho + sdb_out
    mask = np.arange(len(sdb)) < len(sdb_ho)
    return v2_discriminative(mask, cands, sdb, rel_sup)


def v2_solid_counts(db, comp, comps, motifs, cfg, n_jobs=1, B=1000, seeds=(1, 2, 3, 4, 5), n_out=1500, min_lift=2):
    """Re-run v2 sections 2b (bootstrap on fixed candidates + 5 split seeds with mining) and count 'solid' motifs per component."""
    from joblib import Parallel, delayed
    m = cfg["mining"]
    boot = {}
    for c in comps:
        d = motifs[c].copy()
        if len(d):
            cand = [tuple(p.split(" -> ")) for p in d.pattern]
            idx_in = np.flatnonzero(comp == c)
            idx_out = np.flatnonzero(comp != c)
            idx_out = np.random.default_rng(0).choice(idx_out, min(n_out, len(idx_out)), replace=False)
            sdb = [db[i] for i in np.concatenate([idx_in, idx_out])]
            Hm = np.array([[contains(s, p) for s in sdb] for p in cand], dtype=bool)
            L = _bootstrap_lift(Hm, len(idx_in), B)
            d["lift_lo"], d["lift_hi"] = np.percentile(L, [2.5, 97.5], axis=0).round(1)
        boot[c] = d
    keys, jobs = [], []
    for c in sorted(comps, key=lambda c: -int((comp == c).sum())):
        idx_in, idx_out = np.flatnonzero(comp == c), np.flatnonzero(comp != c)
        for s in seeds:
            rng = np.random.default_rng(s)
            perm = rng.permutation(idx_in)
            tr, ho = perm[:len(perm) // 2], perm[len(perm) // 2:]
            out = rng.choice(idx_out, min(n_out, len(idx_out)), replace=False)
            keys.append((c, s))
            jobs.append(delayed(_split_job)([db[i] for i in tr], [db[i] for i in ho], [db[i] for i in out],
                                            m["rel_sup"], m["max_len"], m["max_cand"], m["min_len"]))
    splits = dict(zip(keys, Parallel(n_jobs=n_jobs)(jobs)))
    solid, motif_n = {}, {}
    for c in comps:
        d = boot[c]
        motif_n[c] = len(d)
        if not len(d):
            solid[c] = 0
            continue
        found = collections.Counter(p for s in seeds for p in splits[(c, s)].loc[splits[(c, s)].lift >= min_lift, "pattern"])
        sf = d.pattern.map(lambda p: found.get(p, 0))
        solid[c] = int(((sf >= 4) & (d.lift_lo >= min_lift)).sum())
    return solid, motif_n
