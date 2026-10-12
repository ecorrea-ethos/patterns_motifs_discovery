---
name: pubmed-literature-check
description: Fill the "Supported literature" and "PMIDs" columns (and draft the "Triage suggestion") of a final_table_*.xlsx from the NMF + PrefixSpan notebooks, using PubMed (NLM E-utilities). Use when asked to add literature, PMIDs or triage to a final table, or to re-check citations. Never invent PMIDs.
---

# PubMed literature check for a final table

Full rationale and rating definitions: `docs/literature-search.md`. Scripts: `nb/repr_learn_letrozole/literature_search/`
(`pubmed.py`, `search_entities_patterns.py`, `search_setting.py`, `verify_pmids.py`).

## Rules that never bend
- **No PMID from memory.** Every PMID written to the workbook must have been returned by a PubMed search in this run, then
  confirmed by `verify_pmids.py`. Memory-recalled PMIDs were wrong before (Crew 2007 is 17761973).
- **Search basis (user rule):** at least **3 of the bundle's top-5 entities ANDed together, unordered**, OR the **steps of the
  typical order of care** ANDed together. PubMed cannot test order; say so.
- Keep a hit only if its **title fits the bundle's clinical setting**. Titles were read, abstracts were not: say so.
- Ratings are a draft for clinical review. Never claim a paper "proves" a sequence; no paper tests the order, so no sequence gets `Yes`.

## Steps
1. **Read the table.** Open the target `final_table_*.xlsx` with openpyxl (not pandas alone: it reads the text "None" as blank).
   Columns by header: `Most frequently OMOP clinical entities found`, `Typical order of care…`, `Triage suggestion (Manual RUW / Routine / Unclear)`,
   `Supported literature (Yes / Partly / None)` (drop-down), `PMIDs`. Bundle-level cells are merged; write to the top-left cell.
   Also read the matching `nmf_components_*.xlsx` for the full top-5 entity names.
2. **Set up the search** in `pubmed.py` for this table: add each entity to `T` (a hand-written PubMed clause such as
   `("hemoglobin A1c"[tiab] OR "glycated hemoglobin"[tiab] OR HbA1c[tiab])`, never the raw OMOP name), list each bundle's top-5 in `ENT`,
   and map each pattern row (Excel row number) to its concepts in `PAT`. Skip bundles that have no pattern rows in `PAT` but keep them in `ENT`.
3. **Round 1:** `python search_entities_patterns.py` (all 3-of-5 triples, the 5-entity set, 3 entities + letrozole, each pattern's steps).
   **Round 2:** edit the `Q` dict in `search_setting.py` to add each bundle's setting (e.g. infertility, carrier screening, low back pain),
   then `python search_setting.py`. Both need network access to `eutils.ncbi.nlm.nih.gov`; inside the Claude Code sandbox that host is blocked,
   so run them with the sandbox disabled after the user allows it. Python's own HTTPS fails behind the corporate TLS proxy, which is why the
   scripts call `/usr/bin/curl`. Never turn certificate verification off.
4. **Judge hits.** For each row, from the printed top hits, keep papers whose title fits the setting. Use the definitions:
   - `Yes`: literature addresses the combination as a unit (e.g. a carrier-screening panel).
   - `Partly`: addresses the combination or steps in a different or more general setting; does not test the sequence.
   - `None`: no on-topic hit; PMIDs = `none found`.
5. **Triage (bundle level, draft):** `Manual RUW` = letrozole may be adjuvant cancer therapy; `Routine` = explained by fertility, pregnancy or
   preconception care; `Unclear` = bundle does not show the indication. Base it on entities and bundle name, not on the literature.
6. **Write** `M`, `O`, `P` with openpyxl. Before saving, check no `~$<workbook>` lock file exists (Excel open); if it does, ask the user to close
   it without saving. Keep existing formatting, merged cells and the drop-down. Update the workbook's Notes line to describe the rule if absent.
7. **Verify:** `python verify_pmids.py <workbook>.xlsx` (needs the network, as above). It fails if any PMID is not in PubMed and writes
   `<workbook>_literature_verified.csv`. Also save the query log of what was run (query text and hit counts) next to the workbook.
8. **Report** to the user: ratings per bundle, any rating that changed, which well-known guidelines were not retrieved (and therefore not cited),
   and that a clinician should confirm each `Partly`.

## Pitfalls
- Bare entity triples (HbA1c, ibuprofen, injection codes) are mostly noise; the setting round (step 3, round 2) is what finds relevant papers.
- Peri-operative or physical-therapy entity literature that never mentions letrozole can earn `Partly`: say it means "recognised care", not
  "letrozole is supported".
- Windowed tables have different bundles (oocyte retrieval, prenatal ABO/Rh, STI testing, anesthesia, CBC/CMP/urinalysis); they need their own
  `ENT`/`PAT`/setting entries. Do not copy ratings from the full run.
- Rate limit: about 3 requests/second without an NCBI API key; the scripts sleep 0.35 s between calls.
