"""Worked example: final table (xlsx) -> inject/rows.json for the chest pain deck. Needs pandas and openpyxl.

    python -I gen_rows.py <final_table_chestpain_k8_AHA.xlsx> inject/rows.json

Parses the table's text cells into rows {id, name, n, pct, cp, scored, ents[5], seqs[3]} with shares as fractions, and labels every code in plain English
(LAB: first match wins, so code-specific labels come first). An unlabelled step stops the script, so no code reaches a slide unnamed.
"""
import pandas as pd, re, json, sys
d=pd.read_excel(sys.argv[1])
c=list(d.columns)
NAMES={'c0':'Outpatient check-up and elective cardiac testing','c1':'Prescriptions for acute and chronic illness','c2':"Women's health and urinary tract",'c3':'Acute emergency work-up','c4':'Stomach and bowel work-up and cancer screening','c5':'Muscle and bone care and physical therapy','c6':'Nutrition and hormone blood tests','c7':'Acute respiratory infection'}
LAB=[('96374','Intravenous push, first drug'),('96375','Intravenous push, added drug'),('87491','Chlamydia nucleic acid test'),('87591','Gonorrhea nucleic acid test'),('97112','Movement training'),('87880','Rapid antigen test (87880)'),('87804','Rapid antigen test (87804)'),('chest pain','Chest pain'),('ekg','Electrocardiogram'),('hyperlipidemia','Hyperlipidemia diagnosis'),('General examination','General examination'),('Lipid panel','Lipid panel'),
('chest xray','Chest X-ray'),('troponin','Troponin test'),('Comprehensive metabolic','Comprehensive metabolic panel'),('Complete blood count','Complete blood count'),('Venipuncture','Blood draw'),
('methylprednisolone','Methylprednisolone (steroid)'),('amoxicillin','Amoxicillin with clavulanate'),('azithromycin','Azithromycin (antibiotic)'),('ppi h2','Acid-lowering drug'),('prednisone','Prednisone (steroid)'),
('Gynecologic','Gynecologic examination'),('nucleic','Infection test (DNA or RNA)'),('Cytopathology','Cervical cytology'),('pregnancy','Urine pregnancy test'),
('Therapeutic, prophylactic, or','Intravenous push'),('Triacylglycerol lipase','Lipase test'),
('Level IV','Tissue pathology exam'),('Screening for malignant','Colon cancer screening'),('Endoscopy and biopsy','Upper endoscopy with biopsy'),('gerd','Acid reflux diagnosis'),('Periodic comprehensive','Periodic preventive visit'),
('Manual therapy','Manual therapy'),('Therapeutic procedure','Therapeutic exercise'),('Therapeutic activities','Therapeutic activities'),('Low back pain','Low back pain diagnosis'),
('Vitamin B12','Vitamin B12 test'),('Vitamin D','Vitamin D test'),('T4 free','Free thyroxine test'),('Iron measurement','Iron test'),('Ferritin','Ferritin test'),('hba1c','Hemoglobin A1c test'),
('Cough','Cough'),('Acute upper respiratory','Upper respiratory infection'),('Acute pharyngitis','Sore throat (pharyngitis)'),('Infectious agent antigen','Rapid antigen test')]
def lab(t):
    for k,v in LAB:
        if k.lower() in t.lower(): return v
    raise SystemExit('no label: '+t)
def step(s):
    s=s.strip(); rep=''
    m=re.search(r'\s×(\d+)$',s)
    if m: rep=' ×'+m.group(1); s=s[:m.start()]
    return lab(s)+rep
B=[];cur=None
for i,r in d.iterrows():
    g=str(r[c[0]])
    if re.match(r'c\d ·',g):
        cid=g[:2]; cur=dict(id=cid,short=NAMES[cid],seqs=[])
        m=re.search(r'([\d,]+) \(([\d.]+)%\)\n(\d+) of (\d+) scored',str(r[c[1]]))
        cur['n']=int(m.group(1).replace(',','')); cur['pct']=float(m.group(2)); cur['cpPatterns']=int(m.group(3)); cur['scored']=int(m.group(4))
        ents=[]
        for m in re.finditer(r'(\d)\. (.+?) \((\d+)% of bundle\)\n\s+median (same day as|(\d+) d (before|after)) first chest pain \((\d+)% of them before\)',str(r[c[2]])):
            med=0 if m.group(4)=='same day as' else int(m.group(5))*(-1 if m.group(6)=='before' else 1)
            ents.append(dict(k=lab(m.group(2)),share=int(m.group(3)),med=med,before=int(m.group(7))))
        assert len(ents)==5,(cid,len(ents))
        cur['ents']=ents; B.append(cur)
    if cur is not None and isinstance(r[c[4]],str):
        cur['seqs'].append(dict(steps=[step(x) for x in r[c[4]].split('→')],inB=round(float(r[c[6]])*100,1),out=round(float(r[c[7]])*100,1),lift=float(r[c[10]]),pass_=float(r[c[8]]),verdict=r[c[11]],order=('same-day' if r[c[13]]=='Same-day bundle' else 'dated')))
assert len(B)==8 and all(len(b['seqs'])==3 for b in B)
rows=[]
for b in B:
    rows.append(dict(id=b['id'],name=b['short'],n=b['n'],pct=round(b['pct']/100,3),cp=b['cpPatterns'],scored=b['scored'],
        ents=[dict(k=e['k'],share=round(e['share']/100,2),med=e['med'],before=round(e['before']/100,2)) for e in b['ents']],
        seqs=[dict(steps=s['steps'],inB=round(s['inB']/100,3),out=round(s['out']/100,3),lift=s['lift'],pass_=s['pass_'],verdict=s['verdict'],order=s['order']) for s in b['seqs']]))
json.dump(rows,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print('wrote',sys.argv[2],'| verdicts solid/suggestive/unstable:',sum(1 for b in B for s in b['seqs'] if s['verdict']=='Solid'),sum(1 for b in B for s in b['seqs'] if s['verdict']=='Suggestive'),sum(1 for b in B for s in b['seqs'] if s['verdict']=='Unstable'),'| cohort total',sum(b['n'] for b in B))
