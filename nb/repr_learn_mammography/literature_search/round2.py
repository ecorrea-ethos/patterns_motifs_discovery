"""Round 2: each bundle's entities plus its clinical setting (screening, cardio-oncology, cardio-oncology, breast surgery
anaesthesia, rehabilitation after breast cancer, ...). Writes lit2_results.json; prints counts and the top 6 hits (redirect to round2.log)."""
import json
from pubmed import q, T
G = '(guideline[ti] OR "recommendation statement"[ti] OR "consensus"[ti] OR "scientific statement"[ti] OR "practice guideline"[pt])'
SCR = '(screening[ti] OR screening[tiab])'
Q = {
 'c0 preventive visit + screening mammography': T['prev'] + ' AND ' + T['mam_scr'],
 'c0 preventive services (mammography, cholesterol) delivery primary care': T['mam_scr'] + ' AND (cholesterol[tiab] OR lipid*[tiab]) AND ("preventive services"[tiab] OR "primary care"[tiab])',
 'c0 well-woman exam + mammography + lipid': '"well-woman"[tiab] AND ' + T['mam_scr'],
 'c0 DBT in screening + annual exam': T['tomo'] + ' AND ' + T['mam_scr'] + ' AND (screening[ti])',
 'c1 breast cancer + troponin/ECG cardiotoxicity': T['BC'] + ' AND (' + T['trop'] + ' OR ' + T['ecg'] + ') AND (cardiotoxicity[tiab] OR anthracycline*[tiab] OR trastuzumab[tiab] OR "cardio-oncology"[tiab])',
 'c1 breast arterial calcification mammography + cardiovascular': '("breast arterial calcification"[tiab] OR "breast arterial calcifications"[tiab]) AND (cardiovascular[tiab] OR coronary[tiab])',
 'c1 chest pain in breast cancer patients/survivors': T['CP'] + ' AND ' + T['BC'],
 'c1 cardio-oncology guideline baseline ECG + troponin': '(cardio-oncology[ti] OR cardio-oncology[tiab] OR cardiotoxicity[ti]) AND ' + G + ' AND (' + T['ecg'] + ' OR ' + T['trop'] + ')',
 'c1 chest pain+ECG+troponin+CXR (pleuritic differential)': T['CP'] + ' AND ' + T['ecg'] + ' AND ' + T['trop'] + ' AND ' + T['cxr'],
 'c2 steroid/antibiotic use + mammography screening': '(' + T['pred'] + ' OR ' + T['mpred'] + ' OR ' + T['azithro'] + ' OR corticosteroid*[tiab] OR antibiotic*[tiab]) AND ' + T['mam_scr'],
 'c2 corticosteroid + breast cancer risk or screening': '(corticosteroid*[tiab] OR glucocorticoid*[tiab]) AND ' + T['BC'] + ' AND (risk[tiab] OR screening[tiab])',
 'c2 antibiotics + breast cancer risk': '(antibiotic*[ti] OR azithromycin[tiab]) AND ' + T['BC'] + ' AND (risk[tiab])',
 'c3 well-woman visit: cervical + chlamydia + mammography': '(' + T['cerv'] + ' AND ' + T['naat'] + ' AND (mammograph*[tiab] OR "breast cancer screening"[tiab]))',
 'c3 gynecologic exam / pelvic exam + clinical breast exam': T['gyn'] + ' AND ("clinical breast examination"[tiab] OR "breast examination"[tiab] OR mammograph*[tiab])',
 'c3 breast + cervical screening co-adherence women': T['cerv'] + ' AND ("breast cancer screening"[tiab] OR mammograph*[tiab]) AND (adherence[tiab] OR "receipt"[tiab] OR uptake[tiab])',
 'c3 BRCA / genetic risk + diagnostic breast imaging': '(BRCA[tiab] OR "genetic counseling"[tiab]) AND ' + T['mam_dx'],
 'c4 vitamin D + breast cancer': T['vitd'] + ' AND ' + T['BC'],
 'c4 thyroid function + breast cancer': T['t4'] + ' AND ' + T['BC'],
 'c4 ferritin / iron + breast cancer': T['ferr'] + ' AND ' + T['BC'],
 'c4 vitamin B12 + breast cancer': T['b12'] + ' AND ' + T['BC'],
 'c4 FSH menopausal status + breast cancer endocrine therapy': T['fsh'] + ' AND ' + T['BC'] + ' AND (menopaus*[tiab] OR "aromatase inhibitor"[tiab])',
 'c5 physical therapy / exercise + breast cancer survivors': T['BC'] + ' AND (' + T['ther_ex'] + ' OR ' + T['pt_eval'] + ' OR "exercise"[ti]) AND (survivor*[tiab] OR rehabilitation[tiab])',
 'c5 manual therapy + breast cancer (lymphedema / shoulder)': T['manual'] + ' AND ' + T['BC'],
 'c5 aromatase inhibitor arthralgia + exercise / physical therapy': '("aromatase inhibitor"[tiab] OR "aromatase inhibitors"[tiab]) AND (arthralgia[tiab] OR "joint pain"[tiab] OR musculoskeletal[tiab]) AND (exercise[tiab] OR "physical therapy"[tiab] OR physiotherapy[tiab])',
 'c5 manual therapy + therapeutic exercise (musculoskeletal pain)': T['manual'] + ' AND ' + T['ther_ex'],
 'c5 rehabilitation after breast cancer surgery shoulder': T['BC'] + ' AND ' + T['mastect'] + ' AND (physiotherapy[tiab] OR "physical therapy"[tiab] OR rehabilitation[tiab]) AND shoulder[tiab]',
 'c6 PONV prophylaxis breast surgery/mastectomy (dexamethasone/ondansetron)': T['mastect'] + ' AND (' + T['ondans'] + ' OR ' + T['dexa'] + ') AND ("nausea and vomiting"[tiab] OR PONV[tiab])',
 'c6 dexamethasone + ondansetron PONV breast surgery': T['dexa'] + ' AND ' + T['ondans'] + ' AND (' + T['mastect'] + ' OR "breast surgery"[tiab]) AND ("nausea and vomiting"[tiab] OR PONV[tiab])',
 'c6 anaesthesia breast cancer surgery propofol/fentanyl': T['BC'] + ' AND (' + T['propof'] + ' OR ' + T['fent'] + ') AND (surgery[tiab] OR mastectomy[tiab]) AND anesth*[tiab]',
 'c6 ERAS breast surgery guideline': '("enhanced recovery"[tiab] OR ERAS[tiab]) AND ("breast surgery"[tiab] OR mastectomy[tiab] OR "breast reconstruction"[tiab])',
 'c6 sedation midazolam/fentanyl breast biopsy/procedure': '(' + T['midaz'] + ' AND ' + T['fent'] + ') AND (breast[tiab])',
 'c6 PONV guideline (consensus)': '"postoperative nausea and vomiting"[ti] AND ' + G,
 'c7 breast + colorectal screening co-adherence': T['mam_scr'] + ' AND ' + T['crc'] + ' AND (adherence[tiab] OR "up-to-date"[tiab] OR uptake[tiab] OR concordance[tiab] OR "multiple cancer"[tiab])',
 'c7 breast biopsy surgical pathology': '("breast biopsy"[tiab] OR "breast core biopsy"[tiab]) AND ' + T['surgpath'],
 'c7 skin lesions / keratosis + breast cancer screening': '(' + T['keratosis'] + ' OR ' + T['pigment'] + ') AND ' + T['mam_scr'],
}
res = []
for k, t in Q.items():
    n, arts = q(t, 6); res.append(dict(label=k, query=t, count=n, top=arts)); print(f'\n## {k}  n={n}', flush=True)
    for a in arts: print('   ', a[0], a[1], a[2], '|', a[3], flush=True)
json.dump(res, open('lit2_results.json', 'w'))
