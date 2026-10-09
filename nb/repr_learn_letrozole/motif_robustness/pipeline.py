"""Orchestrator for the first three robustness tiers. Run from nb/repr_learn_letrozole/:

    python -m motif_robustness.pipeline --phase0 --jobs 12
    python -m motif_robustness.pipeline --core   --jobs 12 --rediscovery-seeds 20

Everything is deterministic: explicit seeds from config/robustness.yaml, pattern-keyed tie breaks.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import yaml

from . import SEMANTICS
from .evidence_store import EvidenceStore
from .families import cluster_families, family_any
from .manifest import Timer, build_manifest, write_manifest
from .mining import mine_candidates
from .preprocess import (COMP, build_patient_seqs, first_letrozole_day, load_components, load_pruned_events,
                         truncate_before)
from .scoring import bh_fdr, label_permutation_fwer, score_hits
from .seqindex import hit_matrix
from .stability import (holdout_matrix, nominated_sets, oot_eval, oot_split, pre_index_eval, rate_ci,
                        rediscovery_matrix)
from .verdict import provisional_status

# v2 reference numbers (Day3_prefixspan_v2 run at rel_sup=0.15, max_cand=100; see docs plan section Phase 0)
V2_SIZES = {0: 622, 1: 1600, 2: 641, 3: 760, 4: 269, 5: 406, 6: 349, 7: 591}
V2_MOTIFS = {0: 100, 1: 21, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100}
V2_SOLID = {0: 76, 1: 0, 2: 34, 3: 39, 4: 37, 5: 76, 6: 69, 7: 80}


def load_cfg(path="config/robustness.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def prepare(cfg, timer=None):
    """Load once: events, dated patient sequences, component labels (fixed Day 1 v2 NMF), first-letrozole day."""
    t = timer or Timer()
    with t.phase("load_events"):
        events, person, concept, codesets = load_pruned_events(cfg["paths"]["extract_dir"], cfg["paths"].get("token_level", "group"))
    with t.phase("dated_sequences"):
        pids, ps = build_patient_seqs(events)
        patseqs = [ps[p] for p in pids]
    comp, Hnmf = load_components(cfg["paths"]["nmf_cache"], events, pids)
    idx_day = first_letrozole_day(events).reindex(pids)
    if idx_day.isna().any():
        raise RuntimeError("patients without a letrozole index date in the cohort")
    return {"events": events, "person": person, "concept": concept, "pids": pids, "patseqs": patseqs,
            "db": [p.tokens for p in patseqs], "comp": comp, "H_nmf": Hnmf, "index_day": idx_day.to_numpy()}


# ------------------------------------------------------------------------------------------- Phase 0
def run_phase0(prep, cfg, n_jobs=1, timer=None):
    from .regression import v2_component_motifs, v2_solid_counts
    t = timer or Timer()
    comps = sorted(COMP)
    comp = prep["comp"]
    sizes = {c: int((comp == c).sum()) for c in comps}
    with t.phase("phase0_v2_mining"):
        motifs = v2_component_motifs(prep["db"], comp, comps, cfg, n_jobs=n_jobs)
    with t.phase("phase0_v2_stability"):
        solid, motif_n = v2_solid_counts(prep["db"], comp, comps, motifs, cfg, n_jobs=n_jobs)
    rep = {"sizes": sizes, "motifs": motif_n, "solid": solid,
           "diff_vs_v2": {"sizes": {c: sizes[c] - V2_SIZES[c] for c in comps},
                          "motifs": {c: motif_n[c] - V2_MOTIFS[c] for c in comps},
                          "solid": {c: solid[c] - V2_SOLID[c] for c in comps}}}
    return rep, motifs


# ------------------------------------------------------------------------------------------- core tiers
def _rate_cols(prefix, boolm, fam):
    """Motif-level and family-level rate (+ Wilson CI) from bool (n_motifs, n_seeds, 2)."""
    flat = boolm.reshape(boolm.shape[0], -1)
    r, lo, hi = rate_ci(boolm)
    fr, flo, fhi = rate_ci(family_any(flat, fam).reshape(boolm.shape))
    return {f"{prefix}_rate": r, f"{prefix}_rate_lo": lo, f"{prefix}_rate_hi": hi,
            f"fam_{prefix}_rate": fr, f"fam_{prefix}_rate_lo": flo, f"fam_{prefix}_rate_hi": fhi}


def run_core(prep, cfg, n_jobs=1, rediscovery_seeds=None, timer=None):
    t = timer or Timer()
    m, sc, st = cfg["mining"], cfg["scoring"], cfg["stability"]
    primary, span = cfg["matching"]["primary"], cfg["matching"]["max_span_days"]
    seeds = list(range(cfg["seeds"]["split"], cfg["seeds"]["split"] + st["split_seeds"]))
    red_n = st["rediscovery_seeds"] if rediscovery_seeds is None else rediscovery_seeds
    red_seeds = seeds[:red_n]
    comp, db, patseqs = prep["comp"], prep["db"], prep["patseqs"]
    train_mask, cut = oot_split(pd.Series(prep["index_day"]), st["oot_quantile"])
    train_mask = train_mask.to_numpy()
    with t.phase("pre_index_truncation"):
        pre_seqs = [truncate_before(p, d) for p, d in zip(patseqs, prep["index_day"])]
    store, null, frames = EvidenceStore(), {}, []

    from joblib import Parallel, delayed
    order = sorted(COMP, key=lambda c: -int((comp == c).sum()))            # largest first for load balance
    mine = lambda tokens: mine_candidates(tokens, m["rel_sup"], m["max_len"], m["max_cand"], m["min_len"])
    with t.phase("mine_components"):
        cands_all = dict(zip(order, Parallel(n_jobs=n_jobs)(
            delayed(mine)([db[i] for i in np.flatnonzero(comp == c)]) for c in order)))
    with t.phase("mine_oot_train"):
        oot_all = dict(zip(order, Parallel(n_jobs=n_jobs)(
            delayed(mine)([db[i] for i in np.flatnonzero((comp == c) & train_mask)]) for c in order)))

    for c in sorted(COMP):
        in_idx, out_idx = np.flatnonzero(comp == c), np.flatnonzero(comp != c)
        in_mask = comp == c
        patterns = [p for p, _ in cands_all[c]]
        if not patterns:
            continue
        with t.phase(f"c{c}_hits"):
            Hs = {s: hit_matrix(patseqs, patterns, s, span) for s in SEMANTICS}
            H_pre = hit_matrix(pre_seqs, patterns, primary, span)
        Hp = Hs[primary]
        df = score_hits(Hp, in_mask)
        for s in SEMANTICS:
            sc_s = score_hits(Hs[s], in_mask)
            df[f"sup_in_{s}"], df[f"log_or_{s}"] = sc_s["sup_in"], sc_s["log_or"]
        with t.phase(f"c{c}_fwer"):
            df["p_fwer"], null[f"c{c}_max_log_or_null"] = label_permutation_fwer(
                Hp, in_mask, sc["b_perm"], seed=cfg["seeds"]["permutation"] + c)
        fam, reps, members = cluster_families(Hp[:, in_idx], patterns, df.log_or.to_numpy(), cfg["families"]["jaccard_dist"])
        with t.phase(f"c{c}_holdout"):
            holds = holdout_matrix(Hp, in_idx, out_idx, seeds, m["rel_sup"], sc["min_or"])
        cols = _rate_cols("holdout", holds, fam)
        if red_n > 0:
            with t.phase(f"c{c}_rediscovery"):
                nom = nominated_sets(db, in_idx, red_seeds, m["rel_sup"], m["max_len"], m["max_cand"], m["min_len"], n_jobs)
                red = rediscovery_matrix(patterns, holds[:, :red_n, :], nom, red_seeds)
            cols.update(_rate_cols("rediscovery", red, fam))
        else:
            red = None
        with t.phase(f"c{c}_oot"):
            oot = oot_eval(Hp, in_idx, out_idx, train_mask, m["rel_sup"], sc["min_or"])
            oot_nom = {p for p, _ in oot_all[c]}
        pre = pre_index_eval(H_pre, in_idx, out_idx, st["pre_index_min_sup"], sc["min_or"])
        out = pd.DataFrame({
            "component": c, "group": COMP[c][2], "component_name": COMP[c][1], "family_id": fam,
            "is_representative": [reps[int(f)] == i for i, f in enumerate(fam)],
            "pattern": [" -> ".join(p) for p in patterns], "pattern_len": [len(p) for p in patterns],
            "semantics_primary": primary, "small_component": (len(in_idx) // 2) < st["small_half"],
        })
        out = pd.concat([out, df.reset_index(drop=True), pd.DataFrame(cols)], axis=1)
        for k, v in {**oot, **pre}.items():
            out[k] = v
        out["oot_nominated_in_train"] = [p in oot_nom for p in patterns]
        out["usable_at_decision_proxy"] = out["pre_index_holds"]
        frames.append(out)
        for i in range(len(patterns)):
            if out.is_representative[i]:
                f = int(fam[i])
                store.put(c, f, "holdout_pass", holds[i])
                if red is not None:
                    store.put(c, f, "rediscovered", red[i])
                store.put(c, f, "semantics_log_or", [df[f"log_or_{s}"][i] for s in SEMANTICS])

    res = pd.concat(frames, ignore_index=True)
    res["q_fisher"] = bh_fdr(res["fisher_p"].to_numpy())             # BH over ALL component x motif tests
    stat = [provisional_status(r, cfg) for r in res.to_dict("records")]
    res["provisional_status"], res["reasons"] = [s for s, _ in stat], ["; ".join(r) for _, r in stat]
    res = res.sort_values(["component", "family_id", "pattern"]).reset_index(drop=True)
    fams = (res[res.is_representative]
            .assign(n_members=lambda d: [int(((res.component == r.component) & (res.family_id == r.family_id)).sum())
                                         for r in d.itertuples()])
            [["component", "group", "family_id", "pattern", "n_members", "sup_in", "sup_out", "log_or", "log_or_lo",
              "q_fisher", "p_fwer", "fam_holdout_rate", "fam_holdout_rate_lo", "oot_holds", "pre_index_holds",
              "provisional_status", "reasons"]])
    return res, fams, store, null, {"oot_cut_day": int(cut)}


def write_outputs(res, fams, store, null, cfg, timer, extra, out_dir=None):
    out = out_dir or cfg["paths"]["out_dir"]
    os.makedirs(out, exist_ok=True)
    res.to_csv(os.path.join(out, "motif_robustness_core.csv"), index=False)
    fams.to_csv(os.path.join(out, "motif_families_core.csv"), index=False)
    store.save(os.path.join(out, "motif_evidence_core.npz"))
    np.savez_compressed(os.path.join(out, "null_distributions_core.npz"), **null)
    ex = cfg["paths"]["extract_dir"]
    files = [os.path.join(ex, f) for f in ("master_condition_occurrence.csv", "master_drug_exposure.csv",
                                           "master_procedure_occurrence.csv", "master_measurement.csv",
                                           "master_visit_occurrence.csv", "person.csv", "concept.csv")]
    files.append(cfg["paths"]["nmf_cache"])
    write_manifest(os.path.join(out, "run_manifest_core.json"), build_manifest(cfg, files, timer, extra, repo_dir=".."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase0", action="store_true")
    ap.add_argument("--core", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--rediscovery-seeds", type=int, default=None)
    ap.add_argument("--config", default="config/robustness.yaml")
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    cfg, timer = load_cfg(a.config), Timer()
    if a.out_dir:
        cfg["paths"]["out_dir"] = a.out_dir
    prep = prepare(cfg, timer)
    if a.phase0:
        rep, _ = run_phase0(prep, cfg, a.jobs, timer)
        os.makedirs(cfg["paths"]["out_dir"], exist_ok=True)
        with open(os.path.join(cfg["paths"]["out_dir"], "phase0_regression.json"), "w") as f:
            json.dump(rep, f, indent=2, default=str)
        print(json.dumps(rep, indent=2, default=str))
    if a.core:
        res, fams, store, null, extra = run_core(prep, cfg, a.jobs, a.rediscovery_seeds, timer)
        write_outputs(res, fams, store, null, cfg, timer, extra)
        print(res.groupby(["component", "provisional_status"]).size().unstack(fill_value=0))
    print("timings (s):", json.dumps(timer.times))


if __name__ == "__main__":
    main()
