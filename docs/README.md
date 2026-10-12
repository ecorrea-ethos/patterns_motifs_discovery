# Pattern-discovery notebooks: documentation

## What it is
Three 5-day courses (`nb/repr_learn_chestpain/`, `nb/repr_learn_breastcancer/`,
`nb/repr_learn_letrozole/`) that look for patterns in insurance-claims health data
(OMOP format) without a labelled answer. The chest pain course asks whether claims
history can sort `dx_9487` (atypical chest pain) cases into "likely anxiety/panic" versus
"needs a cardiac workup". These docs cover how **Day 1** (the bag of codes and NMF) is built
and validated. Other days are described in each course's `README_repr_learn.md`.

## Index
| Doc | What it answers |
|---|---|
| [event-labels.md](event-labels.md) | How each medical code gets its column name, and how rare codes are pruned |
| [nmf-validation.md](nmf-validation.md) | How the number of NMF components (k) is chosen and checked; what the chest pain run found |
| [day1-performance.md](day1-performance.md) | Why Day 1 uses a sparse matrix and a parallel sweep, and how it was checked |
| [literature-search.md](literature-search.md) | How the letrozole final table's triage, literature and PMID columns are filled and checked (PubMed search rule, rating definitions) |
| [glossary.md](glossary.md) | Plain-English definitions of the terms used here |
| `../HANDOFF.md` | Current state, open decisions, and next steps |
| [superpowers/specs/](superpowers/specs/) | Design specs written earlier (chest pain triage) |

## Setup
- Python environment: the conda env `ethos_llm`. Notebooks import `ethos_omop` (one copy
  inside each course directory; the three copies must stay in sync, see Gotchas).
- Run each notebook from inside its own course directory, because paths like
  `../../inputs/chest_pain_cohort/` are relative to it.
- Data: `inputs/<cohort>_cohort/` holds the OMOP CSV extract. It is gitignored and comes from
  Snowflake via `eo.extract_cohort(...)`. No credentials belong in these docs or notebooks.

## Key conventions & decisions
- Hand-built clinical codesets live in `codesets.yaml`; they keep their clean names
  (`chest_pain`, `troponin`, ...). Everything else gets a unique generated label
  ([event-labels.md](event-labels.md)).
- All NMF fits in Day 1 share one settings object, `NMF_KW`, so a base fit and its
  bootstrap refits are always converged the same way ([nmf-validation.md](nmf-validation.md)).
- The cohort anchor code (`chest_pain`, `breast_cancer`, `letrozole`) is present for every
  patient **by construction**: it is how the cohort is defined, so it is a known signal and not a
  finding. It is dropped before any SVD/NMF fit (a constant column carries no information) and kept
  in `X` for the demos and Table 1.
- The breast cancer and letrozole cohort SQL queries (`sql/`) are still under review, so their
  cohort sizes (1,704 and 6,103 patients) and Day 1 results may change. Port new Day 1 work to
  them only after that review ([../HANDOFF.md](../HANDOFF.md)).

## Gotchas
- **Three copies of `ethos_omop.py`.** Edits must be applied to all three course directories.
- **Cell order matters in Day 1.** The `nmf_stability` definition cell must run before the k
  sweep; the main NMF fit must run before the stability call and the loadings check.
- **Large notebooks.** After a run, Day 1 holds big outputs; some editor tools refuse to read
  it. Edit the `.ipynb` JSON with a script if needed (it round-trips byte-exactly with
  `json.dumps(nb, indent=1, ensure_ascii=False) + "\n"`).
- **Parallel code and sandboxes.** The parallel sweep uses processes; it runs in Jupyter but
  can be blocked inside a restricted sandbox (see [day1-performance.md](day1-performance.md)).
