"""Fast, date-aware subsequence matching.

Three semantics (all deterministic, all greedy-earliest, which is exact for subsequence containment):
  tie_ordered : v2 `contains` -- steps in sequence order; same-day steps are ordered by the DOMAIN_ORDER tie-break
  strict_date : each step must fall on a strictly LATER calendar date than the previous step
  windowed    : strict_date and the last step is within `max_span_days` of the first step
"""
from bisect import bisect_right

import numpy as np


class PatientSeq:
    """Tokens + integer day numbers (non-decreasing) + per-token position / date lists for bisect."""
    __slots__ = ("tokens", "dates", "pos", "dpos")

    def __init__(self, tokens, dates):
        self.tokens = list(tokens)
        self.dates = np.asarray(dates, dtype=np.int64)
        if len(self.tokens) != len(self.dates):
            raise ValueError("tokens and dates differ in length")
        if len(self.dates) > 1 and (np.diff(self.dates) < 0).any():
            raise ValueError("dates must be non-decreasing")
        pos = {}
        for i, t in enumerate(self.tokens):
            pos.setdefault(t, []).append(i)
        dl = self.dates.tolist()
        self.pos = pos
        self.dpos = {t: [dl[i] for i in p] for t, p in pos.items()}


def match_tie(ps, pat):
    cur = -1
    for t in pat:
        p = ps.pos.get(t)
        if p is None:
            return False
        k = bisect_right(p, cur)
        if k == len(p):
            return False
        cur = p[k]
    return True


def match_strict(ps, pat):
    cur = None
    for t in pat:
        d = ps.dpos.get(t)
        if d is None:
            return False
        if cur is None:
            cur = d[0]
            continue
        k = bisect_right(d, cur)
        if k == len(d):
            return False
        cur = d[k]
    return True


def match_windowed(ps, pat, max_span):
    starts = ps.dpos.get(pat[0])
    if starts is None:
        return False
    for d0 in starts:
        cur, ok = d0, True
        for t in pat[1:]:
            d = ps.dpos.get(t)
            if d is None:
                return False
            k = bisect_right(d, cur)
            if k == len(d):
                ok = False
                break
            cur = d[k]
            if cur - d0 > max_span:
                ok = False
                break
        if ok:
            return True
    return False


def matches(ps, pat, semantics="strict_date", max_span=365):
    if semantics == "tie_ordered":
        return match_tie(ps, pat)
    if semantics == "strict_date":
        return match_strict(ps, pat)
    if semantics == "windowed":
        return match_windowed(ps, pat, max_span)
    raise ValueError(f"unknown semantics {semantics!r}")


def hit_matrix(patseqs, patterns, semantics="strict_date", max_span=365):
    """bool array (len(patterns), len(patseqs)); patseqs is an ordered list of PatientSeq."""
    H = np.zeros((len(patterns), len(patseqs)), dtype=bool)
    for j, ps in enumerate(patseqs):
        pos = ps.pos
        for i, pat in enumerate(patterns):
            if all(t in pos for t in pat) and matches(ps, pat, semantics, max_span):
                H[i, j] = True
    return H
