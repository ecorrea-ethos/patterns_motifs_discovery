"""Check a codeset file against the concept table of the mammography extract, and diff it against the baseline (v1).

usage (conda env with pandas + pyyaml, cwd = nb/repr_learn_mammography/):
    python check_codesets.py                              # codesets_v2.yaml vs codesets.yaml
    python check_codesets.py --names 8 --tags breast_density,tumor_marker
    python check_codesets.py --details                    # also list concepts added / removed per shared tag
    python check_codesets.py --md codesets_v1_vs_v2.md    # write the before / after report

Prints, per tag: concept count and example names (flags EMPTY). Then: tags of the baseline missing from the new file, the
label-defining tags vs baseline, concepts claimed by more than one tag (umbrella overlaps are listed apart), and the count diff.
Exit code 1 when a baseline tag is missing, a label-defining tag differs, or two non-umbrella tags share a concept.
Patterns are unanchored regex on concept_name of STANDARD concepts: always read the matched names, not only the counts.
A tag may carry a `source:` key (guideline section); build_codesets ignores it, --md prints it.
"""
import argparse, os, sys
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ethos_omop as eo  # noqa: E402

UMBRELLA = {"mammography", "antineoplastic_drug"}          # listed so that finer tags win the token; overlap with them is expected
LABEL_TAGS = ("mammography", "breast_cancer", "in_situ")   # define the cohort anchor and the label: v2 must not change them

ap = argparse.ArgumentParser()
ap.add_argument("codesets", nargs="?", default="codesets_v2.yaml")
ap.add_argument("--baseline", default="codesets.yaml")
ap.add_argument("--out-dir", default="../../inputs/mammography_cohort/")
ap.add_argument("--names", type=int, default=4, help="example concept names printed per tag")
ap.add_argument("--tags", default="", help="comma list: print examples only for these tags")
ap.add_argument("--details", action="store_true", help="list concepts added / removed against the baseline per shared tag")
ap.add_argument("--md", default="", help="write the before / after report to this markdown file")
a = ap.parse_args()

concept = eo.load_concept(a.out_dir)
name = concept.set_index("concept_id")["concept_name"].to_dict()
voc = concept.set_index("concept_id")["vocabulary_id"].to_dict()
here = os.path.dirname(os.path.abspath(__file__))
path = lambda p: p if os.path.isabs(p) else os.path.join(here, p)
spec_new, spec_old = eo._load_codesets(path(a.codesets)), eo._load_codesets(path(a.baseline))
new = eo.build_codesets(concept, codesets=spec_new, verbose=False)
old = eo.build_codesets(concept, codesets=spec_old, verbose=False)
show = set(filter(None, a.tags.split(",")))
fail = []


def label(cid):
    return f"{cid} {voc.get(cid, '?')} | {str(name.get(cid, '?'))[:88]}"


def names(ids, n=3):
    return "; ".join(str(name.get(c, "?"))[:60] for c in sorted(ids, key=lambda c: str(name.get(c, "")))[:n])


print(f"{a.codesets}: {len(new)} tags, {len({c for s in new.values() for c in s})} distinct concepts   "
      f"(baseline {a.baseline}: {len(old)} tags, {len({c for s in old.values() for c in s})} distinct concepts)\n")
for tag, ids in new.items():
    flag = "  <-- EMPTY" if not ids else ""
    print(f"{tag:28s}{len(ids):5d}{flag}")
    if (not show or tag in show) and ids:
        for cid in sorted(ids, key=lambda c: str(name.get(c, "")))[: a.names]:
            print(f"      {label(cid)}")

missing = [t for t in old if t not in new]
print("\nbaseline tags missing from the new file:", missing or "none")
if missing:
    fail.append("missing baseline tags")
for t in LABEL_TAGS:
    if new.get(t) != old.get(t):
        print(f"LABEL TAG {t} differs from baseline: +{len(new.get(t, set()) - old.get(t, set()))} -{len(old.get(t, set()) - new.get(t, set()))}")
        fail.append(f"{t} differs")
print("label-defining tags identical to baseline:", [t for t in LABEL_TAGS if new.get(t) == old.get(t)])

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

print(f"\n{'tag':28s}{'baseline':>9s}{'new':>6s}   (shared tags with a different concept set)")
for tag in new:
    if tag in old and old[tag] != new[tag]:
        print(f"{tag:28s}{len(old[tag]):9d}{len(new[tag]):6d}   +{len(new[tag] - old[tag])} -{len(old[tag] - new[tag])}")
        if a.details:
            for sign, ids in (("+", new[tag] - old[tag]), ("-", old[tag] - new[tag])):
                for cid in sorted(ids, key=lambda c: str(name.get(c, "")))[:8]:
                    print(f"      {sign} {label(cid)}")
print("\nnew tags:", ", ".join(t for t in new if t not in old))

if a.md:
    head = []
    with open(path(a.codesets)) as f:                       # the yaml's leading comment block is the narrative of the report
        for line in f:
            if not line.startswith("#"):
                break
            head.append(line[1:].rstrip("\n")[1:] if line.startswith("# ") else line[1:].rstrip("\n"))
    rows = []
    for tag in new:
        o, n = old.get(tag), new[tag]
        status = "new" if o is None else "unchanged" if o == n else "changed"
        src = spec_new[tag].get("source", "")
        add, rem = (n if o is None else n - o), (set() if o is None else o - n)
        rows.append((tag, status, src, len(o) if o is not None else "", len(n), len(add), len(rem),
                     names(add if status == "new" else rem) if (status == "new" or rem) else ""))
    with open(path(a.md), "w") as f:
        w = f.write
        w(f"# Mammography codesets: v1 (`{a.baseline}`) vs v2 (`{a.codesets}`), before and after\n\n")
        w("Generated by `python check_codesets.py --md ...` against the concept table of `inputs/mammography_cohort/`. "
          "Do not edit by hand; edit the yaml and re-run.\n\n")
        w("## Why v2\n\n```\n" + "\n".join(head) + "\n```\n\n")
        w("## Totals\n\n| | v1 | v2 |\n|---|---|---|\n")
        w(f"| tags | {len(old)} | {len(new)} |\n")
        w(f"| distinct concepts | {len({c for s in old.values() for c in s})} | {len({c for s in new.values() for c in s})} |\n")
        w(f"| empty tags | {sum(1 for s in old.values() if not s)} | {sum(1 for s in new.values() if not s)} |\n")
        w(f"| concepts in more than one tag (unexpected) | "
          f"{sum(1 for c in {c for s in old.values() for c in s} if len([t for t, s in old.items() if c in s and t not in UMBRELLA]) > 1)} | {len(bad)} |\n")
        w(f"| label-defining tags identical ({', '.join(LABEL_TAGS)}) | | {'yes' if all(new.get(t) == old.get(t) for t in LABEL_TAGS) else 'NO'} |\n\n")
        w("## Per tag\n\nOrder is the yaml order (first tag wins the group token). `removed` / `added` list up to 3 example names "
          "(removed for changed tags, added for new tags).\n\n")
        w("| tag | status | guideline source | v1 | v2 | +added | -removed | examples |\n|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            w("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |\n")
        gone = [t for t in old if t not in new]
        if gone:
            w(f"\nTags in v1 and not in v2: {', '.join(gone)}\n")
    print(f"\nwrote {os.path.abspath(path(a.md))}")
sys.exit(1 if fail else 0)
