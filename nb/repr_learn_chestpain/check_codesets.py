"""Check a codeset file against the concept table of the chest pain extract, and diff it against the baseline.

usage (conda env with pandas + pyyaml, cwd = nb/repr_learn_chestpain/):
    python check_codesets.py                         # codesets_v2.yaml vs codesets.yaml
    python check_codesets.py codesets_v2.yaml --names 8 --tags ekg,stress_test
    python check_codesets.py codesets_v2.yaml --details # also list concepts added / removed per shared tag

Prints, per tag: concept count and example names (flags EMPTY). Then: tags of the baseline missing from the new file,
chest_pain id set vs baseline, concepts claimed by more than one tag (umbrella overlaps are listed apart), and the count diff.
Exit code 1 when a baseline tag is missing, chest_pain differs, or two non-umbrella tags share a concept.
Patterns are unanchored regex on concept_name of STANDARD concepts: always read the matched names, not only the counts.
"""
import argparse, os, sys
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ethos_omop as eo  # noqa: E402

UMBRELLA = {"stress_test", "cad"}      # listed last in codesets_v2.yaml on purpose; overlap with fine-grained tags is expected

ap = argparse.ArgumentParser()
ap.add_argument("codesets", nargs="?", default="codesets_v2.yaml")
ap.add_argument("--baseline", default="codesets.yaml")
ap.add_argument("--out-dir", default="../../inputs/chest_pain_cohort/")
ap.add_argument("--names", type=int, default=4, help="example concept names printed per tag")
ap.add_argument("--tags", default="", help="comma list: print examples only for these tags")
ap.add_argument("--details", action="store_true", help="list concepts added / removed against the baseline per shared tag")
a = ap.parse_args()

concept = eo.load_concept(a.out_dir)
name = concept.set_index("concept_id")["concept_name"].to_dict()
voc = concept.set_index("concept_id")["vocabulary_id"].to_dict()
here = os.path.dirname(os.path.abspath(__file__))
path = lambda p: p if os.path.isabs(p) else os.path.join(here, p)
new = eo.build_codesets(concept, codesets=eo._load_codesets(path(a.codesets)), verbose=False)
old = eo.build_codesets(concept, codesets=eo._load_codesets(path(a.baseline)), verbose=False)
show = set(filter(None, a.tags.split(",")))
fail = []


def label(cid):
    return f"{cid} {voc.get(cid, '?')} | {str(name.get(cid, '?'))[:88]}"


print(f"{a.codesets}: {len(new)} tags, {len({c for s in new.values() for c in s})} distinct concepts   "
      f"(baseline {a.baseline}: {len(old)} tags)\n")
for tag, ids in new.items():
    flag = "  <-- EMPTY" if not ids else ""
    print(f"{tag:26s}{len(ids):5d}{flag}")
    if (not show or tag in show) and ids:
        for cid in sorted(ids, key=lambda c: str(name.get(c, "")))[: a.names]:
            print(f"      {label(cid)}")

missing = [t for t in old if t not in new]
print("\nbaseline tags missing from the new file:", missing or "none")
if missing:
    fail.append("missing baseline tags")
if "chest_pain" in new and new["chest_pain"] != old.get("chest_pain"):
    print("chest_pain id set differs from baseline:", sorted(new["chest_pain"] ^ old.get("chest_pain", set())))
    fail.append("chest_pain differs")
else:
    print("chest_pain id set identical to baseline:", sorted(new.get("chest_pain", [])))

owner = defaultdict(list)
for tag, ids in new.items():
    for cid in ids:
        owner[cid].append(tag)
shared = {cid: ts for cid, ts in owner.items() if len(ts) > 1}
bad = {cid: ts for cid, ts in shared.items() if len([t for t in ts if t not in UMBRELLA]) > 1}
ok = len(shared) - len(bad)
print(f"\nconcepts in more than one tag: {len(shared)} ({ok} umbrella overlaps, {len(bad)} unexpected)")
pairs = defaultdict(int)
for cid, ts in bad.items():
    for p in combinations(sorted(ts), 2):
        pairs[p] += 1
for p, n in sorted(pairs.items(), key=lambda kv: -kv[1]):
    ex = next(c for c, ts in bad.items() if set(p) <= set(ts))
    print(f"   {p[0]} + {p[1]}: {n}   e.g. {label(ex)}")
if bad:
    fail.append("unexpected overlaps")

print(f"\n{'tag':26s}{'baseline':>9s}{'new':>6s}   (shared tags with a different concept count)")
for tag in new:
    if tag in old and old[tag] != new[tag]:
        print(f"{tag:26s}{len(old[tag]):9d}{len(new[tag]):6d}   +{len(new[tag] - old[tag])} -{len(old[tag] - new[tag])}")
        if a.details:
            for sign, ids in (("+", new[tag] - old[tag]), ("-", old[tag] - new[tag])):
                for cid in sorted(ids, key=lambda c: str(name.get(c, "")))[:8]:
                    print(f"      {sign} {label(cid)}")
print("\nnew tags:", ", ".join(t for t in new if t not in old))
sys.exit(1 if fail else 0)
