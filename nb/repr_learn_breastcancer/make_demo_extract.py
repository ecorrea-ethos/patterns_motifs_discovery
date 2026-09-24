"""
make_demo_extract.py — write a synthetic `omop_extract/` with the real OMOP_54 schema.

Purpose: the notebooks should run before you have Snowflake access, and they should
run against data where you already know the answer. Unsupervised algorithms always
return something, so you need at least one case with planted ground truth to tell
"found structure" apart from "found noise".

Output is byte-compatible with `ethos_omop.load_events()`: same tables, same column
names, integer concept_ids resolved through a `concept.csv`, plus a `truth.csv` that
ONLY the demo has. Real extracts have no truth file — that is the whole problem.

    python make_demo_extract.py [n_patients] [out_dir]
"""

import os, sys, csv
import numpy as np
import pandas as pd

OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "omop_extract"
N        = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEED     = 42

# -------------------------------------------------------------- concept table
# (concept_name, domain_id, vocabulary_id, concept_class_id)
# Names match the regexes in ethos_omop.CODESETS so `build_codesets` resolves them.
CONCEPTS = [
    # drugs
    ("Letrozole 2.5 MG Oral Tablet",        "Drug", "RxNorm", "Clinical Drug"),
    ("Anastrozole 1 MG Oral Tablet",        "Drug", "RxNorm", "Clinical Drug"),
    ("Tamoxifen 20 MG Oral Tablet",         "Drug", "RxNorm", "Clinical Drug"),
    ("Clomiphene citrate 50 MG Oral Tablet","Drug", "RxNorm", "Clinical Drug"),
    ("Chorionic gonadotropin Injection",    "Drug", "RxNorm", "Clinical Drug"),
    ("Metformin hydrochloride 500 MG Oral Tablet", "Drug", "RxNorm", "Clinical Drug"),
    ("Semaglutide 1 MG/ML Injection",       "Drug", "RxNorm", "Clinical Drug"),
    ("Insulin glargine 100 UNT/ML",         "Drug", "RxNorm", "Clinical Drug"),
    ("Metoprolol succinate 50 MG",          "Drug", "RxNorm", "Clinical Drug"),
    ("Atorvastatin 20 MG Oral Tablet",      "Drug", "RxNorm", "Clinical Drug"),
    ("Sertraline 50 MG Oral Tablet",        "Drug", "RxNorm", "Clinical Drug"),
    ("Lisinopril 10 MG Oral Tablet",        "Drug", "RxNorm", "Clinical Drug"),
    ("Omeprazole 20 MG Oral Capsule",       "Drug", "RxNorm", "Clinical Drug"),
    ("Ibuprofen 400 MG Oral Tablet",        "Drug", "RxNorm", "Clinical Drug"),
    ("Amoxicillin 500 MG Oral Capsule",     "Drug", "RxNorm", "Clinical Drug"),
    ("Cetirizine 10 MG Oral Tablet",        "Drug", "RxNorm", "Clinical Drug"),
    # conditions
    ("Malignant neoplasm of breast",        "Condition", "SNOMED", "Clinical Finding"),
    ("Lump of breast",                      "Condition", "SNOMED", "Clinical Finding"),
    ("Female infertility",                  "Condition", "SNOMED", "Clinical Finding"),
    ("Chest pain",                          "Condition", "SNOMED", "Clinical Finding"),
    ("Anxiety disorder",                    "Condition", "SNOMED", "Clinical Finding"),
    ("Panic attack",                        "Condition", "SNOMED", "Clinical Finding"),
    ("Coronary artery disease",             "Condition", "SNOMED", "Clinical Finding"),
    ("Type 2 diabetes mellitus",            "Condition", "SNOMED", "Clinical Finding"),
    ("Diabetic neuropathy",                 "Condition", "SNOMED", "Clinical Finding"),
    ("Essential hypertension",              "Condition", "SNOMED", "Clinical Finding"),
    ("Gastroesophageal reflux disease",     "Condition", "SNOMED", "Clinical Finding"),
    ("Low back pain",                       "Condition", "SNOMED", "Clinical Finding"),
    ("Allergic rhinitis",                   "Condition", "SNOMED", "Clinical Finding"),
    ("Upper respiratory infection",         "Condition", "SNOMED", "Clinical Finding"),
    ("Obesity",                             "Condition", "SNOMED", "Clinical Finding"),
    # procedures
    ("Mastectomy",                          "Procedure", "SNOMED", "Procedure"),
    ("Mammography",                         "Procedure", "SNOMED", "Procedure"),
    ("Biopsy of breast",                    "Procedure", "SNOMED", "Procedure"),
    ("Electrocardiography",                 "Procedure", "SNOMED", "Procedure"),
    ("Cardiac stress test",                 "Procedure", "SNOMED", "Procedure"),
    ("Coronary angiography",                "Procedure", "SNOMED", "Procedure"),
    ("Ultrasonography of pelvis",           "Procedure", "SNOMED", "Procedure"),
    ("Influenza vaccination",               "Procedure", "SNOMED", "Procedure"),
    ("General health examination",           "Procedure", "SNOMED", "Procedure"),
    # measurements
    ("Troponin I cardiac measurement",      "Measurement", "LOINC", "Lab Test"),
    ("Hemoglobin A1c measurement",          "Measurement", "LOINC", "Lab Test"),
    ("Lipid panel",                         "Measurement", "LOINC", "Lab Test"),
    ("Vitamin D measurement",               "Measurement", "LOINC", "Lab Test"),
    # visits + gender
    ("Emergency Room Visit",                "Visit", "Visit", "Visit"),
    ("Office Visit",                        "Visit", "Visit", "Visit"),
    ("FEMALE",                              "Gender", "Gender", "Gender"),
    ("MALE",                                "Gender", "Gender", "Gender"),
]

BASE_ID = 4000000            # arbitrary; real concept_ids come from Athena
CID = {name: BASE_ID + i for i, (name, *_ ) in enumerate(CONCEPTS)}
C = CID.get   # shorthand

# ------------------------------------------------------------------ archetypes
# (concept_name, domain, mean days after previous step)
ARCHETYPES = {
    "FERTILITY_LETROZOLE": dict(sex="FEMALE", age=(26, 38), chain=[
        ("Female infertility", "Condition", 0),
        ("Clomiphene citrate 50 MG Oral Tablet", "Drug", 45),
        ("Letrozole 2.5 MG Oral Tablet", "Drug", 60),
        ("Chorionic gonadotropin Injection", "Drug", 20),
        ("Ultrasonography of pelvis", "Procedure", 15)],
        late=[("Malignant neoplasm of breast", "Condition", 2400, 0.55)]),

    "ONCOLOGY_LETROZOLE": dict(sex="FEMALE", age=(52, 74), chain=[
        ("Lump of breast", "Condition", 0),
        ("Mammography", "Procedure", 20),
        ("Biopsy of breast", "Procedure", 25),
        ("Malignant neoplasm of breast", "Condition", 15),
        ("Mastectomy", "Procedure", 40),
        ("Letrozole 2.5 MG Oral Tablet", "Drug", 35),
        ("Anastrozole 1 MG Oral Tablet", "Drug", 400)], late=[]),

    "DM_STABLE": dict(sex=None, age=(45, 70), chain=[
        ("Type 2 diabetes mellitus", "Condition", 0),
        ("Metformin hydrochloride 500 MG Oral Tablet", "Drug", 20),
        ("Hemoglobin A1c measurement", "Measurement", 180),
        ("Metformin hydrochloride 500 MG Oral Tablet", "Drug", 95),
        ("Hemoglobin A1c measurement", "Measurement", 190),
        ("Metformin hydrochloride 500 MG Oral Tablet", "Drug", 95)], late=[]),

    "DM_PROGRESSIVE": dict(sex=None, age=(48, 72), chain=[
        ("Type 2 diabetes mellitus", "Condition", 0),
        ("Metformin hydrochloride 500 MG Oral Tablet", "Drug", 20),
        ("Hemoglobin A1c measurement", "Measurement", 200),
        ("Semaglutide 1 MG/ML Injection", "Drug", 240),
        ("Hemoglobin A1c measurement", "Measurement", 200),
        ("Insulin glargine 100 UNT/ML", "Drug", 260),
        ("Diabetic neuropathy", "Condition", 300)], late=[]),

    "CHEST_PAIN_ANXIETY": dict(sex=None, age=(24, 46), chain=[
        ("Chest pain", "Condition", 0),
        ("Emergency Room Visit", "Visit", 0),
        ("Electrocardiography", "Procedure", 0),
        ("Anxiety disorder", "Condition", 30),
        ("Sertraline 50 MG Oral Tablet", "Drug", 15),
        ("Panic attack", "Condition", 120)], late=[]),

    "CHEST_PAIN_CARDIAC": dict(sex=None, age=(54, 78), chain=[
        ("Chest pain", "Condition", 0),
        ("Emergency Room Visit", "Visit", 0),
        ("Electrocardiography", "Procedure", 0),
        ("Troponin I cardiac measurement", "Measurement", 1),
        ("Cardiac stress test", "Procedure", 20),
        ("Coronary angiography", "Procedure", 30),
        ("Metoprolol succinate 50 MG", "Drug", 10),
        ("Atorvastatin 20 MG Oral Tablet", "Drug", 10),
        ("Coronary artery disease", "Condition", 60)], late=[]),

    "BACKGROUND": dict(sex=None, age=(20, 80), chain=[], late=[]),
}

AMBIENT = [
    ("General health examination", "Procedure"), ("Lipid panel", "Measurement"),
    ("Essential hypertension", "Condition"), ("Lisinopril 10 MG Oral Tablet", "Drug"),
    ("Upper respiratory infection", "Condition"), ("Amoxicillin 500 MG Oral Capsule", "Drug"),
    ("Low back pain", "Condition"), ("Ibuprofen 400 MG Oral Tablet", "Drug"),
    ("Allergic rhinitis", "Condition"), ("Cetirizine 10 MG Oral Tablet", "Drug"),
    ("Office Visit", "Visit"), ("Influenza vaccination", "Procedure"),
    ("Vitamin D measurement", "Measurement"), ("Gastroesophageal reflux disease", "Condition"),
    ("Omeprazole 20 MG Oral Capsule", "Drug"), ("Obesity", "Condition"),
]

MIX = {"FERTILITY_LETROZOLE": .06, "ONCOLOGY_LETROZOLE": .08, "DM_STABLE": .12,
       "DM_PROGRESSIVE": .09, "CHEST_PAIN_ANXIETY": .10,
       "CHEST_PAIN_CARDIAC": .08, "BACKGROUND": .47}

DOMAIN_TABLE = {
    "Visit":       ("master_visit_occurrence",     "visit_occurrence_id",     "visit_concept_id",       "visit_start_date"),
    "Condition":   ("master_condition_occurrence", "condition_occurrence_id", "condition_concept_id",   "condition_start_date"),
    "Drug":        ("master_drug_exposure",        "drug_exposure_id",        "drug_concept_id",        "drug_exposure_start_date"),
    "Procedure":   ("master_procedure_occurrence", "procedure_occurrence_id", "procedure_concept_id",   "procedure_date"),
    "Measurement": ("master_measurement",          "measurement_id",          "measurement_concept_id", "measurement_date"),
}
DEATH_HAZARD = {"BACKGROUND": .0012, "DM_STABLE": .0018, "DM_PROGRESSIVE": .0045,
                "CHEST_PAIN_ANXIETY": .0011, "CHEST_PAIN_CARDIAC": .0060,
                "FERTILITY_LETROZOLE": .0004, "ONCOLOGY_LETROZOLE": .0052}
CENSOR = pd.Timestamp("2026-06-30")


def main():
    rng = np.random.default_rng(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)

    names = list(MIX); probs = np.array([MIX[k] for k in names]); probs /= probs.sum()
    assigned = rng.choice(names, size=N, p=probs)

    persons, events, deaths, truth = [], [], [], []

    for i in range(N):
        pid  = 100000 + i
        arch = assigned[i]
        spec = ARCHETYPES[arch]
        age  = int(rng.integers(*spec["age"]))
        sex  = spec["sex"] or ("FEMALE" if rng.random() < .52 else "MALE")
        birth = pd.Timestamp(year=2026 - age, month=int(rng.integers(1, 13)), day=15)

        span = int(rng.integers(3 * 365, 10 * 365))
        end   = CENSOR - pd.Timedelta(days=int(rng.integers(0, 730)))
        start = end - pd.Timedelta(days=span)

        persons.append(dict(person_id=pid, gender_concept_id=C(sex),
                            year_of_birth=birth.year, month_of_birth=birth.month,
                            day_of_birth=birth.day, birth_datetime=birth.date(),
                            race_concept_id=0, ethnicity_concept_id=0))

        def emit(name, domain, date):
            events.append((pid, domain, C(name), pd.Timestamp(date).date()))

        for _ in range(int(rng.poisson(9)) + 2):
            name, dom = AMBIENT[rng.integers(len(AMBIENT))]
            emit(name, dom, start + pd.Timedelta(days=int(rng.integers(0, span))))

        if spec["chain"]:
            t = start + pd.Timedelta(days=int(rng.integers(0, max(1, int(span * .55)))))
            for name, dom, gap in spec["chain"]:
                if gap > 0:
                    t += pd.Timedelta(days=max(1, int(rng.gamma(2.0, gap / 2.0))))
                if t > end:
                    break
                if rng.random() < 0.25:          # dropped claim
                    continue
                emit(name, dom, t)
                if dom == "Drug" and rng.random() < .6:
                    for k in range(1, int(rng.integers(2, 7))):
                        t2 = t + pd.Timedelta(days=30 * k + int(rng.integers(-4, 5)))
                        if t2 <= end:
                            emit(name, dom, t2)
            for name, dom, gap, p in spec["late"]:
                if rng.random() < p:
                    t2 = t + pd.Timedelta(days=int(rng.normal(gap, 200)))
                    if start <= t2 <= end:
                        emit(name, dom, t2)

        months = min(rng.exponential(1 / DEATH_HAZARD[arch]), 2000.0)
        dd = start + pd.Timedelta(days=float(months) * 30.44)
        if dd <= CENSOR:
            deaths.append(dict(person_id=pid, death_date=dd.date(),
                               death_type_concept_id=0))
        truth.append(dict(person_id=pid, archetype=arch))

    # ---- write person / death / truth
    pd.DataFrame(persons).to_csv(f"{OUT_DIR}/person.csv", index=False)
    pd.DataFrame(deaths or [{"person_id": None, "death_date": None,
                             "death_type_concept_id": None}]).dropna() \
      .to_csv(f"{OUT_DIR}/death.csv", index=False)
    pd.DataFrame(truth).to_csv(f"{OUT_DIR}/truth.csv", index=False)

    # ---- write domain tables
    ev = pd.DataFrame(events, columns=["person_id", "domain", "concept_id", "date"])
    for domain, (table, idcol, cidcol, datecol) in DOMAIN_TABLE.items():
        sub = ev[ev.domain == domain].reset_index(drop=True)
        out = pd.DataFrame({
            idcol: np.arange(1, len(sub) + 1),
            "person_id": sub.person_id,
            cidcol: sub.concept_id,
            datecol: sub.date,
            f"{cidcol.replace('_concept_id', '')}_source_concept_id": 0,
        })
        out.to_csv(f"{OUT_DIR}/{table}.csv", index=False)
        print(f"{table}: {len(out)} rows")

    # observation table: present but empty of useful rows (ethos_dip is excluded upstream)
    pd.DataFrame(columns=["observation_id", "person_id", "observation_concept_id",
                          "observation_date", "observation_source_concept_id"]) \
      .to_csv(f"{OUT_DIR}/master_observation.csv", index=False)

    # ---- concept table
    rows = [dict(concept_id=cid, concept_name=name, domain_id=dom,
                 vocabulary_id=voc, concept_class_id=cls, standard_concept="S",
                 concept_code=f"{100000 + i}", valid_start_date="1970-01-01",
                 valid_end_date="2099-12-31", invalid_reason="")
            for i, ((name, dom, voc, cls), cid)
            in enumerate(zip(CONCEPTS, [CID[n] for n, *_ in CONCEPTS]))]
    pd.DataFrame(rows).to_csv(f"{OUT_DIR}/concept.csv", index=False)
    print(f"concept: {len(rows)} rows")

    # ---- standard-name symlinks for meds_etl_omop
    for master, standard in [
            ("master_visit_occurrence", "visit_occurrence"),
            ("master_condition_occurrence", "condition_occurrence"),
            ("master_drug_exposure", "drug_exposure"),
            ("master_procedure_occurrence", "procedure_occurrence"),
            ("master_measurement", "measurement"),
            ("master_observation", "observation")]:
        dst = os.path.join(OUT_DIR, f"{standard}.csv")
        if not os.path.exists(dst):
            try:
                os.symlink(f"{master}.csv", dst)
            except OSError:                    # filesystem without symlinks
                import shutil
                shutil.copy(os.path.join(OUT_DIR, f"{master}.csv"), dst)

    print(f"\nwrote {N} patients, {len(ev)} events, {len(deaths)} deaths -> {OUT_DIR}/")
    print("truth.csv exists ONLY in the demo extract. Real extracts have no labels.")


if __name__ == "__main__":
    main()
