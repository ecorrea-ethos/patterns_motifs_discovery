"""
Build the page of Sean's chest pain predicates and composites in the format of Infertility_Predicate_Engine.md (simple technical English)
from the workbook that Chestpain_Sean_predicates.ipynb writes (cell A9):

    outputs/sean_predicates_composites_prevalence.xlsx   ->   outputs/sean_chest_pain_predicates_composites.md

    /opt/miniconda3/envs/ethos_llm/bin/python make_sean_predicates_page.py
    python check_sean_page_style.py            # the style check (it runs lint_page.py on the prose of the page)

Sections, as in the Infertility page: Overview, Predicates and Composites, References, OMOP Implementation (the SQL of each predicate),
hit rates, Reference Concept IDs, Validation Query. Every number comes from the workbook. The sentences are written here, one per predicate
and composite. The SQL comes from sean_predicates_sql.py. Run the notebook again (the workbook changes), then run this script again.
"""
import os
import re
import pandas as pd

import sean_predicates_sql as S

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "outputs", "sean_predicates_composites_prevalence.xlsx")
OUT = os.path.join(HERE, "outputs", "sean_chest_pain_predicates_composites.md")

x = pd.read_excel(XLSX, sheet_name=None)
pred = x["predicates"].rename(columns={"Unnamed: 0": "predicate"}).set_index("predicate")
comp = x["composites"].set_index("id")
cuts = x["time cut-offs"]
pent = x["predicate entities"].set_index("predicate")
codesets = x["code sets"].set_index("code set")
ec = x["entity concepts"]
N = int(x["columns overlap"]["patients"].sum())                  # the population: chest pain code on or before R
N_ALL = int(codesets.loc["chest_pain", "patients, any date"])    # applicants with an application date (all have a chest pain code at some date)
N_LATE = N_ALL - N
f = lambda n: f"{int(n):,}"
pct = lambda n: f"{n / N * 100:.3f}%"
SW = "Sean's words"                                               # a column of the workbook
esc = lambda name: name.replace("_", "\\_")
assert list(pred.index) == S.ORDER, "the predicates of the workbook and of sean_predicates_sql.py differ"
assert list(comp.index) == list(S.COMPOSITES), "the composites of the workbook and of sean_predicates_sql.py differ"
concepts = {s: g["concept_id"].astype(int).tolist() for s, g in ec.groupby("code set", sort=False)}


def _inline_ids(sql):
    """The concept ids inside the IN (...) lists of a query, comments left out."""
    sql = re.sub(r"--[^\n]*", "", sql)
    return {int(i) for lst in re.findall(r"IN \(([^)]*)\)", sql) for i in re.findall(r"\d+", lst)}


# the ids in the SQL are the ids of the workbook: per predicate, and for the whole query
for _p, (_sets, _w) in S.EVENTS.items():
    assert _inline_ids(S.predicate_sql(_p, concepts)) == {c for s in _sets for c in concepts[s]}, _p
assert _inline_ids(S.predicate_sql("no_firm_dx", concepts)) == {c for s in S.SEAN_DX for c in concepts[s]}
assert _inline_ids(S.anchor_sql(concepts)) == set(concepts["chest_pain"])
assert _inline_ids(S.validation_query(concepts, with_cohort=False)) == set(ec["concept_id"].astype(int)), "inline ids differ from the workbook"

# ---------------------------------------------------------------- the sentences (simple technical English)
# predicate -> (title, definition, formula)
P = {
    "age_sex_high_risk": ("Age and sex in the high-risk range",
        "The applicant is a man older than 45, or a woman older than 55, on the date C. Age counts in completed years, "
        "so the applicant is 46 or more, or 56 or more. Sean wrote more than 45 and more than 55, and the limits are strict.",
        "age_sex_high_risk = (sex IS male AND age_at_C > 45) OR (sex IS female AND age_at_C > 55)"),
    "hx_cad": ("Previous coronary artery disease (CAD) diagnosis",
        "The applicant has at least one CAD diagnosis on or before the date C. The list holds angina, old and acute heart attack, "
        "and coronary atherosclerosis. The list has no history-status code and no procedure code, such as bypass or stent.",
        "hx_cad = condition IS IN CAD diagnoses AND event_date <= C"),
    "abnormal_ekg": ("Abnormal electrocardiogram (EKG) code present",
        "The applicant has at least one coded finding of an abnormal EKG on or before R. The code is a finding, not the test. "
        "It comes from the diagnosis code R94.31. Specific findings, such as bundle branch block, are not in the list.",
        "abnormal_ekg = condition IS abnormal EKG finding AND event_date <= R"),
    "extra_cardiac_testing": ("Additional cardiac testing after C",
        "The applicant has at least one cardiac test after the date C. The list holds echocardiography (heart ultrasound), "
        "stress tests, heart scans, coronary computed tomography angiography, and cardiac catheterization. "
        "The first-line EKG and troponin tests are not in the list. The data shows the test and not the result.",
        "extra_cardiac_testing = procedure IS IN additional cardiac tests AND event_date > C"),
    "rx_nitrates": ("Nitrate prescription present",
        "The applicant has at least one nitrate drug on or before R. Nitrates are heart drugs that widen blood vessels. "
        "The list holds nitroglycerin, isosorbide mononitrate, and isosorbide dinitrate, in every dose form. "
        "The dose forms include tablets under the tongue, patches, ointment, and injection, but no rectal ointment.",
        "rx_nitrates = drug IS IN nitrates AND event_date <= R"),
    "troponin": ("Troponin test present",
        "The applicant has at least one troponin test on or before R. Troponin is a blood test for injury to the heart muscle. "
        "The data does not show the type of test or the result.",
        "troponin = measurement IS troponin test AND event_date <= R"),
    "ekg": ("EKG test present",
        "The applicant has at least one EKG test on or before R. An EKG records the electrical signal of the heart. "
        "The list holds the routine 12-lead EKG and 2 screening codes. The data shows that the test happened and not the result.",
        "ekg = procedure IS EKG test AND event_date <= R"),
    "gerd": ("Gastroesophageal reflux disease (GERD) diagnosis present",
        "The applicant has at least one GERD diagnosis on or before R. GERD is acid reflux from the stomach into the food pipe. "
        "The list holds 4 diagnosis codes. Heartburn is one of them.",
        "gerd = condition IS GERD AND event_date <= R"),
    "anxiety": ("Anxiety diagnosis present",
        "The applicant has at least one anxiety diagnosis on or before R. The list holds 12 diagnosis codes. "
        "They range from generalized anxiety disorder to anxiety that a substance causes. Some codes are rare.",
        "anxiety = condition IS anxiety AND event_date <= R"),
    "gi_dx": ("GERD or other gastrointestinal (GI) diagnosis after C",
        "The applicant has at least one GERD diagnosis or other GI diagnosis after the date C. "
        "The other GI diagnoses are gastritis, esophagitis, ulcers, dyspepsia, gallstones, cholecystitis, and pancreatitis. "
        "The list has no reflux code in its GI part, because the GERD list holds it.",
        "gi_dx = condition IS IN (GERD, other GI diagnoses) AND C < event_date <= R"),
    "anxiety_later": ("Anxiety diagnosis after C",
        "The applicant has at least one anxiety diagnosis after the date C. The list is the anxiety list of the low-risk features.",
        "anxiety_later = condition IS anxiety AND C < event_date <= R"),
    "muscle_strain": ("Chest wall muscle strain after C",
        "The applicant has at least one strain or sprain diagnosis of the chest wall after the date C. "
        "The 4 codes are sprains of the thoracic back, the sternoclavicular joint, the chondrocostal joint, and the sternum. "
        "One code, thoracic back sprain, gives most of the applicants.",
        "muscle_strain = condition IS chest wall strain or sprain AND C < event_date <= R"),
    "costochondritis": ("Costochondritis after C",
        "The applicant has at least one costochondritis diagnosis after the date C. Costochondritis is a pain of the rib cartilage. "
        "The list holds 1 code, Tietze's disease.",
        "costochondritis = condition IS costochondritis AND C < event_date <= R"),
    "noncardiac_cp": ("Intercostal or non-cardiac chest pain after F",
        "The applicant has a code for pain of the space between the ribs after the date F, the first chest pain event. "
        "This code is also a chest pain code, so the test uses F and not C. "
        "The list has no code that says non-cardiac chest pain.",
        "noncardiac_cp = condition IS intercostal pain AND F < event_date <= R"),
    "explained_dx": ("Explained diagnosis coded later",
        "The applicant meets at least one of 4 predicates. These are anxiety, GI diagnosis, chest wall muscle strain, "
        "and costochondritis, all after C. The row of the draft calls these the later coded diagnoses.",
        "explained_dx = anxiety_later OR gi_dx OR muscle_strain OR costochondritis"),
    "ekg_no_abnormal_code": ("EKG without an abnormal code",
        "The applicant has an EKG test and no abnormal EKG code on or before R. This is a proxy for a normal EKG. "
        "The claims data has no test results, so the data does not show a normal EKG.",
        "ekg_no_abnormal_code = ekg AND NOT abnormal_ekg"),
    "no_further_cardiac_testing": ("No further cardiac testing",
        "The applicant has no additional cardiac test after the date C.",
        "no_further_cardiac_testing = NOT extra_cardiac_testing"),
    "no_firm_dx": ("No firm diagnosis",
        "None of the diagnoses that the draft lists appears in the history of the applicant on or before R. "
        "The diagnoses are CAD, GERD, other GI diagnoses, anxiety, chest wall muscle strain, costochondritis, "
        "and intercostal or non-cardiac chest pain. The time of the diagnosis does not matter. "
        "The coded abnormal EKG finding is a feature of the draft and not a diagnosis, so it does not count.",
        "no_firm_dx = NOT (hx_cad OR gerd OR anxiety OR gi_dx OR muscle_strain OR costochondritis OR noncardiac_cp), all events up to R"),
}
# composite -> (title, definition)
C = {
    "high_risk_any": ("Any high-risk feature",
        "The applicant meets at least one of 5 predicates: age and sex, previous CAD diagnosis, abnormal EKG code, "
        "additional cardiac testing, and nitrate prescription."),
    "A1": ("No high-risk feature and more than 6 months out",
        "The applicant meets none of the 5 high-risk predicates. The last chest pain event is more than 6 months before R."),
    "A2": ("EKG without an abnormal code and no CAD history",
        "The applicant has an EKG test and no abnormal EKG code. The applicant has no previous CAD diagnosis. "
        "The draft says any time, so months out does not matter."),
    "A3": ("No further cardiac testing, no CAD history, more than 6 months out",
        "The applicant has no additional cardiac test after C and no previous CAD diagnosis. "
        "The last chest pain event is more than 6 months before R."),
    "A4": ("Explained diagnosis coded later and no CAD history",
        "The applicant has an explained diagnosis coded after C. The applicant has no previous CAD diagnosis. "
        "The draft says any time, so months out does not matter."),
    "A5": ("Intercostal or non-cardiac chest pain noted later",
        "The applicant has a code for pain of the space between the ribs after the first chest pain event F. "
        "The draft says any time, so months out does not matter."),
    "A6": ("Coded more than 2 years ago",
        "The last chest pain event is more than 24 months before R. The row has no other condition."),
    "R1": ("Any high-risk feature and less than 6 months out",
        "The applicant meets at least one of the 5 high-risk predicates. The last chest pain event is less than 6 months before R."),
    "R2": ("No firm diagnosis and less than 6 months out",
        "The applicant meets the predicate no firm diagnosis. The last chest pain event is less than 6 months before R."),
    "D1": ("CAD history and less than 1 year out",
        "The applicant has any history of CAD. The last chest pain event is less than 12 months before R. "
        "The time runs from the chest pain event to the application date, not from the CAD diagnosis."),
}

# ---------------------------------------------------------------- Sean's draft, as written
RAW_HIGH = ["Male > 45, Female >55", "Previous Dx of CAD", "Current TO Rating (not in Banner manual as a comorbid condition)", "Abnormal EKG",
            "Additional Cardiac Testing (Echo, Cath, CCTA, etc.) – or any abnormal testing", "Rx Nitrates"]
RAW_LOW = ["Troponin Testing", "EKG", "GERD", "Anxiety"]
RAW_ROWS = [  # id, column, text as written
    ("A1", "APPROVE", "No High Risk Features and >6 months out"),
    ("A2", "APPROVE", "Any time and EKG normal – no Hx of CAD"),
    ("A3", "APPROVE", "No further cardiac testing – no Hx of CAD and >6 months out"),
    ("A4", "APPROVE", "Any time, no Hx of CAD and later coded as Anxiety (suggest to rate as anxiety – Discuss with Dr. Z) , GERD, other GI related Dx, muscle strain, costochondritis"),
    ("A5", "APPROVE", "Any time, later noted as intercostal or non-cardiac chest pain"),
    ("A6", "APPROVE", "Coded > 2 years ago"),
    ("--", "APPROVE", "All cardiac testing within normal limits (wnl)"),
    ("R1", "REFER", "Any High Risk Features and < 6 months"),
    ("R2", "REFER", "No firm diagnosis and < 6 months"),
    ("D1", "DECLINE", "Hx of CAD and < 1 year"),
]


def draft_block():
    out = ["CHEST PAIN WORKFLOW DRAFT (Sean), as written. The ids of the rows are added.", "", "HIGH-RISK FEATURES"]
    out += [f"    {t}" for t in RAW_HIGH] + ["", "LOW-RISK FEATURES"] + [f"    {t}" for t in RAW_LOW]
    for col in ["APPROVE", "REFER", "DECLINE"]:
        out += ["", col] + [f"    {rid:<3} {txt}" for rid, c, txt in RAW_ROWS if c == col]
    return "\n".join(out)


def draft_item(words):
    return f"The draft item is `{words}`."


L = []
a = L.append

# ================================================================ title and overview
a("# Chest Pain Predicate Engine")
a("")
a("*Working Draft — November 2026*")
a("")
a("---")
a("")
a("## Overview")
a("")
a("This document defines the predicates and composites of the chest pain underwriting view of Sean. "
  "It turns the Chest Pain Workflow Draft into yes-or-no questions about the claims history of an applicant. "
  "The claims history comes from the Ethos clinical database in the Observational Medical Outcomes Partnership (OMOP) common data model. "
  "The document gives the OMOP implementation of each predicate, with the concept identifiers (IDs) of each code set. "
  f"It reports how often each predicate and composite is true for {f(N)} applicants with a chest pain event on or before the application date. "
  "The counts are a first look at the data and not a validation.")
a("")
a("---")
a("")

# ================================================================ predicates and composites
a("## Predicates and Composites")
a("")
a("This section defines the building blocks of the chest pain predicate engine. "
  "It covers the predicates, which are individual checks against the claims history of an applicant. "
  "It covers the composites, which combine predicates and time into the rows of the draft of Sean. "
  "This section contains no underwriting logic. The underwriter reviews it to check that the definitions match the draft.")
a("")
a("### Index Date and Anchors")
a("")
a("Every predicate reads the claims history of the applicant up to one index date. The index date R is the application date of the applicant. "
  "An applicant with several policies has one application date, the latest interview start of the policies. "
  "The method ignores every event after R.")
a("")
a("The anchor is the chest pain event. C is the date of the last chest pain event on or before R. F is the date of the first chest pain event. "
  "Months out is the time from C to R, in months of 30.4375 days.")
a("")
a("**Chest pain present.** The applicant has at least one chest pain event on or before R. "
  "The list holds chest pain, precordial pain, chest pain on breathing, and pain of the space between the ribs. "
  f"Every count in this document covers the {f(N)} applicants with this predicate.")
a("")
a("`chest_pain = condition IS chest pain AND event_date <= R`")
a("")
a("`C = MAX(event_date) over chest pain events up to R`")
a("")
a("`F = MIN(event_date) over chest pain events up to R`")
a("")
a("`months_out = (R - C) / 30.4375`")
a("")
a("---")
a("")
a("### Atomic Predicates")
a("")
a("A predicate answers one question about the claims history of an applicant. It returns true or false. "
  "Atomic predicates check directly against the code sets. Derived predicates combine other predicates. "
  "The order follows the groups of the draft: high-risk features, low-risk features, features coded later, and derived predicates.")
a("")
a("The rule of a predicate says which events count. *Up to R* means events on or before R. *On or before C* means events on or before C. "
  "*After C* means events after C and up to R. Age and sex come from the date C.")
for p in S.ORDER:
    title, text, formula = P[p]
    a("")
    a(f"**{title}.** {text} {draft_item(pent.loc[p, SW])}")
    a("")
    a(f"`{formula}`")
a("")
a("---")
a("")
a("### Composites")
a("")
a("A composite combines predicates and time into one row of the draft. The id of a composite keeps the id of the row in the draft. "
  "The first letter of the id names the column of the draft: A, R, or D, from left to right. "
  "The draft has no order between its rows, so one applicant sometimes meets rows of more than one column. "
  "The signs more than and less than are strict. An applicant at exactly 6 months is in neither row.")
for cid in comp.index:
    title, text = C[cid]
    row = comp.loc[cid]
    a("")
    extra = "" if cid == "high_risk_any" else " " + draft_item(row[SW])
    a(f"**{cid}: {title}.** {text}{extra}")
    a("")
    a(f"`{cid} = {row['formula'].replace('months out', 'months_out')}`")
a("")
a("> **Note:** The draft has items that claims data cannot show. Claims hold codes and dates, with no test result and no rating. "
  "The document does not count the current `TO` rating, any abnormal testing, EKG normal, and all cardiac testing within normal limits. "
  "One proxy replaces EKG normal: an EKG and no abnormal EKG code.")
a("")
a("---")
a("")
a("### Decisions and Open Items")
a("")
a("The project team settled these items with Zack on 4 November 2026.")
a("")
for t in [
    "**Age limits.** The limits are strict. The document uses older than 45 for a man and older than 55 for a woman, in completed years.",
    "**Less than 1 year.** The applicant has any history of CAD. The last chest pain event is less than 12 months before the application date.",
    "**No firm diagnosis.** None of the diagnoses that the draft lists appears on or before the application date.",
]:
    a(f"- {t}")
a("")
a("Sean must settle these items.")
a("")
for t in [
    "**Current rating.** The document does not count the current `TO` rating. The claims data holds no rating. Sean must say what `TO` means and where the rating sits.",
    "**Later coded.** The document counts diagnoses strictly after C. The intercostal code counts after F, because it is a chest pain code.",
    "**Abnormal EKG.** The document counts only the coded finding. A test code does not show the result.",
    "**Nitrates.** The list names the 3 drugs in every dose form, injection included. The document does not check where the claims come from.",
    "**Muscle strain.** The list holds chest wall sprains only. A strain of another body part says nothing about chest pain.",
]:
    a(f"- {t}")
a("")
a("---")
a("")
a("### References")
a("")
a("- Chest Pain Workflow Draft of Sean, in the block below as written  ")
a("- Cohort query `sql/chest_pain_cohort.sql`, version 0.3: the persons and the application date R  ")
a("- Notebook `Chestpain_Sean_predicates.ipynb`, version 3.1: the counts of this document  ")
a("- Code sets `codesets_sean_v2.yaml`: the concepts behind each predicate  ")
a("")
a("```")
a(draft_block())
a("```")
a("")
a("---")
a("")

# ================================================================ OMOP implementation
a("## OMOP Implementation")
a("")
a("This section gives the implementation of each predicate as a Structured Query Language (SQL) query on the Ethos clinical database. "
  "Each query returns the distinct person identifiers for which the predicate is true. "
  "A person that is absent from the result is false. A derived predicate reads the queries of the predicates it combines, by their names.")
a("")
a("Each query lists the concept identifiers of its code sets. A comment names each code set and counts its concepts. "
  "A code set is a list of standard concepts for one clinical idea. The Reference Concept IDs below give the name of every concept.")
a("")
a("The code sets use concepts of four vocabularies. "
  "The list starts with Systematized Nomenclature of Medicine Clinical Terms (SNOMED). "
  "It continues with Current Procedural Terminology, fourth edition (CPT4), Healthcare Common Procedure Coding System (HCPCS), and RxNorm.")
a("")
a("All queries reference the `ethos_production.omop_54` schema with `master_` prefixed clinical tables. "
  "The cohort is a set of persons, so the queries use the person identifier and not the policy identifier. "
  "Each query reads the events of a person up to the application date R and ignores later events.")
a("")
a("### Cohort")
a("")
a("The cohort is the query version 0.3 of the file `sql/chest_pain_cohort.sql`, without change. "
  "It returns one row per Ethos person with a chest pain code, with the latest interview start date of the policies of the person. "
  "That date is the application date R. The Validation Query holds the same text as its first step, named `cohort`.")
a("")
a("```sql")
a(S.cohort_query())
a("```")
a("")
a("### Anchor")
a("")
a("The table `chest_pain_dates` holds R, F, C, and months out for each person with a chest pain event on or before R. "
  "It reads the cohort. A person with chest pain only after R has no row, so every query leaves that person out.")
a("")
a("**chest\\_pain\\_dates.**")
a("")
a("```sql")
a(S.anchor_sql(concepts))
a("```")
a("")
a("### Atomic Predicates")
for p in S.ORDER:
    a("")
    a(f"**{esc(p)}.**")
    a("")
    a("```sql")
    a(S.predicate_sql(p, concepts))
    a("```")
a("")
a("---")
a("")

# ================================================================ hit rates
a(f"### Predicate and Composite Validation — Hit Rates Against the Chest Pain Cohort (n={f(N)})")
a("")
a(f"The tables below report how often each predicate and composite is true for the {f(N)} applicants with a chest pain event on or before R. "
  f"The cohort query gives {f(N_ALL)} persons with an application date. "
  f"The other {f(N_LATE)} persons have chest pain events only after R, and every count leaves them out. "
  "See the Validation Query section below for the full query.")
a("")
a("**Atomic Predicates**")
a("")
a("| Predicate | n | % of total |")
a("| :---- | :---- | :---- |")
for p in S.ORDER:
    a(f"| {esc(p)} | {f(pred.loc[p, 'n'])} | {pct(pred.loc[p, 'n'])} |")
a("")
a("**Composites**")
a("")
a("| Composite | n | % of total |")
a("| :---- | :---- | :---- |")
for cid in comp.index:
    a(f"| {esc(cid)} | {f(comp.loc[cid, 'n'])} | {pct(comp.loc[cid, 'n'])} |")
a("")
a("**Time Cut-offs**")
a("")
a("The time rows depend on months out. The table repeats them at other cut-offs. The rows of the draft use 6 months, 12 months, and 24 months.")
a("")
a("| Cut-off (months) | A1 | R1 | R2 | D1 | A6 |")
a("| :---- | :---- | :---- | :---- | :---- | :---- |")
for _, r in cuts.iterrows():
    a(f"| {int(r.iloc[0])} | {f(r.iloc[1])} | {f(r.iloc[2])} | {f(r.iloc[3])} | {f(r.iloc[4])} | {f(r.iloc[5])} |")
a("")
for t in ["A1: no high-risk feature and more than the cut-off.", "R1: any high-risk feature and less than the cut-off.",
          "R2: no firm diagnosis and less than the cut-off.", "D1: CAD history and less than the cut-off.",
          "A6: coded more than the cut-off ago."]:
    a(f"- {t}  ")
a("")
a("> **Note:** The counts come from the notebook `Chestpain_Sean_predicates.ipynb`. "
  "A local test of the Validation Query on the same extract, outside Snowflake, gives the same counts for all predicates, composites, and cut-offs. "
  "A run in Snowflake is the final check. The counts describe the claims data and do not validate the rules.")
a("")
a("---")
a("")

# ================================================================ reference concept ids
a("### Reference Concept IDs")
a("")
a("The table lists every concept of every code set, with the concepts of most applicants first. "
  "The queries show the same concept identifiers inline. The last two rows are the gender concepts of the age predicate.")
a("")
a("| Code set | Concept | Type | Concept ID |")
a("| :---- | :---- | :---- | :---- |")
for _, r in ec.iterrows():
    a(f"| {esc(r['code set'])} | {str(r['concept_name']).replace('|', '/')} | {r['domain_id']} · {r['vocabulary_id']} | {int(r['concept_id'])} |")
for sex, gid, _ in S.AGE:
    a(f"| age\\_sex\\_high\\_risk | {sex.capitalize()} | Gender · Gender | {gid} |")
a("")
a("---")
a("")

# ================================================================ validation query
a("## Validation Query")
a("")
a("This section contains the full query that evaluates all predicates and composites for every person in the cohort. "
  "The query returns one row per person. Each predicate and each composite becomes one column, with 1 for true and 0 for false. "
  "The columns work like a one-hot encoding. A person with several true predicates has several 1s. "
  "The sum of each column is the count in the hit-rate tables above.")
a("")
a("### Backtest Population")
a("")
a("- Cohort: the cohort query version 0.3 (step `cohort`), Ethos persons with chest pain diagnosis codes R07.2, R07.8, R07.82, R07.89, or R07.9, confirmed in OMOP  ")
a("- Policies: policies with a product of the list 1, 5, 14, 15, 21, 25 and an underwriting process other than `TBD`  ")
a("- Index date: the latest interview start date over the policies of the person  ")
a(f"- Scope: persons with a chest pain event on or before the index date (n={f(N)} of {f(N_ALL)})  ")
a("")
a("### Query")
a("")
a("```sql")
a(S.validation_query(concepts))
a("```")
a("")

open(OUT, "w", encoding="utf-8").write("\n".join(L))
print(f"wrote {OUT}: {len(L)} lines; population {N:,}; {N_LATE} only after R")
