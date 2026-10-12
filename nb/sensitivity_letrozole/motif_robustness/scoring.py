"""Effect sizes with CIs, multiple-testing control. All from 2x2 tables: in/out component x has/has-not the motif.

Outside group = ALL patients not in the component (replaces v2's fixed 1,500 sample).
"""
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

Z = 1.959963984540054


def wilson(k, n, z=Z):
    k, n = np.asarray(k, float), np.asarray(n, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(n > 0, k / n, np.nan)
        den = 1 + z * z / n
        centre = (p + z * z / (2 * n)) / den
        half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return np.clip(centre - half, 0, 1), np.clip(centre + half, 0, 1)


def newcombe_diff(a, n1, c, n2, z=Z):
    """Newcombe (method 10) CI for p1 - p2 from Wilson intervals."""
    p1, p2 = np.asarray(a, float) / n1, np.asarray(c, float) / n2
    l1, u1 = wilson(a, n1, z)
    l2, u2 = wilson(c, n2, z)
    d = p1 - p2
    return d, d - np.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + np.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def log_or(a, n1, c, n2):
    """Haldane-Anscombe (+0.5) log odds ratio and Woolf SE. a, c = motif hits in / out; n1, n2 = group sizes."""
    a, c = np.asarray(a, float), np.asarray(c, float)
    b, d = n1 - a, n2 - c
    lor = np.log((a + .5) * (d + .5) / ((b + .5) * (c + .5)))
    se = np.sqrt(1 / (a + .5) + 1 / (b + .5) + 1 / (c + .5) + 1 / (d + .5))
    return lor, se


def or_ci(a, n1, c, n2, z=Z):
    lor, se = log_or(a, n1, c, n2)
    return lor, lor - z * se, lor + z * se


def fisher_greater(a, n1, c, n2):
    """One-sided (enrichment in the component) Fisher exact p-values."""
    return np.array([fisher_exact([[int(x), int(n1 - x)], [int(y), int(n2 - y)]], alternative="greater")[1]
                     for x, y in zip(np.atleast_1d(a), np.atleast_1d(c))])


def bh_fdr(p):
    """Benjamini-Hochberg q-values (NaN-safe: NaN stays NaN)."""
    p = np.asarray(p, float)
    q = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    m = len(pv)
    if m == 0:
        return q
    order = np.argsort(pv, kind="mergesort")
    ranked = pv[order] * m / (np.arange(m) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.clip(ranked, 0, 1)
    q[ok] = out
    return q


def score_hits(H, in_mask):
    """H: bool (n_motifs, N_patients); in_mask: bool (N,). Returns DataFrame of effect sizes for each motif row."""
    in_mask = np.asarray(in_mask, bool)
    n1, n2 = int(in_mask.sum()), int((~in_mask).sum())
    a, c = H[:, in_mask].sum(1), H[:, ~in_mask].sum(1)
    sin_lo, sin_hi = wilson(a, n1)
    sout_lo, sout_hi = wilson(c, n2)
    rd, rd_lo, rd_hi = newcombe_diff(a, n1, c, n2)
    lor, lo, hi = or_ci(a, n1, c, n2)
    return pd.DataFrame({
        "n_in": n1, "n_out": n2, "hits_in": a, "hits_out": c,
        "sup_in": a / n1, "sup_in_lo": sin_lo, "sup_in_hi": sin_hi,
        "sup_out": c / n2, "sup_out_lo": sout_lo, "sup_out_hi": sout_hi,
        "risk_diff": rd, "risk_diff_lo": rd_lo, "risk_diff_hi": rd_hi,
        "log_or": lor, "log_or_lo": lo, "log_or_hi": hi,
        "lift_v2": (a / n1 + .01) / (c / n2 + .01),               # v2 pseudo-count lift, kept for continuity only
        "ppv_for_component": np.where(a + c > 0, a / np.maximum(a + c, 1), np.nan),
        "sens_for_component": a / n1,
        "fisher_p": fisher_greater(a, n1, c, n2),
    })


def label_permutation_fwer(H, in_mask, b_perm=1000, seed=0, chunk=250):
    """Family-wise p per motif: share of label permutations (group sizes kept) whose MAX log OR over all candidates >= observed.

    Candidates stay fixed (no re-mining under the null); documented limitation.
    """
    in_mask = np.asarray(in_mask, bool)
    N, n1 = H.shape[1], int(in_mask.sum())
    n2 = N - n1
    Hf = H.astype(np.float32)
    total = Hf.sum(1)[:, None]
    obs, _ = log_or(H[:, in_mask].sum(1), n1, H[:, ~in_mask].sum(1), n2)
    rng = np.random.default_rng(seed)
    max_null = np.empty(b_perm)
    done = 0
    while done < b_perm:
        b = min(chunk, b_perm - done)
        R = rng.random((N, b))
        idx = np.argpartition(R, n1 - 1, axis=0)[:n1]
        ind = np.zeros((N, b), dtype=np.float32)
        np.put_along_axis(ind, idx, 1.0, axis=0)
        a_null = Hf @ ind
        lor_null, _ = log_or(a_null, n1, total - a_null, n2)
        max_null[done:done + b] = lor_null.max(0)
        done += b
    p = (1 + (max_null[None, :] >= obs[:, None]).sum(1)) / (1 + b_perm)
    return p, max_null
