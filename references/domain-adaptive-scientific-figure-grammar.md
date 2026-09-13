# Domain-adaptive scientific figure grammar

## Purpose

v2.1 adds study-type-specific figure grammar on top of the unified v2.0 workflow.

A transcriptomics paper, a clinical cohort, a survival analysis, a meta-analysis,
a single-cell study, a multimodal phenotype paper, and a prediction paper should
not be forced into the same figure vocabulary.

The domain layer helps decide:

- what evidence should normally appear in main figures;
- which chart families are most natural;
- which diagnostic panels are usually supplementary;
- what evidence sequence best communicates the contribution;
- which visual failure modes are common in the domain.

The domain layer is a **soft scientific grammar**.
It never overrides:
- the study's actual Methods/Results;
- frozen analysis authority;
- target-journal hard requirements;
- evidence availability.

---

## Supported domain profiles

v2.1 includes profiles for:

1. `transcriptomics_bulk`
2. `single_cell`
3. `clinical_cohort`
4. `survival_longitudinal`
5. `prediction_modeling`
6. `meta_analysis`
7. `multimodal_clinical`

A manuscript may map to more than one domain.
Use:
- one **primary domain**;
- optional **secondary domains**.

Example:
- multimodal CSVD paper:
  - primary: `multimodal_clinical`
  - secondary: `clinical_cohort`
- PBMC reanalysis:
  - primary: `transcriptomics_bulk`
  - secondary: `clinical_cohort`

---

## Domain inference

The workflow may infer candidate domains from:

- manuscript Methods;
- Results vocabulary;
- source-table column names;
- evidence graph;
- user-specified article type.

Inference is advisory.

When:
- one domain score is clearly dominant, it can be proposed automatically;
- scores are close, the workflow should request agent confirmation.

Do not infer a domain from journal name alone.

---

## Grammar components

Each domain profile contains:

### Core scientific questions
What strong papers in the domain commonly need to answer.

### Main-figure archetypes
Examples of valid figure-level questions.

### Expected evidence families
Evidence types commonly considered central.

### Preferred chart families
Plot families that naturally express the evidence.

### Main-vs-Supplementary guidance
What belongs in main figures versus diagnostic/supplementary material.

### Domain-specific QA
Common problems that should trigger review.

### Optional benchmark search terms
Search terms useful for selecting top-journal exemplars.

---

## Domain profile examples

### Bulk transcriptomics

Common main-figure sequence:

1. cohort / analysis design;
2. primary molecular contrast;
3. participant-level or model-level robustness;
4. cross-dataset / external context;
5. pathway / mechanism only if directly supported.

Common chart grammar:
- effect plot;
- volcano plot only when the full differential universe matters;
- participant-level expression;
- heatmap with careful scaling semantics;
- robustness range / perturbation plot;
- external evidence matrix.

Common failure:
- large DEG heatmaps replacing an actual statistical result;
- pathway diagrams presented as mechanistic proof;
- multiple volcano plots with no distinct inferential role.

### Single-cell

Common main-figure sequence:

1. atlas / clustering and annotation;
2. cell-composition or state change;
3. cell-type-specific differential signal;
4. trajectory / regulatory / ligand-receptor result;
5. orthogonal validation.

Common failure:
- UMAP as decoration rather than evidence;
- too many UMAPs;
- pseudoreplication;
- cell-level points shown as if independent donors.

### Clinical cohort

Common main-figure sequence:

1. study flow / cohort structure;
2. primary association/effect;
3. participant-level distribution;
4. adjusted/robustness analysis;
5. clinically interpretable subgroup or external validation if pre-specified.

Common failure:
- Table 1 converted into a figure;
- excessive univariable forest plots;
- exploratory subgroup grids in main figures.

### Survival / longitudinal

Common main-figure sequence:

1. risk-set / longitudinal design;
2. cumulative incidence or survival curve;
3. adjusted effect estimates;
4. competing-risk / sensitivity analysis;
5. calibration / prediction only if part of the study question.

Common failure:
- presenting Kaplan-Meier when competing risk estimand is different;
- mixing landmark periods;
- decorative longitudinal spaghetti without inferential purpose.

### Prediction modeling

Common main-figure sequence:

1. derivation/validation flow;
2. discrimination;
3. calibration;
4. clinical utility / decision curve if justified;
5. external validation and robustness.

Common failure:
- ROC-only presentation;
- variable-importance plot replacing model performance;
- no calibration;
- internal CV treated as external validation.

### Meta-analysis

Common main-figure sequence:

1. PRISMA / evidence flow;
2. primary pooled estimate;
3. heterogeneity / influence / subgroup analysis;
4. bias/robustness diagnostics;
5. evidence map if multiple etiologies/outcomes.

Common failure:
- forest plot overload;
- funnel plot promoted despite too few studies;
- subgroup analyses without enough studies;
- mixing incomparable etiologies/time windows.

### Multimodal clinical

Common main-figure sequence:

1. cohort and modality architecture;
2. modality-specific primary effects;
3. cross-modal relation / multiview structure;
4. robustness / contribution decomposition;
5. mechanistic or external anchor.

Common failure:
- forcing all modalities into one composite score;
- using a correlation heatmap as the entire story;
- presenting hundreds of modality indicators without hierarchy.

---

## Domain-aware optimization

The architecture optimizer should add domain-level scores:

- domain core-question coverage;
- domain evidence-family coverage;
- chart-grammar appropriateness;
- main-vs-Supplementary conformity;
- domain-specific risk penalties.

These are soft scores.

Scientific fidelity, claim coverage, source traceability, and evidence-boundary integrity retain veto power.

---

## Domain-aware benchmark retrieval

The benchmark search brief should inherit domain-specific search terms.

Example for `prediction_modeling`:
- calibration
- external validation
- decision curve
- discrimination
- risk prediction

Example for `single_cell`:
- scRNA-seq
- pseudobulk
- donor-level
- cell-state
- regulatory
- ligand-receptor

Use domain terms to improve benchmark retrieval relevance.

---

## Domain-specific visual review

Manual visual review should ask domain-specific questions.

Examples:

### Single-cell
- Are UMAPs carrying scientific evidence or just occupying space?
- Are donor-level units visually distinguished from cells?

### Meta-analysis
- Can the forest plot be read at final width?
- Is heterogeneity visible without overloading labels?

### Multimodal
- Is one modality visually dominating only because it has more variables?
- Are modality-specific and cross-modal findings clearly separated?

### Prediction
- Are discrimination and calibration given comparable visual weight?

---

## Governance

A domain profile is not a recipe.

Do not generate:
- a survival curve when the project has no time-to-event estimand;
- a volcano plot when the project has only a fixed candidate set;
- a decision curve when clinical utility was not evaluated;
- a ligand-receptor panel when no such analysis exists.

The domain profile should improve structure while preserving the actual evidence boundary.
