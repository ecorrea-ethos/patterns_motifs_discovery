"""Split-half helpers shared by the held-out pass-rate code in hybrid.py."""
import numpy as np

from .scoring import wilson


def split_halves(in_idx, seed):
    """Random 50/50 split of a group's patient indices. Returns (A, B)."""
    perm = np.random.default_rng(seed).permutation(in_idx)
    h = len(perm) // 2
    return perm[:h], perm[h:]


def rate_ci(bool_matrix):
    """Per-motif rate over all (seed, direction) evaluations with Wilson 95% CI. bool_matrix: (n_motifs, ...)."""
    flat = bool_matrix.reshape(bool_matrix.shape[0], -1)
    k, n = flat.sum(1), flat.shape[1]
    lo, hi = wilson(k, n)
    return k / n, lo, hi
