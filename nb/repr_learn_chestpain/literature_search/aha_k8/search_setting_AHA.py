"""Round 2 for the AHA k=8 table. Bundle entities plus the bundle's clinical setting (guideline, ED chest pain, noncardiac chest pain,
musculoskeletal chest wall pain, respiratory infection, ...). Writes lit2_results_AHA.json; prints counts and the top 6 hits."""
import json
from pubmed_aha import q, T
G = '(guideline[ti] OR "scientific statement"[ti] OR "consensus"[ti] OR "expert consensus"[ti])'
NCCP = '("noncardiac chest pain"[tiab] OR "non-cardiac chest pain"[tiab])'
MSK = '("musculoskeletal chest pain"[tiab] OR "chest wall pain"[tiab])'
ED = '"emergency department"[tiab]'
Q = {
 'c0/c3 2021 chest pain guideline (title)': '"guideline for the evaluation and diagnosis of chest pain"[ti]',
 'c0 CP+stress/CCTA+stable/outpatient': T['CP'] + ' AND ' + T['stress'] + ' AND ("stable chest pain"[tiab] OR outpatient[tiab] OR "suspected coronary artery disease"[tiab])',
 'c0 CP+lipid+cardiovascular risk+outpatient': T['CP'] + ' AND ' + T['lipid'] + ' AND "cardiovascular risk"[tiab] AND (outpatient[tiab] OR "primary care"[tiab])',
 'c0 CP+ECG+primary care evaluation': T['CP'] + ' AND ' + T['ecg'] + ' AND "primary care"[tiab] AND (evaluation[tiab] OR diagnosis[tiab])',
 'c0 CP+hyperlipidemia+ECG': T['CP'] + ' AND ' + T['hyperl'] + ' AND ' + T['ecg'],
 'c1 CP+corticosteroid/antibiotic+respiratory infection': T['CP'] + ' AND (corticosteroid*[tiab] OR antibiotic*[tiab] OR ' + T['pred'] + ' OR ' + T['mpred'] + ' OR ' + T['azithro'] + ') AND (pneumonia[tiab] OR "respiratory infection"[tiab] OR bronchitis[tiab])',
 'c1 noncardiac CP+PPI': NCCP + ' AND ' + T['ppi'],
 'c1 CP+pericarditis/pleurisy+steroid/NSAID': T['CP'] + ' AND (pericarditis[tiab] OR pleurisy[tiab] OR pleuritic[tiab]) AND (' + T['pred'] + ' OR ' + T['mpred'] + ' OR NSAID*[tiab])',
 'c2 CP+pelvic/gyn exam': T['CP'] + ' AND ' + T['gyn'],
 'c2 CP+pregnancy evaluation': T['CP'] + ' AND pregnan*[tiab] AND (evaluation[tiab] OR diagnosis[tiab] OR ' + ED + ')',
 'c2 CP+cervical screening': T['CP'] + ' AND ' + T['pap'],
 'c3 CP+trop+CXR+ED': T['CP'] + ' AND ' + T['trop'] + ' AND ' + T['cxr'] + ' AND ' + ED,
 'c3 CP+trop+ED+blood tests (CBC/CMP/BMP)': T['CP'] + ' AND ' + T['trop'] + ' AND ' + ED + ' AND (' + T['CBC'] + ' OR ' + T['CMP'] + ' OR "basic metabolic panel"[tiab] OR "routine blood test*"[tiab] OR "laboratory test*"[tiab])',
 'c3 chest pain ED guideline/consensus': '"chest pain"[ti] AND ' + ED + ' AND ' + G,
 'c3 CP+lipase (abdominal/pancreatic mimic)': T['CP'] + ' AND ' + T['lipase'] + ' AND (epigastric[tiab] OR pancreatitis[tiab] OR abdominal[tiab])',
 'c4 noncardiac CP+GERD+endoscopy': NCCP + ' AND ' + T['gerd'] + ' AND ' + T['endo'],
 'c4 noncardiac CP guideline/review': NCCP + ' AND (review[pt] OR guideline[ti] OR "systematic review"[pt] OR consensus[ti])',
 'c4 CP+esophageal biopsy/eosinophilic esophagitis': T['CP'] + ' AND ("eosinophilic esophagitis"[tiab] OR "esophageal biopsy"[tiab] OR "oesophageal biopsy"[tiab])',
 'c5 musculoskeletal CP+physical therapy/manual': MSK + ' AND (' + T['pt'] + ' OR ' + T['manual'] + ' OR chiropractic[tiab])',
 'c5 noncardiac CP+exercise/manual therapy': NCCP + ' AND (' + T['ther_ex'] + ' OR ' + T['manual'] + ' OR exercise[tiab])',
 'c5 CP+LBP+PT': T['CP'] + ' AND ' + T['LBP'] + ' AND ' + T['pt'],
 'c5 musculoskeletal CP guideline/review': MSK + ' AND (review[pt] OR guideline[ti] OR "systematic review"[pt])',
 'c6 CP+vitamin D+coronary': T['CP'] + ' AND ' + T['vitd'] + ' AND (coronary[tiab] OR cardiovascular[tiab])',
 'c6 CP+iron deficiency/anemia': T['CP'] + ' AND (' + T['iron'] + ' OR anemia[tiab] OR anaemia[tiab])',
 'c6 CP+thyroid function': T['CP'] + ' AND (thyroid[tiab] OR thyrotoxicosis[tiab] OR hyperthyroidism[tiab])',
 'c6 CP+vitamin B12': T['CP'] + ' AND ' + T['b12'],
 'c7 CP+respiratory infection+ECG': T['CP'] + ' AND ' + T['uri'] + ' AND ' + T['ecg'],
 'c7 CP+acute bronchitis/cough': T['CP'] + ' AND (cough[tiab] OR bronchitis[tiab]) AND (acute[tiab]) AND ("primary care"[tiab] OR ' + ED + ' OR outpatient[tiab])',
 'c7 CP+pharyngitis': T['CP'] + ' AND ' + T['pharyng'],
 'c7 CP+COVID-19+ECG/troponin': T['CP'] + ' AND "COVID-19"[tiab] AND (' + T['ecg'] + ' OR ' + T['trop'] + ')',
}
res = []
for k, t in Q.items():
    n, arts = q(t, 6); res.append(dict(label=k, query=t, count=n, top=arts)); print(f'\n## {k}  n={n}', flush=True)
    for a in arts: print('   ', a[0], a[1], a[2], '|', a[3], flush=True)
json.dump(res, open('lit2_results_AHA.json', 'w'))
