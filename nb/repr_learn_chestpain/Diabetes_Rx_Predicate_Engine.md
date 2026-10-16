# Diabetes Rx Predicate Engine

*Working Draft — September 2026*

---

## Overview

This document describes the design of the diabetes prescription predicate engine for LGA Term Life underwriting. The engine identifies the diabetes treatment regimen of an applicant. It separates diabetes-indicated drug use from obesity-indicated drug use. It uses prescription patterns, brand names, dose, and days supply drawn from the Ethos clinical database. The predicate set is scoped to the 28 glycemic agents that are prevalent in diabetic-related RUWs.

---

## Predicates and Composites

This section defines the building blocks of the diabetes prescription predicate engine. It covers the atomic predicates and the composites that combine them into named clinical patterns. This section contains no underwriting logic. It is intended for clinical and medical review to validate that the definitions agree with established treatment protocols.

### Atomic Predicates

A predicate answers one question about the prescription history of an applicant. It returns true or false. Atomic predicates check directly against raw data attributes. Ingredients, brand, dose, days supply, and start date are attributes of one fill record.

**Metformin present.** The applicant has at least one metformin fill. Metformin has one approved indication: glycemic control in adult Type 2 diabetes. All other metformin use is off-label. Presence alone does not identify the indication.

`metformin_present = drug IS metformin`

**Metformin at maximum dose.** The applicant has a metformin fill at 2000 mg per day or more. Glycemic benefit stops to increase above this dose. A fill at this dose shows that metformin alone gives no further benefit.

`metformin_max_dose = drug IS metformin AND dose >= 2000 mg/day`

**GLP-1 diabetes brand present.** The applicant has at least one fill of a GLP-1 receptor agonist or a dual GIP/GLP-1 receptor agonist under a diabetes-indicated brand name. The manufacturers sell the same ingredient under different brand names for diabetes and for obesity. The brand name identifies the indication.

`glp1_diabetes_brand_present = drug IS IN (Ozempic, Rybelsus, Mounjaro, Victoza, Trulicity, Byetta, Bydureon, Adlyxin)`

**GLP-1 obesity brand present.** The applicant has at least one fill of a GLP-1 receptor agonist or a dual GIP/GLP-1 receptor agonist under an obesity-indicated brand name. These fills are weight-management therapy. They are not diabetes therapy.

`glp1_obesity_brand_present = drug IS IN (Wegovy, Zepbound, Saxenda)`

**GLP-1 brand unresolved.** The applicant has a GLP-1 receptor agonist fill with no brand name in the drug record. The engine cannot identify the indication of this fill. The engine reports this state. It does not apply a default indication.

`glp1_brand_unresolved = drug IS GLP-1 receptor agonist AND brand IS NULL`

**GLP-1 titration dose only.** Every GLP-1 fill of the applicant is at the starting dose of that ingredient. The starting dose is a titration step. It does not give glycemic control. An applicant at this dose did not reach a treatment dose.

`glp1_titration_dose_only = (drug IS semaglutide AND max dose = 0.25 mg/week) OR (drug IS tirzepatide AND max dose = 2.5 mg/week)`

**SGLT2 inhibitor present.** The applicant has at least one SGLT2 inhibitor fill. Empagliflozin and dapagliflozin also have heart failure and kidney disease indications. Canagliflozin has a kidney indication that applies to diabetic kidney disease.

`sglt2_inhibitor_present = drug IS IN (empagliflozin, dapagliflozin, canagliflozin)`

**Sulfonylurea present.** The applicant has at least one sulfonylurea fill. Sulfonylureas cause more hypoglycemia than the other oral classes.

`sulfonylurea_present = drug IS IN (glipizide, glimepiride, glyburide)`

**DPP-4 inhibitor present.** The applicant has at least one DPP-4 inhibitor fill. This class has intermediate glucose-lowering effect. It has no established cardiovascular benefit.

`dpp4_inhibitor_present = drug IS IN (sitagliptin, linagliptin)`

**Pioglitazone present.** The applicant has at least one pioglitazone fill. Pioglitazone increases heart failure risk and fracture risk.

`pioglitazone_present = drug IS pioglitazone`

**Other oral agent present.** The applicant has at least one fill of a rarely used oral glycemic agent. These agents occur in fewer than five policies each. The engine counts them as oral classes. No composite depends on one of them alone.

`other_oral_agent_present = drug IS IN (acarbose, bromocriptine, repaglinide)`

**Insulin present.** The applicant has at least one insulin fill of any formulation.

`insulin_present = drug IS insulin (any formulation)`

**Basal insulin present.** The applicant has at least one long-acting or intermediate-acting insulin fill. These formulations give background glycemic control.

`basal_insulin_present = drug IS IN (insulin glargine, insulin detemir, insulin degludec, insulin isophane)`

**Bolus insulin present.** The applicant has at least one rapid-acting or short-acting insulin fill. These formulations give mealtime and correction doses.

`bolus_insulin_present = drug IS IN (insulin lispro, insulin aspart, insulin regular)`

**Premixed insulin present.** The applicant has at least one premixed insulin fill. A premixed product contains a basal component and a bolus component. The engine does not count it as bolus insulin alone.

`premixed_insulin_present = drug IS insulin aspart protamine`

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in four groups: indication resolution, the regimen ladder, treatment transitions, and adherence.

#### Indication resolution

These composites remove fills that are not diabetes therapy. Every composite in this group removes a fill. None adds a fill.

**Non-GLP-1 glycemic agent present.** The applicant has at least one glycemic agent that is not a GLP-1 receptor agonist. This composite supports the obesity-only test below.

`non_glp1_glycemic_agent_present = metformin_present OR sulfonylurea_present OR sglt2_inhibitor_present OR dpp4_inhibitor_present OR pioglitazone_present OR other_oral_agent_present OR insulin_present`

**GLP-1 obesity use only.** The applicant has an obesity-branded GLP-1 fill, no diabetes-branded GLP-1 fill, and no other glycemic agent. This applicant has no prescription evidence of diabetes therapy.

`composite_glp1_obesity_only = glp1_obesity_brand_present AND NOT glp1_diabetes_brand_present AND NOT non_glp1_glycemic_agent_present`

**GLP-1 switch from obesity to diabetes.** An obesity-branded fill ends. A diabetes-branded fill starts after that end date. The two fills do not overlap. This sequence shows weight-management therapy that changed to diabetes therapy.

`composite_glp1_switch_obesity_to_diabetes = glp1_obesity_brand_present AND glp1_diabetes_brand_present AND first_diabetes_brand_start_date > last_obesity_brand_end_date`

**GLP-1 switch from diabetes to obesity.** A diabetes-branded fill ends. An obesity-branded fill starts after that end date. The two fills do not overlap. The ingredient does not change in this sequence. A formulary change can cause it.

`composite_glp1_switch_diabetes_to_obesity = glp1_diabetes_brand_present AND glp1_obesity_brand_present AND first_obesity_brand_start_date > last_diabetes_brand_end_date`

**GLP-1 concurrent brands.** A diabetes-branded fill and an obesity-branded fill cover the same day. Both fills contain the same ingredient. This pattern is duplicate therapy. A refill that occurs before the previous supply ends also causes it. The engine applies a 30-day grace period to separate the two causes.

`composite_glp1_concurrent_brands = glp1_diabetes_brand_present AND glp1_obesity_brand_present AND overlap_days > 30`

#### Regimen ladder

These composites identify the treatment regimen. They are mutually exclusive.

**Oral class count.** The number of different oral glycemic classes in the prescription history of the applicant.

`oral_class_count = count of distinct classes IN (metformin, sulfonylurea, DPP-4 inhibitor, SGLT2 inhibitor, pioglitazone, other oral agent) with at least one fill`

**No glycemic therapy.** The applicant has no glycemic agent fill. Obesity-branded GLP-1 fills do not count.

`composite_no_glycemic_therapy = NOT non_glp1_glycemic_agent_present AND NOT glp1_diabetes_brand_present`

**Oral monotherapy.** The applicant has one oral glycemic class, no insulin, and no diabetes-branded GLP-1.

`composite_oral_monotherapy = oral_class_count = 1 AND NOT insulin_present AND NOT glp1_diabetes_brand_present`

**Oral combination therapy.** The applicant has two or more oral glycemic classes, no insulin, and no diabetes-branded GLP-1.

`composite_oral_combination = oral_class_count >= 2 AND NOT insulin_present AND NOT glp1_diabetes_brand_present`

**Oral combination therapy with GLP-1.** The applicant has two or more oral glycemic classes, no insulin, and a diabetes-branded GLP-1.

`composite_oral_combination = oral_class_count >= 2 AND NOT insulin_present AND glp1_diabetes_brand_present`

**Injectable non-insulin therapy.** The applicant has a diabetes-branded GLP-1 fill and no insulin fill.

`composite_injectable_noninsulin = glp1_diabetes_brand_present AND NOT insulin_present`

**Basal insulin therapy.** The applicant has basal insulin and no bolus insulin.

`composite_insulin_basal_only = basal_insulin_present AND NOT bolus_insulin_present AND NOT premixed_insulin_present`

**Basal insulin & GLP-1 therapy.** The applicant has basal insulin, no bolus insulin, and GLP-1 Therapy.

`composite_insulin_basal_only = basal_insulin_present AND NOT bolus_insulin_present AND NOT premixed_insulin_present AND glp1_diabetes_brand_present`

**Basal-bolus insulin therapy.** The applicant has basal insulin and bolus insulin, or a premixed insulin. This is the most intensive insulin regimen.

`composite_insulin_basal_bolus = (basal_insulin_present AND bolus_insulin_present) OR premixed_insulin_present`

**Insulin formulation unresolved.** The applicant has an insulin fill. The engine cannot assign the fill to basal, bolus, or premixed. The engine reports this state.

`composite_insulin_formulation_unresolved = insulin_present AND NOT basal_insulin_present AND NOT bolus_insulin_present AND NOT premixed_insulin_present`

**Hypoglycemia risk regimen.** The regimen of the applicant contains a sulfonylurea or insulin. These agents cause hypoglycemia. The other classes in this engine do not.

`composite_hypoglycemia_risk_regimen = sulfonylurea_present OR insulin_present`

#### Treatment transitions

These composites use fill start dates and days supply. A fill covers the days from its start date to its start date plus its days supply.

**Metformin to GLP-1 augmentation.** A diabetes-branded GLP-1 fill starts while a metformin fill still covers the applicant. The applicant continues metformin and adds a second agent.

`composite_metformin_to_glp1_augmentation = metformin_present AND glp1_diabetes_brand_present AND glp1_start_date <= metformin_end_date AND glp1_start_date >= metformin_start_date`

**Metformin to GLP-1 switch.** A diabetes-branded GLP-1 fill starts after the last metformin fill ends. The applicant stops metformin. Intolerance or a change of strategy causes this pattern.

`composite_metformin_to_glp1_switch = metformin_present AND glp1_diabetes_brand_present AND glp1_start_date > last_metformin_end_date`

**Metformin at maximum dose before escalation.** The applicant reaches the maximum metformin dose before a GLP-1 starts. This sequence shows that metformin alone did not reach the treatment goal.

`composite_metformin_maxed_before_escalation = metformin_max_dose AND (composite_metformin_to_glp1_augmentation OR composite_metformin_to_glp1_switch)`

**Insulin initiation.** An insulin fill starts after a non-insulin glycemic agent. The applicant has no earlier insulin fill. This is the clearest escalation signal in prescription data.

`composite_insulin_initiation = insulin_present AND non_glp1_glycemic_agent_present AND first_insulin_start_date > first_non_insulin_start_date`

**Hypoglycemia risk reduction switch.** A DPP-4 inhibitor, SGLT2 inhibitor, or diabetes-branded GLP-1 starts after a sulfonylurea or insulin ends. The two fills do not overlap. The applicant moves to an agent with lower hypoglycemia risk.

`composite_hypoglycemia_risk_reduction_switch = (dpp4_inhibitor_present OR sglt2_inhibitor_present OR glp1_diabetes_brand_present) AND (sulfonylurea_present OR insulin_present) AND new_agent_start_date > hypoglycemia_agent_end_date`

**Discordant DPP-4 and GLP-1 combination.** A DPP-4 inhibitor fill and a GLP-1 fill cover the same day. This combination gives no additional glucose-lowering benefit.

`composite_discordant_dpp4_glp1 = dpp4_inhibitor_present AND glp1_diabetes_brand_present AND overlap_days >= 1`

**Glycemic therapy discontinued.** The applicant has no glycemic agent fill for 180 days or more at the end of the observation window. The applicant has at least one earlier fill. This pattern is not remission. Non-adherence and loss of coverage cause the same pattern.

`composite_glycemic_therapy_discontinued = (non_glp1_glycemic_agent_present OR glp1_diabetes_brand_present) AND days_since_last_fill_coverage_end >= 180`

**Insulin therapy discontinued.** The applicant has no insulin fills for 180 days or more at the end of the observation window. The applicant has at least one earlier fill. This pattern is not remission. Non-adherence and loss of coverage cause the same pattern.

`composite_insulin_discontinued = insulin_present AND days_since_last_fill_coverage_end >= 180`

#### Adherence

Proportion of days covered (PDC) is the covered days divided by the days in the observation window.

**Oral agent adherence.** PDC across all oral glycemic fills. The threshold of 0.80 follows the CMS Part D Star Ratings specification for oral antihyperglycemic agents.

`composite_oral_pdc_high = PDC(oral glycemic agents) >= 0.80`

`composite_oral_pdc_low = PDC(oral glycemic agents) < 0.80`

**Insulin adherence.** PDC across all insulin fills. The CMS specification excludes insulin. This engine applies the same 0.80 threshold to insulin. Variable dosing and pen dispensing make insulin days supply less exact than oral days supply.

`composite_insulin_pdc_high = PDC(insulin) >= 0.80`

`composite_insulin_pdc_low = PDC(insulin) < 0.80`

**GLP-1 adherence.** PDC across diabetes-branded GLP-1 fills only. One weekly-dose fill usually covers 28 days. One missed fill therefore changes PDC more than one missed oral refill.

`composite_glp1_pdc_high = PDC(diabetes-branded GLP-1) >= 0.80`

`composite_glp1_pdc_low = PDC(diabetes-branded GLP-1) < 0.80`

**Glycemic adherence.** PDC across the agent types that the applicant holds. This composite gives one adherence result for every regimen type. PDC has no value for an applicant with no glycemic fill. A missing value is not a low value.

`composite_glycemic_pdc_high = composite_oral_pdc_high OR composite_insulin_pdc_high OR composite_glp1_pdc_high`

`composite_glycemic_pdc_low = composite_oral_pdc_low OR composite_insulin_pdc_low OR composite_glp1_pdc_low`

---

## Population Coverage

Counts come from a 1,908-policy cohort extracted on 2026-09-15. Percentages are policy-level and distinct. The extract carries ingredient and brand. It does not carry dates or dose, so the transition composites and the adherence composites have no measured rate yet.

### Cohort composition

| Guideline node | Policies | Metformin | Any GLP-1 | Insulin |
| :---- | ----: | ----: | ----: | ----: |
| DIABETES\_TYPE2\_SUPPLEMENTAL\_GUIDELINE\_SUBGROUP | 1,344 | 74% | 44% | 5% |
| PRE\_DIABETES\_GUIDELINE | 358 | 24% | 18% | 3% |
| PRE\_DIABETES\_SUPPLEMENTAL\_GUIDELINE\_SUBGROUP | 147 | 11% | 12% | 1% |
| DIABETES\_TYPE1\_SUPPLEMENTAL\_GUIDELINE\_SUBGROUP | 50 | 42% | 30% | 80% |
| DIABETES\_TYPE2\_GUIDELINE | 35 | 69% | 51% | 11% |
| GESTATIONAL\_DIABETES\_GUIDELINE | 3 | 67% | 67% | 33% |

Unmapped rows are 0.5% of the extract. Rows with a blank ingredient are 1.1%.

### Predicate rates

| Ingredient | Class | Policies | % cohort |
| :---- | :---- | ----: | ----: |
| metformin | biguanide | 1,122 | 58.8% |
| tirzepatide | dual GIP/GLP-1 | 435 | 22.8% |
| semaglutide | GLP-1 | 424 | 22.2% |
| empagliflozin | SGLT2 | 71 | 3.7% |
| dulaglutide | GLP-1 | 65 | 3.4% |
| liraglutide | GLP-1 | 55 | 2.9% |
| insulin glargine | basal | 49 | 2.6% |
| insulin isophane | basal | 44 | 2.3% |
| glipizide | sulfonylurea | 39 | 2.0% |
| dapagliflozin | SGLT2 | 39 | 2.0% |
| insulin lispro | bolus | 29 | 1.5% |
| pioglitazone | TZD | 25 | 1.3% |
| insulin aspart | bolus | 24 | 1.3% |
| glimepiride | sulfonylurea | 21 | 1.1% |
| sitagliptin | DPP-4 | 19 | 1.0% |
| glyburide | sulfonylurea | 15 | 0.8% |
| insulin detemir | basal | 13 | 0.7% |
| insulin regular | bolus | 8 | 0.4% |
| acarbose | other oral | 8 | 0.4% |
| insulin degludec | basal | 8 | 0.4% |
| canagliflozin | SGLT2 | 7 | 0.4% |
| exenatide | GLP-1 | 4 | 0.2% |
| lixisenatide | GLP-1 | 3 | 0.2% |
| linagliptin | DPP-4 | 2 | 0.1% |
| repaglinide | meglitinide | 2 | 0.1% |
| bromocriptine | other oral | 2 | 0.1% |

At least one glycemic agent occurs in 1,364 policies (71.5%). No glycemic agent occurs in 544 policies (28.5%).

### Brand resolution rates

| Ingredient | Diabetes brand | Rows | Obesity brand | Rows |
| :---- | :---- | ----: | :---- | ----: |
| semaglutide | Ozempic, Rybelsus | 638 | Wegovy | 412 |
| tirzepatide | Mounjaro | 888 | Zepbound | 595 |
| liraglutide | Victoza | 22 | Saxenda | 33 |
| dulaglutide | Trulicity | 124 | — | — |

Diabetes brands only occur in 406 policies (21.3%). Obesity brands only occur in 159 policies (8.3%). Both brand types occur in 132 policies (6.9%). Six liraglutide rows carry no brand.

Of the 159 obesity-only policies, 62 have no other glycemic agent. The remaining 97 have another glycemic agent. 55 of the 159 are in a prediabetes node.

### Regimen ladder rates

| Composite | Policies | % cohort |
| :---- | ----: | ----: |
| composite\_no\_glycemic\_therapy | 606 | 31.8% |
| composite\_oral\_monotherapy | 634 | 33.2% |
| composite\_oral\_combination | 58 | 3.0% |
| composite\_injectable\_noninsulin | 506 | 26.5% |
| composite\_insulin\_basal\_only | 50 | 2.6% |
| composite\_insulin\_basal\_bolus | 47 | 2.5% |
| composite\_insulin\_formulation\_unresolved | 7 | 0.4% |

Oral monotherapy and injectable non-insulin therapy hold 59.7% of the cohort. Oral combination therapy holds 3.0%. This cohort therefore moves from metformin to a GLP-1 receptor agonist. It does not move through oral combination therapy first.

---

## References

- American Diabetes Association Professional Practice Committee. *9\. Pharmacologic Approaches to Glycemic Treatment: Standards of Care in Diabetes—2026.* Diabetes Care 2026;49(Suppl. 1):S183–S215. doi:10.2337/dc26-S009.  
- American Diabetes Association Professional Practice Committee. *6\. Glycemic Goals, Hypoglycemia, and Hyperglycemic Crises: Standards of Care in Diabetes—2026.* Diabetes Care 2026;49(Suppl. 1):S132–S149. doi:10.2337/dc26-S006.  
- FDA-approved product labeling via DailyMed (NIH) for metformin, semaglutide, tirzepatide, liraglutide, dulaglutide.  
- PQA and CMS Part D Star Ratings adherence measure specification, oral antihyperglycemic class.

