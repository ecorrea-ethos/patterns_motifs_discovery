"""
Write ONE consolidated predicate and composite page for a use case (chest pain, mammography, colonoscopy, ...).

    python build_page.py path/to/config.yaml        # env ethos_llm (pandas, openpyxl, pyyaml)

Page layout: overview -> predicates once (all care patterns share them) -> composites of every care pattern ->
window fit, entity rates, sequence rates -> references. No triage and no underwriting wording: the page is a clinical
grouping of codes. Nothing is measured here; every number is read from the final table, the member table and the
literature csv named in the config. Wording of entities and the care pattern definitions come from the config.
Config format: ../references/config_format.md. Worked example: nb/repr_learn_chestpain/chest_pain_page.yaml.
"""
import os
import re
import sys

import openpyxl
import pandas as pd
import yaml

# final table column -> header regex (columns are found by header text; the three use cases differ in position and count)
HEADERS = {
    "group": r"Group", "n": r"n \(%\)", "ents": r"Most frequently", "rank": r"Rank", "text": r"Typical order",
    "sup_in": r"Share of group with pattern", "sup_out": r"Share of everyone else", "passrate": r"Held-out pass rate|Re-tests found",
    "holds": r"Holds up", "lift": r"Times as common", "verdict": r"Final verdict", "order": r"Order shown", "pmids": r"PMIDs",
}
AN_FIRST = set("AEFHILMNORSX")      # letters whose name starts with a vowel sound, for acronyms
ORD = {2: "second", 3: "third", 4: "fourth", 5: "fifth"}


def with_article(noun):
    w = noun.split()[0]
    if w.isupper() or any(c.isupper() for c in w[1:]):         # acronym: ECG, CMP, HbA1c
        return ("an " if w[0] in AN_FIRST else "a ") + noun
    noun = noun[0].lower() + noun[1:]
    return ("an " if noun[0] in "aeiou" and not noun.startswith("ur") else "a ") + noun


def fmt_pct(x):
    return f"{float(x) * 100:.1f}%"


def days_text(med):
    return "same day" if med == 0 else f"{abs(med):,} day{'' if abs(med) == 1 else 's'} {'before' if med < 0 else 'after'}"


def cap(t):
    return t[0].upper() + t[1:]


class Page:
    def __init__(self, cfg_path):
        self.base = os.path.dirname(os.path.abspath(cfg_path))
        self.cfg = cfg = yaml.safe_load(open(cfg_path))
        self.anchor = cfg["anchor"]
        self.ENT = cfg["entities"]
        self.CP = cfg["care_patterns"]
        self.ORDER = list(self.CP)
        self.W = cfg.get("window_days", 1)
        self.MIN = cfg.get("min_entities", 3)
        self.Wtxt = f"{self.W} day" + ("" if self.W == 1 else "s")
        files = cfg["files"]
        self.out_file = self.path(cfg["output"])
        self.members = pd.read_csv(self.path(files["members"]), low_memory=False)
        self.members_name = os.path.basename(files["members"])
        self.lit = pd.read_csv(self.path(files["literature"]), dtype=str) if files.get("literature") else None
        self.parse_table(self.path(files["final_table"]))
        self.check()

    def path(self, p):
        return p if os.path.isabs(p) else os.path.join(self.base, p)

    # ------------------------------------------------------------------ the final table
    def parse_table(self, path):
        ws = openpyxl.load_workbook(path).active
        col = {}
        for i, c in enumerate(ws[1], start=1):
            h = str(c.value or "")
            for key, pat in HEADERS.items():
                if key not in col and re.match(pat, h):
                    col[key] = i
        missing = [k for k in HEADERS if k not in col]
        assert not missing, f"final table has no column for {missing}"
        head = ws.cell(1, col["passrate"]).value
        if head.startswith("Held-out"):
            self.pass_label, self.pass_fmt = "Held-out pass rate", lambda v: f"{float(v):.0%}"
        else:                                                      # "Re-tests found (of 5)"
            n_of = re.search(r"\(of (\d+)\)", head).group(1)
            self.pass_label, self.pass_fmt = head, lambda v: f"{int(float(v))} of {n_of}"
        self.TABLE = {}
        cur = None
        for r in range(2, ws.max_row + 1):
            g = ws.cell(r, col["group"]).value
            mt = re.match(r"(c\d+)\b", str(g or ""))
            if mt:
                cur = mt.group(1)
                n, pct = re.match(r"([\d,]+) \(([\d.]+%)\)", str(ws.cell(r, col["n"]).value)).groups()
                ents = []
                for blk in re.split(r"\n(?=\d\. )", str(ws.cell(r, col["ents"]).value)):
                    headline, _, tail = blk.partition("\n")
                    name = re.sub(r"^\d\. ", "", headline)
                    share = int(re.search(r"\((\d+)% of (?:bundle|group)\)", name).group(1))
                    name = re.sub(r" \(\d+% of (?:bundle|group)\)", "", name)
                    if "same day as" in tail:
                        med = 0
                    else:
                        d, side = re.search(r"median ([\d,]+) d (before|after)", tail).groups()
                        med = int(d.replace(",", "")) * (-1 if side == "before" else 1)
                    before = int(re.search(r"\((\d+)% of them before\)", tail).group(1))
                    ents.append(dict(name=name, share=share, med=med, before=before))
                self.TABLE[cur] = dict(n=n, pct=pct, ents=ents, pats=[])
            if cur and ws.cell(r, col["text"]).value and ws.cell(r, col["rank"]).value:
                v = lambda k: ws.cell(r, col[k]).value
                self.TABLE[cur]["pats"].append(dict(
                    sup_in=v("sup_in"), sup_out=v("sup_out"), passrate=v("passrate"), holds=v("holds"), lift=v("lift"),
                    verdict=v("verdict"), order=v("order"), pmids=str(v("pmids") or "")))

    def check(self):
        """Stop on a config that does not match the table, before any text is written."""
        a = self.anchor["key"]
        assert a not in self.ENT and "x2" not in self.ENT, "anchor key or x2 used as an entity key"
        roles = self.roles()
        flat = [k for ks in self.cfg["families"].values() for k in ks]
        assert set(flat) == set(roles), f"families vs entities used: {set(flat) ^ set(roles)}"
        assert len(flat) == len(set(flat)), "an entity is in two families"
        for k, e in self.ENT.items():
            assert all(x in e for x in ("name", "noun", "sents", "pred", "desc")), f"entity {k} lacks a field"
            assert ("token" in e) or ("union" in e) or ("vocab" in e and "code" in e), f"entity {k} has no code"
        names = [self.seq_name(s) for cn in self.ORDER for s in self.CP[cn]["pats"]]
        assert len(names) == len(set(names)), "sequence names collide"
        for cn in self.ORDER:
            T = self.TABLE[cn]
            assert len(T["pats"]) == len(self.CP[cn]["pats"]), f"{cn}: table has {len(T['pats'])} patterns, config {len(self.CP[cn]['pats'])}"
            idx = sorted(i for _, ix in self.CP[cn]["services"] for i in ix)
            assert idx == list(range(len(T["ents"]))), f"{cn}: services must cover table entities 0..{len(T['ents']) - 1} once, got {idx}"
        self.n_top = len(self.TABLE[self.ORDER[0]]["ents"])

    # ------------------------------------------------------------------ small text helpers
    def roles(self):
        """entity key -> {care pattern: set('entity', 'step')}"""
        r = {}
        for cn in self.ORDER:
            B = self.CP[cn]
            for k, _ in B["services"]:
                r.setdefault(k, {}).setdefault(cn, set()).add("entity")
            for steps in B["pats"]:
                for q in steps:
                    if q not in (self.anchor["key"], "x2"):
                        r.setdefault(q, {}).setdefault(cn, set()).add("step")
        return r

    def role_text(self, rs):
        out = []
        for cn in self.ORDER:
            if cn in rs:
                v = rs[cn]
                out.append(f"{cn} ({'entity and step' if len(v) == 2 else 'entity' if 'entity' in v else 'step'})")
        return ", ".join(out)

    def seq_name(self, steps):
        keep = steps if steps[0] != self.anchor["key"] else steps[1:]
        return "composite_seq_" + "_".join(keep)

    def root_step(self, steps, j):
        """(entity key, n) of step j; n = 1 for a first event, 2 for the 'x2' that repeats it, 3 for a second 'x2', ..."""
        n = 1
        while steps[j] == "x2":
            j, n = j - 1, n + 1
        return steps[j], n

    def noun(self, steps, j):
        k = steps[j]
        if k == self.anchor["key"]:
            return self.anchor["name"]
        if k == "x2":
            b, n = self.root_step(steps, j)
            return f"{ORD[n]} {self.ENT[b]['noun']}"
        return self.ENT[k]["noun"]

    def phrase(self, steps, j):
        k = steps[j]
        if k == self.anchor["key"]:
            return with_article(self.anchor["name"] + " event")
        if k == "x2":
            return "a " + self.noun(steps, j)
        return with_article(self.ENT[k]["noun"])

    def step_pred(self, k, steps, i):
        if k == self.anchor["key"]:
            return self.anchor["pred"]
        return self.ENT[self.root_step(steps, i)[0]]["pred"] if k == "x2" else self.ENT[k]["pred"]

    def cid_of(self, vocab, code):
        s = self.members[(self.members.vocabulary_id == vocab) & (self.members.concept_code.astype(str) == str(code))]
        assert len(s) >= 1, (vocab, code)
        return int(s.concept_id.iloc[0])

    def code_text(self, k):
        e = self.ENT[k]
        if "union" in e:
            return " + ".join(f"{v} {c} (concept_id {self.cid_of(v, c)})" for v, c in e["union"])
        if "token" in e:
            n = int((self.members.token == e["token"]).sum())
            assert n >= 1, e["token"]
            return f"group `{e['token']}`, {n} concepts (see the member table)"
        return f"{e['vocab']} {e['code']} (concept_id {self.cid_of(e['vocab'], e['code'])})"

    def ent_labels(self, cn):
        """Readable label + code for each entity of the table."""
        out = []
        for i, e in enumerate(self.TABLE[cn]["ents"]):
            k = next(k for k, idx in self.CP[cn]["services"] if i in idx)
            tags = re.findall(r"\[(.*?)\]", e["name"])          # the last tag is the code; a brand name can come first: "[Versed] [RxNorm 94517]"
            tok = self.ENT[k].get("token")
            code = (tags[-1].replace("code group", "code group " + tok) if tok else tags[-1]) if tags else ""
            out.append(f"{self.ENT[k]['name']} ({code})" if code else self.ENT[k]["name"])
        return out

    # ------------------------------------------------------------------ the page
    def build(self):
        cfg, an, ENT, CP, ORDER, T = self.cfg, self.anchor, self.ENT, self.CP, self.ORDER, self.TABLE
        aname, apred, W, MIN, N = an["name"], an["pred"], self.Wtxt, self.MIN, self.n_top
        has = an.get("has", aname)
        n_cohort = cfg["cohort_n"]
        R = self.roles()
        L = []
        a = L.append

        a(f"# {cfg['title']}")
        a("")
        a(f"*{cfg['status_line']}*")
        a("")
        a("---")
        a("")
        a("## Overview")
        a("")
        a(f"This document defines the predicates and composites for {aname} applicants. It is one page for all care patterns. "
          f"The cohort has {n_cohort:,} {aname} patients. A data method groups these patients by the care they receive. "
          f"The method found {len(ORDER)} care patterns, {ORDER[0]} to {ORDER[-1]}. "
          "Each predicate has one definition, and all care patterns use it.")
        a("")
        a(f"The same rules apply to every care pattern. An entity is one of the {N} most frequent entities of the care pattern. "
          f"The entity is in the window when its event is not more than {W} from {with_article(aname + ' event')}. "
          f"A care pattern needs {MIN} or more entities in the window and one of its 3 ordered sequences. "
          "The sequences are the 3 patterns with the highest lift.")
        a("")
        a("The document contains no underwriting logic and no product decision. It is a clinical grouping of codes. It is a draft and has no validation yet.")
        a("")
        if cfg.get("abbreviations"):                # full term first, then the abbreviation; the lint checks that no abbreviation comes earlier
            a("The page uses these abbreviations. Each line gives the full term, then the abbreviation.")
            a("")
            for ab, full in cfg["abbreviations"].items():
                a(f"- {full} ({ab})")
            a("")
        for para in cfg.get("extra_overview", []):
            a(para)
            a("")
        a("| Care pattern | Name | Patients | % cohort |")
        a("| :---- | :---- | ----: | ----: |")
        for cn in ORDER:
            a(f"| {cn} | {CP[cn]['name']} | {T[cn]['n']} | {T[cn]['pct']} |")
        a("")
        a("---")
        a("")
        a("## Predicates and Composites")
        a("")
        a(f"Each predicate uses a list of codes. The code is in the text. The member table `{self.members_name}` shows every concept of a code group.")
        a("")
        a("### Atomic Predicates")
        a("")
        a("A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.")
        a("")
        a(f"**{cap(aname)} present.** The applicant has at least one {aname} event. {an['codes_text']} All care patterns use it.")
        a("")
        a(f"`{apred}_present = event IS {an['desc']}`")
        a("")
        a(f"**First {aname} date.** This is the date of the first {aname} event. The engine measures the other dates from this date.")
        a("")
        a(f"`first_{apred}_date = MIN(event_date) over {aname} events`")
        a("")
        for fam, keys in cfg["families"].items():
            a(f"#### {fam}")
            a("")
            for k in keys:
                e = ENT[k]
                a(f"**{e['name']} present.** The applicant has at least one {e['noun']}. {' '.join(e['sents'])} "
                  f"Code: {self.code_text(k)}; care patterns: {self.role_text(R[k])}.")
                a("")
                a(f"`{e['pred']}_present = event IS {e['desc']}`")
                a("")
        a("#### Entity in window")
        a("")
        a(f"An entity is in the window when its event is not more than {W} before or after {with_article(aname + ' event')}. The window is {W}. "
          f"Each of the {N} entities of a care pattern has one window predicate. The window is a draft and has no calibration yet.")
        a("")
        a(f"`workup_window_days = {self.W}`")
        a("")
        a(f"`<entity>_in_window = <entity>_present AND EXISTS {aname} event date d, entity event date e with |e - d| <= workup_window_days`")
        a("")
        a("---")
        a("")
        a("### Composites")
        a("")
        a("A composite combines atomic predicates, or other composites, into a named clinical pattern. Each care pattern has the same four composites: entity count, entities, sequence, and care pattern.")
        a("")
        a(f"**Entities.** The applicant has {MIN} or more of the entities of the care pattern in the window. The value {MIN} is a draft. It has no calibration yet.")
        a("")
        if cfg.get("sequence_rule"):
            a(f"**Sequences.** {cfg['sequence_rule']}")
            a("")
        else:
            a("**Sequences.** A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. "
              f"A step after the {aname} step is not more than {W} after that {aname} event. A step before the {aname} step has no time limit. A step is true for any code of its list.")
            a("")
            a(f"`sequence_window_days = {self.W}`")
            a("")
        a("**Same-day order.** Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. "
          "Inside one type, a lower concept identifier comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.")
        a("")
        a(f"**Care pattern.** The applicant has {has}, {MIN} or more entities in the window, and at least one sequence. "
          "This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.")
        a("")
        for cn in ORDER:
            B = CP[cn]
            p = B["prefix"]
            a(f"#### {cn}: {cap(B['name'])}")
            a("")
            a(f"`{p}_entity_count = " + " + ".join(f"{ENT[k]['pred']}_in_window" for k, _ in B["services"]) + "`")
            a("")
            a(f"`composite_{p}_entities = {p}_entity_count >= {MIN}`")
            a("")
            names = []
            for i, steps in enumerate(B["pats"]):
                nm = self.seq_name(steps)
                names.append(nm)
                ph = [self.phrase(steps, j) for j in range(len(steps))]
                a(f"**Sequence {cn}-{'ABC'[i]}.** The applicant has {', then '.join(ph)}.")
                a("")
                a("`" + nm + " = " + " -> ".join(self.step_pred(q, steps, j) for j, q in enumerate(steps)) + "`")
                a("")
            a(f"`composite_{p}_sequence = " + " OR ".join(names) + "`")
            a("")
            a(f"`composite_{p}_pattern = {apred}_present AND composite_{p}_entities AND composite_{p}_sequence`")
            a("")
        a("---")
        a("")
        a("## Population Coverage")
        a("")
        a(f"Counts come from the {aname} cohort of {n_cohort:,} patients. The tables come from {cfg['run_text']}. "
          "The engine has no measured rate for any predicate or composite yet. Each patient is in the care pattern with the highest weight for that patient.")
        a("")
        a("### Window fit")
        a("")
        a(f"The window is {W}. The table shows how far the {N} entities of each care pattern are from the first {aname}. The median is the median day of the first event of the entity.")
        a("")
        a(f"| Care pattern | Earliest median | Latest median | Entities more than {W} from the first {aname} |")
        a("| :---- | :---- | :---- | ----: |")
        for cn in ORDER:
            meds = [e["med"] for e in T[cn]["ents"]]
            a(f"| {cn} | {days_text(min(meds))} | {days_text(max(meds))} | {sum(1 for x in meds if abs(x) > self.W)} of {N} |")
        a("")
        a("### Entity rates")
        a("")
        a("The rates count an entity at any time, not only in the window. The share is the share of the patients of the care pattern.")
        a("")
        a(f"| Care pattern | Entity | Patients with the entity | Median day against first {aname} | Share that had it before first {aname} |")
        a("| :---- | :---- | ----: | :---- | ----: |")
        for cn in ORDER:
            for e, lab in zip(T[cn]["ents"], self.ent_labels(cn)):
                a(f"| {cn} | {lab} | {e['share']}% | {days_text(e['med'])} | {e['before']}% |")
        a("")
        a("### Sequence rates")
        a("")
        a(cfg["sequence_rates_note"])
        a("")
        a(f"| Sequence | Steps | Patients of the care pattern | Patients of the other care patterns | Times as common | {self.pass_label} | Verdict |")
        a("| :---- | :---- | ----: | ----: | ----: | ----: | :---- |")
        n_pass = n_all = 0
        for cn in ORDER:
            for i, (pt, steps) in enumerate(zip(T[cn]["pats"], CP[cn]["pats"])):
                txt = ", ".join(self.noun(steps, j) for j in range(len(steps)))
                order = " (same-day order)" if pt["order"] == "Same-day bundle" else ""
                n_all += 1
                n_pass += pt["holds"] == "Yes"
                a(f"| {cn}-{'ABC'[i]} | {txt}{order} | {fmt_pct(pt['sup_in'])} | {fmt_pct(pt['sup_out'])} | {float(pt['lift']):.1f} | {self.pass_fmt(pt['passrate'])} | {pt['verdict']} |")
        a("")
        check = cfg.get("sequence_check_name", "held-out check")
        passed = (f"No sequence passed the {check}." if n_pass == 0 else f"All {n_all} sequences passed the {check}." if n_pass == n_all
                  else f"{n_pass} of the {n_all} sequences passed the {check}. The other sequences did not pass it.")
        a(f"{passed} Read them as a draft. The window and the rule of {MIN} entities narrow the match.")
        a("")
        a("---")
        a("")
        a("## References")
        a("")
        for line in cfg.get("references", []):
            a(f"- {line}")
        if self.lit is not None:
            seen = set(str(x) for x in cfg.get("skip_pmids", []))
            for cn in ORDER:
                for pt in T[cn]["pats"]:
                    for x in re.split(r"[;,\s]+", pt["pmids"]):
                        if x.isdigit() and x not in seen:
                            seen.add(x)
                            r = self.lit[self.lit.PMID == x]
                            if len(r):
                                r = r.iloc[0]
                                a(f"- {r['first_author']} et al. *{str(r['title (as returned by PubMed)']).rstrip('.')}.* {r['journal']} {r['year']}. PMID {x}.")
            a("")
            a("The papers come from the literature check of the final table. They cover the care type of the pattern. They do not test the order of the steps.")
        return "\n".join(L) + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = Page(sys.argv[1])
    text = page.build()                         # build first: a failed build must not truncate the old page
    unused = [ab for ab in page.cfg.get("abbreviations", {}) if len(re.findall(rf"\b{re.escape(ab)}\b", text)) < 2]
    if unused:
        print("warning: abbreviation listed but never used:", ", ".join(unused))
    os.makedirs(os.path.dirname(page.out_file), exist_ok=True)
    open(page.out_file, "w").write(text)
    print("wrote", page.out_file)
