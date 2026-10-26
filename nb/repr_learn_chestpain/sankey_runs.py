"""Sankey of patient flow between the bundles of two NMF runs (same cohort, same patients).

usage (conda env ethos_llm, cwd = nb/repr_learn_chestpain/):
    python sankey_runs.py                       # AHA k=8 vs full k=8 and vs full k=5, writes outputs/sankey_*.png
    python sankey_runs.py LEFT RIGHT            # run labels as in nmf_k{K}_chestpain_{label}.npz, e.g. AHA full_k8

Left = first run, one node per bundle, height = patients. Band = patients that sit in bundle i of the left run and bundle j of the right
run; its colour is the left bundle. Right nodes are ordered by the weighted mean position of their left bundles, to cut crossings.
Names come from the DESCR block saved in nmf_k{K}_chestpain_{label}_components.json (text before the first bracket).
"""
import json, os, sys, textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

HERE = os.path.dirname(os.path.abspath(__file__))
# label -> (file stem, display name, short tag for the output file name)
RUNS = {"AHA":     ("nmf_k8_chestpain_AHA",      "AHA k=8 (group tokens, codeset v2)",    "AHA_k8"),
        "full_k8": ("nmf_k8_chestpain_full_k8",  "full k=8 (concept tokens, codeset v1)", "full_k8"),
        "full":    ("nmf_k5_chestpain_full",     "full k=5 (concept tokens, codeset v1)", "full_k5")}
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#17becf"]


def load(label):
    stem, shown, tag = RUNS[label]
    z = np.load(os.path.join(HERE, stem + ".npz"), allow_pickle=True)
    comps = json.load(open(os.path.join(HERE, stem + "_components.json")))["components"]
    names = {int(c): (d.get("name") or f"bundle {c}").split(" (")[0] for c, d in comps.items()}
    return dict(pids=z["pids"], labels=z["labels"], names=names, shown=shown, tag=tag, k=int(z["labels"].max()) + 1)


def smooth(t):
    return 3 * t ** 2 - 2 * t ** 3


def sankey(left, right, out):
    a, b = pd.Series(left["labels"], index=left["pids"]), pd.Series(right["labels"], index=right["pids"])
    pids = a.index.intersection(b.index)
    li, ri = a.loc[pids].to_numpy(), b.loc[pids].to_numpy()
    n = len(pids)
    ct = np.zeros((left["k"], right["k"]), dtype=int)
    np.add.at(ct, (li, ri), 1)
    ari, nmi = adjusted_rand_score(li, ri), normalized_mutual_info_score(li, ri)

    lorder = list(range(left["k"]))
    pos = {i: p for p, i in enumerate(lorder)}
    bary = {j: (ct[:, j] * np.array([pos[i] for i in range(left["k"])])).sum() / max(ct[:, j].sum(), 1) for j in range(right["k"])}
    rorder = sorted(range(right["k"]), key=lambda j: bary[j])

    gap = 0.018 * n
    def stack(sizes, order):
        y, out_ = 0.0, {}
        for i in order:
            out_[i] = y; y += sizes[i] + gap
        return out_, y - gap
    ly, lh = stack(ct.sum(1), lorder)
    ry, rh = stack(ct.sum(0), rorder)
    H = max(lh, rh)
    lo, ro = (H - lh) / 2, (H - rh) / 2                      # centre the shorter column

    fig, ax = plt.subplots(figsize=(15, 9))
    W = 0.018
    lcur = {i: ly[i] + lo for i in lorder}
    rcur = {j: ry[j] + ro for j in rorder}
    t = np.linspace(0, 1, 60)
    for i in lorder:                                        # bands, drawn per left node, ordered by right position
        for j in rorder:
            v = ct[i, j]
            if v == 0:
                continue
            a0, b0 = lcur[i], rcur[j]
            lcur[i] += v; rcur[j] += v
            top = a0 + (b0 - a0) * smooth(t)
            bot = (a0 + v) + (b0 - a0) * smooth(t)
            ax.fill_between(W + (1 - 2 * W) * t, top, bot, color=COLORS[i % len(COLORS)], alpha=0.45, lw=0)
            if v >= 0.03 * n:                               # label the big flows at the left end of the band, where bands do not cross
                k_ = 7
                ax.text(W + (1 - 2 * W) * t[k_] + 0.005, (top[k_] + bot[k_]) / 2, f"{v:,} ({v / ct[i].sum():.0%} of c{i})", ha="left", va="center", fontsize=8, color="#111")
    for order, start, x, sizes, run, side in ((lorder, ly, 0.0, ct.sum(1), left, "l"), (rorder, ry, 1.0 - W, ct.sum(0), right, "r")):
        off = lo if side == "l" else ro
        for i in order:
            y0 = start[i] + off
            ax.add_patch(Rectangle((x, y0), W, sizes[i], color=COLORS[i % len(COLORS)] if side == "l" else "#6b7280", lw=0))
            name = "\n".join(textwrap.wrap(run["names"].get(i, f"bundle {i}"), 38))
            txt = f"c{i} · {name}\n{sizes[i]:,} ({sizes[i] / n:.1%})"
            ax.text(x - 0.012 if side == "l" else x + W + 0.012, y0 + sizes[i] / 2, txt, ha="right" if side == "l" else "left", va="center", fontsize=8.5)
    ax.set_xlim(-0.42, 1.42); ax.set_ylim(H + 0.02 * n, -0.02 * n); ax.axis("off")
    fig.suptitle(f"{left['shown']}  →  {right['shown']}", fontsize=14, fontweight="bold", y=0.97)
    ax.set_title(f"{n:,} patients. Band width = patients in both bundles; colour = {left['shown'].split(' (')[0]} bundle.   ARI {ari:.2f}, NMI {nmi:.2f}",
                 fontsize=10, color="#444")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, dpi=160, facecolor="white")
    plt.close(fig)

    print(f"\n{os.path.basename(out)}: {n:,} patients, ARI {ari:.3f}, NMI {nmi:.3f}")
    print(f"{'left bundle':<48}{'n':>8}  top destination (share of the left bundle) | second")
    for i in lorder:
        r = np.argsort(-ct[i])[:2]
        d = " | ".join(f"c{j} {right['names'].get(j, '')[:30]} {ct[i, j] / ct[i].sum():.0%}" for j in r)
        print(f"c{i} {left['names'].get(i, '')[:44]:<45}{ct[i].sum():>8,}  {d}")
    return ct


if __name__ == "__main__":
    pairs = [tuple(sys.argv[1:3])] if len(sys.argv) >= 3 else [("AHA", "full_k8"), ("AHA", "full")]
    for a, b in pairs:
        L, R = load(a), load(b)
        sankey(L, R, os.path.join(HERE, "outputs", f"sankey_{L['tag']}_vs_{R['tag']}.png"))
