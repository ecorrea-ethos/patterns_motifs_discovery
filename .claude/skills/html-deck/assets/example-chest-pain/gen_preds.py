"""Worked example: predicate page + guideline code file -> inject/preds.json for the chest pain deck. Standard library only.

    python3 -I gen_preds.py <chest_pain_all_patterns.md> <codesets_v2.yaml> inject/preds.json

Reads the one-file predicate page and the guideline code file, so every predicate count on the slides is parsed, not typed:
  families   the care predicates by family, each with the care patterns that use it
  reuse      how many predicates serve one pattern, how many serve several, and the broadest one
  windowFit  main events whose median day lies more than 1 day from first chest pain, per pattern (the page's window-fit table)
  guideline  code groups per guideline family, and how many the predicates draw on
  examples   concept counts for the two predicates the anatomy slide names
The chest pain entry rule is not a care predicate; its group `chest_pain` is counted as used by the guideline coverage.
"""
import re, json, sys, collections

md = open(sys.argv[1], encoding='utf-8').read()
ym = open(sys.argv[2], encoding='utf-8').read()

# --- care predicates, by family
FAM = {'Diagnoses': 'dx', 'Lab tests': 'lab', 'Procedures, imaging, and visits': 'proc', 'Drugs': 'drug'}
fam, fams, order = None, collections.OrderedDict(), []
for line in md.split('\n'):
    h = re.match(r'#### (.+)$', line)
    if h:
        fam = h.group(1) if h.group(1) in FAM else None
        if fam: fams[fam] = []
        continue
    if line.startswith('### '):
        fam = None
    m = re.match(r'\*\*(.+?) present\.\*\*', line)
    if fam and m:
        pats = re.findall(r'(c\d)\s*\((?:entity and step|entity|step)\)', line)
        if not pats: sys.exit('no care pattern parsed for predicate: ' + m.group(1))
        fams[fam].append({'k': m.group(1), 'pats': pats})
# slide wording: full terms, same plain names as the sequence steps (the page uses abbreviations such as ECG and CMP)
LABEL = {'GERD': 'Acid reflux', 'Low back pain': 'Low back pain', 'Acute upper respiratory infection': 'Upper respiratory infection', 'Acute pharyngitis': 'Sore throat (pharyngitis)',
         'Troponin': 'Troponin test', 'Lipase': 'Lipase test', 'CMP': 'Comprehensive metabolic panel', 'CBC': 'Complete blood count', 'HbA1c': 'Hemoglobin A1c test',
         'Vitamin B12': 'Vitamin B12 test', 'Vitamin D': 'Vitamin D test', 'Free T4': 'Free thyroxine test', 'Iron': 'Iron test', 'Ferritin': 'Ferritin test',
         'STI test': 'Infection test (DNA or RNA)', 'Venipuncture': 'Blood draw', 'ECG': 'Electrocardiogram', 'IV push': 'Intravenous push',
         'Surgical pathology': 'Tissue pathology exam', 'PPI or H2 blocker': 'Acid-lowering drug'}
for v in fams.values():
    for p in v: p['k'] = LABEL.get(p['k'], p['k'])
families = [{'id': FAM[f], 'name': f, 'n': len(v), 'items': v} for f, v in fams.items()]
allp = [p for f in families for p in f['items']]

# --- reuse
multi = sorted([p for p in allp if len(set(p['pats'])) > 1], key=lambda p: (-len(set(p['pats'])), p['k']))
reuse = {'single': len(allp) - len(multi), 'multi': len(multi), 'max': len(set(multi[0]['pats'])), 'maxName': multi[0]['k'],
         'rows': [{'k': p['k'], 'n': len(set(p['pats']))} for p in multi]}
for f in families:
    for p in f['items']: p['n'] = len(set(p['pats']))

# --- window fit (page table: | c0 | 104 d before | same day | 3 of 5 |)
wf = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in re.finditer(r'^\| (c\d) \|[^|]*\|[^|]*\| (\d+) of (\d+) \|$', md, re.M)]
if len(wf) != 8: sys.exit('window-fit table not found: %d rows' % len(wf))
windowFit = {'out': sum(o for _, o, _ in wf), 'total': sum(t for _, _, t in wf), 'rows': [{'id': i, 'out': o, 'of': t} for i, o, t in wf]}

# --- guideline coverage (yaml: section headers '# N. Title', groups are top-level keys)
SHORT = {1: 'Chest pain and equivalents', 2: 'Test ladder', 3: 'Cardiac causes', 4: 'Noncardiac causes', 5: 'Risk factors and history', 6: 'Therapy', 7: 'Umbrella tags'}
sec, groups = None, collections.OrderedDict((n, []) for n in SHORT)
for line in ym.split('\n'):
    h = re.match(r'# (\d)\. ', line)
    if h: sec = int(h.group(1)); continue
    k = re.match(r'([a-z_0-9]+):\s*$', line)
    if k and sec:
        if k.group(1) not in groups[sec]: groups[sec].append(k.group(1))
used = set(re.findall(r'group `([a-z_0-9]+)`', md)) | {'chest_pain'}
everything = [g for v in groups.values() for g in v]
if len(everything) != len(set(everything)): sys.exit('duplicate group names in the code file')
if not used <= set(everything): sys.exit('page cites groups missing from the code file: %s' % sorted(used - set(everything)))
guideline = {'groups': len(everything), 'used': len(used), 'usedNames': sorted(used),
             'families': [{'k': SHORT[n], 'total': len(v), 'used': len([g for g in v if g in used])} for n, v in groups.items()]}

# --- concept counts quoted by the anatomy slide
ex = {}
for key, name in (('troponin', 'troponin'), ('ecg', 'ekg')):
    m = re.search(r'group `%s`, (\d+) concepts' % name, md)
    if not m: sys.exit('concept count not found for ' + name)
    ex[key] = int(m.group(1))

out = {'care': len(allp), 'families': families, 'reuse': reuse, 'windowFit': windowFit, 'guideline': guideline, 'examples': ex}
json.dump(out, open(sys.argv[3], 'w'), indent=1, ensure_ascii=False)
print('care predicates %d (%s); single %d multi %d; window out %d of %d; guideline used %d of %d' % (
    len(allp), ', '.join('%s %d' % (f['id'], f['n']) for f in families), reuse['single'], reuse['multi'], windowFit['out'], windowFit['total'], guideline['used'], guideline['groups']))
print([(f['k'], '%d/%d' % (f['used'], f['total'])) for f in guideline['families']])
