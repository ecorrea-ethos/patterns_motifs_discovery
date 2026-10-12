"""PROVISIONAL tiering using only the checks built so far (effect + FDR/FWER, held-out replication, out-of-time).

The final catalog verdict (spec section 12) needs order, length-confounding and criterion checks, which come later. This file uses
different tier names (`core_*`) so a provisional result cannot be mistaken for a final `catalog_*` verdict.
NMF-label stability is deliberately not a check: the Day 1 v2 NMF is treated as fixed and already validated.
"""
import numpy as np


def provisional_status(row, cfg):
    """row: dict-like with q_fisher, p_fwer, log_or_lo, fam_holdout_rate_lo, oot_holds, same_day... Returns (status, reasons list)."""
    s, st = cfg["scoring"], cfg["stability"]
    min_log = np.log(s["min_or"])
    reasons = []
    ok_q = row["q_fisher"] < s["alpha"]
    if not ok_q:
        reasons.append(f"fdr: q_fisher {row['q_fisher']:.3f} >= {s['alpha']}")
    ok_fwer = row["p_fwer"] < s["alpha"]
    if not ok_fwer:
        reasons.append(f"fwer: p_fwer {row['p_fwer']:.3f} >= {s['alpha']}")
    ok_or = row["log_or_lo"] >= min_log
    if not ok_or:
        reasons.append(f"effect: OR lower CI {np.exp(row['log_or_lo']):.2f} < {s['min_or']}")
    ok_hold = row["fam_holdout_rate_lo"] >= st["min_holdout_rate_lo"]
    if not ok_hold:
        reasons.append(f"holdout: family rate lower CI {row['fam_holdout_rate_lo']:.2f} < {st['min_holdout_rate_lo']}")
    ok_oot = bool(row["oot_holds"])
    if not ok_oot:
        reasons.append("out_of_time: does not hold on later patients")
    if row.get("small_component"):
        reasons.append("small_component: half-size below threshold, split tiers noisy")
    effect_ok = ok_q and ok_fwer and ok_or
    if effect_ok and ok_hold and ok_oot:
        return "core_pass", reasons
    if effect_ok and ok_hold:
        return "core_candidate", reasons
    if ok_q:
        return "exploratory_lead", reasons
    return "reject", reasons
