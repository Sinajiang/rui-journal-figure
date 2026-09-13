# Benchmark-informed figure planning

## Purpose

v1.4 changes figure planning from:

> "read the manuscript and invent a reasonable figure set"

to:

> **internal evidence inventory + external benchmark grammar + journal contract → candidate figure architectures → scored promotion decision**

The planner must use both:

1. **Internal scientific material**
   - Methods
   - Results
   - source tables / source-data files
   - frozen statistical authority
   - current legends / figures if they exist

2. **External benchmark material**
   - recent high-quality papers from the target journal where possible
   - strong peer-journal papers with comparable study design / data modality
   - field-defining benchmark papers when recent target-journal examples are insufficient

The external literature informs **figure grammar and evidence architecture**, not the truth of the current study.

---

## Two different kinds of benchmark

### A. Scientific benchmark
Used to understand what strong papers in the field consider central evidence.

Extract:
- which Results-level questions receive main figures;
- what evidence is placed in main figures versus Supplementary/Extended Data;
- what robustness analyses are considered necessary;
- whether participant-level plots are expected;
- whether external validation, orthogonal assays, sensitivity analysis, or mechanism appear in main figures.

### B. Visual benchmark
Used to learn presentation grammar.

Extract:
- panel count;
- panel order;
- anchor-panel size;
- chart types;
- legend placement;
- direct labeling;
- typography density;
- whitespace strategy;
- schematic-to-quantitative ratio;
- use of raw observations;
- uncertainty display.

Do not copy exact artwork or layouts.

---

## Benchmark selection hierarchy

Prefer, in order:

1. target journal + similar scientific question + similar data modality;
2. target journal + similar article type;
3. high-impact peer journal + similar scientific question and data modality;
4. field-defining paper with highly transferable figure architecture.

For each benchmark record:

- citation / DOI / URL;
- journal;
- year;
- article type;
- scientific similarity;
- methodological similarity;
- data-modality similarity;
- figure relevance;
- why it is being used.

### Recommended benchmark set

Default target:
- 3–8 papers for focused work;
- 5–12 papers for a complete manuscript reconstruction.

Do not enforce a fixed count when the field is sparse. Quality and relevance override count.

---

## Internal evidence inventory

Before proposing figures, the planner must enumerate what the current study actually has.

For every result object record:

- analysis ID;
- source file;
- sample / unit of analysis;
- estimand/statistic;
- uncertainty;
- multiplicity adjustment;
- robustness status;
- whether analysis is frozen;
- whether it is main, secondary, exploratory, or contextual;
- whether re-analysis is allowed.

The planner must not propose a panel that requires unavailable evidence unless it is explicitly labeled:

`OPTIONAL_NEW_ANALYSIS`

Such panels cannot be promoted into the current figure plan until the analysis exists.

---

## Benchmark-to-study mapping

For every transferable benchmark pattern, classify it as:

### DIRECTLY_AVAILABLE
The study already contains equivalent evidence.

### STRUCTURALLY_ADAPTABLE
The figure grammar is useful, but the exact evidence differs.

### OPTIONAL_NEW_ANALYSIS
The benchmark suggests a valuable analysis that is scientifically feasible but not currently available.

### NOT_APPLICABLE
The benchmark pattern depends on a design, modality, sample, or endpoint the current study does not have.

This prevents "benchmark imitation" from creating unsupported panels.

---

## Candidate architecture generation

The planner should normally generate 2–4 candidate figure plans.

Examples:

### Candidate A — contribution-forward
Prioritizes:
- central discovery;
- participant-level support;
- robustness;
- external context.

### Candidate B — mechanism-forward
Used only when direct mechanistic evidence exists.

### Candidate C — clinical-translational
Prioritizes:
- cohort / phenotype;
- effect magnitude;
- clinically interpretable stratification;
- validation.

### Candidate D — reproducibility-forward
Prioritizes:
- provenance;
- robustness;
- leave-one-out / alternate model;
- cross-dataset evidence.

The planner must not force all archetypes. Generate only plans compatible with the study.

---

## Scoring dimensions

Every candidate architecture should be scored on:

1. **Scientific fidelity**
   - does every panel exist in the current evidence base?

2. **Claim coverage**
   - does the figure set cover the manuscript's main Results-level claims?

3. **Contribution visibility**
   - is the paper's real contribution visually obvious?

4. **Evidence diversity**
   - are panels inferentially complementary rather than redundant?

5. **Benchmark concordance**
   - does the architecture follow transferable high-quality patterns?

6. **Journal fit**
   - figure count / density / dimensions / style compatible with target journal?

7. **Information efficiency**
   - is important evidence prioritized without overloading?

8. **Visual feasibility**
   - can it be rendered at final size without unreadable density?

9. **Evidence-boundary integrity**
   - does it avoid overstating replication, mechanism, or causality?

10. **Source-data traceability**
   - can every quantitative panel be traced to a frozen source?

---

## Promotion logic

A candidate may be promoted only if:

- no panel depends on unavailable evidence;
- no hard scientific or journal gate fails;
- all main Results claims are covered;
- no major main-figure redundancy remains;
- benchmark influence is structural, not imitative;
- final architecture is better than the current baseline.

If a benchmark-inspired panel would be valuable but requires new analysis, keep it in a separate:

`ANALYSIS_UPGRADE_CANDIDATES`

list.

Never smuggle it into the promoted figure plan.

---

## What the planner should output

1. **Internal evidence inventory**
2. **Benchmark set**
3. **Benchmark grammar extraction**
4. **Benchmark-to-study mapping**
5. **2–4 candidate figure architectures**
6. **Candidate score table**
7. **Recommended architecture**
8. **Panels moved to Supplementary**
9. **Optional new analyses**
10. **Evidence ceiling / unavailable components**
11. **Exact source-data mapping for the promoted plan**
