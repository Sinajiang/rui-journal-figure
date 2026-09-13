# Unified autonomous top-journal figure workflow

## Purpose

v2.0 unifies the v1.1–v1.9 modules into one resumable, fail-closed workflow.

The user should be able to provide:

- manuscript;
- source-data files / directories;
- target journal;
- project scientific authority;
- manuscript authority;
- optional current figures / legends;
- optional frozen sentinel contracts.

The workflow then coordinates:

1. manuscript/source ingestion;
2. journal-contract resolution;
3. benchmark retrieval planning;
4. benchmark verification / ranking;
5. internal evidence inventory;
6. evidence graph;
7. domain-adaptive figure grammar;
8. figure architecture planning and 3/4/5-figure optimization;
9. contribution-weighted visual-area allocation;
10. benchmark-derived layout grammar;
11. automatic visual hierarchy / typography budgets;
12. automatic annotation and legend intelligence;
13. structural prototype and promote / repair / rollback;
14. real-data rendering;
15. sentinel and geometric QA;
16. cross-figure compilation;
17. manuscript reintegration;
18. final submission-figure package state.

---

## Critical design constraint

Some stages cannot be completed safely by a deterministic local script alone.

Examples:

- current web benchmark retrieval;
- expert interpretation of Methods / Results;
- scientific claim-strength adjudication;
- manual final-size visual inspection;
- final journal upload-preview inspection.

Therefore the workflow distinguishes:

### AUTOMATED
Can be executed deterministically by scripts.

### AGENT_ACTION_REQUIRED
Requires the AI agent to research, inspect, map, or produce an artifact.

### HUMAN_REVIEW_REQUIRED
Requires human / expert approval.

### BLOCKED
A hard failure has occurred.

### COMPLETE
The stage has passed.

The workflow must never pretend an AGENT_ACTION_REQUIRED or HUMAN_REVIEW_REQUIRED stage has been completed.

---

## Workflow state machine

Recommended states:

1. `INIT`
2. `INGEST_COMPLETE`
3. `JOURNAL_CONTRACT_COMPLETE`
4. `BENCHMARK_SEARCH_REQUIRED`
5. `BENCHMARK_CORPUS_COMPLETE`
6. `EVIDENCE_MAPPING_REQUIRED`
7. `EVIDENCE_GRAPH_COMPLETE`
8. `ARCHITECTURE_OPTIMIZED`
9. `VISUAL_WEIGHTING_COMPLETE`
10. `LAYOUT_GRAMMAR_COMPLETE`
11. `VISUAL_HIERARCHY_COMPLETE`
12. `ANNOTATION_INVENTORY_REQUIRED` or `ANNOTATION_INTELLIGENCE_COMPLETE`
13. `PROTOTYPE_REVIEW_REQUIRED`
14. `ARCHITECTURE_PROMOTED`
15. `REAL_DATA_RENDERED_PRE_PROMOTION`
16. `FINAL_FIGURE_REVIEW_REQUIRED`
17. `FIGURES_PROMOTED`
18. `FIGURE_PACKAGE_COMPILED_PRE_SUBMISSION`
19. `CONTACT_SHEET_REVIEW_REQUIRED`
20. `MANUSCRIPT_REINTEGRATION_REQUIRED`
21. `FIGURE_PACKAGE_SUBMISSION_READY`

Any hard failure moves the workflow to:

`BLOCKED`

with:
- stage;
- reason;
- artifacts;
- recommended next action.

---

## Checkpointing

Every stage writes to:

`WORKFLOW_STATE.json`

The state file contains:

- project ID;
- run ID;
- current stage;
- stage status;
- timestamps;
- input hashes;
- artifact paths;
- hard-gate results;
- pending agent actions;
- pending human reviews;
- exact versions.

The workflow should be resumable.

Do not restart benchmark search or overwrite a promoted baseline when a later stage fails.

---

## Fail-closed rule

When the workflow cannot safely infer something, it should stop and request the missing action.

Examples:

### Benchmark corpus absent
State:
`BENCHMARK_SEARCH_REQUIRED`

Required agent action:
- search target journal / peer literature;
- verify metadata;
- fill benchmark candidate manifest;
- extract benchmark grammar.

### Evidence graph absent
State:
`EVIDENCE_MAPPING_REQUIRED`

Required agent action:
- read Methods / Results / legends / source tables;
- construct claim → panel → source mappings.

### Manual visual review absent
State:
`PROTOTYPE_REVIEW_REQUIRED`
or
`FINAL_FIGURE_REVIEW_REQUIRED`

No auto-promotion is allowed.

---

## Input contract

Use `workflow_project.yaml`.

Required:

```yaml
project:
  id: ""
  title: ""
  target_journal: ""
  scientific_authority: ""
  manuscript_authority: ""

inputs:
  manuscript: ""
  source_data:
    - ""
```

Optional:
- current figures;
- current legends;
- journal profile;
- sentinel contracts;
- prior accepted baseline;
- benchmark corpus;
- evidence graph.

---

## Stage 1 — Ingest

Automated tasks:

- hash manuscript;
- extract manuscript sections;
- inventory source tables;
- hash source files;
- record current figures / legends if supplied.

Output:
- `INGEST/manifest.json`
- `INGEST/manuscript_sections.json`
- `INGEST/source_inventory.json`

---

## Stage 2 — Journal contract

If an existing current profile is supplied:
- validate retrieval date;
- use profile.

If not:
- set `AGENT_ACTION_REQUIRED` when current official guidelines need web verification.

The workflow may use a bundled journal profile as a starting point, but must not silently claim it is current beyond its recorded retrieval date.

---

## Stage 3 — Benchmark retrieval

The orchestrator can:
- generate benchmark search brief;
- generate query families;
- validate supplied benchmark candidates;
- normalize / rank / select supplied candidates.

Actual current web retrieval is an agent action.

This separation is deliberate.

---

## Stage 4 — Evidence mapping

The orchestrator can:
- extract manuscript sections;
- inspect source tables;
- validate an evidence graph.

Constructing the evidence graph requires scientific reading and should be performed by the agent / expert.

---

## Stage 5 — Architecture optimization

Automated once:
- panel candidate inventory;
- optimizer input;
are available.

Outputs:
- redundancy matrix;
- 3/4/5 candidate architectures;
- panel actions;
- recommended architecture.

---

## Stage 6 — Contribution, layout and annotation intelligence

Automated once the promoted architecture and benchmark annotations exist:

- score panel contribution;
- allocate visual area;
- aggregate benchmark layout grammar;
- solve physical panel rectangles;
- derive bounded typography/annotation budgets;
- derive `DIRECT` / `LEGEND` / `SUPPRESS` annotation decisions;
- audit P/FDR/CI/n/effect-size/direction redundancy and legend density.

If a structured annotation inventory is absent, the workflow first attempts evidence-graph extraction and otherwise stops at `ANNOTATION_INVENTORY_REQUIRED` for agent materialization from Results, Methods and source tables. Frozen statistics must not be recalculated.

## Stage 7 — Prototype loop

Automated:
- build structural prototypes;
- compute heuristic visual metrics.

Human/agent required:
- final-size visual review.

Promotion cannot occur without review status.

---

## Stage 8 — Real-data rendering

Automated when:
- render specs exist;
- sentinels exist or are explicitly waived by contract;
- architecture is promoted.

Outputs:
- PDF/SVG/TIFF/PNG;
- source-data TSVs;
- provenance;
- terminal QA.

Final promotion still requires manual visual review.

---

## Stage 9 — Figure-set compilation

Automated:
- manifest validation;
- cross-figure style audit;
- raster audit;
- contact sheet;
- package hash manifest.

Human/agent required:
- contact-sheet review;
- manuscript reintegration;
- journal upload-contract closure.

---

## Run modes

### `--status`
Read current workflow state only.

### `--resume`
Continue from the first incomplete stage.

### `--stage <name>`
Run one deterministic stage.

### `--dry-run`
Report what would run and what agent/human actions are required.

### `--reset-stage <name>`
Invalidate one stage and all downstream stages.

Reset must never silently delete scientific source data or promoted artifacts.

---

## Governance

The workflow should make it impossible to confuse:

- generated prototype;
- rendered pre-promotion figure;
- promoted final figure;
- compiled pre-submission package;
- submission-ready figure package.

Every state transition should be explicit.
