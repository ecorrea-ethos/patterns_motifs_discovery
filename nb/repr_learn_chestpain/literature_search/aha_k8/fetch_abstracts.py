"""Read the abstract of every candidate paper (efetch) and list which steps of the table rows its title or abstract mentions.
Candidates were all returned by the searches of round 1 / round 2 of this run (round1_AHA.log, round2_AHA.log).
usage: python fetch_abstracts.py PMID [PMID ...]   -> abstracts_AHA.json (merged) and a printed summary"""
import json, os, re, subprocess, sys, time
import xml.etree.ElementTree as ET
B = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
KW = {'chest pain': r'chest pain|chest discomfort|angina', 'ECG': r'electrocardiogra|\bECGs?\b|\bEKGs?\b', 'troponin': r'troponin',
      'chest X-ray': r'chest radiograph|chest x-?ray|chest film|radiograph', 'lipid': r'lipid|cholesterol', 'HbA1c': r'hba1c|glycated|glycosylated|haemoglobin a1c|hemoglobin a1c',
      'blood panel': r'metabolic panel|blood count|laborator|blood test|biochemi', 'blood draw': r'venipuncture|blood collection|blood draw|blood sampl',
      'steroid': r'steroid|methylprednisolone|prednisone|prednisolone', 'antibiotic': r'azithromycin|antibiotic',
      'PPI': r'proton pump|PPI', 'GERD': r'reflux|GERD', 'endoscopy': r'endoscop|EGD', 'biopsy': r'biops|patholog|histolog',
      'manual therapy': r'manual therapy|manipulat|physiotherapy|physical therapy|chiropract', 'exercise': r'exercise|stretching|neuromuscular',
      'vitamin D': r'vitamin d|25-hydroxy', 'physical exam': r'physical examination|physical exam|history and|bedside', 'outpatient': r'outpatient|primary care|office',
      'ED': r'emergency department|emergency room', 'pharyngitis': r'pharyngitis|sore throat|tonsillitis', 'cough/URI': r'cough|respiratory (tract )?infection|bronchitis', 'COVID': r'covid'}
def fetch(ids):
    x = subprocess.run(['/usr/bin/curl', '-sS', '-f', '-m', '60', B + 'efetch.fcgi?db=pubmed&retmode=xml&id=' + ','.join(ids)], capture_output=True, text=True, check=True).stdout
    out = {}
    for a in ET.fromstring(x).iter('PubmedArticle'):
        pmid = a.findtext('.//PMID')
        title = ''.join(a.find('.//ArticleTitle').itertext())
        ab = ' '.join(''.join(t.itertext()) for t in a.findall('.//Abstract/AbstractText'))
        out[pmid] = dict(title=title, abstract=ab, year=a.findtext('.//PubDate/Year') or (a.findtext('.//PubDate/MedlineDate') or '')[:4],
                         journal=a.findtext('.//Journal/ISOAbbreviation'), types=[p.text for p in a.findall('.//PublicationType')])
    return out
path = 'abstracts_AHA.json'
store = json.load(open(path)) if os.path.exists(path) else {}
ids = [i for i in sys.argv[1:] if i not in store]
for k in range(0, len(ids), 20):
    store.update(fetch(ids[k:k + 20])); time.sleep(0.4)
json.dump(store, open(path, 'w'), indent=1)
for i in sys.argv[1:]:
    d = store.get(i)
    if not d: print(i, 'NOT RETURNED'); continue
    txt = d['title'] + ' ' + d['abstract']
    hit = [k for k, p in KW.items() if re.search(p, txt, re.I)]
    print(f"{i} {d['year']} {d['journal']} | {d['title']}\n    types: {', '.join(d['types'])}; abstract: {'yes, %d chars' % len(d['abstract']) if d['abstract'] else 'NONE'}\n    mentions: {', '.join(hit)}")
