# Chest pain: three NMF runs compared (139,416 patients, same events)

**Summary**
1. We ran the same patients through three NMF bundle runs: full k=5 and full k=8 (our codeset, concept codes) and AHA k=8 (2021 guideline codeset, grouped codes).
2. AHA k=8 is the most stable (re-run score 0.88, vs 0.77 for k=5 and 0.71 for full k=8); full k=8 is unstable, do not use.
3. All three find the same same-day ED bundle (troponin, ECG, chest X-ray, IV drugs) and the same background bundles; none finds a psych bundle.
4. Grouping codes matters more than which codeset: AHA k=8 matches the older grouped-code run (agreement 0.91), full k=8 matches neither; only the ED bundle carries across runs (91% of AHA's ED patients are in k=5's, 58% in k=8's).
5. Next: AHA k=8 as working reference, k=5 as fallback; UW to confirm "Manual RUW = ED bundle", then rebuild the flag rule and literature ratings on AHA c3. Nothing is validated against outcomes.

| | **Full k=5** (our codeset, concept codes) | **Full k=8** (our codeset, concept codes) | **AHA k=8** (guideline codeset, grouped codes) |
|---|---|---|---|
| Bundles found | 5 | 8 | 8 |
| Re-run stability (0–1; ≥0.75 solid) | 0.77 | **0.71** | **0.88** |
| Weakest bundle | none | peri-procedural / sedation (fragile) | none |
| Pattern rows: Solid / Suggestive / Unstable | 6 / 3 / 6 of 15 | 11 / 3 / 10 of 24 | 11 / 7 / 6 of 24 |
| ED bundle (patients) | 25,953 (18.6%) | 20,392 (14.6%) | 17,250 (12.4%) |
| Troponin / chest X-ray in ED bundle | 77% / 66% | 85% / 66% | 81% / 86% |
| Top ED pattern (in bundle vs rest) | chest pain → X-ray → troponin: 48% vs 16% (2.9×) | chest pain → X-ray → ECG → troponin: 48% vs 14% (3.3×) | chest pain → X-ray → troponin → metabolic panel: 59% vs 24% (2.4×) |
| Order shown by dates | no, same-day | no, same-day | no, same-day |
| Psych evidence before troponin (ED bundle) | 53% | 48% | 53% |
| Events with a clinical tag | 9% | 9% | 16% |
| Code shown per entity | yes | yes | no (grouped tags); member list in `token_members_k8_chestpain_AHA.csv` and final-table columns Q–R once the member-table cell is run |

**All three agree**
- One ED bundle: troponin, ECG, chest X-ray, IV drugs, same day. Order of steps is a same-day tie-break, not shown by dates.
- Same background bundles every time: outpatient check-up, women's health, physical therapy, acute-illness prescriptions.
- No anxiety/psych bundle. Psych evidence precedes troponin in 57% of patients with both, in every run.

**Where they differ**
- Granularity: k=5 keeps one 39% outpatient bundle; both k=8 runs split out nutrition/endocrine labs and acute respiratory infection. Each also has a GI bundle, but different: AHA = GI work-up + cancer screening; full k=8 = sedation / endoscopy drugs.
- ED bundle membership is not the same: 91% of AHA's ED patients are in k=5's; only 58% are in k=8's.
- AHA ED bundle is the most cardiac: D-dimer, PE, TEE, BNP, V/Q scan load there. ECG is no longer a defining code (46% of ECG loads on the outpatient bundle).
- Full k=8 ED bundle is broader (CBC, metabolic panels, D-dimer, magnesium).
- Token level drives structure more than codeset content: AHA k=8 matches the older Day 1 k=8 run (v1 codeset, grouped codes) almost exactly; full k=8 (concept codes) matches neither (agreement 0.46 vs 0.46).

**Where patients go** (same 139,416 patients; band width = patients; share = % of the AHA bundle)

![AHA k=8 to full k=8](sankey_AHA_k8_vs_full_k8.png)
![AHA k=8 to full k=5](sankey_AHA_k8_vs_full_k5.png)

- AHA → full k=8 (agreement 0.46): respiratory, women's health, nutrition/endocrine and prescriptions carry over (75–82%). The ED bundle keeps 58% (10,017 of 17,250); 24% goes to full's GI / peri-procedural bundle. AHA outpatient (83%) and GI + cancer screening (64%) both land in full's outpatient bundle.
- AHA → full k=5 (agreement 0.40): the ED bundle is the one clean match, 91% (15,652). Full's outpatient bundle (39% of patients) absorbs 93% of AHA outpatient, 61% of GI + cancer screening and 54% of nutrition/endocrine.
- No k=5 counterpart for AHA's respiratory bundle (36% to outpatient, 24% to prescriptions) or nutrition/endocrine (54% outpatient, 27% women's health).
- Reading: the ED bundle is the only structure all runs share; every other difference is how finely the background care is split.

**Watch-outs**
- Full k=8 is unstable: 7 of 10 resamples score 0.66 or lower. Do not use.
- AHA: grouped tags have no single code (member list: notebook section 5, run it before reading entities as codes); chronic PPI refills show up as a pattern; "methylprednisolone → chest pain → ECG" (4.3×) is a hypothesis only.
- Bundles describe care delivered, not diagnosis. Nothing is validated against outcomes.

**Recommendation (draft)**
- Working reference: **AHA k=8** (most stable, cleanest ED bundle). Keep k=5 as the conservative fallback.
- Before adopting: UW to confirm "Manual RUW = ED bundle"; rebuild the flag rule and literature ratings on AHA c3 (they are built on k=5 c0); clinician review of patterns.

*Sources:* `nmf_k5_chestpain_full.npz`, `nmf_k8_chestpain_full_k8.npz`, `nmf_k8_chestpain_AHA.npz`; final tables `final_table_chestpain_k5_full.xlsx`, `..._k8_full_k8.xlsx`, `..._k8_AHA.xlsx`; notebooks `Chestpain_NMF_PrefixSpan_full`, `..._full_k8`, `..._AHA`. Stability = bootstrap agreement of bundle assignments (10 resamples). Flow diagrams: `sankey_runs.py`.
