"""PubMed (NLM E-utilities) helpers for the letrozole literature column of the final table.

Used by search_entities_patterns.py and search_setting.py. Read-only GET requests, no API key (about 3 requests/s).
Uses /usr/bin/curl, not urllib: behind the corporate TLS proxy Python rejects the certificate chain, curl uses the macOS trust store.
Edit T (concept -> PubMed clause), ENT (bundle -> top-5 entities) and PAT (table row -> pattern concepts) for another cohort.
"""
import itertools, json, subprocess, urllib.parse, time, csv
B='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
def curl(u): return json.loads(subprocess.run(['/usr/bin/curl','-sS','-f','-m','40',u],capture_output=True,text=True,check=True).stdout)
def q(term,n=4):
    for _ in range(3):
        try:
            r=curl(B+'esearch.fcgi?db=pubmed&retmode=json&sort=relevance&retmax=%d&term=%s'%(n,urllib.parse.quote(term)))['esearchresult']; break
        except Exception: time.sleep(2)
    else: return -1,[]
    ids=r['idlist']; arts=[]
    if ids:
        s=curl(B+'esummary.fcgi?db=pubmed&retmode=json&id='+','.join(ids))['result']
        arts=[(i,s[i]['pubdate'][:4],s[i]['source'],s[i]['title'][:110]) for i in ids]
    time.sleep(0.35); return int(r['count']),arts
T={ # concept -> PubMed clause
 'A1c':'("hemoglobin A1c"[tiab] OR "glycated hemoglobin"[tiab] OR HbA1c[tiab])','TSH':'(TSH[tiab] OR thyrotropin[tiab] OR "thyroid stimulating hormone"[tiab])',
 'lipid':'("lipid panel"[tiab] OR "lipid profile"[tiab] OR lipids[tiab] OR cholesterol[tiab])','FSH':'("follicle stimulating hormone"[tiab] OR FSH[tiab])','vitD':'("vitamin D"[tiab] OR "25-hydroxyvitamin D"[tiab])',
 'amox':'("amoxicillin clavulanate"[tiab] OR "amoxicillin-clavulanate"[tiab])','azithro':'azithromycin[tiab]','ibu':'ibuprofen[tiab]','flucon':'fluconazole[tiab]','pred':'prednisone[tiab]',
 'E2oral':'("oral estradiol"[tiab] OR "estradiol valerate"[tiab] OR "estradiol tablets"[tiab])','infert':'("infertility, female"[mh] OR "female infertility"[tiab])','HSG':'(hysterosalpingography[tiab] OR "tubal patency"[tiab] OR "hysterosalpingo-contrast"[tiab])',
 'Pinj':'("intramuscular progesterone"[tiab] OR "progesterone in oil"[tiab] OR "progesterone injection"[tiab] OR "luteal support"[tiab])','E2':'(estradiol[tiab])','hCG':'("human chorionic gonadotropin"[tiab] OR hCG[tiab])','Prog':'(progesterone[tiab])',
 'livebirth':'("live birth"[tiab])','OGTT':'("glucose tolerance test"[tiab] OR "glucose challenge"[tiab] OR "gestational diabetes"[tiab])','USpreg':'("obstetric ultrasound"[tiab] OR "obstetric ultrasonography"[tiab] OR "ultrasound"[tiab] AND pregnancy[tiab])',
 'postnatal':'("postpartum visit"[tiab] OR "postnatal care"[tiab] OR "postpartum care"[tiab])','TVUS':'("transvaginal ultrasound"[tiab] OR "transvaginal ultrasonography"[tiab])','immun':'(immunization[tiab] OR vaccination[tiab])',
 'CFTR':'(CFTR[tiab] OR "cystic fibrosis"[tiab])','IKBKAP':'("familial dysautonomia"[tiab] OR IKBKAP[tiab] OR ELP1[tiab])','HEXA':'("Tay-Sachs"[tiab] OR HEXA[tiab])','FMR1':'("fragile X"[tiab] OR FMR1[tiab])','GBA':'(Gaucher[tiab] OR GBA[tiab])','carrier':'("carrier screening"[tiab])',
 'ondans':'ondansetron[tiab]','ketor':'ketorolac[tiab]','dexa':'dexamethasone[tiab]','inj':'(injection[tiab])','BMP':'("basic metabolic panel"[tiab] OR "metabolic panel"[tiab])','CBC':'("complete blood count"[tiab] OR "blood count"[tiab])','CMP':'("comprehensive metabolic panel"[tiab])',
 'PT':'("physical therapy"[tiab] OR physiotherapy[tiab] OR "therapeutic exercise"[tiab])','manual':'("manual therapy"[tiab])','LBP':'("low back pain"[mh] OR "low back pain"[tiab])','neuro':'("neuromuscular re-education"[tiab] OR "neuromuscular reeducation"[tiab] OR "motor control"[tiab])','activ':'("therapeutic activities"[tiab] OR "functional activities"[tiab])',
 'letro':'(letrozole[tiab])','AI':'("aromatase inhibitor"[tiab] OR "aromatase inhibitors"[tiab])','venip':'(venipuncture[tiab])'}
ENT={'c0':['A1c','TSH','lipid','FSH','vitD'],'c1':['amox','azithro','ibu','flucon','pred'],'c2':['E2oral','infert','HSG','Pinj','E2'],'c3':['livebirth','OGTT','USpreg','postnatal','TVUS'],
     'c4':['CFTR','IKBKAP','HEXA','FMR1','GBA'],'c5':['ondans','ketor','dexa','inj','BMP'],'c6':['PT','manual','LBP','neuro','activ']}
PAT={2:['lipid','A1c','letro'],3:['A1c','TSH','letro'],4:['FSH','TSH','letro'],5:['flucon','letro'],6:['flucon','letro'],7:['ondans','letro'],
     8:['letro','E2'],9:['letro','E2','hCG'],10:['letro','E2','Prog'],11:['letro','OGTT','livebirth'],12:['letro','OGTT','livebirth'],13:['letro','immun','livebirth'],
     15:['letro','CBC','CMP'],16:['letro','CBC','CMP'],17:['letro','CBC','CMP'],18:['letro','PT','manual'],19:['letro','PT','manual'],20:['letro','PT','manual']}
