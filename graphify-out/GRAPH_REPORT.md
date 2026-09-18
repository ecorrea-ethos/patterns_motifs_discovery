# Graph Report - ethos_foundation_llm  (2026-09-15)

## Corpus Check
- 222 files · ~119,263 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1526 nodes · 2494 edges · 146 communities (91 shown, 49 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 270 edges (avg confidence: 0.85)
- Token cost: 988,950 input · 0 output

## Community Hubs (Navigation)
- Transformer
- Femr Docs
- Utils New
- Shahlab Secure Config
- Flat Tokenizer
- Labelers Core
- Hf Ehr Docs
- Processor
- Test CodeLabelers
- Tokenizers Utils
- Scripts Run
- Featurizers Core
- Starr Eda
- Dataset Stats Utils
- Featurizers Utils
- Omop
- Val Ppl
- Hierarchical Tokenizer
- Test TimeHorizonEventLabeler
- Test Featurizers
- Stanford
- Gpt
- Create Cookbook
- Hf Ehr Utils
- Featurizers
- Generate Labels
- Ontology
- Hf Ehr Config
- Base
- Tasks
- Test Batch Creator
- Hf Ehr Config
- Tokenization
- Create Desc
- Tokenization
- Parallel Gpt Clmbr K
- Dataset Statistics
- Hyena
- Featurizers
- Featurizers
- Hf Test
- V8 Alltokens
- Bert
- Carina Config
- Tasks
- Stanford
- Hf Ehr Config
- Test Transforms
- Ehrshot
- Tokenization
- Datasets
- Reloggers
- Hf Ehr Utils
- Samplers
- Tokenization
- Ehrshot
- Loaders
- Tasks
- Tokenization
- Based
- Test Survival Calculator
- Tokenization
- T5
- Hf Upload
- Samplers
- Ehrshot Events Cdf Train
- Featurizers Core
- Omop
- Tasks
- Ontology
- Llama
- Mamba
- Femr Test Tools
- Hyena Large
- Tokenization
- Ehrshot Events Cdf Val
- Based Base
- Omop
- Rmsnorm
- Hierarchical Tokenizer
- Xformers
- Splits
- Test Ontology
- Download Bigquery
- Fsdp
- Base
- Ehrshot Events Cdf Test
- Ehrshot Tokens Cdf Test
- Main
- Test Checkpoints
- Main
- Test TimeHorizonEventLabeler
- Gpt2 Hazyresearch LoCoV1 Documents Test
- Ehrshot Att V Non Att
- Tokenizers Utils
- Val Stats Irr
- Hf Ehr Config
- Avg Brier Across Metrics
- Meds Dev 1
- Meds Dev 2sh
- Parallel 512
- Parallel Based
- Parallel Bert
- Parallel Gpt
- Parallel Large
- Parallel Llama
- Parallel Mamba
- Val Ppl
- Val Ppl Wikitext
- Post Etl Pipelines Init
- Llama Base
- Data Docs
- Gen Dataset Stats
- Train Seq Lengths
- Bucket By Metrics
- Calc Stratification Metrics
- Debug
- Split Meds Dataset
- Ehrshot
- Debug
- Tokenizers Docs
- Pyproject
- .pre Commit Config
- .pre Commit Config
- .pre Commit Config
- .pre Commit Config
- .pre Commit Config
- Mamba Large
- Mamba Medium
- Mamba Small
- Mamba Tiny
- Mamba Xlarge
- T5 Base
- Data Docs
- Data Docs
- Ehrshot Tokens Cdf Train
- Tokenizers Docs
- Thinking
- Requirements
- Requirements

## God Nodes (most connected - your core abstractions)
1. `TimeHorizon` - 37 edges
2. `Event` - 37 edges
3. `BaseModel` - 33 edges
4. `FEMRDataset` - 29 edges
5. `Ontology` - 26 edges
6. `BaseTokenizer` - 24 edges
7. `main()` - 24 edges
8. `CLMBRTokenizer` - 23 edges
9. `CountFeaturizer` - 22 edges
10. `Label` - 20 edges

## Surprising Connections (you probably didn't know these)
- `hf_ehr repository (som-shahlab/hf_ehr)` --shares_data_with--> `Main Hydra training config (config.yaml)`  [AMBIGUOUS]
  femr/README.md → hf_ehr/hf_ehr/configs/config.yaml
- `MIMIC-4 Dataset (eval usage)` --semantically_similar_to--> `MIMIC-IV Demo Dataset`  [INFERRED] [semantically similar]
  hf_ehr/hf_ehr/scripts/eval/README.md → MEDS_ML4H_2025_Tutorial/README.md
- `meds-etl==0.3.11` --semantically_similar_to--> `MIMIC-IV Demo Dataset`  [INFERRED] [semantically similar]
  requirements.txt → MEDS_ML4H_2025_Tutorial/README.md
- `CLMBR Tokenizer Config (default)` --references--> `CLMBRTokenizer`  [EXTRACTED]
  hf_ehr/hf_ehr/configs/tokenizer/clmbr.yaml → hf_ehr/hf_ehr/data/tokenization.py
- `MIMIC-4 FEMR data config` --shares_data_with--> `FEMR (Framework for Electronic Medical Records)`  [INFERRED]
  hf_ehr/hf_ehr/configs/data/mimic4.yaml → femr/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hydra Architecture Config Group (@package _global_)** — hf_ehr_hf_ehr_configs_config_config, hf_ehr_hf_ehr_configs_architecture_based_based_config, hf_ehr_hf_ehr_configs_architecture_bert_bert_config, hf_ehr_hf_ehr_configs_architecture_gpt2_gpt2_config, hf_ehr_hf_ehr_configs_architecture_hyena_hyena_config, hf_ehr_hf_ehr_configs_architecture_llama_llama_config, hf_ehr_hf_ehr_configs_architecture_mamba_mamba_config, hf_ehr_hf_ehr_configs_architecture_t5_t5_config [INFERRED 0.85]
- **Hydra Data Config Group (@package _global_)** — hf_ehr_hf_ehr_configs_config_config, hf_ehr_hf_ehr_configs_data_meds_dev_meds_dev_config, hf_ehr_hf_ehr_configs_data_meds_mimic4_demo_meds_mimic4_demo_config, hf_ehr_hf_ehr_configs_data_mimic4_mimic4_config, hf_ehr_hf_ehr_configs_data_truven_debug_truven_debug_config, hf_ehr_hf_ehr_configs_data_truven_truven_config [INFERRED 0.85]
- **FEMR CI/CD and Code-Quality Pipeline** — femr__github_workflows_tests_test_job, femr__github_workflows_build_build_job, femr__pre_commit_config_black_hook, femr__pre_commit_config_flake8_hook, femr__pre_commit_config_mypy_hook, femr__pre_commit_config_isort_hook [INFERRED 0.75]
- **V8 FEMR Data Config Family (shared extract path)** — hf_ehr_hf_ehr_configs_data_v8, hf_ehr_hf_ehr_configs_data_v8_alltokens, hf_ehr_hf_ehr_configs_data_v8_debug [INFERRED 0.85]
- **V9 FEMR Data Config Family** — hf_ehr_hf_ehr_configs_data_v9, hf_ehr_hf_ehr_configs_data_v9_alltokens, hf_ehr_hf_ehr_configs_data_v9_lite [INFERRED 0.75]
- **Based Hybrid Mixer Architecture (BaseConv + LinearAttention/TaylorExp)** — hf_ehr_hf_ehr_configs_model_based_base, based_models_mixers_convolution_baseconv, based_models_mixers_linear_attention_linearattention, based_models_mixers_linear_attention_taylorexp [EXTRACTED 1.00]
- **MEDS Data Standard Ecosystem** — hf_ehr_readme_meds_standard, meds_ml4h_2025_tutorial_readme_meds_ml4h_tutorial, requirements_meds_etl_dependency [INFERRED 0.75]

## Communities (146 total, 49 thin omitted)

### Community 0 - "Transformer"
Cohesion: 0.06
Nodes (28): device, FEMRModelConfig, FEMRTaskConfig, FEMRTransformerConfig, Any, Defined a configuration for a FEMR Transformer. Arguments: vocab_size: The…, A generic FEMR task definition. This holds state used for initalizing a…, A model config is defined as the combination of a transformer config and a task… (+20 more)

### Community 1 - "Femr Docs"
Cohesion: 0.05
Nodes (45): Hugging Face `datasets` library (env-info boilerplate), HAI article: How foundation models can advance AI in healthcare, HAI article: Shaky Foundations of foundation models in healthcare, hazyresearch/based-360m (HF model), bert-base-uncased (HF model), gpt2 (HF model), LongSafari/hyenadna-large-1m-seqlen-hf (HF model), meta-llama/Meta-Llama-3.1-8B-Instruct (HF model) (+37 more)

### Community 2 - "Utils New"
Cohesion: 0.07
Nodes (34): FEMRTokenizer, FEMRDataset, ndarray, Dataset that returns patients in a FEMR extract. dataset[idx] = a specific…, Return patient ids for this split, Return all event codes for this patient at `idx` in `self.split`., Return patient ids for this split, Return all event codes for this patient at `idx` in `self.split`. (+26 more)

### Community 3 - "Shahlab Secure Config"
Cohesion: 0.04
Nodes (24): base_llama.sh script, base.sh script, HF_CACHE_DIR, HF_DATASETS_CACHE, HF_HOME, HUGGINGFACE_HUB_CACHE, config.sh script, TRANSFORMERS_CACHE (+16 more)

### Community 4 - "Flat Tokenizer"
Cohesion: 0.06
Nodes (22): agg_statistics(), convert_statistics_to_msgpack(), FlatTokenizer, map_statistics(), Any, PathLike, Subject, SubjectDatabase (+14 more)

### Community 5 - "Labelers Core"
Cohesion: 0.09
Nodes (24): compute_random_num(), _label_map_func(), Labeler, NLabelsPerSubjectLabeler, ABC, DataFrame, datetime, Labeler (+16 more)

### Community 6 - "Hf Ehr Docs"
Cohesion: 0.07
Nodes (33): FEMR Format Support, Irregularity Metric (std), Repetitiveness Metric (rr_1), EHRSHOT Stratification Experiment, Timeline Lengths Metric (n_tokens), EHRSHOT Model Evaluation Notebooks, ehrshot.sh (few/zero-shot eval script), MIMIC-4 Dataset (eval usage) (+25 more)

### Community 7 - "Processor"
Cohesion: 0.09
Nodes (19): _add_dimension(), _batch_generator(), BatchCreator, FEMRBatchProcessor, map_preliminary_batch_stats(), Any, ndarray, Subject (+11 more)

### Community 8 - "Test CodeLabelers"
Cohesion: 0.13
Nodes (21): _assert_labvalue_constructor_correct(), _create_specific_labvalue_labeler(), DummyLabeler_OMOPConcept, DummyOntology_Base, DummyOntology_Lupus, DummyOntology_Mortality, DummyOntology_OMOPConcept, DummyOntology_OMOPConcept_Specific (+13 more)

### Community 9 - "Tokenizers Utils"
Cohesion: 0.11
Nodes (28): CountOccurrencesTCEStat, Count of the # of times a token occurs in a dataset split., add_categorical_codes(), add_occurrence_count_to_codes(), calc_categorical_codes(), calc_code_2_occurrence_count(), calc_code_2_unique_patient_count(), calc_numerical_range_codes() (+20 more)

### Community 10 - "Scripts Run"
Cohesion: 0.11
Nodes (16): Callback, Rewrite paths for Carina partitions to use local-scratch directories., rewrite_paths_for_carina_from_config(), GradNormCallback, main(), MetricBasedCheckpoint, DictConfig, main (+8 more)

### Community 11 - "Featurizers Core"
Cohesion: 0.11
Nodes (16): _features_map_func(), Featurizer, _preprocess_map_func(), ABC, Any, Subject, Core featurizer functionality, shared across Featurizers., A Featurizer takes a Subject and a list of Labels, then returns a row for each… (+8 more)

### Community 12 - "Starr Eda"
Cohesion: 0.13
Nodes (20): A module for generating labels on subject timelines., Buckets EHRSHOT patients by a specific stratification metric Usage: python3…, Calculates stratification metrics for each (patient, label) Usage: python3…, calc_inter_event_times(), calc_longest_repeated_substring(), calc_n_gram_count(), DataFrame, datetime (+12 more)

### Community 13 - "Dataset Stats Utils"
Cohesion: 0.14
Nodes (24): calc_code_2_count(), calc_code_2_unique_patient_count(), calc_parallelize(), calc_patient_2_sequence_length(), calc_patient_2_unique_sequence_length(), flatten_tokenized(), merge_code_2_count(), merge_code_2_unique_patient_count() (+16 more)

### Community 14 - "Featurizers Utils"
Cohesion: 0.13
Nodes (15): OnlineStatistics, Merge a list of online statistics., Initialize online statistics. `mean` accumulates the mean of the entire dataset…, Add an observation to the calculation using Welford's online algorithm. Taken…, Return the current mean., Return the current sample variance., Return the current standard devation., Merge two sets of online statistics using Chan's parallel algorithm. Taken… (+7 more)

### Community 15 - "Omop"
Cohesion: 0.12
Nodes (23): AKICodeLabeler, AnemiaCodeLabeler, HyperkalemiaCodeLabeler, HypoglycemiaCodeLabeler, HyponatremiaCodeLabeler, identity(), LupusCodeLabeler, move_datetime_to_end_of_day() (+15 more)

### Community 16 - "Val Ppl"
Cohesion: 0.12
Nodes (23): add_calcs_to_df(), calc_weighted_average(), eval(), get_path_to_output_dir(), load_config(), main(), map_datasource_to_femr_extract(), parse_args() (+15 more)

### Community 17 - "Hierarchical Tokenizer"
Cohesion: 0.12
Nodes (14): DataType, agg_statistics(), convert_statistics_to_msgpack(), entropy(), HierarchicalTokenizer, map_statistics(), Any, Subject (+6 more)

### Community 18 - "Test TimeHorizonEventLabeler"
Cohesion: 0.26
Nodes (18): EventsWithLabels, An interval of time. Mandatory `start`, optional `end`., TimeHorizon, Labeler, run_test_for_labeler(), DummyLabeler, Path, Dummy labeler that returns True if the event's `code` is in… (+10 more)

### Community 19 - "Test Featurizers"
Cohesion: 0.16
Nodes (15): FeaturizerList, FeaturizerList consists of a list of Featurizers that will be used to…, CodeLabeler, Apply a label based on 1+ outcome_codes' occurrence(s) over a fixed time…, Create a CodeLabeler, which labels events whose index in your Ontology is in…, _assert_featurized_subjects_structure(), Any, DataFrame (+7 more)

### Community 20 - "Stanford"
Cohesion: 0.14
Nodes (18): _apply_transformations(), femr_stanford_omop_fixer_program(), _get_stanford_transformations(), _is_visit_measurement(), MutableSubject, An ETL script for doing an end to end transform of Stanford data into a…, Flowsheets in STARR-OMOP have known timing bugs, making them unsuitable for use…, Get the list of current OMOP transformations. (+10 more)

### Community 21 - "Gpt"
Cohesion: 0.12
Nodes (16): GPT2Attention, apply_rotary_pos_emb(), fixed_pos_embedding(), GPTLanguageModel, Any, DictConfig, Tensor, # TODO: Implement loading of pretrained weights (+8 more)

### Community 22 - "Create Cookbook"
Cohesion: 0.15
Nodes (21): Given a path to a `tokenizer_config.json` file, saves the JSON config to disk., save_tokenizer_config_to_path(), check_add_categorical_codes(), check_add_numerical_range_codes(), check_add_occurrence_count_to_codes(), check_add_unique_codes(), check_remove_codes_belonging_to_vocabs(), main() (+13 more)

### Community 23 - "Hf Ehr Utils"
Cohesion: 0.13
Nodes (16): calculate_flops_per_token(), Returns FLOPs per token for model., # NOTE: Assumes `loss` has been scaled per-token already, convert_lab_value_to_token_from_quantiles(), get_lab_value_token_name(), _get_linear_schedule_with_warmup_lr_lambda(), get_most_recent_ckpt_from_output_dir(), hash_string_to_uuid() (+8 more)

### Community 24 - "Featurizers"
Cohesion: 0.13
Nodes (10): ColumnValue, NamedTuple, A value for a particular column `column` is the index for the column `value` is…, AgeFeaturizer, OnlineStatistics, Subject, Produces the (possibly normalized) age at each label timepoint., Args: is_normalize (bool, optional): If TRUE, then normalize a subject's age at… (+2 more)

### Community 25 - "Generate Labels"
Cohesion: 0.17
Nodes (11): Label, NamedTuple, _label_map_func(), Labeler, MIMICInpatientMortalityLabeler, MIMICLongAdmissionLabeler, Subject, SubjectDatabase (+3 more)

### Community 26 - "Ontology"
Cohesion: 0.14
Nodes (7): Subject, Ontology, Get a description of a code., Get the children for a given code., Get the parents for a given code., Get all children, including through the ontology., Create an Ontology from an Athena download and an optional meds Code Metadata…

### Community 27 - "Hf Ehr Config"
Cohesion: 0.16
Nodes (16): copy_file(), copy_resources_to_local(), CountPatientsTCEStat, load_tokenizer_config_and_metadata_from_path(), load_tokenizer_config_from_path(), PPLTCEStat, Any, Average perplexity of a token in a dataset split. (+8 more)

### Community 28 - "Base"
Cohesion: 0.13
Nodes (7): BaseModel, DictConfig, Restore each metric's state from the checkpoint., Base PyTorchLightning model with some common methods., Post-initialization method to be called by subclass., Sets Learning rate for different parameter groups., Save each metric's state in the checkpoint.

### Community 29 - "Tasks"
Cohesion: 0.13
Nodes (4): MOTORTask, Tensor, Add per-subject labels to the global task labels., Task

### Community 30 - "Test Batch Creator"
Cohesion: 0.20
Nodes (11): create_subjects_dataset(), SubjectDatabase, Creates a list of subjects, each with the same events contained in `events`, assert_two_batches_equal_third(), DummyTokenizer, timedelta, This asserts that batch1 + batch2 = batchs3, test_split_subjects_concat_no_task() (+3 more)

### Community 31 - "Hf Ehr Config"
Cohesion: 0.13
Nodes (12): CategoricalTCE, CodeTCE, NumericalRangeTCE, A vanilla code token. Examples: - LOINC/1234 - ICD10/1234 - SNOMED/1234, A token that represents a numerical range. Examples: - LOINC/1234 || mg/dL ||…, A token that represents a specific (set of) categorical values. Examples: -…, parse_args(), Namespace (+4 more)

### Community 32 - "Tokenization"
Cohesion: 0.18
Nodes (8): Event, Tensor, Provide default implementation where one Event => one token, Returns all events that DO get mapped to tokens, Returns all events that DO NOT get mapped to tokens, Tokenize a batch of patient timelines, where each timeline is a list of event…, Convert a list of events into a list of tokens, inserting ATT tokens based on…, Tokenize a batch of patient timelines, where each timeline is a list of event…

### Community 33 - "Create Desc"
Cohesion: 0.18
Nodes (14): MEDSDataset, Dataset that returns patients in a MEDS dataset (after it has been converted to…, check_add_unique_codes(), check_remove_codes_belonging_to_vocabs(), main(), parse_args(), Namespace, Creates a tokenizer config for the DescEmb tokenizer Usage: python… (+6 more)

### Community 34 - "Tokenization"
Cohesion: 0.17
Nodes (9): BaseTokenizer, is_metadata_equal(), Example path:…, Example path: /share/pi/nigam/mwornow/hf_ehr/cache/tokenizer_v8/versions/2021-…, Given a dataset and a range of indices, return the sequence length of each…, Fetch the sequence length of every patient in `dataset`, save to cache, and…, Return TRUE if `metadata1` EXACTLY EQUALS `metadata2`, Override the default `from_pretrained()` method to allow for custom tokenizer… (+1 more)

### Community 35 - "Parallel Gpt Clmbr K"
Cohesion: 0.12
Nodes (7): base.sh script, parallel_gpt_clmbr_k.sh script, parallel_hyena.sh script, mimic4.sh script, clmbr.sh script, cookbook.sh script, desc.sh script

### Community 36 - "Dataset Statistics"
Cohesion: 0.23
Nodes (15): compute_statistics(), create_age_box_plot(), create_age_race_distribution_plot(), create_race_sex_plot(), get_json_path(), log(), main(), DictConfig (+7 more)

### Community 37 - "Hyena"
Cohesion: 0.18
Nodes (10): AutoModelForCausalLM, CausalLMOutput, FloatTensor, hyena_forward(), HyenaLanguageModel, Any, DictConfig, Tensor (+2 more)

### Community 38 - "Featurizers"
Cohesion: 0.17
Nodes (10): Deque, exclusion_helper(), datetime, timedelta, Args: is_ontology_expansion (bool, optional): If TRUE, then do ontology…, ReservoirSampler, _reshuffle_count_time_bins(), get_subject_birthdate() (+2 more)

### Community 39 - "Featurizers"
Cohesion: 0.18
Nodes (5): CountFeaturizer, Any, Produces one column per each diagnosis code, procedure code, and prescription…, Some featurizers need to do some preprocessing in order to prepare for…, This encorperates data generated from generate_preprocess_data across the…

### Community 40 - "Hf Test"
Cohesion: 0.14
Nodes (10): CLMBR Tokenizer Config (118k vocab), CLMBR Tokenizer Config (16k vocab), CLMBR Tokenizer Config (64k vocab), CLMBR Tokenizer Config (8k vocab), CLMBR Tokenizer Config (96k vocab), CLMBR Tokenizer Config (nbins=0), CLMBR Tokenizer Config (nbins=5), CLMBRTokenizer (+2 more)

### Community 41 - "V8 Alltokens"
Cohesion: 0.14
Nodes (14): AllTokensFEMRDataset (dataset class), FEMRDataset (dataset class), GPT2 Architecture Config (referenced), V8 Data Config, V8 All-Tokens Data Config, V8 Debug Data Config, V9 Data Config, V9 All-Tokens Data Config (+6 more)

### Community 42 - "Bert"
Cohesion: 0.19
Nodes (7): BertSelfAttention, BERTLanguageModel, Any, DictConfig, Tensor, BERT with a Language Model head., RoPEBertSelfAttention

### Community 43 - "Carina Config"
Cohesion: 0.14
Nodes (13): HF_CACHE_DIR, HF_DATASETS_CACHE, HF_HOME, HUGGINGFACE_HUB_CACHE, config.sh script, TRANSFORMERS_CACHE, TRITON_CACHE_DIR, WANDB_ARTIFACT_DIR (+5 more)

### Community 44 - "Tasks"
Cohesion: 0.21
Nodes (7): _prefit_motor_agg(), _prefit_motor_map(), Any, datetime, SubjectDatabase, timedelta, SurvivalCalculator

### Community 45 - "Stanford"
Cohesion: 0.22
Nodes (12): move_billing_codes(), _move_date_to_end(), move_pre_birth(), move_to_day_end(), datetime, MutableSubject, Move all events to after the birth of a subject., Move billing codes to the end of each visit. One issue with our OMOP extract is… (+4 more)

### Community 46 - "Hf Ehr Config"
Cohesion: 0.21
Nodes (9): A token in the tokenizer config. One entry per unique token. Includes metadata…, Returns stat with specified type (required) and settings (optional), TokenizerConfigEntry, limit_to_top_k_codes(), main(), parse_args(), Namespace, Purpose: Limit a Cookbook tokenizer to top-k most frequently occurring codes.… (+1 more)

### Community 47 - "Test Transforms"
Cohesion: 0.38
Nodes (11): move_visit_start_to_first_event_start(), Assign visit start times to equal start time of first event in visit This…, DummyEvent, DummySubject, test_delta_encode(), test_move_billing_codes(), test_move_visit_start_doesnt_move_without_event(), test_move_visit_start_ignores_other_visits() (+3 more)

### Community 48 - "Ehrshot"
Cohesion: 0.30
Nodes (7): Float, CookbookModelWithClassificationHead, Module, Tensor, Return logits for classification task, Return a probability distribution over classes., Return index of predicted class.

### Community 49 - "Tokenization"
Cohesion: 0.17
Nodes (5): CEHR Tokenizer Config, BaseCodeTokenizer, CEHRTokenizer, Here, `text` will be a single code (e.g. "LOINC/13"), so just map it back to…, Here, `text` will be a single code (e.g. "LOINC/13"), so just map it back to…

### Community 50 - "Datasets"
Cohesion: 0.17
Nodes (4): AllTokensFEMRDataset, Wrapper around FEMRDataset that returns all tokens in the dataset. dataset[idx]…, Return all event codes for this example at `idx` in `self.split`. Maps this…, Usage: python3 val_ppl_nlp.py --model_name gpt2 --dataset_name…

### Community 51 - "Reloggers"
Cohesion: 0.23
Nodes (6): Go through all the prev_wandb_run_id_*.txt files (including wandb_run_id.txt)…, Updates the wandb run ID in the run_log_dir., Gets the last step from the model checkpoint., Relog all metrics history into a new run up to the last step logged by the ckpt…, Handles the relogging of metrics from a previous wandb run into a new run., WandbRelogger

### Community 52 - "Hf Ehr Utils"
Cohesion: 0.29
Nodes (11): main(), parse_args(), process_checkpoint(), Any, load_config_from_ckpt(), load_model_from_path(), load_tokenizer_from_path(), Module (+3 more)

### Community 53 - "Samplers"
Cohesion: 0.18
Nodes (6): BatchSampler, ApproxBatchSampler, Credit: https://github.com/microsoft/protein-sequence-…, # NOTE: Only do this check if we know aprior what the…, Ensures different shuffling for each epoch, Parameters: ----------- sampler : Pytorch Sampler Choose base sampler class to…

### Community 54 - "Tokenization"
Cohesion: 0.20
Nodes (10): BERT Architecture Config (referenced), BERT-Base Model Config, BERT-Large Model Config, BERT-XLarge Model Config, hf_ehr Configs Directory README, CLMBR Tokenizer Config (default), Cookbook Tokenizer Config, CookbookTokenizer (+2 more)

### Community 55 - "Ehrshot"
Cohesion: 0.27
Nodes (10): compute_feature_matrix(), get_ckpt_name(), main(), parse_args(), process_in_batches(), Any, Namespace, Usage: python3 ehrshot.py \ --path_to_database /share/pi/nigam/mwornow/ehrshot-… (+2 more)

### Community 56 - "Loaders"
Cohesion: 0.29
Nodes (9): DataLoader, Dataset, BaseDataset, collate_femr_timelines(), Collate function for FEMR timelines Truncate or pad to max length in batch., load_dataloaders(), load_datasets(), DictConfig (+1 more)

### Community 58 - "Tokenization"
Cohesion: 0.20
Nodes (4): Desc Tokenizer Config, DescTokenizer, Dump vocab for this tokenizer version, Converts codes => textual descriptions, then tokenizes using a normal text…

### Community 59 - "Based"
Cohesion: 0.20
Nodes (7): BasedLanguageModel, Any, DictConfig, Tensor, Based with a Language Model head., # TODO: Implement loading of pretrained weights, # NOTE: Based doesn't return loss, so manually calculate

### Community 60 - "Test Survival Calculator"
Cohesion: 0.28
Nodes (6): assert_labels_are_accurate(), DataFrame, datetime, Passes if the labels in `labeled_subjects` for `subject_id` exactly match the…, DummyOntology, test_calculator()

### Community 61 - "Tokenization"
Cohesion: 0.22
Nodes (8): Prepare masked tokens inputs/labels for masked language modeling: 80% MASK, 10%…, Typing for `seq_length_per_patient.json` cache file, # NOTE: When `is_split_into_words=True`, then __call__() will fail when a list…, # NOTE: CLMBR ignores units, # NOTE: CLMBR ignores units, TokenizerSeqLengthPerPatientCache, torch_mask_tokens(), TypedDict

### Community 62 - "T5"
Cohesion: 0.28
Nodes (5): Any, DictConfig, Tensor, T5 with a Language Model head., T5LanguageModel

### Community 63 - "Hf Upload"
Cohesion: 0.22
Nodes (7): readme_text(), get_param_count(), Usage: python hf_upload.py Purpose: Upload an hf_ehr model+tokenizer to Hugging…, Returns the number of parameters in the model., # NOTE: Setting original == max will cause this warning to throw:…, # NOTE: By default, Hyena sets `pad_vocab_size_multiple` to 8, # NOTE: By default, Hyena sets `pad_vocab_size_multiple` to 8

### Community 64 - "Samplers"
Cohesion: 0.22
Nodes (5): This gets called once at the start of every epoch., Ensures different shuffling for each epoch, Returns indices such that inputs with similar lengths are close together. Set…, SortishSampler, Sampler

### Community 65 - "Ehrshot Events Cdf Train"
Cohesion: 0.43
Nodes (8): EHRSHOT Benchmark, EHRSHOT Prediction Tasks (Hypertension, Long LOS, Hypoglycemia, Lupus, Hyponatremia, Pancreatic Cancer, Anemia, Acute MI, 30-Day Readmission, Thrombocytopenia, Hyperlipidemia, Celiac, Hyperkalemia, ICU Admission), EHRSHOT Train Split, CDF of Number of Events per Prediction, EHRSHOT # of Events per Prediction (Train Split) CDF Plot, EHRSHOT # of Tokens per Prediction CDF (Validation Split), Divergence Between Positive-Label and All-Label Event Count Distributions (e.g., Lupus, Celiac, 30-Day Readmission), Token Count per Prediction (Cumulative Distribution)

### Community 66 - "Featurizers Core"
Cohesion: 0.32
Nodes (6): join_labels(), DataFrame, ndarray, SubjectDatabase, Preprocess `self.featurizers` on the provided set of labels., Apply a list of Featurizers (in sequence) to obtain a feature matrix for each…

### Community 67 - "Omop"
Cohesion: 0.25
Nodes (6): get_death_concepts(), MortalityCodeLabeler, Apply a label for whether or not a subject dies within the `time_horizon`. Make…, Create a Mortality labeler., Create a MortalityCodeLabeler for codes 3 and 6, test_MortalityCodeLabeler()

### Community 68 - "Tasks"
Cohesion: 0.25
Nodes (3): LabeledSubjectTask, LabeledSubjectTask currently has no per label state., As there is no per label state, this is ignored

### Community 69 - "Ontology"
Cohesion: 0.25
Nodes (4): _get_all_codes_map(), Subject, SubjectDatabase, Get all parents, including through the ontology.

### Community 70 - "Llama"
Cohesion: 0.25
Nodes (5): LlamaLanguageModel, Any, DictConfig, Tensor, Llama with a Language Model head.

### Community 71 - "Mamba"
Cohesion: 0.25
Nodes (5): MambaLanguageModel, Any, DictConfig, Tensor, Mamba with a Language Model head.

### Community 72 - "Femr Test Tools"
Cohesion: 0.33
Nodes (3): dict, DummyDatabase, Any

### Community 73 - "Hyena Large"
Cohesion: 0.29
Nodes (7): Hyena Architecture Config (referenced), Hyena-Large Model Config, Hyena-Medium Model Config, Hyena-Small Model Config, Hyena-Tiny Model Config, Hyena-XLarge Model Config, Hyena XXLarge Model Config

### Community 74 - "Tokenization"
Cohesion: 0.43
Nodes (3): filter_tokenizer_config(), Any, Given a set of filters, applies them to the `tokenizer_config`. Returns two…

### Community 75 - "Ehrshot Events Cdf Val"
Cohesion: 0.53
Nodes (6): EHRSHOT Benchmark, EHRSHOT Clinical Prediction Tasks (Hypertension, Long LOS, Hypoglycemia, Lupus, Hyponatremia, Pancreatic Cancer, Anemia, Acute MI, 30-Day Readmission, Thrombocytopenia, Hyperlipidemia, Celiac, Hyperkalemia, ICU Admission), EHRSHOT Validation Split, Number of Events per Prediction (Patient Timeline Length Proxy), Positive-Label vs All-Label Event-Count Distribution Shift (e.g. Celiac task), EHRSHOT # of Events per Prediction CDF (Validation Split)

### Community 76 - "Based Base"
Cohesion: 0.40
Nodes (5): based.models.mixers.convolution.BaseConv, based.models.mixers.linear_attention.LinearAttention, based.models.mixers.linear_attention.TaylorExp, Based Architecture Config (referenced), Based-Base Model Config

### Community 77 - "Omop"
Cohesion: 0.40
Nodes (3): Subject, Return each event's start time (possibly modified by…, Return the start times of this subject's events whose `code` is in…

### Community 79 - "Hierarchical Tokenizer"
Cohesion: 0.40
Nodes (3): PathLike, Load the FEMR tokenizer. Parameters: pretrained_model_name_or_path (`str` or…, Save the FEMR tokenizer. This method make sure the batch processor can then be…

### Community 80 - "Xformers"
Cohesion: 0.60
Nodes (4): memory_efficient_attention_wrapper(), Tensor, ref_attention(), ref_attention_bmhk()

### Community 82 - "Test Ontology"
Cohesion: 0.80
Nodes (4): create_fake_athena(), Path, test_athena_and_custom(), test_only_athena()

### Community 83 - "Download Bigquery"
Cohesion: 0.40
Nodes (4): download(), A tool for downloading datasets from BigQuery. Setup: ``` pip install --upgrade…, # NOTE: the `HTTPIterator` can be iterated over like a list, but only once…, Download the results (a set of .csv.gz's) of the BigQuery extract job to our…

### Community 84 - "Fsdp"
Cohesion: 0.50
Nodes (5): FSDP Trainer Config (2 GPUs), Multi-GPU-2 Trainer Config (DDP), Multi-GPU-4 Trainer Config (DDP), Single-GPU Trainer Config (DDP), loaders.py (dataset/dataloader helpers)

### Community 86 - "Ehrshot Events Cdf Test"
Cohesion: 0.60
Nodes (5): EHRSHOT Clinical Prediction Tasks (14 labels), EHRSHOT Benchmark (Test Split), EHRSHOT # of Events per Prediction CDF (Test Split), Number of Events per Prediction (Metric), Rare-Outcome Positive-Label CDF Divergence (Lupus, Celiac, Pancreatic Cancer, Acute MI, ICU Admission)

### Community 87 - "Ehrshot Tokens Cdf Test"
Cohesion: 0.80
Nodes (5): EHRSHOT # of Tokens per Prediction CDF (Test Split), All-Labels vs Positive-Labels Token-Length Divergence, EHRSHOT Clinical Prediction Tasks (14 tasks: Hypertension, Long LOS, Hypoglycemia, Lupus, Hyponatremia, Pancreatic Cancer, Anemia, Acute MI, 30-Day Readmission, Thrombocytopenia, Hyperlipidemia, Celiac, Hyperkalemia, ICU Admission), EHRSHOT Benchmark (Test Set), Token Count Distribution per Prediction (CDF)

### Community 88 - "Main"
Cohesion: 0.60
Nodes (4): main(), map_model_partition_to_batch_size(), parse_args(), Determine how big our batches can be given model + partition settings. Returns…

### Community 90 - "Main"
Cohesion: 0.60
Nodes (4): main(), map_model_to_batch_size(), parse_args(), Determine how big our batches can be given model + partition settings. Returns…

### Community 92 - "Gpt2 Hazyresearch LoCoV1 Documents Test"
Cohesion: 0.83
Nodes (4): GPT-2 (hazyresearch), Token Position vs Median PPL (EMA) - GPT-2 on LoCoV1-Documents Test Set, LoCoV1-Documents Test Set, Median Perplexity (EMA) vs Token Position

### Community 93 - "Ehrshot Att V Non Att"
Cohesion: 0.83
Nodes (3): clean_data_before_grouping(), compare_att_non_att_across_tasks(), process_all_tasks()

### Community 94 - "Tokenizers Utils"
Cohesion: 0.50
Nodes (4): add_unique_codes(), merge_unique_codes(), Merge results from `calc_unique_codes`., For each unique code in dataset, add a CodeTCE to tokenizer config.

### Community 95 - "Val Stats Irr"
Cohesion: 0.67
Nodes (3): EHR-OMOP Dataset, Validation Set Time-Between-Events Statistics (Mean, Std Dev, IQR) for EHR-OMOP, Time-Between-Events Irregularity Metric

### Community 96 - "Hf Ehr Config"
Cohesion: 0.67
Nodes (3): patch_config(), DictConfig, Rewrite paths for Carina partitions.

## Ambiguous Edges - Review These
- `Bug Report Issue Template` → `Hugging Face `datasets` library (env-info boilerplate)`  [AMBIGUOUS]
  femr/.github/ISSUE_TEMPLATE/bug_report.md · relation: references
- `hf_ehr repository (som-shahlab/hf_ehr)` → `Main Hydra training config (config.yaml)`  [AMBIGUOUS]
  femr/README.md · relation: shares_data_with

## Knowledge Gaps
- **157 isolated node(s):** `femr`, `gen_dataset_stats.sh script`, `train_seq_lengths.sh script`, `bucket_by_metrics.sh script`, `calc_stratification_metrics.sh script` (+152 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 672 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Bug Report Issue Template` and `Hugging Face `datasets` library (env-info boilerplate)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `hf_ehr repository (som-shahlab/hf_ehr)` and `Main Hydra training config (config.yaml)`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **Why does `Event` connect `Tokenization` to `Utils New`, `Tokenization`, `Flat Tokenizer`, `Featurizers`, `Featurizers`, `Hf Test`, `Tokenizers Utils`, `Starr Eda`, `Hierarchical Tokenizer`, `Datasets`, `Tokenization`, `Stanford`, `Tokenization`, `Ehrshot`, `Loaders`, `Hf Ehr Config`, `Tokenization`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **Why does `Ontology` connect `Ontology` to `Transformer`, `Omop`, `Flat Tokenizer`, `Ontology`, `Featurizers`, `Tasks`, `Hierarchical Tokenizer`, `Hierarchical Tokenizer`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `FEMRDataset` connect `Utils New` to `Create Desc`, `Tokenization`, `Hf Ehr Config`, `Val Ppl`, `Datasets`, `Tokenization`, `Create Cookbook`, `Loaders`, `Tokenization`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `TimeHorizon` (e.g. with `CodeLabeler` and `MortalityCodeLabeler`) actually correct?**
  _`TimeHorizon` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `BaseModel` (e.g. with `eval()` and `run_ckpt()`) actually correct?**
  _`BaseModel` has 2 INFERRED edges - model-reasoned connections that need verification._