"""Chest pain code lists (codesets_v2.yaml, AHA/ACC 2021 guideline) -> one workbook for clinical review.

usage (conda env with pandas, pyyaml and openpyxl, cwd = nb/repr_learn_chestpain/):
    python -I export_codesets_xlsx.py                       # writes outputs/chestpain_AHA_codesets_for_review.xlsx
    python -I export_codesets_xlsx.py out.xlsx

Reads three files that sit beside this script and joins them, so nothing on a sheet is typed by hand:
  codesets_v2.yaml                  the code groups: search terms, excluded terms, vocabularies, and the rationale in the comments
  chestpain_plain_labels.yaml       the plain-English label, family and purpose of each group, the abbreviations and the glossary
  token_members_k8_chestpain_AHA.csv  the concepts each group found in the chest pain extract, with applicant and event counts
  outputs/chest_pain_all_patterns.md  which groups the engine's predicates actually use

Sheets: Read me, Code groups, Concepts, Codes to add, Glossary. The yellow columns are for the reviewer.
"""
import re, sys, os, yaml
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

here = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(here, f)
out = sys.argv[1] if len(sys.argv) > 1 else P('outputs/chestpain_AHA_codesets_for_review.xlsx')

raw = open(P('codesets_v2.yaml'), encoding='utf-8').read().split('\n')
cs = yaml.safe_load('\n'.join(raw))
pl = yaml.safe_load(open(P('chestpain_plain_labels.yaml'), encoding='utf-8'))
mem = pd.read_csv(P('token_members_k8_chestpain_AHA.csv'))
page = open(P('outputs/chest_pain_all_patterns.md'), encoding='utf-8').read()
COHORT = int(mem.loc[mem.token == 'chest_pain', 'token_n_patients'].iloc[0])

# rationale: the indented comment lines right under each group key
note = {}
for i, line in enumerate(raw):
    m = re.match(r'^([a-z_0-9]+):\s*$', line)
    if m:
        buf, j = [], i + 1
        while j < len(raw) and re.match(r'^\s+#', raw[j]):
            buf.append(re.sub(r'^\s+#\s?', '', raw[j]).strip()); j += 1
        note[m.group(1)] = ' '.join(buf)

used = set(re.findall(r'group `([a-z_0-9]+)`', page)) | {'chest_pain'}      # chest pain entry rule uses the chest_pain group
assert set(cs) == set(pl['code_lists']), 'code file and plain labels disagree on the group names'

# members: one row per (group, concept); a concept shared with an umbrella group appears under both
mem = mem[mem.groups.notna()].copy()
mem['group'] = mem.groups.str.split('|')
mem = mem.explode('group')
mem['also'] = [', '.join(x for x in g.split('|') if x != k) for g, k in zip(mem.groups, mem.group)]
detail = pl.get('details', {})
mem['detail'] = mem.concept_id.map(detail).fillna('')
owner_patients = mem.drop_duplicates('token').set_index('token').token_n_patients.to_dict()
order = {k: i for i, k in enumerate(cs, 1)}
mem['ord'] = mem.group.map(order)
mem = mem.sort_values(['ord', 'n_patients', 'concept_name'], ascending=[True, False, True])

# ---- sheet: Code groups
rows = []
for k, v in cs.items():
    L = pl['code_lists'][k]; g = mem[mem.group == k]
    rows.append({
        'Order': order[k], 'Code group': k,
        'Guideline note': note.get(k, ''),
        'Included terms': ', '.join('"%s"' % t if ',' in t else t for t in v.get('patterns', [])) or ('fixed concept IDs: ' + ', '.join(map(str, v['concept_ids'])) if v.get('concept_ids') else ''),
        'Vocabularies': ', '.join(v.get('vocabularies', [])) or 'all',
        'Domain': v.get('domain', ''),
        'Concepts found': len(g), 'Concepts seen in the data': int((g.n_patients > 0).sum()),
        'Applicants with the group': owner_patients.get(k) if k in owner_patients and pd.notna(owner_patients.get(k)) else None,
        'Used by the engine predicates': 'Yes' if k in used else 'No',
        'Review: keep, change or remove?': None, 'Review: comment': None})
G = pd.DataFrame(rows)

# ---- sheet: Concepts
C = pd.DataFrame({
    'Code group': mem.group, 'Concept ID': mem.concept_id,
    'Concept name': mem.concept_name, 'Vocabulary': mem.vocabulary_id, 'Code': mem.concept_code.astype(str), 'Domain': mem.domain,
    'Applicants with the concept': mem.n_patients, 'Events': mem.n_events, 'Also in group': mem.also, 'Detail': mem.detail,
    'Review: keep or remove?': None, 'Review: comment': None})

# ---- sheet: Codes to add (blank, with a drop-down of the group names)
A = pd.DataFrame({'Code group': [None] * 40, 'Code or concept to add': None, 'Name or description': None, 'Why it matters': None})

# ---- sheet: Glossary
gl = [[abbr, full] for abbr, full in sorted(pl['abbreviations'].items())]
W = pd.DataFrame(gl, columns=['Abbreviation', 'Meaning'])
T = pd.DataFrame(pl['uw_vs_data'], columns=['Plain term', 'Data-team word', 'Meaning'])

# ---- sheet: Read me
nit = mem[mem.group == 'nitrate_antianginal']
ranol = nit[nit.concept_name.str.contains('ranolazine', case=False)]
blank = [k for k in cs if k not in owner_patients or pd.isna(owner_patients[k])]
R = [
    ['Chest pain code lists for clinical review', ''],
    ['', ''],
    ['Source', 'codesets_v2.yaml (version 5, guideline rewrite), exported 2026-10-26. Built from: Gulati M, et al. 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain. Circulation 2021;144:e368-e454. doi:10.1161/CIR.0000000000001029.'],
    ['What it is', f'{len(cs)} code groups in {len(pl["families"])} families. Each group is a list of standard medical codes (SNOMED, CPT4, HCPCS, LOINC, RxNorm) found by searching concept names for the included terms on the Code groups sheet. A group stands for one clinical idea, for example a troponin test or an acid reflux diagnosis.'],
    ['Population', f'Counts come from the chest pain extract of {COHORT:,} applicants who have a chest pain code. They are numbers of applicants and events in the data, not rates for the general population.'],
    ['Used by the engine', f'The predicates and composites of the draft rule engine draw on {len(used)} of the {len(cs)} groups (column "Used by the engine predicates"). The other groups define what the guideline names but the engine does not use yet.'],
    ['', ''],
    ['Sheets', ''],
    ['Code groups', 'One row per group: the guideline note, the included terms (comma-separated; a term that itself contains a comma is in quotation marks), vocabularies, number of concepts found, and the review columns.'],
    ['Concepts', 'One row per concept in each group, with applicants and events. A concept shared with an umbrella group appears under both. Concepts never seen in the data have zero applicants.'],
    ['Codes to add', 'Blank rows for codes or concepts you think are missing, with the group they belong to.'],
    ['Glossary', 'Abbreviations used in the notes and the plain-language terms.'],
    ['', ''],
    ['How to review', 'Fill the yellow columns and send the file back. On Code groups: keep, change or remove, with a comment. On Concepts: keep or remove for single codes. On Codes to add: anything missing.'],
    ['', ''],
    ['Quick facts that may matter for the review', ''],
    ['Nitrates', f'Group nitrate_antianginal has {len(nit)} concepts, all prescription drugs, and {int(owner_patients.get("nitrate_antianginal", 0)):,} applicants ({owner_patients.get("nitrate_antianginal", 0) / COHORT:.1%} of the cohort) have one, so nitrates are captured but rarely. It also holds {len(ranol)} ranolazine concepts; ranolazine is an antianginal medicine, not a nitrate.'],
    ['Reading the included terms', 'Terms are matched against the standard concept name, ignoring capitals, and may contain symbols such as ^ (start of the name) or .* (anything). Always read the concept list on the Concepts sheet, not only the terms.'],
    ['Applicant counts', 'Counts on the Concepts sheet are per concept and overlap, so do not add them up. "Applicants with the group" is the number with any concept of the group. It is blank for ' + ', '.join(blank) + ': the umbrella groups only repeat concepts of other groups, and a group none of whose concepts occur in the data has no count.'],
]
R = pd.DataFrame(R, columns=['', ' '])

os.makedirs(os.path.dirname(out), exist_ok=True)
with pd.ExcelWriter(out, engine='openpyxl') as xw:
    R.to_excel(xw, sheet_name='Read me', index=False, header=False)
    G.to_excel(xw, sheet_name='Code groups', index=False)
    C.to_excel(xw, sheet_name='Concepts', index=False)
    A.to_excel(xw, sheet_name='Codes to add', index=False)
    W.to_excel(xw, sheet_name='Glossary', index=False, startrow=0)
    T.to_excel(xw, sheet_name='Glossary', index=False, startrow=len(W) + 3)

# ---- styling
wb = load_workbook(out)
HEAD = PatternFill('solid', fgColor='24574D'); REV = PatternFill('solid', fgColor='FFF2CC'); thin = Side(style='thin', color='D9D9D9')
wrap = Alignment(wrap_text=True, vertical='top')
def style(ws, widths, review_cols=(), freeze='A2', header_row=1):
    for c in ws[header_row]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD; c.alignment = Alignment(wrap_text=True, vertical='center')
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=header_row + 1):
        for c in row:
            c.alignment = wrap; c.border = Border(bottom=thin)
            if c.column in review_cols: c.fill = REV
    for c in ws[header_row]:
        if c.column in review_cols: c.fill = PatternFill('solid', fgColor='BF9000')
    ws.freeze_panes = freeze; ws.auto_filter.ref = ws.dimensions

ws = wb['Code groups']
style(ws, [7, 24, 66, 52, 16, 12, 10, 12, 14, 12, 18, 40], review_cols=(11, 12), freeze='C2')
dv = DataValidation(type='list', formula1='"Keep,Change,Remove"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'K2:K{ws.max_row}')
for r in ws.iter_rows(min_row=2, min_col=7, max_col=9):
    for c in r: c.number_format = '#,##0'
ws = wb['Concepts']
style(ws, [24, 12, 62, 12, 16, 13, 12, 10, 24, 30, 14, 40], review_cols=(11, 12), freeze='D2')
for r in ws.iter_rows(min_row=2, min_col=7, max_col=8):
    for c in r: c.number_format = '#,##0'
dv2 = DataValidation(type='list', formula1='"Keep,Remove"', allow_blank=True); ws.add_data_validation(dv2); dv2.add(f'K2:K{ws.max_row}')
ws = wb['Codes to add']
style(ws, [26, 26, 50, 60], review_cols=(1, 2, 3, 4))
dv3 = DataValidation(type='list', formula1="='Code groups'!$B$2:$B$%d" % (len(G) + 1), allow_blank=True); ws.add_data_validation(dv3); dv3.add(f'A2:A{ws.max_row}')
ws = wb['Glossary']
style(ws, [26, 60, 70], freeze='A2')
for c in ws[len(W) + 4]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD
ws.auto_filter.ref = None
ws = wb['Read me']
ws.column_dimensions['A'].width = 34; ws.column_dimensions['B'].width = 120
for row in ws.iter_rows():
    for c in row: c.alignment = wrap
ws['A1'].font = Font(bold=True, size=16)
for r in ws.iter_rows(min_row=2):
    if r[0].value in ('Sheets', 'Quick facts that may matter for the review'): r[0].font = Font(bold=True, size=12)
    elif r[0].value: r[0].font = Font(bold=True)
wb.move_sheet('Read me', offset=-wb.index(wb['Read me']))
wb.active = 0
wb.save(out)
print(out, '|', len(G), 'groups,', len(C), 'concept rows,', int((C['Applicants with the concept'] == 0).sum()), 'never seen')
