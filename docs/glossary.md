# Glossary

Plain-English definitions of terms used in these docs and notebooks.

- **OMOP**: a standard layout for health records (people, visits, conditions, drugs, procedures).
  The data here is an OMOP extract of Ethos claims.
- **Concept / `concept_id`**: one standard medical idea in OMOP (a diagnosis, drug or procedure).
  Each has a numeric id, a name and a `concept_class_id` (its kind, such as "Clinical Drug").
- **Codeset / codeset tag**: a hand-built group of concepts with one clean name (for example
  `troponin`), defined in `codesets.yaml`. Untagged concepts get a generated fallback label
  ([event-labels.md](event-labels.md)).
- **Cohort anchor**: the code that defines who is in the cohort (`chest_pain`, `breast_cancer`,
  `letrozole`). It is present for almost everyone, so it is dropped before modelling.
- **Bag of codes**: a table with one row per patient and one column per code; 1 if the patient
  ever had that code, else 0. It ignores order and timing.
- **Prevalence**: the share of patients who have a code. The **prevalence floor** is the minimum
  number of patients a code needs to be kept.
- **NMF (non-negative matrix factorisation)**: splits the patient-by-code table into a few
  "bundles" of codes that occur together, plus how much of each bundle each patient has. Bundles
  can only add up, never subtract, so they read as groups of codes.
- **k**: the number of bundles (NMF components) asked for.
- **Component / bundle**: one NMF group of codes. **Loading**: how strongly a code belongs to a bundle.
- **`argmax` group**: assigning each patient to the single bundle they have most of. It discards
  mixed membership.
- **SVD**: another way to compress the table to a few numbers per patient; used for distances,
  clustering and the silhouette. Its components cannot be read as code groups.
- **Cosine similarity**: how similar two vectors' directions are (1 = same). Used to compare
  patients and to check whether a code bundle comes back after refitting.
- **Silhouette**: how much closer each patient is to their own group than to the nearest other
  group (higher is better separated).
- **Bootstrap / refit**: redraw patients with replacement, fit again, and see what changes.
- **ARI (adjusted Rand index)**: how much two groupings of the same patients agree (1 = identical,
  about 0 = chance). Cut-offs here: 0.75 solid, 0.60 suggestive.
- **Held-out set**: patients not used to fit the model, used to score it fairly.
- **Split seed**: the random seed that decides which patients are training and which held-out.
- **Sparse matrix**: a way to store a mostly-zero table keeping only the non-zero entries.
- **Weak label**: a rough label built from nearby evidence (for example anxiety diagnoses or
  SSRIs for "psych"; troponin or stress tests for "cardiac"), used because there is no true answer.
- **RUW**: the underwriting review team that currently manually reviews every `dx_9487` case.
- **`dx_9487`**: the IRIX diagnosis code for atypical chest pain, which maps to five nonspecific
  ICD-10 codes (R07.89, R07.9, R07.2, R07.8, R07.82).
