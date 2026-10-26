"""Regex that decides whether a paper's title or abstract names a step of a table row (shared by the fill script)."""
STEP = {
 'ecg': r'electrocardiogra|\bECGs?\b|\bEKGs?\b', 'chem': r'metabolic panel|chemistry|liver function|biochem|renal function',
 'CBC': r'blood count|\bCBC\b|hematolog|haematolog', 'venip': r'venipuncture|blood collection|blood draw|blood sampl|blood test|laborator',
 'phys': r'physical examination|physical exam|general examination|routine examination|health maintenance|periodic health|annual (physical|exam)|check-?up',
 'lipid': r'lipid|cholesterol', 'psa': r'prostate.specific antigen|\bPSA\b',
 'crc_scr': r'colorectal cancer screening|colorectal screening|colon cancer screening|colonoscop|cancer screening',
 'ppi': r'proton pump|\bPPIs?\b|H2.(receptor )?(blocker|antagonist)|omeprazole|pantoprazole|famotidine|acid suppress',
 'azithro': r'azithromycin', 'amox': r'amoxicillin', 'mpred': r'methylprednisolone', 'pred': r'prednison',
 'prev': r'preventive (care|services|health|visit|medicine)|health maintenance|periodic health|annual (physical|exam)',
 'bc_scr': r'mammograph|breast (cancer )?screening|tomosynthesis', 'cerv': r'cervical (cancer )?screening|cervical cytology|pap (smear|test)|papanicolaou|cervical cancer',
 'gyn': r'pelvic exam|gyn[a]?ecolog\w* exam',
 'manual': r'manual therapy|manipulat|mobili[sz]ation|physiotherap|physical therapy', 'ther_ex': r'exercise|stretching|strengthening',
 'ther_act': r'therapeutic activit|functional activit',
 'divert': r'diverticul', 'polyp': r'polyp|adenoma', 'polypectomy': r'polypectom|polyp removal|mucosal resection', 'biopsy': r'biops',
 'vitd': r'vitamin d|25-hydroxy', 'b12': r'vitamin b12|\bb12\b|cobalamin', 't4': r'thyroxine|\bT4\b|thyroid function|thyroid',
 'A1c': r'hba1c|glycated|glycosylated|hemoglobin a1c',
}
