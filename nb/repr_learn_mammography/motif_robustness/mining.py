"""PrefixSpan (moved from the v2 notebook) with deterministic ties.

v2 iterated `Counter.items()` built from `set(seq)`, so result ORDER depended on PYTHONHASHSEED and the "top max_cand by support"
cut was arbitrary among ties. Here every sort has the pattern as a secondary key, so output is identical across runs.
"""
import collections

import pandas as pd


def prefixspan(db, min_sup, max_len=4):
    """db: list of token lists. Returns DataFrame(pattern tuple, support, support_pct) sorted by (-support, pattern)."""
    n, results = len(db), []

    def scan(projected, prefix):
        counts = collections.Counter()
        for seq in projected:
            for item in set(seq):
                counts[item] += 1
        for item in sorted(counts):                       # deterministic iteration
            c = counts[item]
            if c < min_sup:
                continue
            new_prefix = prefix + [item]
            results.append((tuple(new_prefix), c))
            if len(new_prefix) >= max_len:
                continue
            nxt = [seq[seq.index(item) + 1:] for seq in projected if item in seq]
            if nxt:
                scan(nxt, new_prefix)

    scan([list(s) for s in db], [])
    df = pd.DataFrame(results, columns=["pattern", "support"])
    df["support_pct"] = (df.support / n * 100).round(1) if n else 0.0
    return df.sort_values(["support", "pattern"], ascending=[False, True]).reset_index(drop=True)


def contains(seq, pat):
    """v2 definition (tie-ordered subsequence)."""
    it = iter(seq)
    return all(x in it for x in pat)


def mine_candidates(db, rel_sup=0.15, max_len=4, max_cand=100, min_len=3):
    """Top `max_cand` ordered patterns of >= min_len steps present in >= rel_sup of `db`, deterministic.
    Returns list of (pattern tuple, support count)."""
    pats = prefixspan(db, max(3, int(rel_sup * len(db))), max_len=max_len)
    pats = pats[pats.pattern.map(len) >= min_len].head(max_cand)
    return list(zip(pats.pattern, pats.support))
