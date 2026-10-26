"""Round 2: each bundle's entities plus its clinical setting (acute care and colorectal cancer treatment, preventive screening,
bowel preparation, polypectomy surveillance, iron deficiency, ...). Writes lit2_results.json; prints counts and the top 6 hits (redirect to round2.log)."""
import json
from pubmed import q, T
G = '(guideline[ti] OR "recommendation statement"[ti] OR "consensus"[ti] OR "scientific statement"[ti] OR "practice guideline"[pt])'
Q = {
 'c0 colorectal cancer + troponin/ECG fluoropyrimidine cardiotoxicity': T['CRC'] + ' AND (' + T['trop'] + ' OR ' + T['ecg'] + ') AND (cardiotoxicity[tiab] OR ' + T['chemoCRC'] + ')',
 'c0 colorectal surgery + abdominal pain + emergency presentation': T['colectomy'] + ' AND ' + T['abdpain'] + ' AND (emergency[tiab] OR "emergency department"[tiab])',
 'c0 colorectal cancer chemotherapy + ondansetron nausea vomiting': T['CRC'] + ' AND ' + T['ondans'] + ' AND (chemotherapy[tiab] OR "nausea and vomiting"[tiab])',
 'c0 abdominal pain + troponin + ECG (differential)': T['abdpain'] + ' AND ' + T['trop'] + ' AND ' + T['ecg'],
 'c0 colorectal surgery preoperative ECG and blood tests (chemistry, CBC)': T['colectomy'] + ' AND ' + T['ecg'] + ' AND (' + T['chem'] + ' OR ' + T['CBC'] + ' OR "preoperative testing"[tiab])',
 'c0 colorectal cancer + emergency presentation complications': T['CRC'] + ' AND ("emergency presentation"[tiab] OR "emergency department"[tiab]) AND (complication*[tiab] OR obstruction[tiab] OR perforation[tiab] OR bleeding[tiab])',
 'c1 colorectal cancer screening + preventive visit + PSA/lipid': T['crc_scr'] + ' AND ' + T['prev'] + ' AND (' + T['psa'] + ' OR ' + T['lipid'] + ')',
 'c1 PSA screening + colorectal cancer screening co-adherence': T['psa'] + ' AND ' + T['crc_scr'] + ' AND (adherence[tiab] OR uptake[tiab] OR concordance[tiab] OR "up-to-date"[tiab] OR "multiple cancer"[tiab])',
 'c1 preventive services delivery primary care (colorectal screening, cholesterol)': T['crc_scr'] + ' AND ("preventive services"[tiab] OR "primary care"[tiab]) AND (cholesterol[tiab] OR lipid*[tiab])',
 'c1 periodic health examination + colorectal screening uptake': '("periodic health examination"[tiab] OR "annual physical"[tiab] OR "annual examination"[tiab] OR "preventive visit"[tiab]) AND ' + T['crc_scr'],
 'c1 immunization + colorectal cancer screening up-to-date': T['immun'] + ' AND ' + T['crc_scr'] + ' AND ("up-to-date"[tiab] OR uptake[tiab] OR adherence[tiab])',
 'c2 bowel preparation + PPI / antibiotics': T['bowelprep'] + ' AND (' + T['ppi'] + ' OR antibiotic*[tiab])',
 'c2 PPI use + colorectal cancer risk': T['ppi'] + ' AND ' + T['CRC'] + ' AND (risk[tiab])',
 'c2 antibiotics + colorectal cancer / adenoma risk': '(antibiotic*[ti] OR azithromycin[tiab]) AND (' + T['CRC'] + ' OR ' + T['polyp'] + ') AND (risk[tiab])',
 'c2 corticosteroid + colorectal neoplasia': '(corticosteroid*[tiab] OR glucocorticoid*[tiab]) AND (' + T['CRC'] + ' OR ' + T['polyp'] + ')',
 'c2 steroids and antibiotics in acute respiratory illness in primary care': '(' + T['pred'] + ' OR ' + T['mpred'] + ' OR ' + T['azithro'] + ' OR ' + T['amox'] + ') AND ("acute respiratory"[tiab] OR bronchitis[tiab] OR sinusitis[tiab]) AND ("primary care"[tiab] OR outpatient[tiab])',
 'c3 breast + cervical + colorectal screening co-adherence women': T['cerv'] + ' AND ' + T['crc_scr'] + ' AND ' + T['bc_scr'],
 'c3 breast + cervical screening co-adherence women': T['cerv'] + ' AND ' + T['bc_scr'] + ' AND (adherence[tiab] OR uptake[tiab] OR receipt[tiab])',
 'c3 gynecologic / pelvic exam + cancer screening in women': T['gyn'] + ' AND (' + T['bc_scr'] + ' OR ' + T['cerv'] + ' OR ' + T['crc_scr'] + ')',
 'c3 well-woman preventive visit + cancer screening': '("well-woman"[tiab] OR ' + T['prev'] + ') AND ' + T['bc_scr'] + ' AND ' + T['cerv'],
 'c4 physical therapy / exercise + colorectal cancer survivors': T['CRC'] + ' AND (' + T['ther_ex'] + ' OR ' + T['pt_eval'] + ' OR "exercise"[ti]) AND (survivor*[tiab] OR rehabilitation[tiab])',
 'c4 manual therapy + therapeutic exercise (musculoskeletal pain)': T['manual'] + ' AND ' + T['ther_ex'],
 'c4 physical therapy low back / neck / shoulder pain': T['pt_eval'] + ' AND (back pain[tiab] OR "neck pain"[tiab] OR "shoulder pain"[tiab]) AND (exercise[tiab] OR manual[tiab])',
 'c4 therapeutic activities + exercise + manual therapy rehabilitation': T['ther_act'] + ' AND ' + T['ther_ex'] + ' AND ' + T['manual'],
 'c5 polypectomy + pathology + polyp surveillance': T['polypectomy'] + ' AND ' + T['surgpath'] + ' AND ' + T['polyp'],
 'c5 post-polypectomy surveillance guideline': '(polypectomy[ti] OR "post-polypectomy"[ti] OR "follow-up after colonoscopy"[ti]) AND ' + G + ' AND surveillance[tiab]',
 'c5 colorectal screening guideline (USPSTF / consensus)': T['crc_scr'] + ' AND ' + G + ' AND (screening[ti])',
 'c5 diverticular disease + colonoscopy + polyps': T['divert'] + ' AND ' + T['colonoscopy'] + ' AND ' + T['polyp'],
 'c5 colonoscopy biopsy + polypectomy findings (adenoma detection)': T['colonoscopy'] + ' AND ' + T['polypectomy'] + ' AND ' + T['biopsy'] + ' AND (adenoma*[tiab] OR polyp*[tiab])',
 'c5 benign colorectal neoplasm / adenoma + surgical pathology + screening': T['benign_neo'] + ' AND ' + T['surgpath'] + ' AND ' + T['crc_scr'],
 'c6 iron deficiency + colorectal cancer / colonoscopy': T['iron'] + ' AND (' + T['CRC'] + ' OR ' + T['colonoscopy'] + ')',
 'c6 vitamin D + colorectal cancer / adenoma': T['vitd'] + ' AND (' + T['CRC'] + ' OR ' + T['polyp'] + ')',
 'c6 vitamin B12 + colorectal': T['b12'] + ' AND ' + T['CRC'],
 'c6 thyroid function + colorectal cancer': T['t4'] + ' AND ' + T['CRC'],
 'c6 testosterone + colorectal cancer': T['testo'] + ' AND ' + T['CRC'],
 'c6 CEA tumor marker colorectal surveillance guideline': T['cea'] + ' AND ' + T['CRC'] + ' AND (surveillance[tiab] OR follow-up[tiab]) AND ' + G,
 'c6 HbA1c + vitamin D + thyroid (metabolic and endocrine screening in adults)': T['A1c'] + ' AND ' + T['vitd'] + ' AND ' + T['t4'],
}
res = []
for k, t in Q.items():
    n, arts = q(t, 6); res.append(dict(label=k, query=t, count=n, top=arts)); print(f'\n## {k}  n={n}', flush=True)
    for a in arts: print('   ', a[0], a[1], a[2], '|', a[3], flush=True)
json.dump(res, open('lit2_results.json', 'w'))
