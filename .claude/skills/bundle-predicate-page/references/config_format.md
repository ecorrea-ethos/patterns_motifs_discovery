# Config format for `scripts/build_page.py`

One YAML file per use case, stored next to the notebook (`nb/repr_learn_<use_case>/<use_case>_page.yaml`). Paths are relative to the YAML file. The worked example is `nb/repr_learn_chestpain/chest_pain_page.yaml`; its page (`outputs/chest_pain_all_patterns.md`) is reproduced byte for byte by the script, so copy from it.

## Top-level keys

| Key | Type | Feeds |
| :-- | :-- | :-- |
| `title` | text | page title |
| `status_line` | text | italic line under the title, e.g. `Working Draft — October 2026` |
| `cohort_n` | int | "The cohort has N <anchor> patients" |
| `run_text` | text | "The tables come from <run_text>", e.g. ``the k=8 run of the data method (`nmf_k8_chestpain_AHA`)`` |
| `files.final_table` | path | final table xlsx (see below) |
| `files.members` | path | token member csv (`vocabulary_id`, `concept_code`, `concept_id`, `token`); its file name is quoted in the page |
| `files.literature` | path, optional | `..._literature_verified.csv` (`PMID`, `first_author`, `year`, `journal`, `title (as returned by PubMed)`); omit when the table has no PMIDs |
| `output` | path | the page |
| `anchor` | map | the index event, see below |
| `window_days` | int, default 1 | entity window and sequence limit after the anchor step |
| `min_entities` | int, default 3 | entities needed in the window |
| `sequence_rule` | text, optional | replaces the default "Sequences" paragraph and drops the `sequence_window_days` line. Use it when the table's patterns are not anchored on the index event or have no time limit between steps (mammography: mined on the full history, no gap limit). Without it the page says a step after the anchor step is within `window_days` of it |
| `sequence_rates_note` | text | intro of the "Sequence rates" table. Say how the other care patterns were sampled and what the check column means for this run |
| `sequence_check_name` | text, default `held-out check` | name of the check in the closing sentence of that section |
| `abbreviations` | map `ABBR: full term`, optional but needed whenever the page has an abbreviation | printed as a list "full term (ABBR)" right after the "no underwriting logic" paragraph, before every other use. Include code systems (CPT4, SNOMED, HCPCS). Single letters with a digit (T4, H2) count too |
| `extra_overview` | list of text, optional | extra paragraphs after the "no underwriting logic" paragraph; use for a fact the reader needs, e.g. how in-situ breast disease is counted |
| `references` | list of text | fixed reference lines (guidelines) before the PMID list |
| `skip_pmids` | list of text | PMIDs already in `references` |
| `families` | map family name -> list of entity keys | groups of the predicate section, in order. Every entity key used as an entity or as a step must be in exactly one family |
| `entities` | map | see below |
| `care_patterns` | map `c0`, `c1`, ... -> map | see below. The keys must match the `cN` of the final table |

`anchor`: `key` (step keyword used in `pats`, e.g. `cp`), `name` (lower-case noun used in sentences, e.g. `chest pain`), `pred` (predicate stem, e.g. `chest_pain`, gives `chest_pain_present`), `desc` (what the event is, e.g. `chest pain diagnosis`), `codes_text` (one sentence that lists the anchor codes), `has` (optional; text after "The applicant has" in the care pattern composite, default `name`).

## Entities

One entry per clinical service. Two table rows of one service (ECG with and without report, STI chlamydia and gonorrhea) are one entity.

```yaml
lipid:
  name: Lipid panel                  # heading of the predicate: "Lipid panel present." (an abbreviation here must be in `abbreviations`)
  noun: lipid panel                  # "The applicant has at least one lipid panel." and sequence text
  sents:                             # plain-English definition, 1 to 3 sentences, each <= 25 words
  - A lipid panel is a blood test for cholesterol and other fats.
  pred: lipid_panel                  # snake_case stem: lipid_panel_present, lipid_panel_in_window
  desc: lipid panel                  # "event IS <desc>"
  vocab: CPT4                        # one code: vocab + code (string) ...
  code: '80061'
  # token: ekg                       # ... or a code group of the member table (use instead of vocab/code)
  # union: [[CPT4, '97110'], [CPT4, '97112']]   # ... or a union of codes (use instead of vocab/code)
```

Take the code from the `[VOCAB code]` tag of the final table or from the member table. The script looks up the concept_id and stops when the code is not in the member table. Never type a concept_id by hand.

## Care patterns

```yaml
c0:
  prefix: checkup                    # composite names: composite_checkup_entities, composite_checkup_sequence, ...
  name: outpatient check-up and elective cardiac testing   # lower case; plain English, no risk or decision words
  services: [[lipid, [0]], [venip, [1]], [ecg, [3]]]       # [entity key, indices of the final table entities it stands for]
  pats: [[cp, ecg, hld], [cp, genexam, lipid], [cp, ecg, genexam]]   # the 3 table patterns, in table order
```

`services` indices are the 0-based positions in the "Most frequently ..." cell of the table row. Together they must cover every table entity once (the script checks it). Step keywords in `pats`: the anchor `key` (leave it out of `pats` when the table has no anchor step); an entity key; `x2` = the previous step again, as a second event. The table writes this as `X ×2`; `X ×4` is `[X, x2, x2, x2]` and reads "a second, a third, a fourth". Steps that repeat with other steps between them (`cbc → chem → cbc → chem`) are plain entity keys, not `x2`.

## What the script reads from the final table

Columns are found by header text, so the layout may differ between use cases: `Group`, `n (%)`, `Most frequently...`, `Rank`, `Typical order...`, `Share of group with pattern`, `Share of everyone else...`, `Held-out pass rate...` or `Re-tests found (of N)`, `Holds up...`, `Times as common`, `Final verdict`, `Order shown...`, `PMIDs`. The triage and literature-rating columns are not read; triage never goes into the page. A group row starts with `cN`. The entity cell must read `1. <name> [CODE] (NN% of bundle|group)` with a `median ... d before|after first <anchor> (NN% of them before)` line, or `median same day as first <anchor>`.

## What the script checks before it writes

Anchor key not an entity key; every entity has a code; every entity used is in a family, once; sequence names are unique; the table has as many patterns per care pattern as the config; `services` cover the table entities once.

## Wording that the script writes itself

Overview, window rule, same-day order, the composite chain (`<prefix>_entity_count`, `composite_<prefix>_entities`, `composite_seq_...`, `composite_<prefix>_sequence`, `composite_<prefix>_pattern`), the three coverage tables, and the closing sentences. Change that text in `build_page.py`, not in one page, so all use cases keep the same engine rules (`workup_window_days` and `sequence_window_days` are fixed names of the engine).
