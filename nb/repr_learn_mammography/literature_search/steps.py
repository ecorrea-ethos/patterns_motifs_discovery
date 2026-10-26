"""Regex that decides whether a paper's title or abstract names a step of a table row (shared by explore and fill scripts)."""
STEP = {
 'mam_dx': r'mammograph|breast imaging|diagnostic imaging', 'mam_scr': r'mammograph|breast (cancer )?screening',
 'tomo': r'tomosynthesis|3D.?mammograph', 'chem': r'metabolic panel|chemistry|liver function|biochem|renal function',
 'CBC': r'blood count|\bCBC\b|hematolog|haematolog', 'venip': r'venipuncture|blood collection|blood draw|blood sampl|blood test|laborator',
 'cerv': r'cervical (cancer )?screening|cervical cytology|pap (smear|test)|papanicolaou|cervical cancer', 'phys': r'physical examination|physical exam|clinical (breast )?examination|general examination|health maintenance|periodic health|annual (physical|exam)|check-?up',
 'lipid': r'lipid|cholesterol', 'ecg': r'electrocardiogra|\bECGs?\b|\bEKGs?\b', 'naat': r'nucleic acid|chlamydia|gonorrh',
 'vitd': r'vitamin d|25-hydroxy', 'b12': r'vitamin b12|\bb12\b|cobalamin', 't4': r'thyroxine|\bT4\b|thyroid function|thyroid', 'ferr': r'ferritin|\biron\b',
 'manual': r'manual therapy|manipulat|mobili[sz]ation|physiotherap|physical therapy', 'ther_ex': r'exercise|stretching|strengthening',
 'prev': r'preventive (care|services|health|visit|medicine)|health maintenance|periodic health|annual (physical|exam)|well-woman',
 'gyn': r'pelvic exam|gyn[a]?ecolog\w* exam',
 'A1c': r'hba1c|glycated|glycosylated|hemoglobin a1c',
 'neuro_re': r'neuromuscular (re-?education|training)|proprioceptive',
 'ther_act': r'therapeutic activit|functional activit',
 'mpred': r'methylprednisolone',
 'dexa': r'dexamethasone', 'ondans': r'ondansetron', 'midaz': r'midazolam', 'propof': r'propofol', 'fent': r'fentanyl',
 'crc': r'colorectal|colonoscop', 'neoplasm_scr': r'cancer screening|screening (for|tests)', 'flutic': r'fluticasone', 'pred': r'prednison', 'azithro': r'azithromycin',
}
