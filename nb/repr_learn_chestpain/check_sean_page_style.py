"""
Style check of outputs/sean_chest_pain_predicates_composites.md with the skill's lint (.claude/skills/bundle-predicate-page/scripts/lint_page.py).

    python check_sean_page_style.py

The lint reads code lines as prose. This page holds SQL, Sean's draft as written (with the words of his columns), and a table of vocabulary concept names
(ECG, CABG, ...). A copy without these three parts goes to the lint. The rest of the page, prose and tables, is checked in full.
A script check of the style of ASD-STE100 (sentence length, modal verbs, passive, perfect tense, abbreviations, decision wording). It is not a certification.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "outputs", "sean_chest_pain_predicates_composites.md")
LINT = os.path.join(HERE, "..", "..", ".claude", "skills", "bundle-predicate-page", "scripts", "lint_page.py")

keep, in_fence, in_ref = [], False, False
for ln in open(PAGE, encoding="utf-8").read().split("\n"):
    if ln.startswith("```"):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    if ln.startswith("### Reference Concept IDs"):
        in_ref = True
    elif in_ref and ln.startswith("---"):
        in_ref = False
    if in_ref and ln.startswith("|"):
        continue
    keep.append(ln)
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as t:
    t.write("\n".join(keep))
print(f"{len(keep)} of the lines go to the lint (SQL, the draft block, and the concept table are left out)")
sys.exit(subprocess.call([sys.executable, LINT, t.name]))
