"""Round 2. Bundle entities (>=3, unordered) plus the bundle's clinical setting, e.g. chest pain evaluation, cardiovascular risk,
non-cardiac chest pain, musculoskeletal chest wall pain. Writes lit2_results.json; prints counts + top hits."""
import json
from pubmed import q, T
G = '(guideline[ti] OR "scientific statement"[ti] OR "consensus"[ti] OR "expert consensus"[ti])'
Q = {
 'c0 CP+trop+ECG guideline': T['CP'] + ' AND ' + T['trop'] + ' AND ' + T['ecg'] + ' AND ' + G,
 'c0 CP+trop+ECG+CXR': T['CP'] + ' AND ' + T['trop'] + ' AND ' + T['ecg'] + ' AND ' + T['cxr'],
 'c0 CP+trop+ECG emergency department': T['CP'] + ' AND ' + T['trop'] + ' AND ' + T['ecg'] + ' AND "emergency department"[tiab]',
 'c0 CP+CXR+trop': T['CP'] + ' AND ' + T['cxr'] + ' AND ' + T['trop'],
 'c1 CP+women (pelvic/gyn)': T['CP'] + ' AND ' + T['gyn'],
 'c1 CP+pregnancy test': T['CP'] + ' AND ' + T['upt'] + ' AND (emergency[tiab] OR pregnan*[tiab])',
 'c1 CP+cervical screening': T['CP'] + ' AND ' + T['pap'],
 'c2 CP+lipid+A1c+cardiovascular risk': T['CP'] + ' AND ' + T['lipid'] + ' AND ' + T['A1c'] + ' AND "cardiovascular risk"[tiab]',
 'c2 CP+risk factors+outpatient preventive': T['CP'] + ' AND "cardiovascular risk"[tiab] AND (outpatient[tiab] OR primary care[tiab] OR ' + T['prev'] + ')',
 'c2 atypical CP+primary care+risk factors guideline': '"atypical chest pain"[tiab] AND ("primary care"[tiab] OR outpatient[tiab]) AND ("risk factors"[tiab]) AND ' + G,
 'c3 CP+corticosteroid/antibiotic+acute': T['CP'] + ' AND (corticosteroid*[tiab] OR antibiotic*[tiab] OR ' + T['pred'] + ' OR ' + T['mpred'] + ' OR ' + T['azithro'] + ') AND (pneumonia[tiab] OR "respiratory infection"[tiab] OR bronchitis[tiab])',
 'c3 noncardiac CP+NSAID (costochondritis)': '("noncardiac chest pain"[tiab] OR "non-cardiac chest pain"[tiab] OR costochondritis[tiab]) AND (NSAID*[tiab] OR ' + T['ibu'] + ' OR "anti-inflammatory"[tiab])',
 'c3 CP+pleuritic/pericarditis steroid NSAID': T['CP'] + ' AND (pericarditis[tiab] OR pleurisy[tiab] OR pleuritic[tiab]) AND (' + T['ibu'] + ' OR ' + T['pred'] + ' OR NSAID*[tiab])',
 'c4 musculoskeletal CP+physical therapy': '("musculoskeletal chest pain"[tiab] OR "chest wall pain"[tiab]) AND (' + T['pt'] + ' OR ' + T['manual'] + ' OR chiropractic[tiab])',
 'c4 noncardiac CP+exercise/manual therapy': '("noncardiac chest pain"[tiab] OR "non-cardiac chest pain"[tiab]) AND (' + T['ther_ex'] + ' OR ' + T['manual'] + ' OR exercise[tiab])',
 'c4 CP+LBP+PT': T['CP'] + ' AND ' + T['LBP'] + ' AND ' + T['pt'],
 'c4 musculoskeletal CP guideline/review': '("musculoskeletal chest pain"[tiab] OR "chest wall pain"[tiab]) AND (review[pt] OR guideline[ti] OR "systematic review"[pt])',
}
res = []
for k, t in Q.items():
    n, arts = q(t, 6); res.append(dict(label=k, query=t, count=n, top=arts)); print(f'\n## {k}  n={n}')
    for a in arts: print('   ', a[0], a[1], a[2], '|', a[3])
json.dump(res, open('lit2_results.json', 'w'))
