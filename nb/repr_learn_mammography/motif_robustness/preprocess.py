"""Dated sequences: tokens + the day each token first occurred. Same dedup / collapse rules as ethos_omop.sequences()."""
import numpy as np

from .seqindex import PatientSeq


def sequences_with_dates(events, col="tag", dedup_same_day=True, collapse_repeats=True):
    """person_id -> (tokens, day_numbers). A collapsed run keeps its FIRST date.

    Relies on `events` being sorted by (person_id, event_date, domain order, concept_id), which eo.load_events guarantees
    (filtering rows keeps that order).
    """
    ev = events
    if dedup_same_day:
        ev = ev.drop_duplicates(["person_id", "event_date", col])
    pid = ev["person_id"].to_numpy()
    tok = ev[col].to_numpy()
    day = ev["event_date"].to_numpy().astype("datetime64[D]").astype("int64")
    bounds = np.flatnonzero(np.r_[True, pid[1:] != pid[:-1], True])
    out = {}
    for s, e in zip(bounds[:-1], bounds[1:]):
        toks, dts, prev = [], [], None
        for t, d in zip(tok[s:e], day[s:e]):
            if not collapse_repeats or t != prev:
                toks.append(t)
                dts.append(d)
            prev = t
        out[pid[s]] = (toks, np.asarray(dts, dtype=np.int64))
    return out


def build_patient_seqs(events, col="tag"):
    """(sorted pids, list of PatientSeq aligned with them)."""
    raw = sequences_with_dates(events, col=col)
    pids = sorted(raw)
    return pids, [PatientSeq(*raw[p]) for p in pids]
