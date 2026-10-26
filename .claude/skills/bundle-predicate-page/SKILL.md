---
name: bundle-predicate-page
description: Build the ONE-file predicate and composite page ("one-file bundle page", "all patterns page") of an Ethos use case from its NMF + PrefixSpan final table - predicates defined once, then the composites of every care pattern (NMF bundle), coverage tables, references. Use whenever the user asks for the consolidated predicates document, the underwriter hand-off page, "the same format as chest pain" for mammography, colonoscopy or any new use case, wants to regenerate or update such a page after a new run, or wants per-bundle engine pages merged into one. Also use when turning a final_table_*.xlsx into predicate and composite definitions, even if the user does not say "bundle".
---

# One-file bundle predicate page

Turns a use case's final table (bundles x 3 ordered patterns) into one markdown page: **overview -> every predicate once -> the four composites of each care pattern -> window fit, entity rates, sequence rates -> references**. The chest pain page (`nb/repr_learn_chestpain/outputs/chest_pain_all_patterns.md`, 8 care patterns, 39 predicates) is the model.

## Why one file, and what stays out

Zack (touch base 2026-10-21) asked for one document per use case, not one per care pattern. Predicates such as chest pain or ECG repeat across care patterns; eight definitions can drift apart. The page goes to underwriters, so it must be an **independent clinical grouping of codes**:

- No triage, routing, accept / decline, "manual review", or product decision. Triage lives in the final table only. Reason: the page must not bias the underwriters.
- No cardiac versus non-cardiac compaction: one flat list of care patterns.
- No measured rates for predicates or composites (none exist yet); coverage tables only repeat what the final table says.
- State facts, not advice. A fact the reader needs (for example, in-situ breast disease is kept and counted as no breast cancer, see the memory note on in-situ handling) goes in `extra_overview` as a plain statement.

## Before you start

You need, for the run you document: the final table xlsx (bundles-only, 3 patterns per bundle), the token member csv, the cohort size, and ideally the `..._literature_verified.csv`. If the final table has no PMIDs yet, build without `files.literature` and say that references are missing; the `pubmed-literature-check` skill fills them. Do not invent codes, PMIDs, or numbers.

## Workflow

1. **Learn the model.** Read `nb/repr_learn_chestpain/chest_pain_page.yaml` and `references/config_format.md` (field by field). The script reproduces the chest pain page byte for byte, so the YAML shows exactly what each field becomes. `nb/repr_learn_mammography/mammography_page.yaml` is the second example: sequences without an anchor step (`sequence_rule`), 4-step sequences, and `×N` repeats.
2. **Read the use case's final table** (openpyxl, header row 1). For each care pattern list its entities and its 3 patterns. Then group table rows into clinical services (two codes of one test are one entity) and map every pattern step to an entity.
3. **Write `<use_case>_page.yaml`** next to the notebook folder.
   - Take codes only from the table's `[VOCAB code]` tags or the member table. The script resolves concept_ids and fails on an unknown code.
   - Write the entity sentences in plain English, ASD-STE100 style: present tense, active voice, no modal verb, each sentence <= 25 words, define the medical term in words a layperson reads, and say what the data cannot show (for example "A high-sensitivity test and a standard test look the same").
   - **Abbreviations: full term first, abbreviation after it, in brackets** ("complete blood count (CBC)", never "CBC (complete blood count)"). List every abbreviation of the page, code systems included (CPT4, SNOMED, HCPCS), in the `abbreviations` map: the page prints that glossary before any other use, so headings such as "CBC present." come after the definition. Write the entity sentences in the same order. Care pattern names use no abbreviation ("gastrointestinal", not "GI"). Names such as RxNorm are not abbreviations; explain them in one `extra_overview` sentence. The lint fails on any abbreviation whose first use is not the bracketed one, and the build warns about a glossary entry the page never uses.
   - Name care patterns from the final table group label, shortened, in plain words. No risk, cancer-likelihood, or decision words.
   - Check how the notebook mined the patterns (`config/robustness.yaml`, the discovery code). If the patterns are not anchored on the index event and have no gap limit between steps, as in mammography, set `sequence_rule` so the page states the rule that matches the measured shares. Do not keep the chest pain 1-day sequence limit for patterns that were never measured with it.
   - `sequence_rates_note` must describe how *this* run's check column was made (held-out halves vs. re-tests); read the notebook or the table header, do not copy chest pain text blindly.
   - An entity that is the anchor itself or its sibling (mammography screening, tomosynthesis, colonoscopy) sits on day 0 and is in the window by construction. Keep it, but tell the user, because it inflates the entity count.
   - When the clinical meaning of a name is unclear, ask the user; a clinician reads the page later.
4. **Build.** Env `ethos_llm` (base python has no numpy):
   ```bash
   /opt/miniconda3/envs/ethos_llm/bin/python .claude/skills/bundle-predicate-page/scripts/build_page.py nb/repr_learn_<use_case>/<use_case>_page.yaml
   ```
   An assertion names the config problem (uncovered table entity, entity missing from a family, unknown code). Fix the YAML, not the script.
5. **Lint.** `scripts/lint_page.py <page.md>` checks sentence and paragraph length, modal, passive, perfect tense, contractions, decision wording, and the abbreviation order. It is a script check, not an ASD-STE100 certification; say so. Zero issues is required before you hand over.
6. **Read the page once**, top to bottom, as an underwriter would. Check: the window-fit table (are most entities far from the anchor? say it), sequence verdicts (how many failed the check), entity names that read as diagnoses of risk.
7. **Report** to the user: output path, lint result, and the open items (clinician read, window needs calibration, weak sequences, missing PMIDs). Add a short dated entry to `HANDOFF.md` in the project's style.

## Changing the engine rules

Window, minimum entities, same-day order, and the composite chain are shared by all use cases so that pages stay comparable. `window_days` and `min_entities` are config values; the wording of rules lives in `build_page.py`. If a rule changes, change the script and rebuild every page, then confirm the chest pain page still reproduces (or diff it on purpose).

## Do not

- Delete or edit the per-pattern pages (`outputs/bundle_engines/`, the v3 ED work-up page) or the final tables. Retiring them is the user's call.
- Put triage, "Manual RUW", or any routing wording on the page, even as a draft.
- Hand-edit the generated page. Edit the YAML or the script, then rebuild.
