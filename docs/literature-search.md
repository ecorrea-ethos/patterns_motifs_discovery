# Literature column and triage: how the final table is filled

## What this covers
How the last three columns of the letrozole final table (`final_table_letrozole_k*.xlsx`) are
filled: **Triage suggestion**, **Supported literature**, and **PMIDs**. It describes the PubMed
search rule, the rating definitions, how citations are checked, and how to repeat or extend it.
It does not cover how the table's other columns are computed (see `../nb/repr_learn_letrozole/`).

Worked example: `final_table_letrozole_k7_full.xlsx` (full history, k=7), filled 2026-10-12.

## The three columns

| Column (header) | Level | Values |
|---|---|---|
| `Triage suggestion (Manual RUW / Routine / Unclear)` | one per bundle (merged cells) | `Manual RUW`, `Routine`, `Unclear` |
| `Supported literature (Yes / Partly / None)` | one per pattern row (drop-down) | `Yes`, `Partly`, `None` |
| `PMIDs` | one per pattern row | PubMed IDs separated by `; `, or `none found` |

A bundle with no letrozole patterns (k=7 full: c4 carrier screening) has a single row. It still
gets a triage value and a literature rating, based on its entities only.

## Triage definitions (bundle level)
- **Manual RUW**: letrozole may be adjuvant cancer therapy, so a human underwriter reviews it
  (stage, treatment status). Used for the peri-operative / oncology bundle.
- **Routine**: letrozole is explained by fertility, pregnancy or preconception care.
- **Unclear**: the bundle does not show why letrozole was prescribed; use other evidence in the record.

These are drafts for underwriter review. They come from the bundle's entities and name, not from the literature search.

## Literature search rule
The search uses PubMed (NLM E-utilities). A row qualifies for a search by **either** of:

1. **Entities, unordered.** At least 3 of the bundle's top-5 entities (column "Most frequently
   OMOP clinical entities found") ANDed together. Run all 10 three-entity combinations and the full
   5-entity set. Also run the first 3 entities with letrozole.
2. **Typical order of care.** The steps of the pattern (column "Typical order of care") ANDed
   together, letrozole included. PubMed cannot test order, so this checks the steps only.

A second round adds the bundle's clinical setting to the entities (for example `infertility`,
`carrier screening`, `low back pain`, `postoperative nausea`), because bare entity triples are
mostly noise for non-specific codes such as HbA1c or ibuprofen.

Each OMOP entity is translated to a PubMed clause by hand, for example `Hemoglobin A1c measurement`
becomes `("hemoglobin A1c"[tiab] OR "glycated hemoglobin"[tiab] OR HbA1c[tiab])`. The map is the
dictionary `T` in `nb/repr_learn_letrozole/literature_search/pubmed.py`. Queries sort by relevance
and read the top hits.

### Keeping a hit
Keep a paper only if its **title fits the bundle's clinical setting** and it was retrieved by one
of the searches above. Do not add papers from memory. Example of a dropped hit: a paediatric
otitis-media drug review that matched the c1 antibiotics, because it is a different population
and unrelated to letrozole. Titles were read; abstracts and full texts were not.

## Rating definitions (per pattern row)
- **Yes**: the literature addresses the combination as a unit. k=7 example: the carrier-screening
  panel of CFTR, HEXA, IKBKAP, FMR1 and GBA.
- **Partly**: the literature addresses the combination or its steps, but in a different or more
  general setting (PCOS lab work-up, letrozole stimulation protocols, perioperative drugs,
  physical therapy for low back pain), and does not test the sequence.
- **None**: no on-topic hit. Write `none found` in PMIDs.

Nothing is rated Yes for a sequence: no retrieved paper tests the order of steps.
Entity-based literature that does not mention letrozole (for example peri-operative drug
combinations) can still earn `Partly`. Read those rows as "this combination is recognised care",
not "letrozole is supported here".

## Verification
Every PMID in the sheet is checked against PubMed `esummary` after the workbook is written. The
check asserts each ID exists and records author, year, journal and title in
`final_table_letrozole_k7_full_literature_verified.csv`, with the table rows that use it.
Model memory is not a source: several PMIDs recalled from memory were wrong (Crew 2007 is
17761973) and were only caught by this check.

## Files

| File | Purpose |
|---|---|
| `nb/repr_learn_letrozole/final_table_letrozole_k7_full.xlsx` | The filled table. Notes line (A32) restates the rule |
| `nb/repr_learn_letrozole/final_table_letrozole_k7_full_literature_verified.csv` | PMID, first author, year, journal, title, rows that use it |
| `nb/repr_learn_letrozole/final_table_letrozole_k7_full_literature_search_log.csv` | Every query run and its PubMed hit count |
| `nb/repr_learn_letrozole/literature_search/pubmed.py` | E-utilities helper, term map `T`, bundle entities `ENT`, pattern concepts `PAT` |
| `nb/repr_learn_letrozole/literature_search/search_entities_patterns.py` | Round 1: entity triples, 5-entity set, pattern steps |
| `nb/repr_learn_letrozole/literature_search/search_setting.py` | Round 2: entities plus clinical setting |
| `nb/repr_learn_letrozole/literature_search/verify_pmids.py` | Checks every PMID in a workbook against PubMed and writes the verified CSV |
| `.claude/skills/pubmed-literature-check/SKILL.md` | Claude Code skill that runs this whole procedure on demand |

## Repeating it (new run or another cohort)
On demand: ask Claude Code to use the `pubmed-literature-check` skill on a final table. It follows the steps below.
Why a skill and not a notebook cell: retrieval and PMID checking are mechanical, but deciding which hits fit the clinical setting and rating each row needs reading, and the scripts need network access that the sandbox blocks.

1. Read the bundle's top-5 entities and the pattern rows from the final table and
   `nmf_components_*.xlsx`.
2. In `pubmed.py`, add each new entity to `T`, list the bundle's entities in `ENT`, and map each
   table row (Excel row number) to its pattern concepts in `PAT`.
3. Run the two scripts from `literature_search/`. They write `lit_results.json` and
   `lit2_results.json` and print counts plus top hits.
4. Read the hits, keep those that fit the setting, rate each row, then write `O` and `P` and
   run `python literature_search/verify_pmids.py <workbook>.xlsx` (fails if any PMID is not in PubMed).
5. Record the date, since PubMed changes.

## Gotchas
- **Network.** Needs access to `eutils.ncbi.nlm.nih.gov`. Inside the Claude Code sandbox the host
  is blocked; the searches in this guide ran outside it.
- **TLS.** The scripts call `/usr/bin/curl`, not Python's `urllib`. Behind the corporate proxy
  Python fails with `CERTIFICATE_VERIFY_FAILED`; curl uses the macOS trust store. Do not turn
  certificate verification off.
- **Rate.** No API key; the scripts sleep 0.35 s between calls (about 3 requests per second).
- **Excel lock.** If the workbook is open in Excel (a `~$…` file next to it), close it without
  saving before writing, or Excel overwrites the edits.
- **`None` in pandas.** `pandas.read_excel` reads the text "None" as blank. The cell does hold
  `None`. Use `keep_default_na=False` or openpyxl to read it.
- **Windowed tables.** `final_table_letrozole_k13_win18.xlsx` and the sensitivity-run tables are
  not filled yet. Their entities differ (for example oocyte retrieval, prenatal ABO/Rh typing),
  so they need their own `ENT` and `PAT` entries.

## Limits
- Search by title/abstract match on hand-built clauses. Missing a relevant paper is possible,
  and an authoritative guideline whose abstract does not name the entities is not retrieved
  (ASRM 2021, ACOG Practice Bulletin 194 and the 2023 PCOS guideline were not found by this
  rule, so they are not cited).
- Ratings come from reading titles. A clinician or librarian should confirm each `Partly`
  against the paper before the table is used for underwriting.
- The search log shows counts, not relevance. Many entity triples return hits that are noise.
