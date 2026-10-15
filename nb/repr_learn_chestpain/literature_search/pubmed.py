"""PubMed (NLM E-utilities) helpers for the literature column of the chest pain final table (final_table_chestpain_k5_full.xlsx).

Used by search_entities_patterns.py and search_setting.py. Read-only GET requests, no API key (about 3 requests/s).
Uses /usr/bin/curl, not urllib: behind the corporate TLS proxy Python rejects the certificate chain, curl uses the macOS trust store.
Edit T (concept -> PubMed clause), ENT (bundle -> top-5 entities) and PAT (table row -> pattern concepts) for another table.
The letrozole copy of this file lives in nb/repr_learn_letrozole/literature_search/.
"""
import json, subprocess, urllib.parse, time
B = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
def curl(u): return json.loads(subprocess.run(['/usr/bin/curl', '-sS', '-f', '-m', '40', u], capture_output=True, text=True, check=True).stdout)
def q(term, n=4):
    for _ in range(3):
        try:
            r = curl(B + 'esearch.fcgi?db=pubmed&retmode=json&sort=relevance&retmax=%d&term=%s' % (n, urllib.parse.quote(term)))['esearchresult']; break
        except Exception: time.sleep(2)
    else: return -1, []
    ids = r['idlist']; arts = []
    if ids:
        s = curl(B + 'esummary.fcgi?db=pubmed&retmode=json&id=' + ','.join(ids))['result']
        arts = [(i, s[i]['pubdate'][:4], s[i]['source'], s[i]['title'][:110]) for i in ids]
    time.sleep(0.35); return int(r['count']), arts

T = {  # OMOP entity -> hand-written PubMed clause (never the raw OMOP name)
 'CP': '("chest pain"[tiab])',
 'ecg': '(electrocardiogram[tiab] OR electrocardiography[tiab] OR ECG[tiab] OR EKG[tiab])',
 'trop': '(troponin[tiab])',
 'cxr': '("chest radiograph"[tiab] OR "chest radiography"[tiab] OR "chest x-ray"[tiab] OR "chest X ray"[tiab])',
 'inj': '("intravenous injection"[tiab] OR "intravenous push"[tiab] OR "intravenous medication"[tiab])',
 'gyn': '("gynecologic examination"[tiab] OR "gynecological examination"[tiab] OR "pelvic examination"[tiab])',
 'naat': '("nucleic acid amplification"[tiab] OR "nucleic acid detection"[tiab])',
 'pap': '("cervical cytology"[tiab] OR "Pap smear"[tiab] OR Papanicolaou[tiab])',
 'upt': '("urine pregnancy test"[tiab] OR "pregnancy test"[tiab])',
 'uc': '("urine culture"[tiab])',
 'lipid': '("lipid panel"[tiab] OR "lipid profile"[tiab] OR lipids[tiab] OR cholesterol[tiab])',
 'phys': '("physical examination"[tiab] OR "general examination"[tiab])',
 'venip': '(venipuncture[tiab] OR "blood draw"[tiab] OR "blood sampling"[tiab])',
 'A1c': '("hemoglobin A1c"[tiab] OR "glycated hemoglobin"[tiab] OR HbA1c[tiab])',
 'prev': '("preventive care"[tiab] OR "preventive medicine"[tiab] OR "annual physical"[tiab] OR "periodic health examination"[tiab] OR "annual health examination"[tiab])',
 'mpred': '(methylprednisolone[tiab])', 'amox': '("amoxicillin clavulanate"[tiab] OR "amoxicillin-clavulanate"[tiab])', 'azithro': '(azithromycin[tiab])',
 'pred': '(prednisone[tiab])', 'ibu': '(ibuprofen[tiab])',
 'ther_ex': '("therapeutic exercise"[tiab] OR "exercise therapy"[tiab])', 'manual': '("manual therapy"[tiab])',
 'LBP': '("low back pain"[mh] OR "low back pain"[tiab])',
 'ther_act': '("therapeutic activities"[tiab] OR "functional activities"[tiab])',
 'pt': '("physical therapy"[tiab] OR physiotherapy[tiab])',
 'CBC': '("complete blood count"[tiab] OR "blood count"[tiab])', 'CMP': '("comprehensive metabolic panel"[tiab] OR "metabolic panel"[tiab])',
}
# top-5 entities per bundle. c0: CPT 93005 and 93010 are the same clinical entity (ECG tracing / interpretation), so 4 distinct clauses.
ENT = {'c0': ['ecg', 'trop', 'cxr', 'inj'],
       'c1': ['gyn', 'naat', 'pap', 'upt', 'uc'],
       'c2': ['lipid', 'phys', 'venip', 'A1c', 'prev'],
       'c3': ['mpred', 'amox', 'azithro', 'pred', 'ibu'],
       'c4': ['ther_ex', 'manual', 'LBP', 'ther_act', 'pt']}
# table row (Excel row number) -> concepts of its typical order of care (chest pain step included; PubMed cannot test order)
PAT = {2: ['CP', 'cxr', 'trop'], 3: ['CP', 'ecg', 'trop'], 4: ['CP', 'ecg', 'trop'],
       5: ['CP', 'venip'], 6: ['venip', 'CP'], 7: ['CP', 'venip', 'CBC'],
       8: ['venip', 'lipid', 'CP'], 9: ['CP', 'lipid', 'A1c'], 10: ['CP', 'venip', 'lipid'],
       11: ['CP', 'CMP', 'CBC'], 12: ['CP', 'ecg', 'trop'], 13: ['CP', 'ecg', 'trop', 'CBC'],
       14: ['CP', 'manual'], 15: ['CP', 'ther_ex'], 16: ['CP', 'ther_ex', 'manual']}
