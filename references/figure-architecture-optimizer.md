# Figure architecture optimizer

## Purpose

v1.6 turns benchmark-informed planning into a constrained architecture-optimization problem.

Inputs:

> Methods + Results + source tables + frozen analyses + evidence graph + benchmark dossier + journal contract

Outputs:

> 3/4/5-figure candidate architectures + main/Supplementary allocation + panel actions + scored recommendation

The optimizer does **not** invent new science. It only organizes evidence that the upstream evidence inventory declares as available.

---

## Upstream dependency

Before optimization, the project should already have:

1. **Internal evidence inventory**
2. **Evidence graph**
3. **Benchmark dossier**
4. **Journal profile / contract**
5. **Panel candidate inventory**

The AI/expert layer extracts scientific semantics.
The scripts perform deterministic structural optimization and auditing.

---

## Panel candidate model

Every candidate panel should declare:

- `panel_id`
- `theme`
- `claim_ids`
- `source_ids`
- `role`
- `evidence_family`
- `chart_type`
- `availability`
- `main_eligible`
- `must_main`
- `priority`
- `contribution_score`
- `benchmark_support_score`
- `source_traceability_score`
- `visual_density`
- `narrative_order`
- `current_location`
- optional `redundancy_group`

### Availability

Allowed:
- `DIRECTLY_AVAILABLE`
- `STRUCTURALLY_ADAPTABLE`
- `OPTIONAL_NEW_ANALYSIS`
- `NOT_APPLICABLE`

Only `DIRECTLY_AVAILABLE` and, where explicitly justified, `STRUCTURALLY_ADAPTABLE` may enter a promoted current figure plan.

`OPTIONAL_NEW_ANALYSIS` must remain outside the promoted plan until completed.

---

## Optimization objectives

The optimizer balances:

### 1. Claim coverage
High-priority manuscript claims should be represented in the main figures.

### 2. Contribution visibility
The true scientific contribution should have visually prominent anchor evidence.

### 3. Evidence diversity
Prefer complementary evidence families:
- anchor result;
- participant-level distribution;
- orthogonal support;
- robustness;
- external context;
- mechanism;
- boundary.

Avoid multiple panels that repeat the same inferential role.

### 4. Benchmark concordance
Use the benchmark dossier as a **soft prior** for:
- typical main-figure count;
- panel density;
- anchor-panel placement;
- schematic-to-quantitative ratio;
- evidence sequencing.

Benchmark grammar never overrides scientific fidelity.

### 5. Journal fit
Respect:
- maximum displays;
- physical dimensions;
- density / readability constraints;
- main-vs-supplement conventions.

### 6. Visual feasibility
Avoid figures whose panel count or total visual density would make final-size rendering unreadable.

### 7. Source traceability
Every quantitative main panel should map to a stable source object.

### 8. Redundancy control
Panels with highly overlapping:
- claims;
- sources;
- evidence family;
- chart type;
should be merged or demoted unless they provide a clearly different inferential function.

---

## Redundancy score

The default deterministic redundancy heuristic combines:

- claim overlap;
- source overlap;
- same evidence family;
- same chart type;
- same redundancy group.

A high score does not automatically mean "delete".
It means the pair requires an explicit reason to coexist.

For example:

- box plot + paired plot from the same data can still be nonredundant if they answer different questions;
- two threshold sensitivity plots with the same estimand may be better merged.

---

## Architecture generation

The optimizer can generate candidate sets for:

- 3 main figures
- 4 main figures
- 5 main figures

or another range specified by the journal/project.

### Grouping logic

1. select eligible high-value panels;
2. preserve `must_main` panels;
3. remove or demote strong redundancies;
4. group panels by scientific `theme`;
5. merge closely related themes if the target figure count is smaller;
6. split over-dense themes if the target figure count is larger;
7. enforce panel-count and density constraints;
8. move low-value / redundant panels to Supplementary.

---

## Main vs Supplementary

Panels should be demoted when they are:

- diagnostically useful but not contribution-critical;
- repetitive threshold sweeps;
- exhaustive robustness grids;
- secondary parameterizations;
- tables disguised as figures;
- low-priority context that weakens the main narrative.

Panels should remain main when they:

- carry a high-priority claim;
- define the study's contribution;
- establish participant-level credibility;
- provide essential robustness;
- provide direct replication or decisive orthogonal evidence.

---

## Panel actions

The optimizer emits actions:

- `PROMOTE`
- `KEEP`
- `REPAIR`
- `MERGE`
- `DEMOTE`
- `SPLIT_FIGURE`
- `UPGRADE_CANDIDATE`
- `DROP_NOT_APPLICABLE`

### PROMOTE
High-value eligible evidence should move into the main figure set.

### KEEP
Current panel remains appropriate.

### REPAIR
Scientific role is valuable, but visual density / chart choice / local architecture needs redesign.

### MERGE
Panel is partly redundant with another panel and should be combined.

### DEMOTE
Useful but better placed in Supplementary / Extended Data.

### SPLIT_FIGURE
A figure contains too many panels or too much visual density for final-size readability.

### UPGRADE_CANDIDATE
Benchmark literature suggests a useful new analysis, but it is not yet available.

### DROP_NOT_APPLICABLE
Benchmark-derived idea is incompatible with the study design or data.

---

## Candidate scoring

Each architecture receives 0–10 sub-scores for:

- scientific fidelity;
- weighted claim coverage;
- contribution visibility;
- evidence diversity;
- benchmark concordance;
- journal fit;
- information efficiency;
- visual feasibility;
- evidence-boundary integrity;
- source traceability;
- redundancy control.

The benchmark-preferred figure count is a **soft prior only**.

A 4-figure benchmark pattern must not force a 4-figure paper if 3 figures communicate the current evidence more efficiently.

---

## Promotion rule

A candidate can be recommended only if:

- no unavailable panel is promoted;
- all `must_main` panels are retained;
- high-priority claims are adequately covered;
- no hard journal constraint fails;
- no severe redundancy remains without justification;
- source traceability is complete;
- visual-density limits are acceptable.

The numerically highest score still requires expert approval.

---

## Recommended workflow

> evidence inventory  
> → benchmark dossier  
> → panel candidate inventory  
> → redundancy matrix  
> → 3/4/5-figure candidate generation  
> → main/Supplementary optimization  
> → panel action recommendations  
> → candidate scoring  
> → expert promotion  
> → figure rendering  
> → collision/journal/evidence QA
