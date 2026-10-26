"""
Check the prose of a one-file predicate page, and the decision words that must not be in it.

    python lint_page.py outputs/chest_pain_all_patterns.md          # exit 1 when it finds an issue

Style (ASD-STE100 spirit, a script check and not a certification): sentence <= 25 words, paragraph <= 6 sentences,
no modal verb (can, may, should, would, will ...), no passive, no perfect tense, no contraction.
Abbreviations: the full term comes first, then the abbreviation in brackets, before any other use ("complete blood count (CBC)").
Scope: no triage, routing, accept / decline, or underwriting-decision wording. The page is a clinical grouping of codes.
Skipped: headings, tables, code lines, and the reference list.
"""
import re
import sys

MAX_WORDS, MAX_SENTENCES = 25, 6
MODAL = re.compile(r"\b(can|could|may|might|shall|should|would|will|ought)\b", re.I)
PP = r"(?:\w+ed|made|done|found|shown|given|held|kept|put|seen|taken|known|written|run|built|chosen|drawn|sent|set|spread|grown|become|gone|come)"
PASSIVE = re.compile(rf"\b(?:is|are|was|were|be|been|being)\s+(?:not\s+)?{PP}\b", re.I)
PERFECT = re.compile(rf"\b(?:has|have|had)\s+(?:not\s+)?(?:been|{PP})\b", re.I)
CONTRACTION = re.compile(r"\b\w+(?:n't|'re|'ve|'ll|'d)\b|\b(?:it|that|there|he|she|what|let)'s\b", re.I)
DECISION = re.compile(r"\b(triage|routes?|routing|routed|RUW|accept\w*|declin\w+|referral|approv\w+|reject\w*|risk class\w*|manual review)\b", re.I)
DISCLAIMER = "no underwriting logic"          # the one sentence that may name the topic
# words that look passive or perfect to the patterns above but are adjectives, nouns, or fixed phrases of the page
OK_PHRASES = ("is a draft", "is not a certification", "are the same", "has no validation", "has no calibration", "held-out", "set of")


ABBR = re.compile(r"\b(?:[A-Z]{2,}[A-Za-z0-9]*|[A-Z][a-z]+[A-Z][A-Za-z0-9]*)\b")      # ECG, CPT4, HbA1c
ALLOWED = {"RxNorm", "PubMed", "II", "III", "IV", "VI"}                                # names and Roman numerals, not abbreviations


def abbreviations(lines):
    """The first use of each abbreviation must be the one in brackets after its full term: 'complete blood count (CBC)'."""
    issues, seen = [], set()
    for n, ln in enumerate(lines, 1):
        if ln.startswith("## References"):
            break
        text = re.sub(r"`[^`]*`", " ", ln)
        for m in ABBR.finditer(text):
            tok = m.group(0)
            if tok in seen or tok in ALLOWED:
                continue
            seen.add(tok)
            if not (text[max(0, m.start() - 1):m.start()] == "(" and text[m.end():m.end() + 1] == ")"):
                issues.append((n, f"abbreviation used before its full term: '{tok}'", ln.strip()[:90]))
    return issues


def prose(lines):
    """Yield (first line number, paragraph text) for each paragraph of plain prose."""
    para, start = [], 0
    for n, ln in enumerate(lines, 1):
        s = ln.strip()
        skip = (not s) or s.startswith(("#", "|", "`", "---", "- ", "*Working"))
        if skip:
            if para:
                yield start, " ".join(para)
            para = []
            continue
        if not para:
            start = n
        para.append(s)
    if para:
        yield start, " ".join(para)


def main(path):
    lines = open(path).read().splitlines()
    issues = []
    for ln, para in prose(lines):
        text = re.sub(r"[*_]{1,2}", "", re.sub(r"`[^`]*`", "X", para))
        sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", text) if s]
        if len(sents) > MAX_SENTENCES:
            issues.append((ln, f"paragraph has {len(sents)} sentences (max {MAX_SENTENCES})", para[:70]))
        for s in sents:
            n = len(s.split())
            if n > MAX_WORDS:
                issues.append((ln, f"sentence has {n} words (max {MAX_WORDS})", s[:90]))
            for name, rx in (("modal verb", MODAL), ("passive", PASSIVE), ("perfect tense", PERFECT), ("contraction", CONTRACTION)):
                for m in rx.finditer(s):
                    ctx = s[max(0, m.start() - 20):m.end() + 20]
                    if not any(p in ctx for p in OK_PHRASES):
                        issues.append((ln, f"{name}: '{m.group(0)}'", ctx))
    in_refs = False
    for n, ln in enumerate(lines, 1):
        if ln.startswith("## References"):
            in_refs = True
        if in_refs or DISCLAIMER in ln:
            continue
        for m in DECISION.finditer(ln):
            issues.append((n, f"decision wording: '{m.group(0)}'", ln.strip()[:90]))
    issues += abbreviations(lines)
    for ln, what, ctx in issues:
        print(f"line {ln}: {what}  <- {ctx}")
    print(f"{len(issues)} issues")
    return 1 if issues else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
