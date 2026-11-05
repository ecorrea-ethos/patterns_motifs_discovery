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
* There is no ground-truth label column. `weak_labels()` and `chest_pain_labels()`
  build rule-based probe labels from corroborating co-evidence. They are for
  evaluation only, never features.

No Snowflake access? Run `make_demo_extract.py` — it writes a synthetic
`omop_extract/` with the same schema so every notebook still runs.
"""

import os
import re
import csv
import glob
import math
import time
import numpy as np
import pandas as pd
import scipy.sparse as sp
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


CHUNK_ROWS   = 500_000                    # rows fetched from Snowflake and written to disk at a time
EXTRACT_DONE = "extract_complete.txt"     # written by extract_cohort() when every table is on disk
RETRIES      = 4                          # attempts per table (query + download) before the error is raised
RETRY_PAUSE  = 60                         # seconds to wait between attempts
_RETRY_ERRNO = {390422, 390111, 390114, 250001, 250003, 250005}   # Snowflake: network policy, session / token gone, cannot connect


def _retriable(e):
    """A dropped or blocked connection (network, VPN, expired session) is worth another try; a SQL error is not."""
    return (isinstance(e, (OSError, TimeoutError)) or getattr(e, "errno", None) in _RETRY_ERRNO
            or type(e).__name__ in ("OperationalError", "InterfaceError"))


def _reconnect(cur, opened):
    """A cursor on a fresh connection. The connection that failed is closed when _dump_core opened it itself (the caller closes its own)."""
    old = getattr(cur, "connection", None)
    if old is not None and old in opened:
        try:
            old.close()
        except Exception:
            pass
        opened.remove(old)
    new = connect()
    opened.append(new)
    return new.cursor()


def _short(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k" if n >= 1e3 else f"{n:.0f}"


def _stream_csv(cur, out_dir, name, chunk_rows=CHUNK_ROWS):
    """
    Write the result of the query just executed on `cur` to <name>.csv, `chunk_rows` rows at a time, so a table of
    tens of millions of rows never sits in memory. The rows go to <name>.csv.part and the file gets its final name
    only after the last block: a dropped connection leaves a .part file, never a half table that looks finished.

    One progress line per block, rewritten in place like an epoch bar: chunk i / total, bar, rows, percent, elapsed,
    eta and rows per second. The total comes from cur.rowcount (the size of the result, known once the query has
    run); without it the line shows the running count only.
    """
    cols = [c[0].lower() for c in cur.description]
    final = os.path.join(out_dir, f"{name}.csv")
    total = getattr(cur, "rowcount", None)
    total = total if isinstance(total, int) and total > 0 else None
    n_chunks = math.ceil(total / chunk_rows) if total else None
    n, i, t0 = 0, 0, time.time()
    with open(final + ".part", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        while True:
            rows = cur.fetchmany(chunk_rows)
            if not rows:
                break
            w.writerows(rows)
            n += len(rows)
            i += 1
            el = time.time() - t0
            rate = n / el if el > 0 else 0.0
            if total:
                frac = min(n / total, 1.0)
                k = int(20 * frac)
                bar = "=" * k + (">" + "." * (19 - k) if k < 20 else "")
                eta = (total - n) / rate if rate else 0.0
                line = (f"{name:<27} {i:>3}/{n_chunks:<3} [{bar}] {_short(n)}/{_short(total)} rows {frac:4.0%}  "
                        f"{el:4.0f}s  eta {eta:4.0f}s  {_short(rate)}/s")
            else:
                line = f"{name:<27} {i:>3} chunks  {_short(n)} rows  {el:4.0f}s  {_short(rate)}/s"
            print("\r" + line, end="", flush=True)
    os.replace(final + ".part", final)
    print(f"\r{name:<27} done: {n:,} rows in {time.time() - t0:.0f}s" + " " * 60)
    return n


def _same_cohort(out_dir, pids):
    """
    True when the CSVs already in out_dir belong to the cohort `pids`: policy.csv (written first by extract_cohort)
    exists and, like person.csv when it is there, lists exactly these person ids.
    """
    want = {int(x) for x in pids}
    for name in ("policy", "person"):
        p = os.path.join(out_dir, f"{name}.csv")
        if os.path.exists(p) and set(pd.read_csv(p, usecols=["person_id"])["person_id"].astype("int64")) != want:
            return False
    return os.path.exists(os.path.join(out_dir, "policy.csv"))


def _dump_core(cur, existing, pids, out_dir, tables=None,
               slim_concept=True, with_ancestors=True, resume=False, chunk_rows=CHUNK_ROWS):
    """
    Dump CORE_TABLES filtered to `pids` (dip-excluded per domain), plus a
    concept.csv (dip-excluded, optionally slimmed to referenced concept_ids)
    and optional concept_ancestor.csv, then add standard-named symlinks for
    meds_etl_omop. Shared by extract_omop() (sampled pids) and
    extract_cohort() (cohort-sourced pids) so both write the identical shape.

    Every table is streamed to disk in blocks of `chunk_rows` rows (_stream_csv). With resume=True a table whose
    CSV is already in out_dir is skipped, so a run that broke off continues with the tables that are missing.
    A table whose query or download fails on a network error is retried RETRIES times, RETRY_PAUSE seconds apart: first on
    the same connection, then on a new one (connect(), which may open the browser sign-in again).
    """
    id_list = ",".join(str(p) for p in pids)

    opened = []                                   # connections opened here by a retry

    def dump(table, where=None, fname=None):
        nonlocal cur
        if table not in existing:
            print(f"skip {table}: not in schema")
            return 0
        if resume and os.path.exists(os.path.join(out_dir, f"{fname or table}.csv")):
            print(f"skip {fname or table}: already on disk (resume)")
            return 0
        sql = f"SELECT * FROM {DATABASE}.{SCHEMA}.{table}"
        if where:
            sql += f" WHERE {where}"
        name = fname or table
        for attempt in range(1, RETRIES + 1):
            try:
                print(f"{name}: query running ...", end="\r", flush=True)
                cur.execute(sql)
                return _stream_csv(cur, out_dir, name, chunk_rows)
            except Exception as e:
                if attempt == RETRIES or not _retriable(e):
                    raise
                how = "on the same connection" if attempt == 1 else "on a new connection (the browser sign-in may open again)"
                print(f"\n{name}: {type(e).__name__}: {str(e).splitlines()[0][:160]}\n"
                      f"  attempt {attempt}/{RETRIES} failed; waiting {RETRY_PAUSE}s, then retrying {how} ...", flush=True)
                time.sleep(RETRY_PAUSE)
                if attempt > 1:
                    cur = _reconnect(cur, opened)

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
            for tbl, col, _, _ in EVENT_SOURCES if tbl in existing)
        where = (f"vocabulary_id IS DISTINCT FROM 'ethos_dip' "
                 f"AND concept_id IN (SELECT cid FROM ({union}))")
    else:
        where = "vocabulary_id IS DISTINCT FROM 'ethos_dip'"
    dump("concept", where)

    if with_ancestors and "concept_ancestor" in existing:
        concept_csv = os.path.join(out_dir, "concept.csv")
        if slim_concept and os.path.exists(concept_csv):
            # the concepts of the cohort are already on disk (the slim concept.csv): ask for their ancestors by id instead of
            # scanning the six event tables a second time (that scan took about 8 minutes on the chest pain cohort)
            cids = pd.read_csv(concept_csv, usecols=["concept_id"])["concept_id"].astype("int64")
            where = f"descendant_concept_id IN ({','.join(str(c) for c in cids)})"
        else:
            union = " UNION ".join(
                f"SELECT DISTINCT {col} AS cid FROM {DATABASE}.{SCHEMA}.{tbl}"
                f" WHERE person_id IN ({id_list})"
                for tbl, col, _, _ in EVENT_SOURCES if tbl in existing)
            where = f"descendant_concept_id IN (SELECT cid FROM ({union}))"
        dump("concept_ancestor", where)

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
    for c in opened:
        try:
            c.close()
        except Exception:
            pass


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
                    tables=None, slim_concept=True, with_ancestors=True, resume=False, chunk_rows=CHUNK_ROWS):
    """
    Cohort-driven extract: cohort_sql (raw SQL, or a path to a .sql file) is
    any query that returns person_id — the seeds. Those ids are then used to
    dump the same CORE_TABLES + concept (+ concept_ancestor) shape as
    extract_omop(), filtered to the cohort and with ethos_dip disclosure rows
    excluded, so notebooks load these CSVs offline afterward instead of
    re-hitting Snowflake.

    A second column in the query, if there is one, is the application date of
    the person (sql/chest_pain_cohort.sql v0.3: the latest interview start of
    the person's policies). It is written to policy.csv (person_id,
    application_date), which load_policy_dates() and reference_dates() read.

    The tables are streamed to disk in blocks of `chunk_rows` rows and each CSV appears only when complete. With
    resume=True the tables already on disk are skipped, so after a dropped connection the same call continues with
    the missing ones; it refuses (ValueError) when the folder holds CSVs of another cohort or of an old extract
    without policy.csv (_same_cohort). When every table is on disk the file EXTRACT_DONE is written.
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
    rows = cur.fetchall()
    pids = [r[0] for r in rows]
    print(f"cohort seeded {len(pids)} person_ids")
    if not pids:
        print("cohort_sql returned 0 person_ids — nothing to dump")
        if close_after:
            conn.close()
        return out_dir
    if resume and any(f.endswith(".csv") for f in os.listdir(out_dir)) and not _same_cohort(out_dir, pids):
        raise ValueError(f"{out_dir} holds CSVs of another cohort, or of an old extract without policy.csv: "
                         "move the folder away, or call without resume")
    if len(rows[0]) > 1:
        _write_csv(out_dir, "policy", ["person_id", "application_date"], [(r[0], r[1]) for r in rows])

    _dump_core(cur, existing, pids, out_dir, tables, slim_concept, with_ancestors, resume, chunk_rows)
    with open(os.path.join(out_dir, EXTRACT_DONE), "w") as f:
        f.write(f"{pd.Timestamp.now():%Y-%m-%d %H:%M}  {len(pids)} persons\n")

    if close_after:
        conn.close()
    return out_dir


POLICY_SQL =os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "sql", "chest_pain_policy_dates.sql")
_EXTRACT_MARK = "-- ==== EXTRACT ===="


def extract_policy_dates(out_dir=OUT_DIR, app_date_col="APPLICATION_DATE", sql_path=POLICY_SQL, conn=None, chunk=10_000):
    """
    Write `policy.csv` (person_id, policy_id, application_date) next to person.csv, for the persons of an existing extract.

    The query is the part of sql/chest_pain_policy_dates.sql after the EXTRACT marker. `app_date_col` is a column of
    dbt_mart_transformation.m_policy_carrier_product; the default is a GUESS, run the DISCOVERY query of that file first and pass the real name.
    Needs Snowflake (externalbrowser sign-in, like extract_cohort). Person ids go in `chunk` at a time.
    """
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", app_date_col):
        raise ValueError(f"app_date_col must be a plain column name, got {app_date_col!r}")
    p = _read(out_dir, "person")
    if p is None:
        raise FileNotFoundError(f"{out_dir}/person.csv not found: run extract_cohort() first")
    pids = p["person_id"].dropna().astype("int64").unique().tolist()
    with open(sql_path) as f:
        txt = f.read()
    if _EXTRACT_MARK not in txt:
        raise ValueError(f"{sql_path} has no '{_EXTRACT_MARK}' line")
    template = txt.split(_EXTRACT_MARK, 1)[1].strip().rstrip(";").replace("{{APPLICATION_DATE_COLUMN}}", app_date_col)
    close_after = conn is None
    if conn is None:
        conn = connect()
    cur = conn.cursor()
    cols, rows = None, []
    for i in range(0, len(pids), chunk):
        cur.execute(template.replace("{{PERSON_IDS}}", ",".join(str(x) for x in pids[i:i + chunk])))
        cols = [c[0].lower() for c in cur.description]
        rows.extend(cur.fetchall())
    if close_after:
        conn.close()
    _write_csv(out_dir, "policy", cols or ["person_id", "policy_id", "application_date"], rows)
    return os.path.join(out_dir, "policy.csv")


# ==============================================================  LOAD (offline)

def _fresh_parquet(out_dir, table):
    """<table>.parquet (made by csv_to_parquet.py) when it exists and is not older than the CSV, else None."""
    pqt = os.path.join(out_dir, f"{table}.parquet")
    csv = os.path.join(out_dir, f"{table}.csv")
    if os.path.exists(pqt) and (not os.path.exists(csv) or os.path.getmtime(pqt) >= os.path.getmtime(csv)):
        return pqt
    return None


def _read(out_dir, table, columns=None, **kw):
    """
    One extract table as a DataFrame, or None when it is absent.

    Reads <table>.parquet when it is fresh (see _fresh_parquet) and holds every requested column
    (columns=None = every column of the CSV), else the CSV. columns limits what is loaded and a
    column the table does not have is skipped. kw go to read_csv only.
    """
    pqt = _fresh_parquet(out_dir, table)
    csv = os.path.join(out_dir, f"{table}.csv")
    if pqt:
        import pyarrow.parquet as pq
        have = set(pq.read_schema(pqt).names)
        if columns is not None:
            need = set(columns)
        else:
            need = set(pd.read_csv(csv, nrows=0).columns) if os.path.exists(csv) else have
        if need <= have:
            return pd.read_parquet(pqt, columns=None if columns is None else list(columns))
    if not os.path.exists(csv):
        return None
    if columns is not None:
        kw["usecols"] = lambda c: c in columns
    return pd.read_csv(csv, low_memory=False, **kw)


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
    # real extract -- this was the root cause of 0% female in the Table 1 cohort description.
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
        df = _read(out_dir, table, columns=["person_id", cid_col, date_col])
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


def load_policy_dates(out_dir=OUT_DIR):
    """
    Earliest application date per person, from policy.csv (written by extract_policy_dates), as a Series indexed by person_id.
    None when the file is missing or holds no usable date. A person with several policies gets the EARLIEST application date.
    """
    d = _read(out_dir, "policy")
    if d is None or not {"person_id", "application_date"} <= set(d.columns):
        return None
    d["application_date"] = pd.to_datetime(d["application_date"], errors="coerce")
    d = d.dropna(subset=["person_id", "application_date"])
    if not len(d):
        return None
    return d.groupby("person_id")["application_date"].min()


def reference_dates(events, out_dir=OUT_DIR, mode="application"):
    """
    The date age and recency are measured from, one row per person of `events`: columns ref_date and ref_source.

    mode 'application'  the application date of policy.csv; persons without one (or every person, when the file is missing) fall back to
                        their last observed event and say so in ref_source. The extract has no observation_period, so the last event is
                        only a PROXY: record dates are spread over 2017-2026 and a record can end long before the application.
    mode 'last_event'   the last observed event of every person.
    """
    if mode not in ("application", "last_event"):
        raise ValueError(f"mode must be 'application' or 'last_event', got {mode!r}")
    ref = pd.DataFrame({"ref_date": events.groupby("person_id")["event_date"].max()})
    ref["ref_source"] = "last_event"
    if mode == "application":
        app = load_policy_dates(out_dir)
        if app is None:
            print(f"WARNING reference_dates: {out_dir}/policy.csv missing or empty, every person falls back to the last observed event "
                  "(run extract_policy_dates, see sql/chest_pain_policy_dates.sql)")
        else:
            a = app.reindex(ref.index)
            use = a.notna()
            ref["ref_date"] = a.where(use, ref["ref_date"])
            ref.loc[use, "ref_source"] = "application"
    return ref


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
    or both: the tag is the union of the literal ids and the name-matched hits (the ids are
      added as given, vocabularies/domain/exclude filter the patterns only).

    Name-resolution is what makes most codesets portable across the real extract and the
    demo extract alike; use literal concept_ids only for a tag where the exact id set is
    small, known, and verified against real data.
    """
    codesets = codesets or CODESETS
    out = {}
    for tag, spec in codesets.items():
        ids = {int(c) for c in spec.get("concept_ids", [])}
        if "patterns" in spec:
            hit = resolve(concept, spec["patterns"],
                          vocabularies=spec.get("vocabularies"),
                          domain=spec.get("domain"),
                          exclude=spec.get("exclude"))
            ids |= set(hit["concept_id"].astype("int64"))
            names, kind = hit["concept_name"], ""
        else:
            names, kind = concept.loc[concept["concept_id"].isin(ids), "concept_name"], " (literal)"
        out[tag] = ids
        if verbose:
            print(f"{tag:16s} {len(ids):5d} concepts{kind}   e.g. {names.head(2).tolist()}")
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


def bag_of_codes_sparse(events, col="tag", min_count=20, binary=True):
    """
    Same patient x code matrix as bag_of_codes(), built straight into a scipy CSR matrix (no dense crosstab).

    Returns (X, person_ids, columns): X is float64 CSR; rows follow the sorted person_ids and columns the sorted code names, i.e. the order
    pd.crosstab gives, so X.toarray() equals bag_of_codes(...).to_numpy(). min_count counts EVENTS per code, as in bag_of_codes().
    binary=False keeps the event counts. Needed once the column count makes a dense frame impossible (feature x age x sex).
    """
    vc   = events[col].value_counts()
    keep = vc[vc >= min_count].index
    sub  = events.loc[events[col].isin(keep), ["person_id", col]]
    pid, pu = pd.factorize(sub["person_id"], sort=True)
    cid, cu = pd.factorize(sub[col], sort=True)
    X = sp.coo_matrix((np.ones(len(sub), dtype=np.float64), (pid, cid)), shape=(len(pu), len(cu))).tocsr()   # duplicate cells are summed
    if binary:
        X.data[:] = 1.0
    return X, np.asarray(pu), list(cu)


# ---------------------------------------------------------------  age and sex columns (extra columns next to the bag of codes)

DEFAULT_AGE_EDGES = (25, 30, 35, 40, 45, 50, 55, 60, 65)    # Census 5-year edges; the thin tails are merged into "<25" and "65+"
_SEX = ("F", "M", "U")


def age_band_labels(edges=DEFAULT_AGE_EDGES):
    """Labels of the bands cut by `edges`: ['<25', '25-29', ..., '60-64', '65+'] for the default."""
    e = sorted(edges)
    return [f"<{e[0]}"] + [f"{a}-{b - 1}" for a, b in zip(e[:-1], e[1:])] + [f"{e[-1]}+"]


def _sex(gender):
    """'female' / 'male' (any case, or 'f' / 'm') -> 'F' / 'M'; anything else, a missing value included, -> 'U'."""
    return gender.astype(str).str.strip().str.lower().map({"female": "F", "f": "F", "male": "M", "m": "M"}).fillna("U")


def demographics(person, ref, edges=DEFAULT_AGE_EDGES):
    """
    person (load_person) and ref (frame indexed by person_id with a `ref_date` column, e.g. the first chest pain) -> one row per person:
    sex 'F' / 'M' / 'U', age (years at ref_date), age_band, stratum 'sex|band'. Persons without a reference date or birth date get NaN age,
    band and stratum. A read-out table (who is in each component); the columns the NMF sees come from age_sex_block and demographic_block.
    """
    d = (person.drop_duplicates("person_id").set_index("person_id")[["gender", "birth_date"]]
               .join(ref[["ref_date"]], how="inner"))
    sex = _sex(d["gender"])
    age = (d["ref_date"] - d["birth_date"]).dt.days / 365.25
    labels = np.array(age_band_labels(edges), dtype=object)
    band = pd.Series(labels[np.searchsorted(sorted(edges), age.to_numpy(), side="right")], index=d.index, dtype=object).where(age.notna())
    return pd.DataFrame({"sex": sex, "age": age, "age_band": band, "stratum": (sex + "|" + band.fillna("")).where(band.notna())})


def demographic_block(events, person, person_ids, edges=DEFAULT_AGE_EDGES, min_patients=1):
    """
    One-hot sex and age band: 'demo_sex_F', 'demo_age_35-39'. `events` are the rows of the anchor event only (the chest pain events);
    the band is the age AT EACH OF THEM, so a patient with chest pain at 38 and again at 44 lights two bands, as in age_sex_block. Sex is
    the person's: one column per patient. Nothing is crossed with a code. Columns with fewer than `min_patients` patients (or none) are
    dropped; an event without a birth date lights no band, and events of people outside `person_ids` are ignored.
    Returns (CSR, names), rows in the order of `person_ids`; column order: F < M < U, then the youngest band first.
    """
    e = sorted(edges)
    labels = age_band_labels(e)
    n = len(person_ids)
    p = person.drop_duplicates("person_id").set_index("person_id")
    sex = pd.Index(_SEX).get_indexer(_sex(p["gender"]).reindex(person_ids).fillna("U").to_numpy())
    row = pd.Index(person_ids).get_indexer(events["person_id"])
    age = ((events["event_date"] - events["person_id"].map(p["birth_date"])).dt.days / 365.25).to_numpy()
    ok = (row >= 0) & ~np.isnan(age)
    band = np.searchsorted(e, age[ok], side="right")
    M_sex = sp.csr_matrix((np.ones(n), (np.arange(n), sex)), shape=(n, len(_SEX)))
    M_age = sp.csr_matrix((np.ones(int(ok.sum())), (row[ok], band)), shape=(n, len(labels)))
    M_age.data[:] = 1                                                    # two chest pain events in one band count once
    X = sp.hstack([M_sex, M_age], format="csr")
    names = [f"demo_sex_{s}" for s in _SEX] + [f"demo_age_{b}" for b in labels]
    keep = np.flatnonzero(np.asarray(X.sum(axis=0)).ravel() >= max(int(min_patients), 1))
    return X[:, keep].tocsr(), [names[j] for j in keep]


def risk_age_sex_block(events, person, person_ids, rules, min_patients=1):
    """
    One 0/1 column per rule, 'demo_<name>': 1 for a patient who, at ANY of `events` (the chest pain events), is of the rule's sex and
    at least its age. `rules` is a tuple of (name, sex, min_age), e.g. (('male_45plus', 'M', 45), ('female_55plus', 'F', 55)), Sean's
    high-risk rule: the visit is on or after the min_age-th birthday (a man on his 45th birthday counts; a 29 Feb birth turns a year older
    on 28 Feb). A man with chest pain at 44 and again at 46 is 1 in 'male_45plus'. Unknown sex, no birth date and events of people outside
    `person_ids` light nothing. Columns with fewer than `min_patients` patients (or none) are dropped.
    Returns (CSR, names), rows in the order of `person_ids`, columns in the order of `rules`.
    """
    p = person.drop_duplicates("person_id").set_index("person_id")
    row = pd.Index(person_ids).get_indexer(events["person_id"])
    sex = _sex(events["person_id"].map(p["gender"])).to_numpy()
    birth = events["person_id"].map(p["birth_date"])
    cols, names = [], []
    for name, s, min_age in rules:
        old_enough = (events["event_date"] >= birth + pd.DateOffset(years=min_age)).to_numpy()      # NaT (no birth date) compares False
        r = np.unique(row[(row >= 0) & (sex == s) & old_enough])
        cols.append(sp.csr_matrix((np.ones(len(r)), (r, np.zeros(len(r), dtype=int))), shape=(len(person_ids), 1)))
        names.append(f"demo_{name}")
    X = sp.hstack(cols, format="csr")
    keep = np.flatnonzero(np.asarray(X.sum(axis=0)).ravel() >= max(int(min_patients), 1))
    return X[:, keep].tocsr(), [names[j] for j in keep]


def age_sex_block(events, person, person_ids, groups, edges=DEFAULT_AGE_EDGES, min_patients=1, col="group", chunk=5_000_000):
    """
    One column per (code, sex, age band AT THE EVENT): 'anxiety_F_35-39' is 1 for a woman who had an event of the code while aged 35-39.
    Age is taken at the date of each event, so a patient with the code at 38 and again at 44 lights two columns; sex is the person's.
    `groups` are the codes to cross, matched on the events column `col`: the NMF token 'tag' crosses every code (curated groups and
    concept-level codes alike), 'group' only the curated ones. Meant to sit NEXT TO the plain columns. Columns with fewer than
    `min_patients` patients are dropped. Events without a birth date drop out. Events are scanned `chunk` rows at a time (46M events).
    Returns (CSR, names), rows in the order of `person_ids`; a name splits back with name.rsplit('_', 2) into code, sex, band.
    Column order: code (sorted), then F < M < U, then the youngest band first.
    """
    e = sorted(edges)
    labels = age_band_labels(e)
    nb, ns = len(labels), len(_SEX)
    gnames = pd.Index(sorted(set(groups)))
    p = person.drop_duplicates("person_id").set_index("person_id")
    pidx = pd.Index(person_ids)
    sex = pd.Index(_SEX).get_indexer(_sex(p["gender"]).reindex(person_ids).fillna("U").to_numpy())
    parts = []
    for s0 in range(0, len(events), chunk):
        ev = events.iloc[s0:s0 + chunk]
        g = gnames.get_indexer(ev[col])                                  # -1: not a code to cross (a missing code included)
        row = pidx.get_indexer(ev["person_id"])
        age = ((ev["event_date"] - ev["person_id"].map(p["birth_date"])).dt.days / 365.25).to_numpy()
        ok = (g >= 0) & (row >= 0) & ~np.isnan(age)
        if ok.any():
            key = (g[ok].astype(np.int64) * ns + sex[row[ok]]) * nb + np.searchsorted(e, age[ok], side="right")
            parts.append(pd.DataFrame({"r": row[ok], "k": key}).drop_duplicates())     # one cell per patient, code, sex and band
    if not parts:
        return sp.csr_matrix((len(person_ids), 0)), []
    cells = pd.concat(parts, ignore_index=True).drop_duplicates()
    n = cells["k"].value_counts()
    keys = np.sort(n[n >= max(int(min_patients), 1)].index.to_numpy())
    if not len(keys):
        return sp.csr_matrix((len(person_ids), 0)), []
    cells = cells[cells["k"].isin(keys)]
    X = sp.csr_matrix((np.ones(len(cells)), (cells["r"].to_numpy(), np.searchsorted(keys, cells["k"].to_numpy()))),
                      shape=(len(person_ids), len(keys)))
    names = [f"{gnames[k // nb // ns]}_{_SEX[k // nb % ns]}_{labels[k % nb]}" for k in keys.tolist()]
    return X, names


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


# ==============================================================  weak labels

def weak_labels(events, person=None, col=None):
    """
    Rule-based PROBE labels for the letrozole indication, from corroborating
    co-evidence only.

    Critical: the time delta is NOT used. If you label by 'drug before diagnosis'
    and then test whether the time delta predicts the label, you get 100% by
    construction and have learned nothing. Co-evidence keeps the test honest.

    Returns person_id, weak_label in {fertility, oncology}. Ambiguous and
    no-evidence patients are dropped — report how many.
    """
    has = lambda tag: set(events.loc[_select(events, tag, col), "person_id"])

    lz = has("letrozole")
    fert = has("clomiphene") | has("gonadotropin") | has("infertility")
    # NOTE: breast_cancer is deliberately NOT oncology evidence. A fertility
    # patient can develop breast cancer years later, so the diagnosis alone is
    # confounded with the very thing we are trying to disambiguate. Only
    # treatment and workup co-evidence counts.
    onco = (has("mastectomy") | has("breast_biopsy")
            | has("anastrozole") | has("tamoxifen"))

    rows = []
    for pid in sorted(lz):
        f, o = pid in fert, pid in onco
        if f and not o:
            rows.append((pid, "fertility"))
        elif o and not f:
            rows.append((pid, "oncology"))
    lab = pd.DataFrame(rows, columns=["person_id", "weak_label"])

    n_amb = len(lz & fert & onco)
    print(f"letrozole patients: {len(lz)}   labelled: {len(lab)}   "
          f"both-evidence (dropped): {n_amb}   no-evidence (dropped): "
          f"{len(lz) - len(lab) - n_amb}")
    return lab


# Corroborating-evidence tags for chest_pain_labels() / Table 1, pulled from
# codesets.yaml rather than hand-typed twice, so both places use the exact
# same list and can't drift apart.
PSYCH_TAGS = ["anxiety", "panic_attack", "ssri", "benzodiazepine"]
CARDIAC_TAGS = ["troponin", "stress_test", "coronary_angio", "cad"]


def chest_pain_labels(events, col=None):
    """
    Rule-based PROBE labels for the dx_9487 chest-pain triage question, from
    corroborating co-evidence only — same contract as weak_labels(): the time
    order of chest_pain vs the evidence is NEVER used here, because that order is
    exactly what Days 3-4 test. Labelling on order and then testing order would be
    circular.

    psych   = anxiety, panic_attack, ssri, or benzodiazepine evidence
    cardiac = troponin, stress_test, coronary_angio, or cad-dx evidence

    Returns person_id, chest_pain_label in {psych, cardiac}. Ambiguous (both) and
    no-evidence (neither) patients are dropped — report how many, same as
    weak_labels(). This is a probe for evaluation, never a feature.
    """
    missing = [t for t in PSYCH_TAGS + CARDIAC_TAGS if t not in CODESETS]
    assert not missing, f"chest_pain_labels tags missing from codesets.yaml: {missing}"

    has = lambda tag: set(events.loc[_select(events, tag, col), "person_id"])

    cp = has("chest_pain")
    psych = set().union(*(has(t) for t in PSYCH_TAGS))
    cardiac = set().union(*(has(t) for t in CARDIAC_TAGS))

    rows = []
    for pid in sorted(cp):
        p, c = pid in psych, pid in cardiac
        if p and not c:
            rows.append((pid, "psych"))
        elif c and not p:
            rows.append((pid, "cardiac"))
    lab = pd.DataFrame(rows, columns=["person_id", "chest_pain_label"])

    n_amb = len(cp & psych & cardiac)
    print(f"chest_pain patients: {len(cp)}   labelled: {len(lab)}   "
          f"both-evidence (dropped): {n_amb}   no-evidence (dropped): "
          f"{len(cp) - len(lab) - n_amb}")
    return lab


def cardiac_workup_outcome(events, window_days=180, col=None):
    """
    Day 5 proxy outcome for dx_9487 triage: did a real cardiac workup happen
    AFTER the patient's first chest_pain code, within `window_days`?

    There is no mortality endpoint for a triage question, so this replaces
    survival_frame() as the primary Day 5 validation target — does a discovered
    cluster or surrogate rule predict who actually got worked up. Forward-looking
    by construction (workup must occur at or after the index date), so this is a
    real outcome, not a feature computed from the same history being clustered.

    Returns person_id, index_date, workup (bool), days_to_workup (NaN if none).

    Caution: what triggers a workup code is itself a downstream reviewer decision.
    A rule that "predicts" workup can be partly predicting the reviewer's past
    behaviour rather than true cardiac risk — state this limitation, don't hide it.
    """
    index = index_dates(events, "chest_pain", col=col).rename(columns={"index_date": "cp_date"})

    cardiac_tags = {"troponin", "stress_test", "coronary_angio", "cad"}
    workup = (events[group_mask(events, cardiac_tags) if col is None else events[col].isin(cardiac_tags)]
              .groupby("person_id")["event_date"].min()
              .rename("workup_date").reset_index())

    df = index.merge(workup, on="person_id", how="left")
    gap = (df["workup_date"] - df["cp_date"]).dt.days
    df["workup"] = (gap >= 0) & (gap <= window_days)
    df["days_to_workup"] = gap.where(df["workup"])
    df = df.rename(columns={"cp_date": "index_date"})

    print(f"chest_pain patients: {len(df)}   workup within {window_days}d: "
          f"{df.workup.sum()} ({df.workup.mean():.1%})")
    return df[["person_id", "index_date", "workup", "days_to_workup"]]


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
        pqt = _fresh_parquet(out_dir, base.replace(".csv", ""))
        if pqt:                                          # row count from the parquet footer, no pass over the CSV
            import pyarrow.parquet as pq
            n = pq.ParquetFile(pqt).metadata.num_rows
        else:
            n = sum(1 for _ in open(p)) - 1
        rows.append({"file": os.path.basename(p), "rows": n,
                     "MB": round(os.path.getsize(p) / 1e6, 1)})
    return pd.DataFrame(rows).sort_values("rows", ascending=False)


if __name__ == "__main__":
    print(describe_extract().to_string(index=False))
    ev = load_events(domains=["Visit", "Condition", "Drug", "Procedure", "Measurement"])
    print("\nevents:", ev.shape, " patients:", ev.person_id.nunique())
    print(ev.head(10).to_string(index=False))
