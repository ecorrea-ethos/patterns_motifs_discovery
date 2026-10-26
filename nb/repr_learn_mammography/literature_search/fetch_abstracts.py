"""Fetch title + abstract (efetch) of candidate papers into abstracts.json (merged). Candidates were all returned by round1.log / round2.log.
usage: python fetch_abstracts.py PMID [PMID ...]"""
import json, os, subprocess, sys, time
import xml.etree.ElementTree as ET
B = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
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
path = 'abstracts.json'
store = json.load(open(path)) if os.path.exists(path) else {}
ids = [i for i in dict.fromkeys(sys.argv[1:]) if i not in store]
for k in range(0, len(ids), 20):
    store.update(fetch(ids[k:k + 20])); time.sleep(0.4)
json.dump(store, open(path, 'w'), indent=1)
missing = [i for i in sys.argv[1:] if i not in store]
print(len(store), 'records;', 'NOT RETURNED:' if missing else 'all returned', missing or '')
