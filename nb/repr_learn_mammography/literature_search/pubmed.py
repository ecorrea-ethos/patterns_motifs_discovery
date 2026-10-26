"""Search definitions for the literature column of final_table_mammography_k8_v2.xlsx (codesets_v2, NMF k=8, group tokens).

Helpers (q, curl) as in nb/repr_learn_chestpain/literature_search/pubmed.py. Read-only GET requests to NCBI E-utilities, no API key
(about 3 requests/s). Uses /usr/bin/curl, not urllib: behind the corporate TLS proxy Python rejects the certificate chain.
T   concept -> hand-written PubMed clause (never the raw OMOP name)
ENT group -> top-5 entities of the group (column C of the table; code pairs that are one clinical entity are merged)
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
 # breast imaging and cancer
 'mam_dx': '("diagnostic mammography"[tiab])',
 'mam_scr': '("screening mammography"[tiab] OR "mammography screening"[tiab] OR "mammographic screening"[tiab])',
 'tomo': '("breast tomosynthesis"[tiab] OR "digital breast tomosynthesis"[tiab] OR tomosynthesis[tiab])',
 'BC': '("breast cancer"[tiab] OR "breast neoplasms"[mh])',
 'receptor': '("hormone receptor"[tiab] OR "estrogen receptor"[tiab] OR "receptor status"[tiab] OR HER2[tiab])',
 'mastect': '(mastectomy[tiab] OR "breast surgery"[tiab] OR "breast-conserving surgery"[tiab])',
 'lymph': '("sentinel lymph node"[tiab] OR "axillary lymph node"[tiab] OR "lymph node biopsy"[tiab] OR "axillary dissection"[tiab])',
 'insitu': '("ductal carcinoma in situ"[tiab] OR DCIS[tiab] OR "lobular carcinoma in situ"[tiab])',
 'tumor_morph': '("tumor morphometry"[tiab] OR "tumour morphometry"[tiab] OR morphometric[tiab] OR "nuclear grade"[tiab])',
 # laboratory and visit
 'chem': '("metabolic panel"[tiab] OR "chemistry panel"[tiab] OR "blood chemistry"[tiab] OR "serum chemistry"[tiab])',
 'CBC': '("complete blood count"[tiab] OR "blood count"[tiab])',
 'venip': '(venipuncture[tiab] OR "blood draw"[tiab] OR "blood sampling"[tiab])',
 'lipid': '("lipid panel"[tiab] OR "lipid profile"[tiab] OR lipids[tiab] OR cholesterol[tiab])',
 'phys': '("physical examination"[tiab] OR "general examination"[tiab] OR "clinical breast examination"[tiab])',
 'prev': '("preventive care"[tiab] OR "preventive health"[tiab] OR "preventive visit"[tiab] OR "annual physical"[tiab] OR "periodic health examination"[tiab] OR "well-woman"[tiab])',
 # cardiac work-up (c1)
 'CP': '("chest pain"[tiab])',
 'ecg': '(electrocardiogram[tiab] OR electrocardiography[tiab] OR ECG[tiab] OR EKG[tiab])',
 'trop': '(troponin[tiab])',
 'cxr': '("chest radiograph"[tiab] OR "chest radiography"[tiab] OR "chest x-ray"[tiab] OR "chest X ray"[tiab])',
 # prescriptions (c2) and no-cancer label bundle
 'mpred': '(methylprednisolone[tiab])', 'azithro': '(azithromycin[tiab])', 'amox': '("amoxicillin clavulanate"[tiab] OR "amoxicillin-clavulanate"[tiab])',
 'pred': '(prednisone[tiab])', 'flucon': '(fluconazole[tiab])', 'flutic': '(fluticasone[tiab])',
 'prog': '(progesterone[tiab])', 'contra': '("hormonal contraceptive"[tiab] OR "hormonal contraception"[tiab] OR "oral contraceptive"[tiab] OR "oral contraceptives"[tiab])',
 'bupro': '(bupropion[tiab])', 'mht': '("menopausal hormone therapy"[tiab] OR "hormone replacement therapy"[tiab] OR "menopausal hormone"[tiab])',
 'benzo': '(benzonatate[tiab])',
 # women's health (c3)
 'naat': '("nucleic acid amplification"[tiab] OR "nucleic acid detection"[tiab] OR chlamydia[tiab] OR gonorrhea[tiab])',
 'cerv': '("cervical screening"[tiab] OR "cervical cancer screening"[tiab] OR "cervical cytology"[tiab] OR "Pap smear"[tiab] OR "Pap test"[tiab])',
 'upt': '("urine pregnancy test"[tiab] OR "pregnancy test"[tiab])',
 'gyn': '("gynecologic examination"[tiab] OR "gynecological examination"[tiab] OR "pelvic examination"[tiab])',
 # endocrine labs (c4)
 'b12': '("vitamin B12"[tiab] OR cobalamin[tiab])', 'vitd': '("vitamin D"[tiab] OR "25-hydroxyvitamin D"[tiab])',
 't4': '("free T4"[tiab] OR "free thyroxine"[tiab] OR "thyroid function"[tiab])', 'A1c': '("hemoglobin A1c"[tiab] OR "glycated hemoglobin"[tiab] OR HbA1c[tiab])',
 'ferr': '(ferritin[tiab] OR "iron studies"[tiab])',
 'fsh': '("follicle stimulating hormone"[tiab] OR "follicle-stimulating hormone"[tiab] OR FSH[tiab])',
 # physical therapy (c5)
 'ther_ex': '("therapeutic exercise"[tiab] OR "exercise therapy"[tiab])', 'manual': '("manual therapy"[tiab])',
 'ther_act': '("therapeutic activities"[tiab] OR "functional activities"[tiab])',
 'neuro_re': '("neuromuscular reeducation"[tiab] OR "neuromuscular re-education"[tiab] OR "neuromuscular training"[tiab])',
 'pt_eval': '("physical therapy evaluation"[tiab] OR "physiotherapy assessment"[tiab] OR "physical therapy"[tiab] OR physiotherapy[tiab])',
 # peri-operative (c6)
 'ondans': '(ondansetron[tiab])', 'fent': '(fentanyl[tiab])', 'propof': '(propofol[tiab])', 'midaz': '(midazolam[tiab])', 'dexa': '(dexamethasone[tiab])',
 # colorectal / pathology / dermatology (c7)
 'crc': '("colorectal cancer screening"[tiab] OR "colorectal screening"[tiab] OR colonoscopy[tiab])',
 'surgpath': '("surgical pathology"[tiab] OR histopathology[tiab] OR "pathology report"[tiab])',
 'neoplasm_scr': '("cancer screening"[tiab] OR "screening for cancer"[tiab])',
 'keratosis': '("seborrheic keratosis"[tiab] OR "senile hyperkeratosis"[tiab] OR "actinic keratosis"[tiab] OR hyperkeratosis[tiab])',
 'pigment': '(hyperpigmentation[tiab] OR "skin lesion"[tiab] OR "pigmented lesion"[tiab])',
}
ENT = {'c0': ['mam_scr', 'lipid', 'phys', 'prev', 'tomo'],
       'c1': ['ecg', 'trop', 'CP', 'cxr'],                       # the two ECG codes (93010, 93005) are one clinical entity
       'c2': ['mpred', 'azithro', 'amox', 'pred', 'flucon'],
       'c3': ['naat', 'cerv', 'upt', 'gyn'],                     # the two NAAT codes (87591, 87491) are one clinical entity
       'c4': ['b12', 'vitd', 't4', 'ferr', 'fsh'],
       'c5': ['ther_ex', 'manual', 'ther_act', 'neuro_re', 'pt_eval'],
       'c6': ['ondans', 'fent', 'propof', 'midaz', 'dexa'],
       'c7': ['crc', 'surgpath', 'neoplasm_scr', 'keratosis', 'pigment']}
# table row (Excel row of the final table, 2-25) -> distinct steps of its typical order of care (order not testable in PubMed).
# Rebuilt 2026-10-19 from the regenerated table (female-only, F3 off); repeated steps (x2, x4) count once.
PAT = {2: ['prev', 'phys', 'lipid'], 3: ['prev', 'phys', 'venip', 'lipid'], 4: ['phys', 'lipid', 'mam_scr'],
       5: ['ecg', 'chem', 'CBC'], 6: ['chem'], 7: ['CBC', 'chem'],
       8: ['pred', 'mam_scr', 'tomo'], 9: ['mam_scr', 'tomo', 'pred'], 10: ['mpred', 'mam_scr', 'tomo'],
       11: ['naat', 'cerv'], 12: ['cerv', 'naat'], 13: ['gyn', 'naat'],
       14: ['vitd', 'b12', 't4'], 15: ['lipid', 'b12', 't4'], 16: ['vitd', 'A1c', 't4'],
       17: ['ther_ex', 'manual', 'ther_act'], 18: ['manual', 'neuro_re'], 19: ['ther_act', 'ther_ex'],
       20: ['dexa', 'ondans', 'midaz', 'propof'], 21: ['fent', 'ondans', 'midaz', 'propof'], 22: ['dexa', 'fent', 'midaz', 'propof'],
       23: ['tomo', 'crc', 'neoplasm_scr'], 24: ['mam_scr', 'tomo', 'crc', 'neoplasm_scr'], 25: ['mam_scr', 'crc', 'neoplasm_scr']}
