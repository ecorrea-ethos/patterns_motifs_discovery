"""
Write ONE consolidated chest pain page: outputs/chest_pain_all_patterns.md

    python make_chest_pain_all_patterns.py       # env ethos_llm (pandas, openpyxl)

Predicates once (shared by all 8 care patterns, c0-c7), then the composites of every care pattern, then the
coverage tables and the references. No triage and no underwriting wording: the page is a clinical grouping of codes.
Everything is read from outputs/final_table_chestpain_k8_AHA.xlsx and the files named in make_bundle_engine_docs.py;
nothing is measured here. Wording and rules come from make_bundle_engine_docs.py (ENT, NOUN, BUNDLES).
"""
import os, re
import make_bundle_engine_docs as m

OUT_FILE = os.path.join(m.OUTPUTS, "chest_pain_all_patterns.md")
ORDER = ["c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7"]
PAGE_NAME = {"c0": "outpatient check-up and elective cardiac testing", "c1": "prescriptions for acute and chronic illness",
             "c2": "women's health and urinary tract", "c3": "ED work-up", "c4": "stomach and bowel work-up and cancer screening",
             "c5": "muscle and bone care and physical therapy", "c6": "nutrition and hormone blood tests", "c7": "acute respiratory infection"}
FAMILIES = [
    ("Diagnoses", ["hld", "gerd", "lbp", "cough", "uri", "pharyngitis"]),
    ("Lab tests", ["trop", "lipase", "lipid", "venip", "cmp", "cbc", "hba1c", "b12", "vitd", "t4", "iron", "ferritin", "upt", "sti", "cyto", "antigen", "path"]),
    ("Procedures, imaging, and visits", ["ecg", "cxr", "ivpush", "genexam", "gyn", "periodic", "crc", "egd", "therproc", "ther97110", "manual", "theract"]),
    ("Drugs", ["methylpred", "amoxclav", "azithro", "ppi", "pred"]),
]


def roles():
    """entity key -> {care pattern: set('entity', 'step')}"""
    r = {}
    for cn in ORDER:
        B = m.BUNDLES[cn]
        for k, _ in B["services"]:
            r.setdefault(k, {}).setdefault(cn, set()).add("entity")
        for steps in B["pats"]:
            for q in steps:
                if q not in ("cp", "x2"):
                    r.setdefault(q, {}).setdefault(cn, set()).add("step")
    return r


def role_text(rs):
    out = []
    for cn in ORDER:
        if cn in rs:
            v = rs[cn]
            out.append(f"{cn} ({'entity and step' if len(v) == 2 else 'entity' if 'entity' in v else 'step'})")
    return ", ".join(out)


def build():
    L = []
    a = L.append
    R = roles()
    flat = [k for _, ks in FAMILIES for k in ks]
    assert set(flat) == set(R), (set(flat) ^ set(R))
    assert len(flat) == len(set(flat))
    seq_names = [m.seq_name(s) for cn in ORDER for s in m.BUNDLES[cn]["pats"]]
    assert len(seq_names) == len(set(seq_names)), "sequence names collide"
    n_ent = {cn: len(m.BUNDLES[cn]["services"]) for cn in ORDER}

    a("# Chest Pain Predicates and Composites: All Care Patterns")
    a("")
    a("*Working Draft — October 2026*")
    a("")
    a("---")
    a("")
    a("## Overview")
    a("")
    a(f"This document defines the predicates and composites for chest pain applicants. It is one page for all care patterns. "
      f"The cohort has {m.N_COHORT:,} chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns, c0 to c7. "
      "Each predicate has one definition, and all care patterns use it.")
    a("")
    a("The same rules apply to every care pattern. An entity is one of the 5 most frequent entities of the care pattern. "
      "The entity is in the window when its event is not more than 1 day from a chest pain event. A care pattern needs 3 or more entities in the window and one of its 3 ordered sequences. "
      "The sequences are the 3 patterns with the highest lift.")
    a("")
    a("The document contains no underwriting logic and no product decision. It is a clinical grouping of codes. It is a draft and has no validation yet.")
    a("")
    a("| Care pattern | Name | Patients | % cohort |")
    a("| :---- | :---- | ----: | ----: |")
    for cn in ORDER:
        a(f"| {cn} | {PAGE_NAME[cn]} | {m.TABLE[cn]['n']} | {m.TABLE[cn]['pct']} |")
    a("")
    a("---")
    a("")
    a("## Predicates and Composites")
    a("")
    a("Each predicate uses a list of codes. The code is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.")
    a("")
    a("### Atomic Predicates")
    a("")
    a("A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.")
    a("")
    a("**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051). All care patterns use it.")
    a("")
    a("`chest_pain_present = event IS chest pain diagnosis`")
    a("")
    a("**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.")
    a("")
    a("`first_chest_pain_date = MIN(event_date) over chest pain events`")
    a("")
    for fam, keys in FAMILIES:
        a(f"#### {fam}")
        a("")
        for k in keys:
            name, sents, pred, desc, vocab, code, tok = m.ENT[k]
            a(f"**{name} present.** The applicant has at least one {m.NOUN[k]}. {' '.join(sents)} Code: {m.code_text(k)}; care patterns: {role_text(R[k])}.")
            a("")
            a(f"`{pred}_present = event IS {desc}`")
            a("")
    a("#### Entity in window")
    a("")
    a("An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. "
      "Each of the 5 entities of a care pattern has one window predicate. The window is a draft and has no calibration yet.")
    a("")
    a("`workup_window_days = 1`")
    a("")
    a("`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`")
    a("")
    a("---")
    a("")
    a("### Composites")
    a("")
    a("A composite combines atomic predicates, or other composites, into a named clinical pattern. Each care pattern has the same four composites: entity count, entities, sequence, and care pattern.")
    a("")
    a("**Entities.** The applicant has 3 or more of the entities of the care pattern in the window. The value 3 is a draft. It has no calibration yet.")
    a("")
    a("**Sequences.** A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. "
      "A step after the chest pain step is not more than 1 day after that chest pain event. A step before the chest pain step has no time limit. A step is true for any code of its list.")
    a("")
    a("`sequence_window_days = 1`")
    a("")
    a("**Same-day order.** Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. "
      "Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.")
    a("")
    a("**Care pattern.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. "
      "This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.")
    a("")
    for cn in ORDER:
        B = m.BUNDLES[cn]
        p = B["prefix"]
        a(f"#### {cn}: {PAGE_NAME[cn][0].upper() + PAGE_NAME[cn][1:]}")
        a("")
        a(f"`{p}_entity_count = " + " + ".join(f"{m.ENT[k][2]}_in_window" for k, _ in B["services"]) + "`")
        a("")
        a(f"`composite_{p}_entities = {p}_entity_count >= 3`")
        a("")
        names = []
        for i, steps in enumerate(B["pats"]):
            nm = m.seq_name(steps)
            names.append(nm)
            ph = [m.phrase(steps, j) for j in range(len(steps))]
            a(f"**Sequence {cn}-{'ABC'[i]}.** The applicant has {', then '.join(ph)}.")
            a("")
            a("`" + nm + " = " + " -> ".join(m.step_pred(q, steps, j) for j, q in enumerate(steps)) + "`")
            a("")
        a(f"`composite_{p}_sequence = " + " OR ".join(names) + "`")
        a("")
        a(f"`composite_{p}_pattern = chest_pain_present AND composite_{p}_entities AND composite_{p}_sequence`")
        a("")
    a("---")
    a("")
    a("## Population Coverage")
    a("")
    a(f"Counts come from the chest pain cohort of {m.N_COHORT:,} patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). "
      "The engine has no measured rate for any predicate or composite yet. Each patient is in the care pattern with the highest weight for that patient.")
    a("")
    a("### Window fit")
    a("")
    a("The window is 1 day. The table shows how far the 5 entities of each care pattern are from the first chest pain. The median is the median day of the first event of the entity.")
    a("")
    a("| Care pattern | Earliest median | Latest median | Entities more than 1 day from the first chest pain |")
    a("| :---- | :---- | :---- | ----: |")
    for cn in ORDER:
        meds = [e["med"] for e in m.TABLE[cn]["ents"]]
        a(f"| {cn} | {m.days_text(min(meds))} | {m.days_text(max(meds))} | {sum(1 for x in meds if abs(x) > 1)} of 5 |")
    a("")
    a("### Entity rates")
    a("")
    a("The rates count an entity at any time, not only in the window. The share is the share of the patients of the care pattern.")
    a("")
    a("| Care pattern | Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |")
    a("| :---- | :---- | ----: | :---- | ----: |")
    for cn in ORDER:
        for e, lab in zip(m.TABLE[cn]["ents"], m.ent_labels(cn)):
            a(f"| {cn} | {lab} | {e['share']}% | {m.days_text(e['med'])} | {e['before']}% |")
    a("")
    a("### Sequence rates")
    a("")
    a("The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients. "
      "The held-out check repeats the test on random halves of the patients, in 40 runs.")
    a("")
    a("| Sequence | Steps | Patients of the care pattern | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |")
    a("| :---- | :---- | ----: | ----: | ----: | ----: | :---- |")
    n_pass = n_all = 0
    for cn in ORDER:
        for i, (pt, steps) in enumerate(zip(m.TABLE[cn]["pats"], m.BUNDLES[cn]["pats"])):
            parts = ["chest pain" if q == "cp" else ("second " + m.NOUN[steps[j - 1]]) if q == "x2" else m.NOUN[q] for j, q in enumerate(steps)]
            txt = ", ".join(parts)
            order = " (same-day order)" if pt["order"] == "Same-day bundle" else ""
            n_all += 1
            n_pass += pt["holds"] == "Yes"
            a(f"| {cn}-{'ABC'[i]} | {txt}{order} | {m.fmt_pct(pt['sup_in'])} | {m.fmt_pct(pt['sup_out'])} | {float(pt['lift']):.1f} | {float(pt['passrate']):.0%} | {pt['verdict']} |")
    a("")
    a(f"{n_pass} of the {n_all} sequences passed the held-out check. The other sequences did not pass it. Read them as a draft. The window and the rule of 3 entities narrow the match.")
    a("")
    a("---")
    a("")
    a("## References")
    a("")
    a("- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.")
    seen = {"34709879"}
    for cn in ORDER:
        for pt in m.TABLE[cn]["pats"]:
            for x in re.split(r"[;,\s]+", pt["pmids"]):
                if x.isdigit() and x not in seen:
                    seen.add(x)
                    r = m.lit[m.lit.PMID == x]
                    if len(r):
                        r = r.iloc[0]
                        a(f"- {r['first_author']} et al. *{str(r['title (as returned by PubMed)']).rstrip('.')}.* {r['journal']} {r['year']}. PMID {x}.")
    a("")
    a("The papers come from the literature check of the final table. They cover the care type of the pattern. They do not test the order of the steps.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    open(OUT_FILE, "w").write(build())
    print("wrote", OUT_FILE)
