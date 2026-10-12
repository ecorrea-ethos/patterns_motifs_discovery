"""Held-out pass rate, family clustering, same-day flag and the hybrid verdict, lifted unchanged from the Day 3 notebooks (sections 2c).

Two entry points because the two cohorts mine differently:
  add_heldout_letrozole : rows = bootstrap-scored motifs (section 2b), `hits` = their hit matrices, writes `hybrid_verdict`.
  add_heldout_chestpain : rows = mined motifs (no bootstrap), writes `holdout_verdict`.
Both mutate and return `rows` (component -> DataFrame) and also return `ho_runs` (component -> family pass matrix, kept for plots).
"""
import numpy as np

from .families import cluster_families, family_any
from .scoring import bh_fdr, or_ci, score_hits
from .seqindex import hit_matrix
from .stability import rate_ci, split_halves


def add_heldout_letrozole(rows, comp, patseqs, hits, n_in, *, rel_sup, ho_seeds, ho_min_or, ho_min_rate_lo, fam_dist,
                          same_day_ratio, min_lift):
    ho_runs, _fisher = {}, []
    for c in rows:
        d = rows[c]
        if not len(d):
            continue
        pats    = [tuple(p.split(' -> ')) for p in d.pattern]
        in_idx  = np.flatnonzero(comp == c)
        out_idx = np.flatnonzero(comp != c)
        Ht      = hit_matrix(patseqs, pats, 'tie_ordered')                       # all patients x motifs, v2 matching
        assert np.allclose(Ht[:, in_idx].mean(1), d.sup_in.to_numpy(), atol=1e-3), "hit matrix disagrees with v2 sup_in"
        sc      = score_hits(Ht, comp == c)
        fam, reps, _ = cluster_families(Ht[:, in_idx], pats, sc.log_or.to_numpy(), fam_dist)

        # (a) held-out pass: lower OR bound >= ho_min_or vs ALL outside patients, on the half not used
        a_all = np.zeros((len(pats), len(ho_seeds), 2), bool)
        # (b) same runs, v2's rule vs the fixed 1,500 outside sample (hits[c] columns = in-component | sample)
        b_all = np.zeros_like(a_all)
        Hin, Hout = hits[c][:, :n_in[c]], hits[c][:, n_in[c]:]
        so = Hout.mean(1)
        for si, s in enumerate(ho_seeds):
            A, B = split_halves(in_idx, s)
            pa, pb = split_halves(np.arange(n_in[c]), s)
            for k, (test, test_pos) in enumerate(((B, pb), (A, pa))):
                n1, n2 = len(test), len(out_idx)
                hit_in, hit_out = Ht[:, test].sum(1), Ht[:, out_idx].sum(1)
                _, lo, _ = or_ci(hit_in, n1, hit_out, n2)
                a_all[:, si, k] = (hit_in / n1 >= rel_sup) & (lo >= np.log(ho_min_or))
                sup_h = Hin[:, test_pos].mean(1)
                b_all[:, si, k] = (sup_h >= rel_sup) & ((sup_h + .01) / (so + .01) >= min_lift)
        fa, fb = a_all.reshape(len(pats), -1), b_all.reshape(len(pats), -1)
        fam_a, fam_b = family_any(fa, fam), family_any(fb, fam)
        r,  lo,  hi  = rate_ci(fa);      fr,  flo,  fhi  = rate_ci(fam_a)
        r2, lo2, hi2 = rate_ci(fb);      fr2, flo2, fhi2 = rate_ci(fam_b)
        Hs = hit_matrix([patseqs[i] for i in in_idx], pats, 'strict_date')       # strictly later dates, in-component only
        d['holdout_rate'], d['holdout_rate_lo'], d['holdout_rate_hi'] = r.round(3), lo.round(3), hi.round(3)
        d['fam_id']            = fam
        d['fam_holdout_rate']  = fr.round(3); d['fam_holdout_rate_lo'] = flo.round(3); d['fam_holdout_rate_hi'] = fhi.round(3)
        d['holdout_rate_v2rule'], d['fam_holdout_rate_v2rule'] = r2.round(3), fr2.round(3)
        d['sup_in_strict']     = Hs.mean(1).round(3)
        d['same_day_bundle']   = d.sup_in_strict < same_day_ratio * d.sup_in
        d['log_or']            = sc.log_or.round(2).to_numpy()
        d['fisher_p']          = sc.fisher_p.to_numpy()
        d['is_family_rep']     = [reps[int(f)] == i for i, f in enumerate(fam)]
        ho_runs[c] = fam_a
        _fisher.append(d.fisher_p.to_numpy())
    q = bh_fdr(np.concatenate(_fisher)); k = 0
    for c in rows:
        if len(rows[c]):
            rows[c]['q_fisher'] = q[k:k + len(rows[c])].round(4); k += len(rows[c])
            d = rows[c]
            d['hybrid_verdict'] = np.where((d.verdict == 'solid') & (d.fam_holdout_rate_lo < ho_min_rate_lo), 'suggestive', d.verdict)
    return rows, ho_runs


def add_heldout_chestpain(motifs, comp, patseqs, *, rel_sup, ho_seeds, ho_min_or, ho_min_rate_lo, fam_dist, same_day_ratio):
    rows, ho_runs, _fisher = {c: motifs[c].copy() for c in motifs}, {}, []
    for c in rows:
        d = rows[c]
        if not len(d):
            continue
        pats    = [tuple(p.split(' -> ')) for p in d.pattern]
        in_idx  = np.flatnonzero(comp == c)
        out_idx = np.flatnonzero(comp != c)
        Ht      = hit_matrix(patseqs, pats, 'tie_ordered')                       # all patients x motifs, v2 matching
        sc      = score_hits(Ht, comp == c)
        assert np.abs(sc.sup_in.to_numpy() - d.sup_in.to_numpy()).max() < 0.06, "full-component support far from the mining sample's"
        fam, reps, _ = cluster_families(Ht[:, in_idx], pats, sc.log_or.to_numpy(), fam_dist)
        passes = np.zeros((len(pats), len(ho_seeds), 2), bool)
        for si, s in enumerate(ho_seeds):
            A, B = split_halves(in_idx, s)
            for k, test in enumerate((B, A)):
                hit_in, hit_out = Ht[:, test].sum(1), Ht[:, out_idx].sum(1)
                _, lo, _ = or_ci(hit_in, len(test), hit_out, len(out_idx))
                passes[:, si, k] = (hit_in / len(test) >= rel_sup) & (lo >= np.log(ho_min_or))
        flat = passes.reshape(len(pats), -1)
        fam_pass = family_any(flat, fam)
        r, lo, hi = rate_ci(flat); fr, flo, fhi = rate_ci(fam_pass)
        Hs = hit_matrix([patseqs[i] for i in in_idx], pats, 'strict_date')       # strictly later dates, in-component only
        d['sup_in_full']       = sc.sup_in.round(3).to_numpy()
        d['holdout_rate'], d['holdout_rate_lo'], d['holdout_rate_hi'] = r.round(3), lo.round(3), hi.round(3)
        d['fam_id']            = fam
        d['fam_holdout_rate']  = fr.round(3); d['fam_holdout_rate_lo'] = flo.round(3); d['fam_holdout_rate_hi'] = fhi.round(3)
        d['sup_in_strict']     = Hs.mean(1).round(3)
        d['same_day_bundle']   = d.sup_in_strict < same_day_ratio * d.sup_in_full
        d['log_or']            = sc.log_or.round(2).to_numpy()
        d['fisher_p']          = sc.fisher_p.to_numpy()
        d['is_family_rep']     = [reps[int(f)] == i for i, f in enumerate(fam)]
        d['holdout_verdict']   = np.where(d.fam_holdout_rate_lo >= ho_min_rate_lo, 'holds', 'weak')
        ho_runs[c] = fam_pass
        _fisher.append(d.fisher_p.to_numpy())
    q = bh_fdr(np.concatenate(_fisher)); k = 0
    for c in rows:
        if len(rows[c]):
            rows[c]['q_fisher'] = q[k:k + len(rows[c])].round(4); k += len(rows[c])
    return rows, ho_runs
