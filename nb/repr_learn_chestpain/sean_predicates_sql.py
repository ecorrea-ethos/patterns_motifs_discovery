"""
SQL of Sean's chest pain predicates and composites for the Ethos OMOP schema in Snowflake. One source for the page
(make_sean_predicates_page.py) and for the local check of the SQL against the extract.

Each predicate is a query that returns the DISTINCT person_id for which the predicate is true. The queries read two names
that the Validation Query defines first:
    cohort               person_id, latest_interview_started_date    the cohort query v0.3 (sql/chest_pain_cohort.sql), as it is
    chest_pain_dates     person_id, r_date, f_date, c_date, months_out    the anchor, one row per applicant with chest pain up to R
Every query lists the concept ids of its code sets inline (IN (...)), one SQL comment per code set; no helper table.
The logic mirrors Chestpain_Sean_predicates.ipynb (cells A3 to A5). The code sets come from codesets_sean_v2.yaml through the notebook workbook.
"""
import os
import re

DB = "ethos_production.omop_54"
HERE = os.path.dirname(os.path.abspath(__file__))
COHORT_SQL = os.path.join(HERE, "..", "..", "sql", "chest_pain_cohort.sql")
MONTH = "30.4375"
CUT = {"recent": 6, "cad": 12, "old": 24}                   # months: Sean's "6 months out", "Hx of CAD and < 1 year", "coded > 2 years ago"
IDS_PER_LINE = 8
AGE = (("male", 8507, 45), ("female", 8532, 55))            # sex, OMOP gender concept id, "older than"

COND = ("master_condition_occurrence", "condition_concept_id", "condition_start_date")
PROC = ("master_procedure_occurrence", "procedure_concept_id", "procedure_date")
DRUG = ("master_drug_exposure", "drug_concept_id", "drug_exposure_start_date")
MEAS = ("master_measurement", "measurement_concept_id", "measurement_date")
SOURCE = {  # code set -> table, concept column, date column (each set has events in one table only, checked on the extract)
    "chest_pain": COND, "uw_cad_dx": COND, "uw_abnormal_ekg": COND, "uw_cardiac_testing": PROC, "nitrates": DRUG, "troponin": MEAS,
    "ekg": PROC, "gerd": COND, "anxiety": COND, "uw_gi_dx": COND, "uw_muscle_strain": COND, "costochondritis": COND, "uw_noncardiac_cp": COND,
}
WINDOW = {  # which events count, as conditions on the date column d
    "R": ["{d} <= cp.r_date"],
    "C": ["{d} <= cp.c_date"],
    "after C": ["{d} > cp.c_date", "{d} <= cp.r_date"],
    "after F": ["{d} > cp.f_date", "{d} <= cp.r_date"],
}
# predicate -> (code sets, window) for the predicates that read events; the order of the page
EVENTS = {
    "hx_cad": (["uw_cad_dx"], "C"),
    "abnormal_ekg": (["uw_abnormal_ekg"], "R"),
    "extra_cardiac_testing": (["uw_cardiac_testing"], "after C"),
    "rx_nitrates": (["nitrates"], "R"),
    "troponin": (["troponin"], "R"),
    "ekg": (["ekg"], "R"),
    "gerd": (["gerd"], "R"),
    "anxiety": (["anxiety"], "R"),
    "gi_dx": (["gerd", "uw_gi_dx"], "after C"),
    "anxiety_later": (["anxiety"], "after C"),
    "muscle_strain": (["uw_muscle_strain"], "after C"),
    "costochondritis": (["costochondritis"], "after C"),
    "noncardiac_cp": (["uw_noncardiac_cp"], "after F"),
}
SEAN_DX = ["uw_cad_dx", "gerd", "uw_gi_dx", "anxiety", "uw_muscle_strain", "costochondritis", "uw_noncardiac_cp"]   # the diagnoses of the draft
ORDER = ["age_sex_high_risk", "hx_cad", "abnormal_ekg", "extra_cardiac_testing", "rx_nitrates", "troponin", "ekg", "gerd", "anxiety",
         "gi_dx", "anxiety_later", "muscle_strain", "costochondritis", "noncardiac_cp", "explained_dx", "ekg_no_abnormal_code",
         "no_further_cardiac_testing", "no_firm_dx"]
HIGH_RISK = ["age_sex_high_risk", "hx_cad", "abnormal_ekg", "extra_cardiac_testing", "rx_nitrates"]
HR = "(" + " + ".join(f"f.{p}" for p in HIGH_RISK) + ") > 0"
COMPOSITES = {
    "high_risk_any": HR,
    "A1": f"NOT ({HR})\n         AND f.months_out > {CUT['recent']}",
    "A2": "f.ekg_no_abnormal_code = 1 AND f.hx_cad = 0",
    "A3": f"f.no_further_cardiac_testing = 1 AND f.hx_cad = 0\n         AND f.months_out > {CUT['recent']}",
    "A4": "f.explained_dx = 1 AND f.hx_cad = 0",
    "A5": "f.noncardiac_cp = 1",
    "A6": f"f.months_out > {CUT['old']}",
    "R1": f"({HR})\n         AND f.months_out < {CUT['recent']}",
    "R2": f"f.no_firm_dx = 1 AND f.months_out < {CUT['recent']}",
    "D1": f"f.hx_cad = 1 AND f.months_out < {CUT['cad']}",
}


def _in_list(expr, sets, concepts, pad=0):
    """`expr IN (ids)` with every concept id of the code sets. A SQL comment names each code set and its number of concepts.
    pad = the indentation of the line that holds `expr`."""
    label = lambda s, ids: f"{s} ({len(ids)} concept{'s' if len(ids) != 1 else ''})"
    groups = [(s, concepts[s]) for s in sets]
    if len(groups) == 1 and len(groups[0][1]) <= IDS_PER_LINE:
        s, ids = groups[0]
        return f"{expr} IN ({', '.join(map(str, ids))})   -- {label(s, ids)}"
    p = " " * pad
    lines = []
    for gi, (s, ids) in enumerate(groups):
        lines.append(f"{p}        -- {label(s, ids)}")
        rows = [", ".join(map(str, ids[i:i + IDS_PER_LINE])) for i in range(0, len(ids), IDS_PER_LINE)]
        for ri, row in enumerate(rows):
            last = gi == len(groups) - 1 and ri == len(rows) - 1
            lines.append(f"{p}        {row}" + ("" if last else ","))
    return f"{expr} IN (\n" + "\n".join(lines) + f"\n{p}    )"


def _events(sets, window, concepts):
    tables = {SOURCE[s] for s in sets}
    assert len(tables) == 1, (sets, tables)
    tbl, cid, d = tables.pop()
    return (f"SELECT DISTINCT e.person_id\n"
            f"FROM {DB}.{tbl} e\n"
            f"JOIN chest_pain_dates cp ON cp.person_id = e.person_id\n"
            f"WHERE " + _in_list(f"e.{cid}", sets, concepts)
            + "".join(f"\n  AND {c.format(d='e.' + d)}" for c in WINDOW[window]))


def anchor_sql(concepts):
    """chest_pain_dates: the anchor. One row per applicant with a chest pain event on or before R (the date of the cohort query v0.3)."""
    tbl, cid, d = SOURCE["chest_pain"]
    return (f"SELECT a.person_id, a.r_date, a.f_date, a.c_date,\n"
            f"       DATEDIFF(day, a.c_date, a.r_date) / {MONTH} AS months_out\n"
            f"FROM (\n"
            f"    SELECT e.person_id, coh.latest_interview_started_date AS r_date,\n"
            f"           MIN(e.{d}) AS f_date,\n"
            f"           MAX(e.{d}) AS c_date\n"
            f"    FROM {DB}.{tbl} e\n"
            f"    JOIN cohort coh ON coh.person_id = e.person_id\n"
            f"    WHERE " + _in_list(f"e.{cid}", ["chest_pain"], concepts, pad=4) + "\n"
            f"      AND e.{d} <= coh.latest_interview_started_date\n"
            f"    GROUP BY e.person_id, coh.latest_interview_started_date\n"
            f") a")


def predicate_sql(p, concepts):
    """The standalone query of one predicate."""
    if p == "age_sex_high_risk":
        parts = [f"(p.gender_concept_id = {gid}   -- {sex}\n"
                 f"     AND cp.c_date >= DATEADD(year, {age + 1}, p.birth_datetime))" for sex, gid, age in AGE]
        return (f"-- older than 45 (man) or 55 (woman), in completed years: the 46th or 56th birthday is on or before C\n"
                f"SELECT DISTINCT cp.person_id\n"
                f"FROM chest_pain_dates cp\n"
                f"JOIN {DB}.person p ON p.person_id = cp.person_id\n"
                f"WHERE " + "\n   OR ".join(parts))
    if p in EVENTS:
        return _events(*EVENTS[p], concepts)
    if p == "explained_dx":
        return ("SELECT person_id FROM anxiety_later\nUNION\nSELECT person_id FROM gi_dx\nUNION\n"
                "SELECT person_id FROM muscle_strain\nUNION\nSELECT person_id FROM costochondritis")
    if p == "ekg_no_abnormal_code":
        return "SELECT person_id FROM ekg\nEXCEPT\nSELECT person_id FROM abnormal_ekg"
    if p == "no_further_cardiac_testing":
        return "SELECT person_id FROM chest_pain_dates\nEXCEPT\nSELECT person_id FROM extra_cardiac_testing"
    if p == "no_firm_dx":
        return ("SELECT person_id FROM chest_pain_dates\nEXCEPT\n" + _events(SEAN_DX, "R", concepts))
    raise KeyError(p)


def _indent(sql, n=4):
    return "\n".join((" " * n + ln) if ln else ln for ln in sql.split("\n"))


def _v03():
    """The text of the cohort query v0.3 in sql/chest_pain_cohort.sql: from its header comment to the end."""
    s = open(COHORT_SQL, encoding="utf-8").read()
    return s[s.index("-- v0.3"):].rstrip()


def cohort_query():
    """The cohort query v0.3 as it stands in the file: person_id, latest_interview_started_date."""
    return _v03()


def cohort_cte():
    """cohort: the cohort query v0.3, unchanged but for the last ORDER BY, as the CTEs that end in one row per person."""
    s = _v03()
    body = s[s.index("WITH cp_codes AS ("):s.index("SELECT op.person_id,")]
    final = re.sub(r"\s*ORDER BY[^;]*;\s*$", "", s[s.index("SELECT op.person_id,"):])
    body = re.sub(r"^WITH ", "", body.strip())
    return _indent(body.rstrip().rstrip(",")) + ",\n    cohort AS (\n" + _indent(final, 8) + "\n    )"


def validation_query(concepts, with_cohort=True):
    """The full query: one row per applicant with a chest pain event on or before R, with one 0/1 column per predicate and composite.
    with_cohort=False leaves out the cohort query, for a run where `cohort` is a table (the local check)."""
    ctes = []
    if with_cohort:
        ctes.append(cohort_cte())
    ctes.append("    chest_pain_dates AS (\n" + _indent(anchor_sql(concepts), 8) + "\n    )")
    for p in ORDER:
        ctes.append(f"    {p} AS (\n" + _indent(predicate_sql(p, concepts), 8) + "\n    )")
    flag_cols = ",\n".join(f"        CASE WHEN {p}.person_id IS NOT NULL THEN 1 ELSE 0 END AS {p}" for p in ORDER)
    joins = "\n".join(f"        LEFT JOIN {p} ON {p}.person_id = cp.person_id" for p in ORDER)
    ctes.append("    flags AS (\n"
                "        SELECT cp.person_id, cp.r_date, cp.c_date, cp.f_date, cp.months_out,\n" + flag_cols + "\n"
                "        FROM chest_pain_dates cp\n" + joins + "\n    )")
    comp_cols = ",\n".join(f"    CASE WHEN {expr}\n         THEN 1 ELSE 0 END AS {cid}" for cid, expr in COMPOSITES.items())
    return ("WITH\n" + ",\n".join(ctes) + "\n"
            "SELECT\n    f.*,\n    -- Composites\n" + comp_cols + "\n"
            "FROM flags f\n"
            "ORDER BY f.person_id;")
