"""Code lists of one use case (colonoscopy, mammography, letrozole) -> one workbook for clinical review.

Same layout as nb/repr_learn_chestpain/outputs/chestpain_AHA_codesets_for_review.xlsx (sheets Read me, Code groups, Concepts, Codes to add, Glossary;
the yellow columns are for the reviewer), plus a Section and an Excluded terms column on Code groups.

usage (conda env ethos_llm, cwd = nb/):
    python -I export_codesets_xlsx.py colonoscopy            # writes repr_learn_colonoscopy/outputs/colonoscopy_codesets_for_review.xlsx
    python -I export_codesets_xlsx.py mammography out.xlsx
    python -I export_codesets_xlsx.py letrozole              # first run builds the member file from the extract (about a minute), then reuses it

Nothing on a sheet is typed by hand except the Read me prose and the glossary wording:
  <use case>/<yaml>             the code groups: search terms, excluded terms, vocabularies, rationale (the comments and the `source:` key)
  <use case>/<members csv>      the concepts each group found, with applicant and event counts (written by the NMF notebook run; for letrozole by this script)
  <use case>/<page md>          which groups the engine's predicates actually use
"""
import datetime, importlib.util, os, re, sys, warnings, yaml
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

warnings.filterwarnings('ignore', message='This pattern is interpreted as a regular expression')

here = os.path.dirname(os.path.abspath(__file__))

CASES = {
    'colonoscopy': dict(
        dir='repr_learn_colonoscopy', yaml='codesets.yaml', inputs='../inputs/colonoscopy_cohort',
        members='outputs/token_members_k7_colonoscopy_v1.csv', page='outputs/colonoscopy_all_patterns.md', used='group',
        out='outputs/colonoscopy_codesets_for_review.xlsx', anchor='colonoscopy', noun='colonoscopy',
        title='Colonoscopy code lists for clinical review',
        source=('codesets.yaml (version 1, written 2026-10-19), exported {today}. Built from four documents: the underwriting note "Colonoscopy and Underwriting" (UW); '
                'the US Preventive Services Task Force (USPSTF) colorectal cancer screening recommendation, JAMA 2021;325:1965-1977, doi:10.1001/jama.2021.6238; '
                'the US Multi-Society Task Force (USMSTF) follow-up after colonoscopy and polypectomy, Gupta S, et al. Gastroenterology 2020;158:1131-1153, doi:10.1053/j.gastro.2019.10.026; '
                'and the American Society for Gastrointestinal Endoscopy (ASGE) guideline on gastroesophageal reflux disease, Desai M, et al. Gastrointest Endosc 2025;101:267-284, used only for the upper endoscopy groups. '
                'Each group carries the document, section or table that justifies it in the Rationale and source column.'),
        example='a colonoscopy with polyp removal or an iron deficiency anemia diagnosis',
        population='each has a colonoscopy code',
        order_example='the umbrella group colonoscopy comes after its finer procedure groups',
        facts=[['In situ disease', 'Applicants with in situ colorectal disease only (carcinoma in situ of the colon or rectum, ICD-10 D01.0 to D01.2) stay in the cohort and count as "no cancer" in the label. '
                                   'They are pre-cancer with some risk and go to manual review (underwriting note: colon cancer guidelines).'],
               ['Sources not in the folder', 'The underwriting note cites the 2024 colonoscopy quality indicators (Am J Gastroenterol 2024;119:1754-1780), which are not among the source documents. '
                                             'The file named as the ASGE endoscopy guideline is the gastroesophageal reflux disease guideline, so the upper endoscopy groups are context for applicants who also have an upper endoscopy.']]),
    'mammography': dict(
        dir='repr_learn_mammography', yaml='codesets_v2.yaml', inputs='../inputs/mammography_cohort',
        members='outputs/token_members_k8_mammography_v2.csv', page='outputs/mammography_all_patterns.md', used='group',
        out='outputs/mammography_codesets_for_review.xlsx', anchor='mammography', noun='mammography',
        title='Mammography code lists for clinical review',
        source=('codesets_v2.yaml (version 2, the guideline rewrite of codesets.yaml), exported {today}. Built from two guidelines: '
                'the US Preventive Services Task Force (USPSTF) breast cancer screening recommendation, JAMA 2024;331(22):1918-1930, doi:10.1001/jama.2024.5534; '
                'and the American Society of Clinical Oncology (ASCO) breast cancer follow-up and surveillance guideline update, Nahleh Z, et al. J Clin Oncol 2026, doi:10.1200/JCO-26-01700 '
                '("Tbl 4 x.y" in the notes is a row of its Table 4). A section carried over from version 1 says so in the Section column.'),
        example='a breast ultrasound or a hormonal contraceptive',
        population='each has a mammography code',
        order_example='the umbrella group mammography comes after mammography_screening and mammography_diagnostic',
        facts=[['In situ disease', 'Applicants with in situ breast disease only (ductal or lobular carcinoma in situ) stay in the cohort and count as "no breast cancer" in the label. '
                                   'They are pre-cancer with some risk and go to manual review. The in_situ group holds their codes, and breast_cancer excludes them.']]),
    'letrozole': dict(
        dir='repr_learn_letrozole', yaml='codesets.yaml', inputs='../inputs/letrozole_cohort',
        members='outputs/token_members_letrozole_groups.csv', page='Letrozole_Rx_Predicate_Engine.md', used='concept_id',
        out='outputs/letrozole_codesets_for_review.xlsx', anchor='letrozole', noun='letrozole',
        title='Letrozole code lists for clinical review',
        source=('codesets.yaml (version 5), exported {today}. There is no clinical guideline behind this file: the groups were chosen to tell letrozole '
                'used for fertility apart from letrozole used after breast cancer (aromatase inhibitors, fertility drugs and procedures, breast cancer and its treatment, menopause). '
                'The file header lists what each version changed; version 5 fixed a breast cancer group that matched benign breast neoplasms.'),
        example='an in vitro fertilization procedure or a breast cancer diagnosis',
        population='women with a letrozole fill and a valid policy',
        order_example='pregnancy_test comes before pregnancy_outcome, whose terms would otherwise swallow the pregnancy tests',
        facts=[['In situ disease', 'Carcinoma in situ of the breast has its own group (dcis) and is not pooled into breast_cancer, because it does not carry the same endocrine therapy expectation.']]),
}

# plain wording for the abbreviations found in the notes; the chest pain list is reused first, these are the ones it lacks
EXTRA_ABBR = {
    'AGA': 'American Gastroenterological Association',
    'ASCO': 'American Society of Clinical Oncology',
    'ASGE': 'American Society for Gastrointestinal Endoscopy',
    'ATM': 'ataxia-telangiectasia mutated gene (breast cancer susceptibility)',
    'BARD1': 'BRCA1-associated RING domain 1 gene (breast cancer susceptibility)',
    'BRCA': 'breast cancer susceptibility genes (BRCA1 and BRCA2)',
    'BRCA1/2': 'breast cancer susceptibility genes 1 and 2',
    'CA': 'cancer antigen (CA 15-3 and CA 27.29 are blood tumor markers followed in breast cancer)',
    'CDH1': 'cadherin 1 gene (hereditary diffuse gastric and lobular breast cancer)',
    'CDK4/6': 'cyclin-dependent kinases 4 and 6 (target of a class of breast cancer drugs)',
    'CEA': 'carcinoembryonic antigen (blood tumor marker)',
    'CHEK2': 'checkpoint kinase 2 gene (breast cancer susceptibility)',
    'CPT': 'Current Procedural Terminology; CPT II codes are the quality-reporting codes',
    'CRC': 'colorectal cancer',
    'CT': 'computed tomography (CT scan)',
    'DBT': 'digital breast tomosynthesis (3D mammography)',
    'DNA': 'deoxyribonucleic acid (genetic material)',
    'DNA-FIT': 'stool DNA test combined with a fecal immunochemical test',
    'EGD': 'esophagogastroduodenoscopy (upper endoscopy)',
    'EMR': 'endoscopic mucosal resection (removal of a flat lesion through the scope)',
    'ESD': 'endoscopic submucosal dissection (removal of a larger lesion through the scope)',
    'FAP': 'familial adenomatous polyposis (inherited syndrome with hundreds of colon polyps)',
    'FDA': 'US Food and Drug Administration',
    'FIT': 'fecal immunochemical test (stool test for blood)',
    'HER2': 'human epidermal growth factor receptor 2 (a breast cancer subtype and drug target)',
    'HNPCC': 'hereditary nonpolyposis colorectal cancer, also called Lynch syndrome',
    'HR': 'hormone receptor (estrogen or progesterone receptor of the tumor)',
    'IBD': 'inflammatory bowel disease (Crohn disease and ulcerative colitis)',
    'ICD-10': 'International Classification of Diseases, 10th revision (diagnosis codes)',
    'IORT': 'intraoperative radiation therapy (radiation given during the operation)',
    'LOINC': 'Logical Observation Identifiers Names and Codes, the coding system for laboratory tests',
    'MRI': 'magnetic resonance imaging',
    'MSI': 'microsatellite instability (tumor marker of Lynch syndrome)',
    'MUTYH': 'MUTYH gene (MUTYH-associated polyposis)',
    'NF1': 'neurofibromin 1 gene (neurofibromatosis type 1)',
    'PALB2': 'partner and localizer of BRCA2 gene (breast cancer susceptibility)',
    'PTEN': 'phosphatase and tensin homolog gene (Cowden syndrome)',
    'RAD51C/D': 'RAD51 paralog C and D genes (breast and ovarian cancer susceptibility)',
    'RxNorm': 'the standard coding system for medicines in the US',
    'RxNorm Extension': 'OMOP extension of RxNorm for medicines RxNorm does not cover',
    'SCADR': 'screening colonoscopy adenoma detection rate (a quality measure)',
    'SSP': 'sessile serrated polyp',
    'STK11': 'serine/threonine kinase 11 gene (Peutz-Jeghers syndrome)',
    'TIF': 'transoral incisionless fundoplication (reflux procedure through the mouth)',
    'TP53': 'tumor protein p53 gene (Li-Fraumeni syndrome)',
    'TSA': 'traditional serrated adenoma (a type of polyp)',
    'USMSTF': 'US Multi-Society Task Force on Colorectal Cancer',
    'USPSTF': 'US Preventive Services Task Force',
}
# upper-case words and code names in the notes that are not abbreviations
NOT_ABBR = {'ANCHOR', 'ALSO', 'BEFORE', 'BOTH', 'COHORT', 'ID', 'NOT', 'REMOVED', 'UMBRELLA', 'WARNING', 'II', 'JAMA', 'US'}


def abbr_table(texts):
    """glossary rows for the abbreviations that occur in `texts`; unknown ones are printed so the dictionary can be completed."""
    pl = yaml.safe_load(open(os.path.join(here, 'repr_learn_chestpain', 'chestpain_plain_labels.yaml'), encoding='utf-8'))
    known = {**pl['abbreviations'], **EXTRA_ABBR}
    blob = '\n'.join(texts)
    found = set(re.findall(r'\b[A-Z][A-Z0-9]+(?:[-/][A-Z0-9]+)*\b', blob))
    found |= {k for k in known if k != k.upper() and re.search(r'\b%s\b' % re.escape(k), blob)}      # RxNorm, RxNorm Extension
    skip = lambda t: (t in NOT_ABBR or re.match(r'^[A-Z]\d', t) or re.search(r'-\d', t) and t not in known        # ICD-10 / HCPCS code names, DOI fragments
                      or all(x in known for x in re.split(r'[-/]', t)))                                         # ASGE-GERD is two known terms
    unknown = sorted(t for t in found if t not in known and not skip(t))
    if unknown:
        print('abbreviations without a glossary entry:', ', '.join(unknown))
    return [[k, known[k]] for k in sorted(found) if k in known], pl


def split_comment(line):
    """(code, comment) of a yaml line; a # inside quotes does not start a comment."""
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q and line[i - 1] != '\\':
                q = None
        elif ch in '"\'':
            q = ch
        elif ch == '#' and (i == 0 or line[i - 1].isspace()):
            return line[:i], line[i + 1:].strip()
    return line, ''


def read_yaml_notes(raw):
    """per tag: the rationale (every comment inside the tag's block) and the section header above it."""
    note, section, sect, cur = {}, {}, '', None
    for line in raw:
        m = re.match(r'^#\s*-{2,}\s*(.+?)\s*-{2,}\s*$', line)
        if m:
            sect = m.group(1)
            continue
        m = re.match(r'^([a-z_0-9]+):', line)
        if m:
            cur = m.group(1); note[cur] = []; section[cur] = sect
            c = split_comment(line)[1]
            if c: note[cur].append(c)
            continue
        if line and not line[0].isspace():                  # a column-0 comment or text ends the block
            cur = None
            continue
        if cur and line.strip():
            c = split_comment(line)[1]
            if c: note[cur].append(c)
    return {k: ' '.join(dict.fromkeys(v)) for k, v in note.items()}, section


def build_members(case, cs, path):
    """letrozole: one row per concept of every group, counted in the extract; written to `path` so the next run is offline."""
    spec = importlib.util.spec_from_file_location('eo_case', os.path.join(here, case['dir'], 'ethos_omop.py'))
    eo = importlib.util.module_from_spec(spec); spec.loader.exec_module(eo)
    inp = os.path.join(here, case['inputs'])
    concept = eo.load_concept(inp)
    code_map = eo.build_codesets(concept, cs, verbose=False)
    ev = eo.load_events(inp)[['person_id', 'concept_id']]
    cnt = ev.groupby('concept_id').agg(n_events=('person_id', 'size'), n_patients=('person_id', 'nunique'))
    groups, owner = {}, {}
    for tag, ids in code_map.items():
        for cid in sorted(ids):
            groups.setdefault(cid, []).append(tag)
    owner = {cid: ts[0] for cid, ts in groups.items()}                           # first tag in file order owns the concept
    own_n = ev.assign(g=ev.concept_id.map(owner)).dropna(subset=['g']).groupby('g').person_id.nunique()
    c = concept.set_index('concept_id')
    rows = [dict(token=owner[cid], concept_id=cid, concept_name=c.at[cid, 'concept_name'], vocabulary_id=c.at[cid, 'vocabulary_id'],
                 concept_code=c.at[cid, 'concept_code'], concept_class_id=c.at[cid, 'concept_class_id'], domain=c.at[cid, 'domain_id'],
                 n_events=int(cnt.n_events.get(cid, 0)), n_patients=int(cnt.n_patients.get(cid, 0)),
                 groups='|'.join(ts), token_n_patients=own_n.get(owner[cid]))
            for cid, ts in groups.items()]
    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.to_csv(path, index=False)
    print('wrote', path, '|', len(out), 'concept rows,', ev.person_id.nunique(), 'applicants with events')
    return out


def main(name, out=None):
    case = CASES[name]
    P = lambda f: os.path.join(here, case['dir'], f)
    out = out or P(case['out'])
    raw = open(P(case['yaml']), encoding='utf-8').read().split('\n')
    cs = yaml.safe_load('\n'.join(raw))
    note, section = read_yaml_notes(raw)
    for k, v in cs.items():                                                      # `source:` is the colonoscopy / mammography way to say why a group exists
        if v.get('source'):
            note[k] = ' '.join(dict.fromkeys([v['source'], note.get(k, '')])).strip()
    page = open(P(case['page']), encoding='utf-8').read()
    mem = pd.read_csv(P(case['members'])) if os.path.exists(P(case['members'])) else build_members(case, cs, P(case['members']))

    person_n = len(pd.read_csv(os.path.join(here, case['inputs'], 'person.csv'), usecols=['person_id']))
    m = re.search(r'cohort has ([\d,]+)', page)
    COHORT = int(m.group(1).replace(',', '')) if m else person_n
    assert set(mem.groups.dropna().str.split('|').explode()) <= set(cs), 'member file has groups the code file does not'

    # used by the engine: the page names the group, or (letrozole) lists the concept id of one of its concepts
    mem = mem[mem.groups.notna()].copy()
    if case['used'] == 'group':
        used = set(re.findall(r'group `([a-z_0-9]+)`', page)) | {case['anchor']}
    else:
        ids = set(re.findall(r'\b(\d{5,10})\b', page))
        used = {g for g, grp in mem.assign(g=mem.groups.str.split('|')).explode('g').groupby('g') if grp.concept_id.astype(str).isin(ids).any()}

    mem['group'] = mem.groups.str.split('|')
    mem = mem.explode('group')
    mem['also'] = [', '.join(x for x in g.split('|') if x != k) for g, k in zip(mem.groups, mem.group)]
    owner_patients = mem.drop_duplicates('token').set_index('token').token_n_patients.to_dict()
    order = {k: i for i, k in enumerate(cs, 1)}
    mem['ord'] = mem.group.map(order)
    mem = mem.sort_values(['ord', 'n_patients', 'concept_name'], ascending=[True, False, True])

    # ---- sheet: Code groups
    rows = []
    for k, v in cs.items():
        g = mem[mem.group == k]
        rows.append({
            'Order': order[k], 'Section': section.get(k, ''), 'Code group': k, 'Rationale and source': note.get(k, ''),
            'Included terms': ', '.join('"%s"' % t if ',' in t else t for t in v.get('patterns', [])) or ('fixed concept IDs: ' + ', '.join(map(str, v['concept_ids'])) if v.get('concept_ids') else ''),
            'Excluded terms': ', '.join(v.get('exclude', [])),
            'Vocabularies': ', '.join(v.get('vocabularies', [])) or 'all', 'Domain': v.get('domain', ''),
            'Concepts found': len(g), 'Concepts seen in the data': int((g.n_patients > 0).sum()),
            'Applicants assigned to the group': owner_patients.get(k) if pd.notna(owner_patients.get(k)) else None,
            'Used by the engine predicates': 'Yes' if k in used else 'No',
            'Review: keep, change or remove?': None, 'Review: comment': None})
    G = pd.DataFrame(rows)

    # ---- sheet: Concepts
    C = pd.DataFrame({
        'Code group': mem.group, 'Concept ID': mem.concept_id, 'Concept name': mem.concept_name, 'Vocabulary': mem.vocabulary_id,
        'Code': mem.concept_code.astype(str), 'Domain': mem.domain, 'Applicants with the concept': mem.n_patients, 'Events': mem.n_events,
        'Also in group': mem.also, 'Review: keep or remove?': None, 'Review: comment': None})
    assert C['Applicants with the concept'].max() <= COHORT, 'a concept has more applicants than the cohort'

    A = pd.DataFrame({'Code group': [None] * 40, 'Code or concept to add': None, 'Name or description': None, 'Why it matters': None})

    # ---- sheet: Read me
    empty = [k for k in cs if G.loc[G['Code group'] == k, 'Concepts found'].iat[0] == 0]
    single = [k for k in cs if G.loc[G['Code group'] == k, 'Concepts found'].iat[0] == 1]
    unseen = int((C['Applicants with the concept'] == 0).sum())
    vocabs = sorted({x for v in cs.values() for x in v.get('vocabularies', [])})
    unrestricted = any(not v.get('vocabularies') for v in cs.values())
    cut = f'; this is the analysis cohort of the NMF run, the extract holds {person_n:,}' if COHORT != person_n else ''
    facts = []
    if empty:
        facts.append(['Empty groups', f'{len(empty)} of the {len(cs)} groups ' + ('have' if len(empty) != 1 else 'has') + ' no concept in the extract: ' + ', '.join(empty) + '. Empty means unverified, not wrong: no concept name in the extract matches the included terms, '
                      'so check the terms, and check whether the codes live in a table the extract does not load' +
                      (' (the extract has no Observation table, where family and personal history codes sit).' if not os.path.exists(os.path.join(here, case['inputs'], 'master_observation.csv')) else '.')])
    blank = int((G['Rationale and source'] == '').sum())
    if blank > len(cs) / 4:
        facts.append(['Rationale', f'The code file has a note or a source for {len(cs) - blank} of the {len(cs)} groups. For the others read the Section column and the concepts.'])
    if single:
        facts.append(['Groups with one concept', f'{len(single)} groups hold a single concept: ' + ', '.join(single) + '. A group this thin can hardly separate care patterns.'])
    if unseen:
        facts.append(['Concepts never seen', f'{unseen} concept rows (a concept shared by two groups counts twice) have zero applicants: the code is valid and matches a group, but nobody in the extract has it.'])
    facts += case['facts']
    R = [
        [case['title'], ''], ['', ''],
        ['Source', case['source'].format(today=datetime.date.today().isoformat())],
        ['What it is', f'{len(cs)} code groups. Each group is a list of standard medical codes ({", ".join(vocabs)}{" and others" if unrestricted else ""}) found by searching concept names for the included terms on the Code groups sheet. '
                       f'A group stands for one clinical idea, for example {case["example"]}.'],
        ['Population', f'Counts come from the {case["noun"]} extract: {COHORT:,} applicants ({case["population"]}{cut}). They are numbers of applicants and events in the data, not rates for the general population.'],
        ['Used by the engine', f'The predicates and composites of the draft rule engine draw on {len(used)} of the {len(cs)} groups (column "Used by the engine predicates"). '
                               + ('The groups are the ones the engine page names. ' if case['used'] == 'group' else 'A group counts as used when the engine page lists the OMOP ID of one of its concepts. ')
                               + 'The other groups define what the sources name but the engine does not use yet.'],
        ['', ''], ['Sheets', ''],
        ['Code groups', 'One row per group, in file order: section of the code file, rationale and source, included and excluded terms (comma-separated; a term that itself contains a comma is in quotation marks), vocabularies, number of concepts found, and the review columns.'],
        ['Concepts', 'One row per concept in each group, with applicants and events. A concept shared by two groups appears under both. Concepts never seen in the data have zero applicants.'],
        ['Codes to add', 'Blank rows for codes or concepts you think are missing, with the group they belong to.'],
        ['Glossary', 'Abbreviations used in the notes and the plain-language terms.'],
        ['', ''],
        ['How to review', 'Fill the yellow columns and send the file back. On Code groups: keep, change or remove, with a comment. On Concepts: keep or remove for single codes. On Codes to add: anything missing.'],
        ['', ''], ['Quick facts that may matter for the review', ''],
        *facts,
        ['Reading the included terms', 'Terms are matched against the standard concept name, ignoring capitals, and may contain symbols such as ^ (start of the name) or .* (anything). Always read the concept list on the Concepts sheet, not only the terms.'],
        ['Order matters', 'A concept that matches several groups belongs to the first of them in the file, so a specific group comes before the general one (for example ' + case['order_example'] + '). Do not sort the groups.'],
        ['Applicant counts', 'Counts on the Concepts sheet are per concept and overlap, so do not add them up. "Applicants assigned to the group" is the number of applicants with a concept the group owns, that is, a concept for which it is the first group in the file. '
                             'An umbrella group listed after finer groups therefore shows only the applicants the finer groups did not take (it can be a handful) and is blank when none are left.'],
    ]
    R = pd.DataFrame(R, columns=['', ' '])

    # ---- sheet: Glossary
    texts = [*G['Rationale and source'], *G['Included terms'], *G['Section'], *G['Vocabularies'], *R[' '].astype(str)]
    gl, pl = abbr_table(texts)
    W = pd.DataFrame(gl, columns=['Abbreviation', 'Meaning'])
    keep = {'list of codes', 'code', 'billing or medical code', 'care pattern', 'service', 'diagnosis'}
    T = pd.DataFrame([r for r in pl['uw_vs_data'] if r[0] in keep], columns=['Plain term', 'Data-team word', 'Meaning'])

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

    col = lambda df, name: list(df.columns).index(name) + 1
    ws = wb['Code groups']
    style(ws, [7, 30, 26, 70, 52, 28, 16, 12, 10, 12, 14, 12, 18, 40], review_cols=(col(G, 'Review: keep, change or remove?'), col(G, 'Review: comment')), freeze='D2')
    kc = get_column_letter(col(G, 'Review: keep, change or remove?'))
    dv = DataValidation(type='list', formula1='"Keep,Change,Remove"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'{kc}2:{kc}{ws.max_row}')
    for r in ws.iter_rows(min_row=2, min_col=col(G, 'Concepts found'), max_col=col(G, 'Applicants assigned to the group')):
        for c in r: c.number_format = '#,##0'
    ws = wb['Concepts']
    style(ws, [26, 12, 62, 12, 16, 13, 12, 10, 24, 14, 40], review_cols=(col(C, 'Review: keep or remove?'), col(C, 'Review: comment')), freeze='D2')
    for r in ws.iter_rows(min_row=2, min_col=col(C, 'Applicants with the concept'), max_col=col(C, 'Events')):
        for c in r: c.number_format = '#,##0'
    kc = get_column_letter(col(C, 'Review: keep or remove?'))
    dv2 = DataValidation(type='list', formula1='"Keep,Remove"', allow_blank=True); ws.add_data_validation(dv2); dv2.add(f'{kc}2:{kc}{ws.max_row}')
    ws = wb['Codes to add']
    style(ws, [26, 26, 50, 60], review_cols=(1, 2, 3, 4))
    gc = get_column_letter(col(G, 'Code group'))
    dv3 = DataValidation(type='list', formula1="='Code groups'!$%s$2:$%s$%d" % (gc, gc, len(G) + 1), allow_blank=True); ws.add_data_validation(dv3); dv3.add(f'A2:A{ws.max_row}')
    ws = wb['Glossary']
    style(ws, [26, 70, 70], freeze='A2')
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
    print(out, '|', len(G), 'groups,', len(C), 'concept rows,', unseen, 'never seen,', len(empty), 'empty groups,', len(used), 'used by the engine, cohort', COHORT)


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in CASES:
        sys.exit('usage: python -I export_codesets_xlsx.py {%s} [out.xlsx]' % '|'.join(CASES))
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
