"""Build the plain-English layer of the chest pain engine: one CSV for the data team and the two annexes of the engine document.

usage (conda env ethos_llm, cwd = nb/repr_learn_chestpain/):
    python build_plain_english_annex.py                      # writes chestpain_plain_english_omop_map.csv and refreshes the annexes
    python build_plain_english_annex.py --engine OTHER.md    # annexes into another markdown file (between the ANNEX markers)

Inputs
    chestpain_plain_labels.yaml          the wording the UW team reviews (abbreviations, UW-vs-data words, one label per code list)
    token_members_k8_chestpain_AHA.csv   one row per OMOP concept with its code list (written by the AHA notebook, section 5)
    codesets_v2.yaml                     only for the order of the code lists (the checker check_codesets.py validates its content)
Outputs
    chestpain_plain_english_omop_map.csv one row per code: plain label, abbreviation, code list, OMOP ID, vocabulary, code, verbatim OMOP name
    Annex A (plain-English guide) and Annex B (parallel mapping to OMOP) inside the engine markdown, between
    <!-- ANNEX:BEGIN --> and <!-- ANNEX:END --> (added at the end of the file when the markers are missing)
    the entity registry table of the engine (one row per OMOP code behind each predicate key), between
    <!-- REGISTRY:BEGIN --> and <!-- REGISTRY:END --> (left alone when the markers are missing)
"""
import argparse
import os
import re

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS, MEMBERS, CODESETS = "chestpain_plain_labels.yaml", "token_members_k8_chestpain_AHA.csv", "codesets_v2.yaml"
CSV_OUT, ENGINE_MD = "chestpain_plain_english_omop_map.csv", "outputs/Chestpain_Workup_Predicate_Engine_v2.md"
BEGIN, END = "<!-- ANNEX:BEGIN -->", "<!-- ANNEX:END -->"
REG_BEGIN, REG_END = "<!-- REGISTRY:BEGIN -->", "<!-- REGISTRY:END -->"
EXTRA_FAMILY = "Other codes used by the engine"
# where each code list or code is used by the v2 engine (design of the engine document, not of the data)
# predicate key of the engine -> code list (by tag) or single codes (by OMOP ID) behind it
REGISTRY = [("chest_pain", "chest_pain"), ("troponin", "troponin"), ("cxr", "chest_xray"), ("lipase", [4021288]),
            ("iv_push", [2314215, 2314216]), ("ecg", "ekg"), ("cmp", [3661905]), ("cbc", [4319466])]
ENGINE_ROLE = {"chest_pain": "anchor: the chest pain date", "troponin": "service 1 and every sequence",
               "chest_xray": "service 2 and sequence A", "ekg": "sequence B (not counted as a service)"}

ap = argparse.ArgumentParser()
ap.add_argument("--engine", default=ENGINE_MD)
args = ap.parse_args()
p = lambda f: f if os.path.isabs(f) else os.path.join(HERE, f)

lab = yaml.safe_load(open(p(LABELS), encoding="utf-8"))
tags = list(yaml.safe_load(open(p(CODESETS), encoding="utf-8")))                       # list order of the validated file
assert set(lab["code_lists"]) == set(tags), f"labels and {CODESETS} differ: {sorted(set(lab['code_lists']) ^ set(tags))}"
assert [t for t in tags if t in lab["code_lists"]] == list(lab["code_lists"]), "label order differs from the codeset file order"
fams = lab["families"]
assert all(v["family"] in fams for v in lab["code_lists"].values()), "a label uses a family that is not listed"

m = pd.read_csv(p(MEMBERS), dtype={"concept_code": str}, keep_default_na=False, na_values=[""])
m["groups"] = m["groups"].fillna("")
members = m[m["groups"] != ""].copy()
members["code_list"] = members["token"]                                                 # first list in file order owns the code
members["also_in"] = [", ".join(g for g in gs.split("|") if g != t) for gs, t in zip(members["groups"], members["code_list"])]
assert members["concept_id"].is_unique, "a code sits under two lists"
assert set(members["code_list"]) <= set(tags), "a code list is not in the codeset file"

rows = []
def add(r, plain, abbr, family, code_list, role, detail, also):
    rows.append(dict(plain_label=plain, abbreviation=abbr, family=family, code_list=code_list, role_in_engine=role,
                     plain_detail=detail, concept_id=int(r.concept_id), vocabulary_id=r.vocabulary_id, concept_code=r.concept_code,
                     omop_concept_name=re.sub(r"\s+", " ", str(r.concept_name)).strip(), domain=r.domain,
                     n_patients=int(r.n_patients), in_cohort=bool(r.in_cohort), also_in_code_lists=also))

for tag in tags:
    L = lab["code_lists"][tag]
    for r in members[members["code_list"] == tag].sort_values(["n_patients", "concept_id"], ascending=[False, True]).itertuples():
        add(r, L["label"], L["abbr"], L["family"], tag, ENGINE_ROLE.get(tag, ""), lab["details"].get(int(r.concept_id), ""), r.also_in)
extra_ids = list(lab["engine_concepts"])
for cid in extra_ids:
    hit = m[m["concept_id"] == cid]
    assert len(hit) == 1 and hit.iloc[0]["groups"] == "", f"engine concept {cid} is missing or sits in a code list"
    E = lab["engine_concepts"][cid]
    add(hit.iloc[0], E["label"], E["abbr"], EXTRA_FAMILY, "", E["role"], "", "")
df = pd.DataFrame(rows)
order = {f: i for i, f in enumerate([EXTRA_FAMILY] + fams)}
df["_f"] = df["family"].map(order); df["_t"] = df["code_list"].map({t: i for i, t in enumerate(tags)}).fillna(-1)
df = df.sort_values(["_f", "_t"], kind="stable").drop(columns=["_f", "_t"])
assert df["plain_label"].ne("").all() and len(df) == len(members) + len(extra_ids)
df.to_csv(p(CSV_OUT), index=False)

# ------------------------------------------------------------------ markdown
esc = lambda s: str(s).replace("|", "\\|")
tok = m[m["groups"] != ""].drop_duplicates("token").set_index("token")["token_n_patients"].fillna(0)   # a list with no code in the cohort has no patient count
umbrella = {t: members[members["groups"].str.split("|").map(lambda g: t in g)] for t in ("stress_test", "cad")}
out = [BEGIN, "",
       "## Annex A. Plain-English guide", "",
       "This annex is for the UW team. It fixes the words used in this document so that the UW team and the data team mean the same thing. "
       f"The wording lives in `{LABELS}` and the tables are generated by `build_plain_english_annex.py`; edit the file and re-run the script, not the tables.", "",
       "### A1. Abbreviations", "", "| Abbreviation | Meaning |", "| :---- | :---- |"]
out += [f"| {esc(a)} | {esc(t)} |" for a, t in sorted(lab["abbreviations"].items(), key=lambda kv: kv[0].lower())]
out += ["", "### A2. UW wording and data-team wording", "",
        "| UW wording (used in this document) | Data-team wording | What it means |", "| :---- | :---- | :---- |"]
out += [f"| {esc(a)} | {esc(b)} | {esc(c)} |" for a, b, c in lab["uw_vs_data"]]
out += ["", "### A3. Plain label of every list of codes", "",
        f"{len(tags)} lists of codes (`{CODESETS}`, validated with `check_codesets.py`). *Patients* is the number of the 139,416 chest pain patients with at least one code of the list; "
        "*Codes* is the number of codes in the list (codes that no patient in this extract has are counted but listed with 0 patients in Annex B).", ""]
for fam in fams:
    out += [f"**{fam}**", "", "| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |", "| :---- | :---- | :---- | :---- | :---- | ----: | ----: |"]
    for tag in tags:
        L = lab["code_lists"][tag]
        if L["family"] != fam:
            continue
        if tag in umbrella:
            n_codes, pats = len(umbrella[tag]), "—"
        else:
            n_codes = int((members["code_list"] == tag).sum()); pats = f"{int(tok.get(tag, 0)):,}"
        out.append(f"| {esc(L['label'])} | {esc(L['abbr']) or '—'} | `{tag}` | {esc(L['what'])} | {esc(ENGINE_ROLE.get(tag, '')) or '—'} | {n_codes} | {pats} |")
    out.append("")
out += ["## Annex B. Parallel mapping to OMOP codes", "",
        "For each plain label, the OMOP concepts behind it, with the verbatim OMOP concept name, the billing or medical code and the OMOP ID (`concept_id`). "
        f"The same rows are in `{CSV_OUT}` for the data team, with the extra columns *domain*, *in cohort* and *also in lists*. "
        "A code that belongs to two lists is shown under the first list in the order of `codesets_v2.yaml`, with the other list noted. "
        "*Patients* is the number of chest pain patients with that code.", "",
        f"### B0. {EXTRA_FAMILY}", "",
        "Single codes that are not in a list of codes. Lipase, IV push, CMP and CBC are part of the rule; the other four are among the ten strongest codes of the ED care pattern and are not used.", "",
        "| Plain label | Used as | Verbatim OMOP concept name | Code | OMOP ID | Patients |", "| :---- | :---- | :---- | :---- | ----: | ----: |"]
for r in df[df["family"] == EXTRA_FAMILY].itertuples():
    out.append(f"| {esc(r.plain_label)} | {esc(r.role_in_engine)} | {esc(r.omop_concept_name)} | {r.vocabulary_id} {r.concept_code} | {r.concept_id} | {r.n_patients:,} |")
out.append("")
for fam in fams:
    out += [f"### B. {fam}", ""]
    for tag in tags:
        L = lab["code_lists"][tag]
        if L["family"] != fam:
            continue
        sub = df[df["code_list"] == tag]
        shown = L["label"] + (f" ({L['abbr']})" if L["abbr"] and L["abbr"] not in L["label"] else "")
        out += [f"#### {shown} · `{tag}`", ""]
        if tag in umbrella:
            parts = sorted({g for gs in umbrella[tag]["groups"] for g in gs.split("|") if g != tag}, key=tags.index)
            out += [f"{len(umbrella[tag])} codes, all of them listed under: {', '.join('`' + g + '`' for g in parts)}.", ""]
            continue
        if sub.empty:
            out += ["No code of this list occurs in the extract.", ""]
            continue
        out += ["| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |", "| :---- | :---- | :---- | ----: | ----: | :---- |"]
        for r in sub.itertuples():
            out.append(f"| {esc(r.plain_detail) or '—'} | {esc(r.omop_concept_name)} | {r.vocabulary_id} {r.concept_code} | {r.concept_id} | {r.n_patients:,} | {esc(r.also_in_code_lists) or '—'} |")
        out.append("")
out += [END]
annex = "\n".join(out)

reg = ["| Predicate key | Plain label | Verbatim OMOP concept name | Code | `concept_id` | Patients |", "| :---- | :---- | :---- | :---- | ----: | ----: |"]
for key, src in REGISTRY:
    sub = df[df["code_list"] == src] if isinstance(src, str) else df[df["concept_id"].isin(src)]
    assert len(sub), f"registry key {key} has no code"
    for r in sub.itertuples():
        plain = r.plain_label + (f", {r.plain_detail}" if r.plain_detail else "")
        reg.append(f"| `{key}` | {esc(plain)} | {esc(r.omop_concept_name)} | {r.vocabulary_id} {r.concept_code} | {r.concept_id} | {r.n_patients:,} |")
registry = "\n".join([REG_BEGIN, ""] + reg + ["", REG_END])

def inject(text, begin, end, block, append):
    if begin in text and end in text:
        return text[:text.index(begin)] + block + text[text.index(end) + len(end):]
    return text.rstrip("\n") + "\n\n---\n\n" + block + "\n" if append else text

path = p(args.engine)
text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
text = inject(text, REG_BEGIN, REG_END, registry, append=False)
text = inject(text, BEGIN, END, annex, append=True)
open(path, "w", encoding="utf-8").write(text)
print(f"wrote {CSV_OUT}: {len(df)} rows ({len(members)} codes of {len(tags)} lists, 2 of them combined lists, + {len(extra_ids)} single engine codes)")
print(f"annexes written into {os.path.basename(path)}: {len(annex.splitlines())} lines; registry: {len(reg) - 2} rows")
