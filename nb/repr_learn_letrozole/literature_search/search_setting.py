"""Round 2. Bundle entities (>=3, unordered) plus the bundle's clinical setting, e.g. infertility, carrier screening, low back pain.
Writes lit2_results.json; prints counts + top hits."""
import json
from pubmed import q, T
Q={
 'c0 infert+TSH+FSH+glucose': 'infertility[tiab] AND '+T['TSH']+' AND '+T['FSH']+' AND (glucose[tiab] OR '+T['A1c']+')',
 'c0 infert+TSH+FSH (guideline)': 'infertility[tiab] AND '+T['TSH']+' AND '+T['FSH']+' AND (guideline[tiab] OR "committee opinion"[tiab])',
 'c0 PCOS+lipid+A1c+TSH': '"polycystic ovary syndrome"[tiab] AND '+T['lipid']+' AND '+T['A1c']+' AND '+T['TSH'],
 'c0 PCOS+lipid+glucose+TSH guideline': '"polycystic ovary syndrome"[tiab] AND '+T['lipid']+' AND glucose[tiab] AND '+T['TSH']+' AND guideline[ti]',
 'c2 letro+E2+ovulation induction': T['letro']+' AND estradiol[tiab] AND "ovulation induction"[tiab]',
 'c2 letro+E2+hCG+IUI/OI': T['letro']+' AND estradiol[tiab] AND '+T['hCG']+' AND ("ovulation induction"[tiab] OR "intrauterine insemination"[tiab])',
 'c2 letro+E2+Prog+ovulation': T['letro']+' AND estradiol[tiab] AND progesterone[tiab] AND ovulation[tiab] AND (monitoring[tiab] OR trigger[tiab])',
 'c3 letro+GDM+pregnancy': T['letro']+' AND "gestational diabetes"[tiab] AND pregnancy[tiab]',
 'c3 letro+live birth+ultrasound+pregnancy outcomes': T['letro']+' AND "live birth"[tiab] AND ultrasound[tiab] AND "pregnancy outcome"[tiab]',
 'c3 letro+immunization+pregnancy (vaccin)': T['letro']+' AND (vaccin*[tiab]) AND pregnan*[tiab]',
 'c4 carrier+CFTR+TaySachs+fragileX guideline': T['carrier']+' AND '+T['CFTR']+' AND '+T['HEXA']+' AND '+T['FMR1'],
 'c4 carrier screening committee opinion preconception ACOG/ACMG': '"carrier screening"[ti] AND (ACOG[tiab] OR ACMG[tiab] OR "practice resource"[tiab] OR "committee opinion"[tiab])',
 'c5 PONV ondansetron+dexa guideline': T['ondans']+' AND '+T['dexa']+' AND "postoperative nausea"[tiab] AND guideline[ti]',
 'c5 letro+ketorolac/perioperative': T['letro']+' AND (perioperative[tiab] OR postoperative[tiab]) AND (ondansetron[tiab] OR ketorolac[tiab] OR dexamethasone[tiab] OR anesthesia[tiab])',
 'c5 AI/letro + CBC + metabolic monitoring': '('+T['letro']+' OR '+T['AI']+') AND ("complete blood count"[tiab] OR "metabolic panel"[tiab]) AND monitoring[tiab]',
 'c6 PT+manual+LBP guideline': T['PT']+' AND '+T['manual']+' AND '+T['LBP']+' AND (guideline[ti] OR "systematic review"[pt])',
 'c6 AI arthralgia + PT/exercise/manual': T['AI']+' AND arthralgia[tiab] AND ('+T['PT']+' OR exercise[tiab] OR '+T['manual']+')',
 'c6 letro + PT/manual': T['letro']+' AND ('+T['PT']+' OR '+T['manual']+')',
 'c1 letro+antibiotic/antifungal': T['letro']+' AND (antibiotic*[tiab] OR antifungal*[tiab] OR amoxicillin[tiab] OR azithromycin[tiab])',
}
res=[]
for k,t in Q.items():
    n,arts=q(t,6); res.append(dict(label=k,query=t,count=n,top=arts)); print(f'\n## {k}  n={n}')
    for a in arts: print('   ',a[0],a[1],a[2],'|',a[3])
json.dump(res,open('lit2_results.json','w'))
