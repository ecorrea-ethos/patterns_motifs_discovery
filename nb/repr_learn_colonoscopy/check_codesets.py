"""Check codesets.yaml of the colonoscopy cohort against a concept table (self-contained: pandas + pyyaml only).

usage (cwd = nb/repr_learn_colonoscopy/):
    python check_codesets.py                         # concept table = inputs/colonoscopy_cohort/concept.csv when it exists,
                                                     # else the union of inputs/*/concept.csv (other cohorts' extracts: PARTIAL, see the yaml header)
    python check_codesets.py --concept PATH.csv --names 6 --tags colonoscopy,in_situ

Applies the same rule as ethos_omop.resolve(): STANDARD concepts, vocabulary / domain filters, unanchored regex on concept_name joined with "|",
then `exclude`. Prints per tag the concept count (flags EMPTY) and example names, then the concepts claimed by more than one tag.
Exit code 1 when two tags that are not an umbrella pair share a concept. Read the matched names, not only the counts.
"""
import argparse, glob, os, sys
from itertools import combinations
import pandas as pd, yaml

UMBRELLA = {"colonoscopy", "antineoplastic_drug"}          # listed after their finer tags on purpose; overlap with them is expected
ap = argparse.ArgumentParser()
ap.add_argument("--yaml", default="codesets.yaml"); ap.add_argument("--concept", default="")
ap.add_argument("--names", type=int, default=3); ap.add_argument("--tags", default="")
a = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
own = os.path.join(here, "../../inputs/colonoscopy_cohort/concept.csv")
files = [a.concept] if a.concept else ([own] if os.path.exists(own) else sorted(glob.glob(os.path.join(here, "../../inputs/*/concept.csv"))))
concept = pd.concat([pd.read_csv(f, low_memory=False) for f in files]).drop_duplicates("concept_id")
print(f"concept table: {len(files)} file(s), {len(concept):,} concepts" + ("" if len(files) == 1 else "  (UNION of other cohorts: partial)"))
std = concept[concept["standard_concept"] == "S"]
spec = yaml.safe_load(open(os.path.join(here, a.yaml)))
name = concept.set_index("concept_id")["concept_name"].to_dict(); voc = concept.set_index("concept_id")["vocabulary_id"].to_dict()

def resolve(sp):
    if "concept_ids" in sp:
        return set(sp["concept_ids"])
    c = std
    if sp.get("vocabularies"): c = c[c["vocabulary_id"].isin(sp["vocabularies"])]
    if sp.get("domain"): c = c[c["domain_id"] == sp["domain"]]
    hit = c[c["concept_name"].str.contains("|".join(f"(?:{p})" for p in sp["patterns"]), case=False, na=False, regex=True)]
    if sp.get("exclude"):
        hit = hit[~hit["concept_name"].str.contains("|".join(f"(?:{p})" for p in sp["exclude"]), case=False, na=False, regex=True)]
    return set(hit["concept_id"].astype("int64"))

sets = {t: resolve(sp) for t, sp in spec.items()}
show = set(filter(None, a.tags.split(",")))
print(f"{len(sets)} tags, {len({c for s in sets.values() for c in s}):,} distinct concepts\n")
for t, ids in sets.items():
    print(f"{t:34s}{len(ids):5d}{'  <-- EMPTY' if not ids else ''}")
    if ids and (not show or t in show):
        for c in sorted(ids, key=lambda c: str(name.get(c)))[:a.names]: print(f"      {c} {voc.get(c)} | {str(name.get(c))[:96]}")
print("\nconcepts claimed by more than one tag:")
bad = 0
for x, y in combinations(sets, 2):
    both = sets[x] & sets[y]
    if both:
        ok = x in UMBRELLA or y in UMBRELLA
        bad += not ok
        print(f"  {'(umbrella) ' if ok else 'UNEXPECTED '}{x} & {y}: {len(both)}  e.g. {'; '.join(str(name.get(c))[:50] for c in sorted(both)[:2])}")
sys.exit(1 if bad else 0)
