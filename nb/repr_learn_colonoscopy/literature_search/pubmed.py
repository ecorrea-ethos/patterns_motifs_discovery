"""Search definitions for the literature column of final_table_colonoscopy_k7_v1.xlsx (codesets v1, NMF k=7, group tokens).

Helpers (q, curl) as in nb/repr_learn_mammography/literature_search/pubmed.py. Read-only GET requests to NCBI E-utilities, no API key
(about 3 requests/s). Uses /usr/bin/curl, not urllib: behind the corporate TLS proxy Python rejects the certificate chain.
T   concept -> hand-written PubMed clause (never the raw OMOP name)
ENT bundle -> top-5 entities of the bundle (column C of the table; code pairs that are one clinical entity are merged)
PAT table row (Excel row number) -> steps of its typical order of care. PubMed cannot test order: the steps are ANDed, unordered.
Run the scripts from this folder.
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

T = {
 # colorectal setting
 'CRC': '("colorectal cancer"[tiab] OR "colorectal neoplasms"[mh] OR "colon cancer"[tiab] OR "rectal cancer"[tiab])',
 'crc_scr': '("colorectal cancer screening"[tiab] OR "colorectal screening"[tiab] OR "colon cancer screening"[tiab] OR colonoscopy[tiab])',
 'colonoscopy': '(colonoscopy[tiab])',
 'polypectomy': '(polypectomy[tiab] OR "polyp removal"[tiab] OR "endoscopic mucosal resection"[tiab])',
 'polyp': '("colorectal polyp"[tiab] OR "colorectal polyps"[tiab] OR "colon polyp"[tiab] OR "colonic polyp"[tiab] OR "colonic polyps"[tiab] OR adenoma*[tiab])',
 'benign_neo': '("benign neoplasm"[tiab] OR "benign colorectal"[tiab] OR "colorectal adenoma"[tiab] OR "colorectal adenomas"[tiab] OR "advanced adenoma"[tiab])',
 'biopsy': '(biopsy[tiab])',
 'divert': '(diverticulosis[tiab] OR diverticular[tiab] OR diverticulitis[tiab])',
 'surgpath': '("surgical pathology"[tiab] OR histopathology[tiab] OR "pathology report"[tiab] OR histology[tiab])',
 'bowelprep': '("bowel preparation"[tiab] OR "bowel prep"[tiab])',
 'colectomy': '(colectomy[tiab] OR ostomy[tiab] OR stoma[tiab] OR "colorectal surgery"[tiab])',
 'chemoCRC': '(fluoropyrimidine*[tiab] OR "5-fluorouracil"[tiab] OR capecitabine[tiab] OR oxaliplatin[tiab] OR FOLFOX[tiab])',
 'cea': '("carcinoembryonic antigen"[tiab] OR CEA[tiab])',
 # laboratory and visit
 'chem': '("metabolic panel"[tiab] OR "chemistry panel"[tiab] OR "blood chemistry"[tiab] OR "serum chemistry"[tiab])',
 'CBC': '("complete blood count"[tiab] OR "blood count"[tiab])',
 'venip': '(venipuncture[tiab] OR "blood draw"[tiab] OR "blood sampling"[tiab])',
 'lipid': '("lipid panel"[tiab] OR "lipid profile"[tiab] OR lipids[tiab] OR cholesterol[tiab])',
 'phys': '("physical examination"[tiab] OR "general examination"[tiab] OR "routine examination"[tiab])',
 'prev': '("preventive care"[tiab] OR "preventive health"[tiab] OR "preventive visit"[tiab] OR "annual physical"[tiab] OR "periodic health examination"[tiab] OR "preventive services"[tiab])',
 'psa': '("prostate-specific antigen"[tiab] OR "prostate specific antigen"[tiab] OR PSA[tiab])',
 'immun': '(immunization[tiab] OR vaccination[tiab] OR vaccine*[tiab])',
 # acute care (c0)
 'ecg': '(electrocardiogram[tiab] OR electrocardiography[tiab] OR ECG[tiab] OR EKG[tiab])',
 'trop': '(troponin[tiab])',
 'abdpain': '("abdominal pain"[tiab])',
 'ondans': '(ondansetron[tiab])',
 # prescriptions (c2)
 'mpred': '(methylprednisolone[tiab])', 'azithro': '(azithromycin[tiab])', 'amox': '("amoxicillin clavulanate"[tiab] OR "amoxicillin-clavulanate"[tiab])',
 'pred': '(prednisone[tiab])',
 'ppi': '("proton pump inhibitor"[tiab] OR "proton pump inhibitors"[tiab] OR PPI[tiab] OR "H2 blocker"[tiab] OR "H2 receptor antagonist"[tiab] OR omeprazole[tiab] OR pantoprazole[tiab] OR famotidine[tiab])',
 # women's preventive care (c3)
 'bc_scr': '("screening mammography"[tiab] OR "mammography screening"[tiab] OR "mammographic screening"[tiab] OR "breast cancer screening"[tiab] OR tomosynthesis[tiab])',
 'cerv': '("cervical screening"[tiab] OR "cervical cancer screening"[tiab] OR "cervical cytology"[tiab] OR "Pap smear"[tiab] OR "Pap test"[tiab])',
 'gyn': '("gynecologic examination"[tiab] OR "gynecological examination"[tiab] OR "pelvic examination"[tiab])',
 # physical therapy (c4)
 'ther_ex': '("therapeutic exercise"[tiab] OR "exercise therapy"[tiab])', 'manual': '("manual therapy"[tiab])',
 'ther_act': '("therapeutic activities"[tiab] OR "functional activities"[tiab])',
 'neuro_re': '("neuromuscular reeducation"[tiab] OR "neuromuscular re-education"[tiab] OR "neuromuscular training"[tiab])',
 'pt_eval': '("physical therapy evaluation"[tiab] OR "physiotherapy assessment"[tiab] OR "physical therapy"[tiab] OR physiotherapy[tiab])',
 # endocrine, nutrient and iron labs (c6)
 'b12': '("vitamin B12"[tiab] OR cobalamin[tiab])', 'vitd': '("vitamin D"[tiab] OR "25-hydroxyvitamin D"[tiab])',
 't4': '("free T4"[tiab] OR "free thyroxine"[tiab] OR "thyroid function"[tiab])', 'A1c': '("hemoglobin A1c"[tiab] OR "glycated hemoglobin"[tiab] OR HbA1c[tiab])',
 'iron': '(ferritin[tiab] OR "iron studies"[tiab] OR "iron deficiency"[tiab] OR "total iron binding capacity"[tiab])',
 'testo': '(testosterone[tiab])',
}
ENT = {'c0': ['ecg', 'abdpain', 'trop', 'ondans'],                 # the two ECG codes (93005, 93010) are one clinical entity
       'c1': ['phys', 'lipid', 'prev', 'venip', 'immun'],
       'c2': ['mpred', 'amox', 'azithro', 'ppi', 'pred'],
       'c3': ['bc_scr', 'gyn', 'cerv', 'prev'],                    # breast screening tests and the breast screening visit are one clinical entity
       'c4': ['ther_ex', 'manual', 'ther_act', 'neuro_re', 'pt_eval'],
       'c5': ['polypectomy', 'polyp', 'surgpath', 'benign_neo', 'crc_scr'],
       'c6': ['vitd', 'b12', 't4', 'iron', 'testo']}
# table row (Excel row of the final table, 2-22) -> distinct steps of its typical order of care (order not testable in PubMed).
# Repeated steps (x2) count once.
PAT = {2: ['ecg', 'chem'], 3: ['ecg', 'chem', 'CBC'], 4: ['ecg', 'venip', 'chem'],
       5: ['phys', 'lipid', 'psa'], 6: ['venip', 'lipid', 'psa'], 7: ['phys', 'lipid', 'crc_scr'],
       8: ['ppi', 'azithro'], 9: ['amox', 'ppi'], 10: ['ppi', 'amox'],
       11: ['cerv', 'prev', 'bc_scr'], 12: ['bc_scr', 'prev', 'gyn'], 13: ['prev', 'gyn'],
       14: ['manual', 'ther_ex', 'ther_act'], 15: ['manual', 'ther_ex', 'ther_act'], 16: ['ther_ex', 'manual', 'ther_act'],
       17: ['divert', 'polyp', 'polypectomy'], 18: ['polyp', 'biopsy', 'polypectomy'], 19: ['divert', 'polyp', 'polypectomy', 'crc_scr'],
       20: ['lipid', 'vitd', 't4'], 21: ['vitd', 'A1c', 't4'], 22: ['lipid', 'vitd', 'b12', 'A1c']}
