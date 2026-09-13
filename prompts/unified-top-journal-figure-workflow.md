# Prompt — unified top-journal figure workflow

Use `workflow_project.yaml` as the governing input.

Run the workflow fail-closed.

At every stage:

1. read `WORKFLOW_STATE.json`;
2. complete only the current required action;
3. write the required artifact;
4. run the deterministic validator;
5. update state;
6. stop at any hard gate;
7. do not mark manual reviews PASS without explicit review.

## Agent responsibilities

When state is `BENCHMARK_SEARCH_REQUIRED`:
- search current literature;
- verify benchmark metadata;
- inspect figures/legends where available;
- build benchmark corpus and dossier.

When state is `EVIDENCE_MAPPING_REQUIRED`:
- read Methods / Results / source tables;
- build the evidence graph;
- build panel candidate inventory.


When state is `ANNOTATION_INVENTORY_REQUIRED`:
- read Results, Methods, source tables, the evidence graph, benchmark grammar, and visual hierarchy;
- materialize candidate P/FDR/q/CI/n/effect-size/direction/method annotations without recalculating frozen statistics;
- let the deterministic planner assign `DIRECT`, `LEGEND`, or `SUPPRESS`;
- preserve an explicit reason for every suppressed item.

When state is `REAL_DATA_RENDER_SPEC_REQUIRED`:
- create explicit source mappings and sentinels;
- inject the approved annotation-intelligence plan into render specs;
- never guess scientific columns.

When state is `MANUSCRIPT_REINTEGRATION_REQUIRED`:
- synchronize exact panel citations and legends;
- make only evidence-supported manuscript edits.

## Human-review boundaries

Never self-certify:
- prototype final-size visual PASS;
- final figure visual PASS;
- contact-sheet PASS;
- actual portal upload-contract PASS.

These require an explicit review record.

## Final state

Do not call the package submission-ready unless:

`current_state == FIGURE_PACKAGE_SUBMISSION_READY`
