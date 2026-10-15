"""Motif families: near-duplicate motifs (same patients, one extra step) are one finding, not several."""
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist


def cluster_families(H_in, patterns, log_or, dist=0.2):
    """H_in: bool (n_motifs, n_in_patients) coverage of each motif among the component's patients.

    Returns (family_id int array 1..F, representative index per family, dict fid -> member indices).
    Average-linkage on Jaccard distance; representative = shortest, then highest log OR, then lexical pattern.
    """
    n = H_in.shape[0]
    if n == 0:
        return np.array([], int), {}, {}
    if n == 1:
        fam = np.array([1])
    else:
        D = pdist(H_in.astype(bool), "jaccard")
        D = np.nan_to_num(D, nan=0.0)                     # two all-zero rows are identical
        fam = fcluster(linkage(D, "average"), t=dist, criterion="distance")
    reps, members = {}, {}
    for f in np.unique(fam):
        idx = np.flatnonzero(fam == f)
        members[int(f)] = idx.tolist()
        reps[int(f)] = int(min(idx, key=lambda i: (len(patterns[i]), -log_or[i], patterns[i])))
    return fam, reps, members


def family_any(member_matrix, fam):
    """member_matrix: bool (n_motifs, n_eval). Family-level 'found' = any member found, broadcast back per motif."""
    out = np.zeros_like(member_matrix, dtype=bool)
    for f in np.unique(fam):
        idx = np.flatnonzero(fam == f)
        out[idx] = member_matrix[idx].any(0)
    return out
