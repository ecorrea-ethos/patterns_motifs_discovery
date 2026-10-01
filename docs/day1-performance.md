# Day 1 performance: sparse matrix and parallel sweep

## What this covers
Why the chest pain Day 1 notebook fits NMF on a sparse matrix and runs the k sweep in parallel,
how it was verified, and what is not done yet for the other two cohorts.

## What changed (chest pain Day 1)
- **Sparse copy `Xs`.** The bag of codes is a 0/1 table that is mostly zeros. `Xs` is a
  `scipy.sparse` CSR copy without the anchor column. NMF, SVD (`normalize`, `TruncatedSVD`) and
  `transform` all accept it. The dense `Xv` and the frame `X_nmf` were removed; only the
  column names (`nmf_cols`) and the row count (`n_pat`) are kept.
- **Parallel sweep.** sklearn's NMF uses one core per fit. Every (split, k) job is independent,
  so `joblib.Parallel` runs them on `N_JOBS = cpu_count - 2` workers. The splits are sliced
  once in the main process so each worker receives a small matrix. Large k are started first.
- **Held-out error without a dense product.** The sweep computes
  `||X - WH|| / ||X||` with the identity `||X||^2 - 2*sum((X H^T) * W) + trace((W^T W)(H H^T))`,
  so it never builds the dense reconstruction.
- **Nearest-neighbour demo.** The full-cohort Jaccard/cosine distance in cell 20 densifies the
  matrix 10,000 rows at a time (`dist_to_all`), because sklearn's Jaccard does not accept sparse input.

## Evidence
- Synthetic benchmark (10,000 x 5,000, 1.2% filled, k=10): dense fit 3.3 s, sparse fit 1.4 s
  (2.4x), identical components (max difference 0.0), memory 400 MB versus 7 MB.
- Old dense serial code versus the new sparse parallel code on the same synthetic data: held-out
  error, silhouette, ARI, cosine, unstable and used counts all equal to 12 decimals; the SVD
  output was identical (difference exactly 0.0).
- Real run, chest pain: 24 jobs on 12 workers took 2.2 minutes of wall time; summed fit time was
  21.9 CPU-minutes (about a 10x speedup).

## Gotchas
- Parallel workers need multiprocessing. Inside a restricted sandbox (for example a coding agent's)
  joblib can fail with `PermissionError` on `os.sysconf("SC_SEM_NSEMS_MAX")`. That is the
  sandbox, not the code; run it in Jupyter or outside the sandbox.
- `X` itself is still a dense table (up to about 12 GB at the old 10.8k-column width).
  Only the copies were removed. Lower `N_JOBS` if memory is tight.
- Python's `len()` is ambiguous on a sparse matrix; use `.shape[0]`.

## Not done yet
`nb/repr_learn_breastcancer/` and `nb/repr_learn_letrozole/` still use the dense `Xv`/`X_nmf`
and a serial sweep, and do not have the prevalence-floor or loadings cells. They share the same
code shape, so the same changes should apply. Their cohorts are small (1,704 and 6,103
patients), so speed matters less there. Porting is deferred until their cohort SQL queries
(`sql/breast_cancer_cohort.sql`, `sql/letrozole_cohort.sql`) have been reviewed, since the cohorts
may change. Chest pain's anchor code is 100% by construction (see [README.md](README.md)).
