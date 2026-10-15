"""
ethos_omop.py — extract from ETHOS_PRODUCTION.OMOP_54 and load into the shape the
notebooks expect.

Two halves:

  EXTRACT  (needs Snowflake)   extract_omop()   ->  omop_extract/*.csv
  LOAD     (offline)           load_events()    ->  one long event frame

Design notes
------------
* `master_*` tables are the source of truth from Snowflake. Standard-named symlinks
  are added alongside them so `meds_etl_omop` can find the data, since it hardcodes
  standard OMOP table names.
* `ethos_dip` (the custom disclosure vocabulary) is excluded at the source on both
  concept_id and source_concept_id, preventively, for every domain table.
* Claims carry a DATE, not a timestamp. Intra-day ordering is therefore arbitrary and
  is fixed here by an explicit DOMAIN_ORDER rule. This is a modelling decision, not a
  detail — see `sequences()`.
* There is no ground-truth label column. The mammography notebook derives its breast-cancer
  label from the raw condition rows (ICD source codes) and never feeds it to a feature.

No Snowflake access? Run `make_demo_extract.py` — it writes a synthetic
`omop_extract/` with the same schema so every notebook still runs.
"""

import os
import csv
import glob
import numpy as np
import pandas as pd
import yaml

DATABASE = "ETHOS_PRODUCTION"
SCHEMA   = "OMOP_54"
OUT_DIR  = "omop_extract"

CORE_TABLES = [
    "person", "master_visit_occurrence", "master_condition_occurrence",
    "master_drug_exposure", "master_procedure_occurrence", "master_measurement",
    "master_observation", "death",
]

# concept_id / source_concept_id columns each master_* table uses
DOMAIN_CONCEPT_COLUMNS = {
    "master_visit_occurrence":     ("visit_concept_id", "visit_source_concept_id"),
    "master_condition_occurrence": ("condition_concept_id", "condition_source_concept_id"),
    "master_drug_exposure":        ("drug_concept_id", "drug_source_concept_id"),
    "master_procedure_occurrence": ("procedure_concept_id", "procedure_source_concept_id"),
    "master_measurement":          ("measurement_concept_id", "measurement_source_concept_id"),
    "master_observation":          ("observation_concept_id", "observation_source_concept_id"),
}

MASTER_TO_STANDARD_NAME = {
    "master_visit_occurrence":     "visit_occurrence",
    "master_condition_occurrence": "condition_occurrence",
    "master_drug_exposure":        "drug_exposure",
    "master_procedure_occurrence": "procedure_occurrence",
    "master_measurement":          "measurement",
    "master_observation":          "observation",
}

# (table, concept_id column, date column, domain label) for building the event stream
EVENT_SOURCES = [
    ("master_visit_occurrence",     "visit_concept_id",       "visit_start_date",      "Visit"),
    ("master_condition_occurrence", "condition_concept_id",   "condition_start_date",  "Condition"),
    ("master_drug_exposure",        "drug_concept_id",        "drug_exposure_start_date", "Drug"),
    ("master_procedure_occurrence", "procedure_concept_id",   "procedure_date",        "Procedure"),
    ("master_measurement",          "measurement_concept_id", "measurement_date",      "Measurement"),
    ("master_observation",          "observation_concept_id", "observation_date",      "Observation"),
]

# Deterministic intra-day ordering. Arbitrary, but written down.
DOMAIN_ORDER = {"Visit": 0, "Condition": 1, "Procedure": 2,
                "Measurement": 3, "Drug": 4, "Observation": 5}


# ===========================================================  EXTRACT (Snowflake)

def _dip_exclusion_clause(concept_col, source_concept_col):
    return (
        f"NOT EXISTS (SELECT 1 FROM {DATABASE}.{SCHEMA}.concept c "
        f"WHERE c.concept_id = {concept_col} AND c.vocabulary_id = 'ethos_dip') "
        f"AND NOT EXISTS (SELECT 1 FROM {DATABASE}.{SCHEMA}.concept c "
        f"WHERE c.concept_id = {source_concept_col} AND c.vocabulary_id = 'ethos_dip')"
    )


def connect():
    """externalbrowser auth, same as the working extract script."""
    import snowflake.connector
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        authenticator="externalbrowser",
        database=DATABASE,
        schema=SCHEMA,
    )


def _resolve_sql(cohort_sql):
    """Accept either a raw SQL string or a path to a .sql file. A path-looking
    string (single token, no whitespace, ends in .sql) that doesn't exist is a
    mistake, not SQL -- raise instead of silently sending the path to Snowflake
    as a query (the confusing failure mode this used to have)."""
    stripped = cohort_sql.strip()
    looks_like_path = stripped.endswith(".sql") and not any(c.isspace() for c in stripped)
    if looks_like_path:
        if not os.path.isfile(cohort_sql):
            raise FileNotFoundError(
                f"cohort_sql looks like a .sql file path but was not found: "
                f"{cohort_sql!r} (cwd={os.getcwd()})")
        with open(cohort_sql) as f:
            cohort_sql = f.read()
    return cohort_sql.strip().rstrip(";")


def _write_csv(out_dir, name, cols, rows):
    with open(os.path.join(out_dir, f"{name}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def _dump_core(cur, existing, pids, out_dir, tables=None,
               slim_concept=True, with_ancestors=True):
    """
    Dump CORE_TABLES filtered to `pids` (dip-excluded per domain), plus a
    concept.csv (dip-excluded, optionally slimmed to referenced concept_ids)
    and optional concept_ancestor.csv, then add standard-named symlinks for
    meds_etl_omop. Shared by extract_omop() (sampled pids) and
    extract_cohort() (cohort-sourced pids) so both write the identical shape.
    """
    id_list = ",".join(str(p) for p in pids)
    dumped  = set(tables or CORE_TABLES)          # concept / concept_ancestor are slimmed to these tables only

    def dump(table, where=None, fname=None):
        if table not in existing:
            print(f"skip {table}: not in schema")
            return 0
        sql = f"SELECT * FROM {DATABASE}.{SCHEMA}.{table}"
        if where:
            sql += f" WHERE {where}"
        cur.execute(sql)
        cols = [c[0].lower() for c in cur.description]
        rows = cur.fetchall()
        _write_csv(out_dir, fname or table, cols, rows)
        return len(rows)

    for table in (tables or CORE_TABLES):
        where = f"person_id IN ({id_list})"
        if table in DOMAIN_CONCEPT_COLUMNS:
            where += " AND " + _dip_exclusion_clause(*DOMAIN_CONCEPT_COLUMNS[table])
        dump(table, where)

    # --- concept: slim to what the sample actually references
    if slim_concept:
        union = " UNION ".join(
            f"SELECT DISTINCT {col} AS cid FROM {DATABASE}.{SCHEMA}.{tbl}"
            f" WHERE person_id IN ({id_list})"
            for tbl, col, _, _ in EVENT_SOURCES if tbl in existing and tbl in dumped)
        where = (f"vocabulary_id IS DISTINCT FROM 'ethos_dip' "
                 f"AND concept_id IN (SELECT cid FROM ({union}))")
    else:
        where = "vocabulary_id IS DISTINCT FROM 'ethos_dip'"
    dump("concept", where)

    if with_ancestors and "concept_ancestor" in existing:
        union = " UNION ".join(
            f"SELECT DISTINCT {col} AS cid FROM {DATABASE}.{SCHEMA}.{tbl}"
            f" WHERE person_id IN ({id_list})"
            for tbl, col, _, _ in EVENT_SOURCES if tbl in existing and tbl in dumped)
        dump("concept_ancestor",
             f"descendant_concept_id IN (SELECT cid FROM ({union}))")

    # --- standard-named symlinks for meds_etl_omop
    for master, standard in MASTER_TO_STANDARD_NAME.items():
        src = f"{master}.csv"
        dst = os.path.join(out_dir, f"{standard}.csv")
        if os.path.exists(os.path.join(out_dir, src)) and not os.path.exists(dst):
            try:
                os.symlink(src, dst)
                print(f"linked {dst} -> {src}")
            except OSError:                    # filesystem without symlinks
                import shutil
                shutil.copy(os.path.join(out_dir, src), dst)
                print(f"copied {dst} <- {src}")


def extract_omop(n_patients=10000, out_dir=OUT_DIR, conn=None,
                 tables=None, slim_concept=True, with_ancestors=True):
    """
    Dump a random patient sample to CSV.

    slim_concept    restrict concept.csv to concept_ids actually present in the
                    sample. The full table is millions of rows and hundreds of MB;
                    you almost never want it locally.
    with_ancestors  also dump the concept_ancestor rows touching the sample, which
                    is what you need for ontology rollup (unspecified cardiac codes
                    to their parents, drug to ingredient).
    """
    close_after = conn is None
    if conn is None:
        conn = connect()
    cur = conn.cursor()
    os.makedirs(out_dir, exist_ok=True)

    cur.execute(f"SHOW TABLES IN SCHEMA {DATABASE}.{SCHEMA}")
    existing = {row[1].lower() for row in cur.fetchall()}

    cur.execute(f"SELECT person_id FROM {DATABASE}.{SCHEMA}.person "
                f"SAMPLE ({min(100, max(1, n_patients // 100))}) LIMIT {n_patients}")
    pids = [r[0] for r in cur.fetchall()]
    if not pids:   # tiny schema or SAMPLE unsupported — fall back to a plain LIMIT
        cur.execute(f"SELECT person_id FROM {DATABASE}.{SCHEMA}.person LIMIT {n_patients}")
        pids = [r[0] for r in cur.fetchall()]
    print(f"sampled {len(pids)} person_ids")

    _dump_core(cur, existing, pids, out_dir, tables, slim_concept, with_ancestors)

    if close_after:
        conn.close()
    return out_dir


def extract_cohort(cohort_sql, out_dir="../data_input", conn=None,
                    tables=None, slim_concept=True, with_ancestors=True):
    """
    Cohort-driven extract: cohort_sql (raw SQL, or a path to a .sql file) is
    any query that returns person_id — the seeds. Those ids are then used to
    dump the same CORE_TABLES + concept (+ concept_ancestor) shape as
    extract_omop(), filtered to the cohort and with ethos_dip disclosure rows
    excluded, so notebooks load these CSVs offline afterward instead of
    re-hitting Snowflake.
    """
    cohort_sql = _resolve_sql(cohort_sql)
    close_after = conn is None
    if conn is None:
        conn = connect()
    cur = conn.cursor()
    os.makedirs(out_dir, exist_ok=True)

    cur.execute(f"SHOW TABLES IN SCHEMA {DATABASE}.{SCHEMA}")
    existing = {row[1].lower() for row in cur.fetchall()}

    cur.execute(cohort_sql)
    pids = [r[0] for r in cur.fetchall()]
    print(f"cohort seeded {len(pids)} person_ids")
    if not pids:
        print("cohort_sql returned 0 person_ids — nothing to dump")
        if close_after:
            conn.close()
        return out_dir

    _dump_core(cur, existing, pids, out_dir, tables, slim_concept, with_ancestors)

    if close_after:
        conn.close()
    return out_dir


# ==============================================================  LOAD (offline)

def _read(out_dir, table, **kw):
    p = os.path.join(out_dir, f"{table}.csv")
    if not os.path.exists(p):
        return None
    return pd.read_csv(p, low_memory=False, **kw)


def load_concept(out_dir=OUT_DIR):
    c = _read(out_dir, "concept")
    if c is None:
        raise FileNotFoundError(
            f"{out_dir}/concept.csv not found. Run extract_omop(), or "
            "python make_demo_extract.py for a synthetic stand-in.")
    c["concept_code"]  = c["concept_code"].astype(str)   # never parse as numeric
    c["vocabulary_id"] = c["vocabulary_id"].astype(str)
    return c


def load_person(out_dir=OUT_DIR):
    p = _read(out_dir, "person")
    # gender_source_value ("male"/"female", already on the person row) rather than mapping
    # gender_concept_id through concept.csv: that table is slimmed to concept_ids referenced
    # by clinical EVENTS (extract_cohort()'s slim_concept), never person.gender_concept_id,
    # so the map always misses and everyone silently becomes "Unknown". Verified against the
    # real chest-pain extract this session -- same bug, same fix.
    if "gender_source_value" in p and p["gender_source_value"].notna().any():
        p["gender"] = p["gender_source_value"].astype(str)
    else:
        g = load_concept(out_dir).set_index("concept_id")["concept_name"]
        p["gender"] = p["gender_concept_id"].map(g).fillna("Unknown")
    if "birth_datetime" in p and p["birth_datetime"].notna().any():
        p["birth_date"] = pd.to_datetime(p["birth_datetime"], errors="coerce")
    else:
        p["birth_date"] = pd.to_datetime(
            dict(year=p["year_of_birth"],
                 month=p.get("month_of_birth", 1).fillna(1) if "month_of_birth" in p else 1,
                 day=p.get("day_of_birth", 1).fillna(1) if "day_of_birth" in p else 1),
            errors="coerce")
    return p[["person_id", "gender", "birth_date", "year_of_birth"]]


def load_events(out_dir=OUT_DIR, domains=None, standard_only=True):
    """
    Union the domain tables into one long event stream.

    Returns person_id, event_date, domain, concept_id, vocabulary_id, concept_code,
    concept_name, concept_class_id (when concept.csv has it), token.

    token = 'vocabulary_id/concept_code', e.g. SNOMED/184099003 — the same form
    CLMBR and MEDS use, so this frame is one step from a MEDS conversion.

    domains        subset of {'Visit','Condition','Drug','Procedure',
                   'Measurement','Observation'}. Measurement is usually the
                   biggest table and often the least useful for claims.
    standard_only  keep only standard concepts (standard_concept = 'S').
    """
    concept = load_concept(out_dir)
    if standard_only:
        keep = concept[concept["standard_concept"] == "S"]
    else:
        keep = concept
    cmap_cols = ["vocabulary_id", "concept_code", "concept_name"]
    if "concept_class_id" in keep:
        cmap_cols.append("concept_class_id")             # needed by tag_events' fallback label
    cmap = keep.set_index("concept_id")[cmap_cols]

    frames = []
    for table, cid_col, date_col, domain in EVENT_SOURCES:
        if domains and domain not in domains:
            continue
        df = _read(out_dir, table)
        if df is None or cid_col not in df or date_col not in df:
            continue
        sub = df[["person_id", cid_col, date_col]].rename(
            columns={cid_col: "concept_id", date_col: "event_date"})
        sub["domain"] = domain
        frames.append(sub)

    if not frames:
        raise FileNotFoundError(f"no domain tables found under {out_dir}/")

    ev = pd.concat(frames, ignore_index=True)
    ev["event_date"] = pd.to_datetime(ev["event_date"], errors="coerce")
    ev = ev.dropna(subset=["event_date", "concept_id"])
    ev["concept_id"] = ev["concept_id"].astype("int64")
    ev = ev[ev["concept_id"] != 0]                       # 0 = unmapped
    ev = ev.join(cmap, on="concept_id", how="inner")     # drops non-standard
    ev["token"] = ev["vocabulary_id"] + "/" + ev["concept_code"]

    ev["_d"] = ev["domain"].map(DOMAIN_ORDER).fillna(9)
    ev = (ev.sort_values(["person_id", "event_date", "_d", "concept_id"])
            .drop(columns="_d").reset_index(drop=True))
    return ev


def observation_window(events):
    """
    Proxy enrolment window from first/last observed event.

    The extract does not include observation_period, so this is a proxy and it
    UNDERSTATES the true window. Anyone whose history starts near their first
    event is left-truncated: 'no prior diagnosis' may mean 'not observed yet'.
    Carry `lookback_days` as a feature and exclude short-lookback patients from
    any analysis that depends on absence of a code.
    """
    g = events.groupby("person_id")["event_date"]
    w = pd.DataFrame({"first_event": g.min(), "last_event": g.max()}).reset_index()
    w["lookback_days"] = (w["last_event"] - w["first_event"]).dt.days
    return w


def load_death(out_dir=OUT_DIR):
    d = _read(out_dir, "death")
    if d is None or len(d) == 0:
        return pd.DataFrame(columns=["person_id", "death_date"])
    d["death_date"] = pd.to_datetime(d["death_date"], errors="coerce")
    return d[["person_id", "death_date"]].dropna()


# =====================================================  concept set resolution

def resolve(concept, patterns, vocabularies=None, domain=None, standard_only=True,
            exclude=None):
    """
    Find concept_ids by name pattern. Returns a DataFrame for eyeballing —
    ALWAYS look at it before trusting a code set.

        resolve(concept, ['letrozole'], vocabularies=['RxNorm'])

    exclude drops any hit whose concept_name also matches one of these
    patterns -- e.g. excluding "history of"/"screening" from a diagnosis
    codeset so it doesn't pick up "Family history of breast cancer" or
    "Screening for malignant neoplasm of breast" alongside the real thing.
    """
    c = concept
    if standard_only:
        c = c[c["standard_concept"] == "S"]
    if vocabularies:
        c = c[c["vocabulary_id"].isin(vocabularies)]
    if domain:
        c = c[c["domain_id"] == domain]
    pat = "|".join(patterns)
    hit = c[c["concept_name"].str.contains(pat, case=False, na=False, regex=True)]
    if exclude:
        excl_pat = "|".join(exclude)
        hit = hit[~hit["concept_name"].str.contains(excl_pat, case=False, na=False, regex=True)]
    return hit[["concept_id", "concept_name", "vocabulary_id",
                "concept_code", "domain_id"]].sort_values("concept_name")


def expand_descendants(concept_ids, out_dir=OUT_DIR):
    """Roll a code set down through concept_ancestor (ingredient -> all products)."""
    ca = _read(out_dir, "concept_ancestor")
    if ca is None:
        return set(concept_ids)
    kids = ca.loc[ca["ancestor_concept_id"].isin(concept_ids), "descendant_concept_id"]
    return set(concept_ids) | set(kids.astype("int64"))


def roll_up(concept_ids, levels=1, out_dir=OUT_DIR):
    """Roll a code set UP to parents. Useful for unspecified diagnoses."""
    ca = _read(out_dir, "concept_ancestor")
    if ca is None:
        return set(concept_ids)
    sel = ca[(ca["descendant_concept_id"].isin(concept_ids)) &
             (ca["min_levels_of_separation"] <= levels) &
             (ca["min_levels_of_separation"] > 0)]
    return set(sel["ancestor_concept_id"].astype("int64"))


# --- The clinical code sets the notebooks work with, loaded from codesets.yaml
# --- (same directory as this file) so they're portable/editable without touching code.
def _load_codesets(path=None):
    path = path or os.path.join(os.path.dirname(__file__), "codesets.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


CODESETS = _load_codesets()


def build_codesets(concept, codesets=None, verbose=True):
    """
    Resolve CODESETS to concept_id sets. Returns dict tag -> set(concept_id).

    Each entry in codesets.yaml is either:
      tag: {patterns: [...], vocabularies: [...], domain: ..., exclude: [...]}
                                                      # name-matched via resolve() --
                                                      # vocabularies/domain/exclude optional
    or:
      tag: {concept_ids: [...]}                      # literal, resolve() skipped entirely

    Name-resolution is what makes most codesets portable across the real extract and the
    demo extract alike; use literal concept_ids only for a tag where the exact id set is
    small, known, and verified against real data.
    """
    codesets = codesets or CODESETS
    out = {}
    for tag, spec in codesets.items():
        if "concept_ids" in spec:
            ids = {int(c) for c in spec["concept_ids"]}
            out[tag] = ids
            if verbose:
                names = concept.loc[concept["concept_id"].isin(ids), "concept_name"]
                print(f"{tag:16s} {len(ids):5d} concepts (literal)   "
                      f"e.g. {names.head(2).tolist()}")
            continue
        hit = resolve(concept, spec["patterns"],
                      vocabularies=spec.get("vocabularies"),
                      domain=spec.get("domain"),
                      exclude=spec.get("exclude"))
        out[tag] = set(hit["concept_id"].astype("int64"))
        if verbose:
            print(f"{tag:16s} {len(out[tag]):5d} concepts   "
                  f"e.g. {hit['concept_name'].head(2).tolist()}")
    return out


# Accent fold used for the fallback label (same tables as the Snowflake TRANSLATE).
_ACCENT_FROM = "àáâãäåāăąçćčèéêëēėęěìíîïīįñńòóôõöøōőśšùúûüūůýÿžźż"
_ACCENT_TO   = "aaaaaaaaaccceeeeeeeeiiiiiinnoooooooossuuuuuuyyzzz"
assert len(_ACCENT_FROM) == len(_ACCENT_TO)
_ACCENT_TABLE = str.maketrans(_ACCENT_FROM, _ACCENT_TO)


def _clean(s):
    """Lower-case, fold accents, drop everything that is not a-z/0-9/space, spaces -> '_'."""
    s = str(s).lower().translate(_ACCENT_TABLE)
    s = "".join(ch for ch in s if (ch.isascii() and ch.isalnum()) or ch == " ")
    return "_".join(s.split())


def _fallback_label(name, cls, cid):
    """
    Unique label for an event with no codeset tag: <name20>__<class>__<concept_id>.

    name20 = cleaned concept_name cut to 20 characters (not re-stripped after the
    cut, matching the SQL steps); class = cleaned concept_class_id, omitted when
    missing; concept_id makes the label unique per concept, so no two concepts
    ever share a bag-of-codes column.
    """
    parts = [_clean(name)[:20]]
    if not pd.isna(cls):
        parts.append(_clean(cls))
    parts.append(str(cid))
    return "__".join(parts)


def tag_events(events, code_map, fallback="name", token_level="group", multi_group=False):
    """
    Add a `tag` column (the token sequences / bag-of-codes / NMF are built from) and a
    `group` column (the curated codeset an event belongs to, NaN when none).

    token_level  'group'   (default) curated concepts collapse to their group name, the
                           ontology-rollup step done by hand that makes Day 3 legible;
                           `tag` == `group` for them.
                 'concept' every event keeps its own concept-level token, curated ones
                           included (`fallback` decides the form); the group survives only
                           in `group`, so details stay available to later pipelines.
                           Select a group by name with `events["group"]`, or let the
                           helpers below do it (their `col=None` default).

    multi_group  False (default) a concept matched by several codesets belongs only to the FIRST one in
                 `code_map` order (legacy). True: `group` still holds that first codeset, but a new
                 `groups` column lists ALL of them ("ekg|stress_test"); the helpers below (`group_mask`,
                 `index_dates`, the label functions) then select on every group the concept is in.

    fallback  'name'  events without a `tag` get <name20>__<class>__<concept_id>
                      (readable and unique per concept; see _fallback_label)
              'token' they keep vocabulary/code (compact, opaque)
              'drop'  untagged events are removed (focus mode; loses context;
                      only with token_level='group')
    """
    if token_level not in ("group", "concept"):
        raise ValueError(f"token_level must be 'group' or 'concept', got {token_level!r}")
    if token_level == "concept" and fallback == "drop":
        raise ValueError("fallback='drop' removes untagged events; it only makes sense with token_level='group'")
    lookup, members = {}, {}
    for tag, ids in code_map.items():
        for cid in ids:
            lookup.setdefault(cid, tag)          # first tag wins
            members.setdefault(cid, []).append(tag)
    ev = events.copy()
    ev["group"] = ev["concept_id"].map(lookup)
    if multi_group:
        ev["groups"] = ev["concept_id"].map({cid: "|".join(ts) for cid, ts in members.items()}).astype("category")
    ev["in_codeset"] = ev["group"].notna()
    ev["tag"] = (ev["group"] if token_level == "group"        # NaN everywhere at concept level
                 else pd.Series(np.nan, index=ev.index, dtype=object))
    if fallback == "drop":
        ev = ev[ev["in_codeset"]]
    elif fallback == "name":
        # build the label once per concept_id that still has no tag, not once per event
        cls = ev["concept_class_id"] if "concept_class_id" in ev else pd.Series(np.nan, index=ev.index)
        u = (ev.assign(_cls=cls).loc[ev["tag"].isna(), ["concept_id", "concept_name", "_cls"]]
               .drop_duplicates("concept_id"))
        labels = pd.Series([_fallback_label(n, c, i)
                            for i, n, c in zip(u["concept_id"], u["concept_name"], u["_cls"])],
                           index=u["concept_id"])
        ev["tag"] = ev["tag"].fillna(ev["concept_id"].map(labels))
    else:
        ev["tag"] = ev["tag"].fillna(ev["token"])
    return ev.reset_index(drop=True)


def load_truth(out_dir=OUT_DIR):
    """
    Demo extracts carry truth.csv with the planted archetype. Real extracts do
    not — that absence is the entire problem this course is about. Returns None
    when running against real data, and every notebook degrades gracefully.
    """
    t = _read(out_dir, "truth")
    return t if t is not None else None


# ==================================================================  features

def bag_of_codes(events, col="tag", min_count=20, binary=True):
    """Patient x code matrix. The representation we are trying to beat."""
    vc   = events[col].value_counts()
    keep = vc[vc >= min_count].index
    sub  = events[events[col].isin(keep)]
    X    = pd.crosstab(sub["person_id"], sub[col])
    return (X > 0).astype(int) if binary else X


def sequences(events, col="tag", dedup_same_day=True, collapse_repeats=True):
    """
    person_id -> ordered token list.

    Two decisions, both arbitrary and both written down:
      * same-day events have no true order in claims data; DOMAIN_ORDER breaks ties
      * consecutive repeats (drug refills) collapse to one token, otherwise every
        pattern is metformin -> metformin -> metformin. Capture chronicity as a
        separate feature instead.
    """
    ev = events
    if dedup_same_day:
        ev = ev.drop_duplicates(["person_id", "event_date", col])
    out = {}
    for pid, g in ev.groupby("person_id", sort=True):
        seq, prev = [], None
        for c in g[col]:
            if not collapse_repeats or c != prev:
                seq.append(c)
            prev = c
        out[pid] = seq
    return out


def _gcol(events, col):
    """Column that holds curated group names: `group` when tag_events wrote it, else `tag`."""
    return col or ("group" if "group" in events.columns else "tag")


def group_mask(events, names):
    """Boolean mask of events whose concept is in ANY of the curated group(s) `names` (str or iterable).

    Uses the `groups` column when tag_events(multi_group=True) wrote it, so a concept matched by several
    codesets counts in each of them; otherwise falls back to the single-valued `group` (or `tag`) column.
    """
    names = {names} if isinstance(names, str) else set(names)
    if "groups" in events.columns:
        pairs = events[["concept_id", "groups"]].drop_duplicates("concept_id").dropna()
        hit = pairs["groups"].astype(str).str.split("|").map(lambda ts: bool(names.intersection(ts)))
        return events["concept_id"].isin(pairs.loc[hit.to_numpy(), "concept_id"])
    return events[_gcol(events, None)].isin(names)


def _select(events, tag, col):
    """Events of group/tag `tag`: every group the concept is in (col=None) or an explicit column's value."""
    return group_mask(events, tag) if col is None else events[col] == tag


def group_tokens(events, name):
    """The `tag` tokens (columns of a bag-of-codes / NMF) that belong to curated group `name`."""
    return set(events.loc[group_mask(events, name), "tag"].unique())


def group_loadings(H, events):
    """components x tokens matrix -> components x curated groups: a group's loading is the sum over its tokens
    (a token counts in every group it belongs to)."""
    if "groups" in events.columns:
        names = sorted({g for gs in events["groups"].dropna().astype(str).unique() for g in gs.split("|")})
    else:
        names = sorted(events["group"].dropna().unique())
    return pd.DataFrame({g: H[H.columns.intersection(list(group_tokens(events, g)))].sum(axis=1) for g in names}, index=H.index)


def index_dates(events, tag, col=None):
    """First occurrence of group/tag `tag` per patient — the point-in-time anchor."""
    hit = events[_select(events, tag, col)]
    return (hit.groupby("person_id")["event_date"].min()
               .rename("index_date").reset_index())


def truncate_at(events, index, col="tag"):
    """Keep only events at or before each patient's index_date. Prevents leakage."""
    ev = events.merge(index, on="person_id", how="inner")
    return ev[ev["event_date"] <= ev["index_date"]].drop(columns="index_date")


def signed_gap(events, tag_a, tag_b, col=None):
    """Days from first tag_a to first tag_b, per patient. Negative = b came first."""
    a = index_dates(events, tag_a, col).rename(columns={"index_date": "t_a"})
    b = index_dates(events, tag_b, col).rename(columns={"index_date": "t_b"})
    m = a.merge(b, on="person_id", how="inner")
    m["days_a_to_b"] = (m["t_b"] - m["t_a"]).dt.days
    return m


def window_around_anchor(events, anchor, months=18, days_per_month=30.4375, dedup=True):
    """Keep each patient's events within `months` of ANY event of the anchor group (union of the windows around every anchor date).

    A window is +/- round(months * days_per_month) days (548 days for 18 months), both ends inclusive. Windows that overlap are merged, so an event
    covered by two anchor dates is kept once and a patient stays one patient. Patients with no anchor event are dropped. With dedup=True, exact repeats
    (same person, concept, date) are dropped afterwards. Row order (and so the same-day tie-break) is preserved.
    """
    half = int(round(months * days_per_month))
    anc = events.loc[group_mask(events, anchor), ["person_id", "event_date"]]
    if not len(anc):
        return events.iloc[0:0].copy()
    day = lambda s: s.to_numpy().astype("datetime64[D]").astype("int64")
    d_ev, d_an = day(events["event_date"]), day(anc["event_date"])
    dmin = int(min(d_ev.min(), d_an.min()))
    pid = pd.Index(pd.unique(events["person_id"]))
    STRIDE = 1 << 22                                           # >> (date range + 3 * half), so keys of different patients never fall within `half`
    key_ev = pid.get_indexer(events["person_id"]).astype(np.int64) * STRIDE + (d_ev - dmin + half + 1)
    key_an = np.unique(pid.get_indexer(anc["person_id"]).astype(np.int64) * STRIDE + (d_an - dmin + half + 1))
    i = np.searchsorted(key_an, key_ev)
    lo, hi = key_an[np.clip(i - 1, 0, len(key_an) - 1)], key_an[np.clip(i, 0, len(key_an) - 1)]
    keep = np.minimum(np.abs(key_ev - lo), np.abs(key_ev - hi)) <= half
    out = events.loc[keep]
    if dedup:
        out = out.drop_duplicates(["person_id", "concept_id", "event_date"])
    return out.reset_index(drop=True)


def survival_frame(events, person, death, admin_censor="2026-06-30"):
    """
    time-to-event frame for Day 5, anchored at each patient's first event.

    Real `death` table, so this is an actual outcome rather than a simulation.
    Coverage is usually low in claims, which is itself worth reporting — low event
    counts mean wide confidence intervals, not a null result.
    """
    w  = observation_window(events)
    df = w.merge(person[["person_id"]], on="person_id", how="left") \
          .merge(death, on="person_id", how="left")
    cens = pd.Timestamp(admin_censor)
    df["event"] = df["death_date"].notna().astype(int)
    end = df["death_date"].fillna(cens)
    df["time_months"] = ((end - df["first_event"]).dt.days / 30.44).clip(lower=0)
    print(f"deaths observed: {df.event.sum()} / {len(df)} ({df.event.mean():.2%})")
    return df[["person_id", "time_months", "event", "lookback_days"]]


# ===================================================================  summary

def describe_extract(out_dir=OUT_DIR):
    rows = []
    for p in sorted(glob.glob(os.path.join(out_dir, "*.csv"))):
        base = os.path.basename(p)
        if os.path.islink(p) or base.replace(".csv", "") in MASTER_TO_STANDARD_NAME.values():
            continue
        n = sum(1 for _ in open(p)) - 1
        rows.append({"file": os.path.basename(p), "rows": n,
                     "MB": round(os.path.getsize(p) / 1e6, 1)})
    return pd.DataFrame(rows).sort_values("rows", ascending=False)


if __name__ == "__main__":
    print(describe_extract().to_string(index=False))
    ev = load_events(domains=["Visit", "Condition", "Drug", "Procedure", "Measurement"])
    print("\nevents:", ev.shape, " patients:", ev.person_id.nunique())
    print(ev.head(10).to_string(index=False))
