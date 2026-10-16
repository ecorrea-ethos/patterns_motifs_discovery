"""Search definitions for the literature column of final_table_chestpain_k8_AHA.xlsx (AHA/ACC code lists, NMF k=8).

Helpers (q, curl) and the clauses shared with the k=5 table come from ../pubmed.py; only the new clauses, the top-5 entities of
each k=8 bundle (ENT) and the pattern rows (PAT, Excel row number -> steps) are defined here. Run from this folder.
PubMed cannot test order: the steps of a pattern are ANDed, unordered. Clauses are hand-written, never the raw OMOP name.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from pubmed import q, T as T_K5

T = {**T_K5,
 'hyperl': '(hyperlipidemia[tiab] OR dyslipidemia[tiab] OR hypercholesterolemia[tiab])',
 'ppi': '("proton pump inhibitor"[tiab] OR "proton pump inhibitors"[tiab] OR PPI[tiab] OR "H2 blocker"[tiab] OR "H2 receptor antagonist"[tiab])',
 'lipase': '(lipase[tiab])',
 'gerd': '("gastroesophageal reflux"[tiab] OR "gastro-oesophageal reflux"[tiab] OR GERD[tiab])',
 'endo': '("upper endoscopy"[tiab] OR "upper gastrointestinal endoscopy"[tiab] OR esophagogastroduodenoscopy[tiab] OR EGD[tiab] OR endoscopy[tiab])',
 'path': '("surgical pathology"[tiab] OR histopathology[tiab] OR biopsy[tiab])',
 'cscreen': '("cancer screening"[tiab] OR "colorectal cancer screening"[tiab] OR colonoscopy[tiab])',
 'neuro_re': '("neuromuscular reeducation"[tiab] OR "neuromuscular re-education"[tiab] OR "neuromuscular training"[tiab])',
 'b12': '("vitamin B12"[tiab] OR cobalamin[tiab] OR "B12 deficiency"[tiab])',
 'vitd': '("vitamin D"[tiab] OR "25-hydroxyvitamin D"[tiab])',
 't4': '("free T4"[tiab] OR "free thyroxine"[tiab] OR "thyroid function"[tiab])',
 'iron': '(iron[tiab] OR "iron deficiency"[tiab])',
 'ferr': '(ferritin[tiab])',
 'cough': '(cough[tiab])',
 'uri': '("upper respiratory infection"[tiab] OR "upper respiratory tract infection"[tiab] OR "respiratory tract infection"[tiab])',
 'pharyng': '(pharyngitis[tiab] OR "sore throat"[tiab])',
 'antigen': '("rapid antigen"[tiab] OR "antigen detection"[tiab] OR "rapid strep"[tiab] OR "rapid influenza"[tiab])',
 'stress': '("stress test"[tiab] OR "stress testing"[tiab] OR "exercise testing"[tiab] OR "coronary CT angiography"[tiab] OR CCTA[tiab])',
}
# top-5 entities per bundle (ekg, troponin, chest X-ray, gerd, ppi/h2 are curated lists, one entity each)
ENT = {'c0': ['lipid', 'venip', 'phys', 'ecg', 'CMP'],
       'c1': ['mpred', 'amox', 'azithro', 'ppi', 'pred'],
       'c2': ['gyn', 'naat', 'pap', 'upt'],               # the two NAAT codes (87491, 87591) are one clinical entity here
       'c3': ['trop', 'inj', 'lipase', 'cxr'],            # IV push first drug (96374) and each additional drug (96375) are one entity
       'c4': ['path', 'cscreen', 'endo', 'gerd', 'prev'],
       'c5': ['ther_ex', 'manual', 'ther_act', 'LBP', 'neuro_re'],
       'c6': ['b12', 'vitd', 't4', 'iron', 'ferr'],
       'c7': ['cough', 'uri', 'pharyng', 'antigen']}      # the two antigen codes (87880, 87804) are one entity
# table row (Excel row) -> steps of its typical order of care, chest pain step included (order not testable in PubMed)
PAT = {2: ['CP', 'ecg', 'hyperl'], 3: ['CP', 'phys', 'lipid'], 4: ['CP', 'ecg', 'phys'],
       5: ['mpred', 'CP', 'ecg'], 6: ['azithro', 'CP', 'ecg'], 7: ['CP', 'ecg', 'mpred'],
       8: ['CP', 'CBC', 'venip'], 9: ['CP', 'venip'], 10: ['venip', 'CP', 'ecg'],
       11: ['CP', 'cxr', 'trop', 'CMP'], 12: ['CP', 'ecg', 'trop', 'CMP'], 13: ['CP', 'trop', 'CMP', 'CBC'],
       14: ['CP', 'gerd', 'endo'], 15: ['CP', 'path', 'endo'], 16: ['CP', 'gerd', 'path'],
       17: ['CP', 'manual', 'ther_ex'], 18: ['CP', 'manual'], 19: ['CP', 'ther_ex', 'manual'],
       20: ['CP', 'lipid', 'vitd'], 21: ['CP', 'lipid', 'A1c'], 22: ['CP', 'ecg', 'lipid'],
       23: ['pharyng', 'CP', 'ecg'], 24: ['CP', 'ecg', 'uri'], 25: ['cough', 'CP', 'ecg']}
