"""Held-out validation: repeated split-half, out-of-time, pre-index (decision-time proxy).

All tiers score the FULL-RUN motifs directly on patients that were not used (`holds_out`), which removes the dependence on the
candidate cutoff; the split-half tier also reports v2's `rediscovered` (nominated by mining the train half AND passing on test).
"""
import numpy as np
import pandas as pd

from .mining import mine_candidates
from .scoring import Z, or_ci, wilson


def split_halves(in_idx, seed):
    """Random 50/50 split of the component's patient indices. Returns (A, B)."""
    perm = np.random.default_rng(seed).permutation(in_idx)
    h = len(perm) // 2
    return perm[:h], perm[h:]


def passes(H, test_in, out_idx, rel_sup, min_or):
    """Does each motif (rows of H) pass on `test_in` vs `out_idx`? support floor AND log_or_lo >= log(min_or)."""
    n1, n2 = len(test_in), len(out_idx)
    if n1 == 0 or n2 == 0:
        z = np.zeros(H.shape[0], bool)
        return z, np.full(H.shape[0], np.nan), np.full(H.shape[0], np.nan), np.full(H.shape[0], np.nan), np.zeros(H.shape[0])
    a, c = H[:, test_in].sum(1), H[:, out_idx].sum(1)
    lor, lo, hi = or_ci(a, n1, c, n2)
    sup = a / n1
    return (sup >= rel_sup) & (lo >= np.log(min_or)), lor, lo, hi, sup


def holdout_matrix(H, in_idx, out_idx, seeds, rel_sup, min_or):
    """bool (n_motifs, n_seeds, 2): motif passes on the held-out half. [..., 0] test=B (train A); [..., 1] test=A (train B)."""
    out = np.zeros((H.shape[0], len(seeds), 2), bool)
    for si, s in enumerate(seeds):
        A, B = split_halves(in_idx, s)
        out[:, si, 0] = passes(H, B, out_idx, rel_sup, min_or)[0]
        out[:, si, 1] = passes(H, A, out_idx, rel_sup, min_or)[0]
    return out


def _mine_half(tokens_train, rel_sup, max_len, max_cand, min_len):
    return {p for p, _ in mine_candidates(tokens_train, rel_sup, max_len, max_cand, min_len)}


def nominated_sets(token_lists, in_idx, seeds, rel_sup, max_len, max_cand, min_len, n_jobs=1):
    """For each (seed, direction) mine the TRAIN half and return the set of nominated patterns. Order: seed-major, direction 0 then 1."""
    from joblib import Parallel, delayed
    jobs, keys = [], []
    for s in seeds:
        A, B = split_halves(in_idx, s)
        for d, train in ((0, A), (1, B)):
            keys.append((s, d))
            jobs.append(delayed(_mine_half)([token_lists[i] for i in train], rel_sup, max_len, max_cand, min_len))
    res = Parallel(n_jobs=n_jobs)(jobs) if n_jobs != 1 else [j[0](*j[1], **j[2]) for j in jobs]
    return dict(zip(keys, res))


def rediscovery_matrix(patterns, holds, nominated, seeds):
    """bool (n_motifs, n_seeds, 2): motif nominated on the train half AND passes on the test half."""
    out = np.zeros_like(holds)
    for si, s in enumerate(seeds):
        for d in (0, 1):
            nom = nominated[(s, d)]
            out[:, si, d] = np.array([p in nom for p in patterns]) & holds[:, si, d]
    return out


def rate_ci(bool_matrix):
    """Per-motif rate over all (seed, direction) evaluations with Wilson 95% CI. bool_matrix: (n_motifs, ...)."""
    flat = bool_matrix.reshape(bool_matrix.shape[0], -1)
    k, n = flat.sum(1), flat.shape[1]
    lo, hi = wilson(k, n)
    return k / n, lo, hi


def oot_split(index_day, quantile):
    """Boolean train mask per patient (aligned with index_day Series): first-letrozole date <= quantile of the cohort."""
    cut = index_day.quantile(quantile)
    return (index_day <= cut), cut


def oot_eval(H, in_idx, out_idx, train_mask, rel_sup, min_or):
    """Score full-run motifs on test-period patients only. train_mask: bool over ALL patients (aligned with H columns)."""
    test = ~np.asarray(train_mask, bool)
    in_t = np.intersect1d(in_idx, np.flatnonzero(test))
    out_t = np.intersect1d(out_idx, np.flatnonzero(test))
    holds, lor, lo, hi, sup = passes(H, in_t, out_t, rel_sup, min_or)
    return {"oot_holds": holds, "oot_log_or": lor, "oot_log_or_lo": lo, "oot_log_or_hi": hi, "oot_sup_in": sup,
            "oot_n_in": len(in_t), "oot_n_out": len(out_t)}


def pre_index_eval(H_pre, in_idx, out_idx, min_sup, min_or):
    """Score full-run motifs on sequences truncated to events strictly before first letrozole (decision-time proxy)."""
    holds, lor, lo, hi, sup = passes(H_pre, in_idx, out_idx, min_sup, min_or)
    return {"pre_index_holds": holds, "pre_index_log_or": lor, "pre_index_log_or_lo": lo, "pre_index_log_or_hi": hi,
            "pre_index_sup_in": sup}
