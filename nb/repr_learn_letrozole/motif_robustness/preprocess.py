"""Cohort loading and dated sequences. Reuses ethos_omop loaders; changes none of them."""
import os

import numpy as np
import pandas as pd

from .seqindex import PatientSeq

DOMAINS = ["Visit", "Condition", "Drug", "Procedure", "Measurement"]

# NMF group labels (same as Day3_prefixspan_v2 COMP): fertility c0+c2+c4+c7, oncology c5, background c1+c3+c6
FERT, ONCO, BG = "fertility", "oncology", "background"
COMP = {0: ("pregnancy_outcome", "pregnancy outcome", FERT),
        1: ("amoxicillin_875", "acute-infection pharmacy", BG),
        2: ("gonadotropin_drug", "fertility treatment", FERT),
        3: ("lipid_panel", "preventive labs", BG),
        4: ("cftr", "preconception carrier screening", FERT),
        5: ("ondansetron_injectio", "peri-operative / oncology", ONCO),
        6: ("therapeutic_procedur", "therapeutic / manual procedures", BG),
        7: ("abo_typing", "prenatal labs (ABO / Rh)", FERT)}


def load_pruned_events(extract_dir, token_level="group"):
    """Same load + visit pruning + tagging as Day3_prefixspan_v2 cell 1. Returns events, person, concept, codesets.

    token_level="concept" gives every event its own concept-level token (curated groups stay in `events.group`).
    """
    import ethos_omop as eo
    concept = eo.load_concept(extract_dir)
    codesets = eo.build_codesets(concept, verbose=False)
    raw = eo.load_events(extract_dir, domains=DOMAINS)
    person = eo.load_person(extract_dir)
    is_visit = (raw["domain"].astype(str).str.lower().eq("visit")
                | raw["vocabulary_id"].astype(str).str.lower().eq("visit"))
    events = eo.tag_events(raw[~is_visit].reset_index(drop=True), codesets, token_level=token_level)
    return events, person, concept, codesets


def sequences_with_dates(events, col="tag", dedup_same_day=True, collapse_repeats=True):
    """person_id -> (tokens, day_numbers). Same dedup / collapse rules as eo.sequences; a collapsed run keeps its FIRST date.

    Relies on `events` being sorted by (person_id, event_date, domain order, concept_id), which eo.load_events guarantees.
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


def build_patient_seqs(events):
    """dict pid -> PatientSeq (sorted pids list returned separately)."""
    raw = sequences_with_dates(events)
    pids = sorted(raw)
    return pids, {p: PatientSeq(*raw[p]) for p in pids}


def first_letrozole_day(events):
    """pid -> day number of first letrozole event (the index date; proxy for decision time)."""
    col = "group" if "group" in events.columns else "tag"          # curated group name, whatever the token level
    lz = events[events[col] == "letrozole"].groupby("person_id")["event_date"].min()
    return pd.Series(lz.to_numpy().astype("datetime64[D]").astype("int64"), index=lz.index)


def truncate_before(ps, idx_day):
    """New PatientSeq with only events strictly before idx_day (pre-index / decision-time proxy)."""
    keep = ps.dates < idx_day
    return PatientSeq([t for t, k in zip(ps.tokens, keep) if k], ps.dates[keep])


def load_components(nmf_cache, events, pids, KEEP_MIN=5, N_TRAIN_CAP=20_000):
    """Component label per patient from the Day 1 NMF cache (fixed; not re-validated here).

    Checks the cache against the current extract (same code columns / patient ids) as the v2 notebook does and raises if stale.
    """
    n_pat = events.person_id.nunique()
    n_train = min(N_TRAIN_CAP, int(0.6 * n_pat))
    min_pat = int(np.ceil(KEEP_MIN * n_pat / n_train))
    prev = events.groupby("tag").person_id.nunique()
    anchor = events.loc[events["group"] == "letrozole", "tag"].unique() if "group" in events.columns else ["letrozole"]
    nmf_cols = prev.index[(prev >= min_pat) & ~prev.index.isin(anchor)]       # drop EVERY token of the anchor group
    z = np.load(nmf_cache)
    if set(z["cols"]) != set(nmf_cols) or set(z["pids"]) != set(events.person_id.unique()):
        raise RuntimeError(f"{nmf_cache} is stale for this extract; refit it with the matching Day1_nmf notebook (columns or patient ids differ)")
    H = pd.DataFrame(z["H"], columns=z["cols"])
    lab = pd.Series(z["labels"], index=z["pids"])
    comp = lab.reindex(pids).fillna(-1).astype(int).to_numpy()
    return comp, H


def confirmed_breast_cancer_ids(extract_dir):
    """Confirmed dx: ICD-9 174.x, ICD-10 C50.x (condition_source_value) or SNOMED concept_id 4162253 (Table 1 rule)."""
    cond = pd.read_csv(os.path.join(extract_dir, "master_condition_occurrence.csv"),
                       usecols=["person_id", "condition_concept_id", "condition_source_value"],
                       dtype={"condition_source_value": str})
    src = cond["condition_source_value"].fillna("").str.upper().str.replace(".", "", regex=False)
    m = src.str.startswith("174") | src.str.startswith("C50") | cond["condition_concept_id"].eq(4162253)
    return set(cond.loc[m, "person_id"])
