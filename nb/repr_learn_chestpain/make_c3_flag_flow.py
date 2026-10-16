"""Draw the decision flow of the chest pain c3 pattern for the UW team.

usage (conda env omop_local, cwd = nb/repr_learn_chestpain/):
    python make_c3_flag_flow.py             # flag wording of the v2 engine (Manual RUW, routine box) -> chestpain_c3_flag_flow.png
    python make_c3_flag_flow.py --neutral   # ASD-STE100 wording, no routing words, for the v3 engine -> chestpain_c3_pattern_flow.png

The care pattern sizes come from nmf_k8_chestpain_AHA_components.json. The share of c3 patients with each service sits in a text cell of
final_table_chestpain_k8_AHA.xlsx (care pattern c3, column "Most frequently OMOP clinical entities found"), so it is typed below.
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ap = argparse.ArgumentParser(); ap.add_argument("--neutral", action="store_true"); args = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
comp = json.load(open(os.path.join(HERE, "nmf_k8_chestpain_AHA_components.json")))
N, C = comp["n_patients"], comp["components"]
size = lambda k: f"{C[str(k)]['n']:,}"
c3 = C["3"]
assert c3["name"].startswith("acute / ED workup")

if args.neutral:
    OUT = "chestpain_c3_pattern_flow.png"
    TITLE = "Chest pain applicants: does the care match the ED work-up pattern (c3)?"
    SUB = ('Read the steps from top to bottom. The first "No" ends the check: the pattern is not found. '
           "The pattern shows the type of care. It does not show a diagnosis.")
    STEP1 = "STEP 1\nDoes the applicant have a\nchest pain diagnosis?"
    STEP2 = ("STEP 2\nDoes the applicant have at least 3 of\nthese 4 services, each not more than\n1 day before or after a\nchest pain diagnosis?\n\n"
             "(A service that is further away\ndoes not count. An ECG does not count here.)")
    STEP3 = ("STEP 3\nAfter a chest pain diagnosis, does the\napplicant have ONE of these sequences?\n"
             "(The steps are in this order. Other events\nare allowed between them. The last step is\nnot more than 1 day after the diagnosis.)")
    RESULT = f"ED WORK-UP PATTERN FOUND\n(c3: {size(3)} of {N:,}\nchest pain patients, {c3['pct']:.1f}%)"
    LEFT = (f"NOT FOUND\n\nThe care is one of the\nother 7 care patterns:\n\n"
            f" c0  outpatient check-up and\n       elective cardiac testing   ({size(0)})\n"
            f" c1  prescriptions for acute and\n       chronic illness   ({size(1)})\n"
            f" c2  women's health and\n       urinary tract   ({size(2)})\n"
            f" c4  stomach and bowel work-up,\n       cancer screening   ({size(4)})\n"
            f" c5  muscle and bone care,\n       physical therapy   ({size(5)})\n"
            f" c6  nutrition and hormone\n       blood tests   ({size(6)})\n"
            f" c7  acute respiratory\n       infection   ({size(7)})")
    NOTE1 = ("Chest pain diagnosis: chest pain, precordial pain\n(pain over the heart), chest pain on breathing,\n"
             "or pain of the space between the ribs.\nSteps 2 and 3 count from the date of a\nchest pain diagnosis.")
    NOTE2 = ("The 4 services (share of c3 patients with the\nservice at any time; timing against the first chest pain)\n\n"
             "1  Troponin blood test\n    81% of patients, median same day\n"
             "2  Chest X-ray\n    86% of patients, median same day\n"
             "3  Lipase blood test (pancreas marker)\n    59% of patients, median same day\n"
             "4  IV push injection (into a vein)\n    first drug 66%, each additional drug 55%,\n    median same day")
    NOTE3 = ("The 3 sequences\n\n"
             "A   chest pain  ->  chest X-ray  ->  troponin  ->  CMP\n"
             "B   chest pain  ->  ECG  ->  troponin  ->  CMP\n"
             "C   chest pain  ->  troponin  ->  CMP  ->  CBC\n\n"
             "CMP = comprehensive metabolic panel (blood chemistry)\nCBC = complete blood count\nECG = electrocardiogram (heart tracing)\n"
             "Claims have a date and no time. Events of the same day\nfollow a fixed order: diagnosis, procedure, lab test.\nLab tests follow the order of their code number.")
    FOOT = ("Care patterns come from the k=8 chest pain run on the AHA/ACC code lists. "
            "Each patient is in the care pattern with the highest weight for that patient.")
else:
    OUT = "chestpain_c3_flag_flow.png"
    TITLE = "Chest pain applicants: when is the c3 (emergency work-up) pattern flagged for Manual RUW?"
    SUB = ('Follow the questions from top to bottom. The first "No" ends the check: the applicant is routine for this rule. '
           "Draft for clinical review. The flag marks a care pattern, not a diagnosis.")
    STEP1 = "STEP 1\nDoes the applicant have a\nchest pain diagnosis?"
    STEP2 = ("STEP 2\nAt least 3 of these 4 services,\neach seen within 1 day of a\nchest pain diagnosis?\n\n"
             "(a service seen further away than that\ndoes not count; an ECG does not count here)")
    STEP3 = ("STEP 3\nAfter a chest pain diagnosis, did ONE of\nthese work-up sequences follow?\n"
             "(in this order, other events may sit\nin between; all within 1 day)")
    RESULT = f"MANUAL RUW  ·  c3 pattern\nemergency (ED) work-up\n(c3: {size(3)} of {N:,} chest pain patients, {c3['pct']:.1f}%)"
    LEFT = (f"ROUTINE for this rule\n(not flagged)\n\nCompared against, one against all\n(the 7 other care patterns):\n\n"
            f"CARDIAC WORK-UP (comparison)\n c0  outpatient check-up and\n       elective cardiac testing   ({size(0)})\n\n"
            f"NON-CARDIAC EXPLANATION\n c4  GI work-up and cancer\n       screening   ({size(4)})\n"
            f" c7  acute respiratory\n       infection   ({size(7)})\n\n"
            f"BACKGROUND CARE (routine: care\nunrelated to the chest pain)\n c2  women's health and\n       urinary tract   ({size(2)})\n"
            f" c5  musculoskeletal / physical\n       therapy   ({size(5)})\n"
            f" c6  nutrition and endocrine\n       labs   ({size(6)})\n\n"
            f"DRUG DOMAIN (clinical context\nunclear: use other evidence)\n c1  acute-illness and chronic\n       prescriptions   ({size(1)})")
    NOTE1 = ('Chest pain diagnosis = chest pain [SNOMED 29857009],\nprecordial pain (pain over the heart), chest pain on\nbreathing, or pain of the intercostal space.\n'
             'Steps 2 and 3 are measured from the date of a\nchest pain diagnosis.')
    NOTE2 = ("The 4 services (share of c3 patients who have it at any\ntime; timing against the first chest pain)\n\n"
             "1  Troponin blood test  [CPT4 84484, 84512]\n    seen in 81%, median same day\n"
             "2  Chest X-ray, 1 to 4 or more views  [CPT4 71045 to 71048]\n    seen in 86%, median same day\n"
             "3  Lipase blood test (pancreas marker)  [SNOMED 104988000]\n    seen in 59%, median same day\n"
             "4  IV push injection  [CPT4 96374 first drug, 96375 each\n    additional drug]  seen in 66% and 55%, median same day")
    NOTE3 = ("Any one of the 3 sequences\n\n"
             "A   chest pain  ->  chest X-ray  ->  troponin  ->  CMP\n"
             "B   chest pain  ->  ECG  ->  troponin  ->  CMP\n"
             "C   chest pain  ->  troponin  ->  CMP  ->  CBC\n\n"
             "CMP = comprehensive metabolic panel [SNOMED 371361000119107]\n"
             "CBC = complete blood count [SNOMED 9564003]\n"
             "ECG = heart tracing [CPT4 93000, 93005, 93010]\n"
             "Same-day steps are ordered by a fixed tie-break (diagnosis,\nprocedure, lab test, then code ID), not by clock time: in c3\nthe order is mostly that tie-break.")
    FOOT = ("Full code lists with OMOP IDs and the flag rule: Chestpain_Workup_Predicate_Engine_v2.md (Annex B).  Sizes: k=8 chest pain run on the AHA/ACC "
            "code lists (nmf_k8_chestpain_AHA), patients counted in the care pattern of their dominant NMF component.")

W, H = 1730, 1190
INK, MUTED = "#1a202c", "#5a6578"
GOLD, BLUE, ORANGE, RED, GREEN = "#b7791f", "#2b6cb0", "#c05621", "#c53030", "#2f855a"
fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")


def box(x, y, w, h, fc, ec, lw=1.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=10", fc=fc, ec=ec, lw=lw))


def text(x, y, s, size=10.5, weight="normal", color=INK, ha="left", va="center", ls=1.45):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va, linespacing=ls, family="DejaVu Sans")


def arrow(x0, y0, x1, y1, color):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16, lw=2.4, color=color, shrinkA=0, shrinkB=0))


def tag(x, y, s, color):
    ax.text(x, y, s, fontsize=10.5, fontweight="bold", color=color, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=color, lw=1.2))


text(30, 36, TITLE, 18, "bold")
text(30, 74, SUB, 10, color=MUTED)

# steps (centre column)
cx, bw = 765, 550
steps = [(131, 133, "#fbf0db", GOLD, STEP1), (343, 286, "#e8eff9", BLUE, STEP2), (709, 209, "#fdf0e6", ORANGE, STEP3)]
for y, h, fc, ec, label in steps:
    box(cx - bw / 2, y, bw, h, fc, ec)
    text(cx, y + h / 2, label, 13, "bold", ha="center", ls=1.5)
ax.add_patch(FancyBboxPatch((cx - 315, 996), 630, 145, boxstyle="round,pad=0,rounding_size=12", fc=ORANGE, ec=ORANGE))
text(cx, 1068, RESULT, 14, "bold", "white", "center", ls=1.55)

# yes arrows down, no arrows left
for (y0, y1) in [(264, 343), (629, 709), (918, 996)]:
    arrow(cx, y0, cx, y1 - 2, GREEN); tag(cx + 53, (y0 + y1) / 2, "Yes", GREEN)
for y, h, *_ in steps:
    arrow(cx - bw / 2, y + h / 2, 425, y + h / 2, RED); tag(455, y + h / 2 - 31, "No", RED)

# left box: where the "No" arrows lead
box(25, 131, 397, 806, "#f7fafc", RED)
text(47, 534, LEFT, 9.6, ls=1.4)

# right notes
rx, rw = 1110, 590
for y, h, ec in [(131, 133, GOLD), (314, 354, BLUE), (689, 248, ORANGE)]:
    box(rx, y, rw, h, "white", ec, 1.5)
for ey, ec in [(197, GOLD), (486, BLUE), (813, ORANGE)]:
    ax.plot([cx + bw / 2, rx], [ey, ey], color=ec, lw=1.6, ls=(0, (1, 3)))
text(rx + 22, 197, NOTE1, 10)
text(rx + 22, 486, NOTE2, 10)
text(rx + 22, 813, NOTE3, 9.3)
text(30, 1170, FOOT, 8.8, color=MUTED)

out = os.path.join(HERE, OUT)
fig.savefig(out, dpi=100, facecolor="white")
print("wrote", out)
