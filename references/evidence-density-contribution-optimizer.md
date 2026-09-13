# Evidence-density and contribution optimizer

## Purpose

v2.2 maps **scientific contribution strength** to **visual weight**.

A publication figure should not allocate equal visual area to unequal evidence.
A workflow diagram, a secondary sensitivity panel, and the manuscript's decisive result should not automatically receive identical panel sizes.

The optimizer uses the current study's evidence inventory, claim priority, source traceability, benchmark grammar, domain grammar, and redundancy structure to decide:

- which panels deserve the largest visual area;
- which panels should remain compact;
- which high-density panels require more space rather than smaller fonts;
- which lower-contribution panels should move to Supplementary;
- whether the current layout visually misrepresents the scientific hierarchy.

The optimizer does **not** change scientific results.

---

## Scientific contribution model

Each panel receives a contribution score based on declared metadata.

Recommended components:

1. **Claim priority** — importance of the linked manuscript claim.
2. **Evidence directness** — direct test, robustness, context, mechanism, boundary.
3. **Contribution value** — how much the panel advances the paper's central contribution.
4. **Source traceability** — whether the panel maps cleanly to stable source data.
5. **Robustness / replication value** — whether it materially strengthens confidence.
6. **Benchmark support** — whether top-journal exemplars commonly give this evidence main-figure prominence.
7. **Domain-core relevance** — whether it addresses a core question for the study type.
8. **Redundancy penalty** — whether another panel answers essentially the same question.
9. **Evidence-boundary penalty** — whether the panel is contextual, exploratory, or otherwise limited.

The contribution score is a visual-priority signal, not a statistical significance score.

A small P value does not automatically justify a large panel.

---

## Visual-density model

A panel's visual area should depend on both:

- **scientific contribution**; and
- **rendering density**.

High-contribution + high-density panels generally need more area.

Examples:

- a five-gene external evidence matrix may need more area than a small workflow schematic;
- a participant-level plot may require more width than a one-number robustness annotation;
- a dense forest plot may need more vertical height than a compact paired-dot panel.

The optimizer should not solve density pressure by shrinking text below the journal-readable floor.

---

## Visual-weight classes

Recommended classes:

### ANCHOR
The central result or decisive contribution.
Typical relative visual weight: high.

### MAJOR_SUPPORT
Participant-level support, direct replication, essential robustness, or key orthogonal evidence.
Typical visual weight: medium-high.

### SUPPORT
Useful but not central evidence.
Typical visual weight: medium.

### CONTEXT
External disease/state context or secondary interpretive evidence.
Typical visual weight: low-medium.

### PROVENANCE
Study flow, workflow, or methods schematic.
Typical visual weight: compact unless study design itself is a major contribution.

### SUPPLEMENTARY_CANDIDATE
Valid evidence with low incremental contribution or high redundancy.
Should normally not compete for main-figure area.

---

## Area-allocation rules

The default area allocator should:

1. preserve all must-main evidence;
2. identify the highest-contribution panel in each figure;
3. allocate more area to higher contribution and higher density;
4. cap workflow/provenance panels unless they carry a major scientific claim;
5. prevent tiny panels that force unreadable text;
6. flag inversions where a low-contribution panel is visually larger than the anchor;
7. preserve benchmark/domain visual grammar as a soft prior.

### Typical structural choices

For 2–4 panel figures:

- one clear anchor → anchor-left / anchor-top dominant layout;
- no clear anchor → balanced grid;
- one dense matrix → allocate wider panel even if its claim priority is slightly lower;
- workflow + quantitative panels → workflow compact, quantitative evidence dominant.

---

## Main vs Supplementary optimization

A panel should be considered for demotion when:

- contribution score is low;
- redundancy is high;
- it is exploratory/contextual;
- it consumes disproportionate visual area;
- it duplicates a table;
- it adds diagnostic completeness rather than argument-level evidence.

A panel should resist demotion when:

- it carries a must-cover claim;
- it is the primary effect;
- it provides participant-level credibility;
- it is direct external replication;
- it closes a major evidence gap.

---

## Visual-scientific alignment audit

The optimizer should flag:

- `ANCHOR_AREA_TOO_SMALL`
- `WORKFLOW_AREA_TOO_LARGE`
- `CONTRIBUTION_AREA_INVERSION`
- `DENSE_PANEL_UNDERSIZED`
- `HIGH_VALUE_PANEL_DEMOTED`
- `LOW_VALUE_PANEL_DOMINATES`
- `REDUNDANT_MAIN_PANEL`

These are review signals. Some may be justified by geometry, but justification must be explicit.

---

## Promotion logic

A visually attractive layout must not be promoted when its visual hierarchy contradicts the scientific hierarchy.

Promotion requires:

- scientific gates pass;
- main claims remain covered;
- area allocation does not materially invert contribution priority;
- dense panels remain readable;
- no high-value panel is demoted merely to simplify layout;
- final rendered review confirms the intended emphasis.

---

## Final principle

> The largest panel should usually communicate the largest scientific contribution, unless density or journal geometry provides a documented reason otherwise.
