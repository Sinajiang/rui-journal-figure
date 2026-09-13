# Real-data figure production engine

## Purpose

v1.8 converts an **architecture-promoted figure plan** into real scientific figure files using explicit source-data mappings.

The production engine is intentionally conservative.

It does not infer:

- which column is the outcome;
- which column is the group;
- which statistic should be plotted;
- whether filtering is permitted;
- whether a transformation is scientifically valid.

Those decisions must be declared in the plotting specification.

The engine then executes the declared contract reproducibly.

---

## Required upstream state

Real-data rendering should begin only after:

1. the architecture candidate is `PROMOTE`;
2. scientific authority is locked;
3. source tables are available;
4. panel-to-source mapping is explicit;
5. frozen sentinels are declared;
6. target journal / dimensions are known.

If these conditions are not met, the renderer should stop rather than guess.

---

## Panel plotting specification

Each panel declares:

- panel ID;
- panel letter;
- chart type;
- source table;
- data filters;
- x / y / group / label fields;
- ordering;
- transformation;
- statistic field;
- uncertainty fields;
- statistical annotation fields;
- color semantics;
- title/subtitle policy;
- legend policy;
- export/source-data requirements.

All filtering must be explicit.

Example:

```yaml
panel_id: P02
panel_letter: B
chart_type: effect_plot
source:
  path: source_effects.tsv
  format: tsv
mapping:
  label: gene
  estimate: logFC
  lower: ci_low
  upper: ci_high
  significance: fdr
filters:
  - column: analysis_set
    op: "=="
    value: primary
```

---

## Supported core chart families

The built-in Python renderer supports a conservative set of reusable chart families:

- `dot_box`
- `paired_dot`
- `effect_plot`
- `lollipop`
- `heatmap`
- `scatter`
- `grouped_bar`
- `evidence_matrix`
- `workflow`

These are not intended to cover every scientific visualization.

When a panel requires a specialized chart:

- keep the data/source contract;
- use a custom renderer;
- preserve the same sentinel / provenance / export QA pathway.

---

## Scientific sentinels

Every promoted real-data figure should define exact frozen values.

Sentinels may validate:

- sample size;
- row count;
- exact effect estimate;
- exact P value;
- exact FDR;
- exact permutation count;
- exact group count;
- exact category set;
- selected-gene list;
- one or more source-table values.

A sentinel mismatch is a hard failure.

Do not "repair" source data in the plotting layer.

---

## Source-data extraction

Every quantitative panel should produce a panel-specific source-data extract containing only the rows / columns needed for the plotted result.

Recommended outputs:

- `Figure_1_Panel_B_source_data.tsv`
- `Figure_1_Panel_C_source_data.tsv`

The source-data extract should preserve:

- original values;
- stable IDs;
- group labels;
- plotted statistic;
- uncertainty;
- annotation fields.

Do not include unrelated participant variables.

---

## Data transformations

Transformations must be declared.

Examples:

- `none`
- `log10`
- `log2`
- `zscore_by_row`
- `zscore_by_column`
- `percent`
- `neglog10`

A transformation should be applied only if scientifically justified upstream.

The rendering engine should not choose transformations for aesthetic reasons.

---

## Filtering rules

Allowed filtering must be explicit in the plotting specification.

Examples:

- exact equality;
- membership in a declared list;
- numeric threshold;
- non-missing restriction.

Every filter should generate:

- rows before;
- rows after;
- filter expression.

Unexpected row loss is a review or hard failure depending on the project contract.

---

## Color semantics

Color is part of the scientific encoding.

The figure-level style contract should map semantic groups to colors.

Examples:

- disease group A;
- disease group B;
- positive direction;
- negative direction;
- significant;
- non-significant;
- contextual evidence;
- missing evidence.

Once a semantic color is accepted, reuse it across the manuscript unless there is a strong reason not to.

---

## Figure-level renderer

The figure renderer should:

1. load the figure specification;
2. validate source paths;
3. validate sentinels;
4. apply declared filters and transformations;
5. render panels;
6. export:
   - PDF;
   - SVG;
   - TIFF;
   - PNG preview;
7. emit panel source-data files;
8. emit provenance JSON;
9. emit render log;
10. run production QA.

---

## Physical sizing

The renderer should use journal-facing dimensions in millimetres.

Do not optimize a figure only in pixel space.

The export contract should specify:

- width mm;
- height mm;
- TIFF DPI;
- font sizes;
- line widths;
- panel-label sizes.

The final PDF remains the authoritative geometry object for text-size and collision auditing.

---

## Separation of concerns

### Scientific layer
Defines:
- what should be plotted;
- what each value means;
- what transformations are allowed.

### Rendering layer
Defines:
- axes;
- markers;
- line widths;
- spacing;
- labels;
- legends.

### QA layer
Verifies:
- sentinels;
- dimensions;
- fonts;
- collisions;
- journal constraints;
- source traceability.

Do not let the rendering layer silently change scientific semantics.

---

## Production failure policy

Stop with a hard failure when:

- a required source file is missing;
- a mapped column is missing;
- a sentinel fails;
- a filter removes unexpected required evidence;
- a panel requests an unavailable analysis;
- a source-data output cannot be reconstructed.

Visual repair may continue only after scientific integrity passes.

---

## Final promotion

A successful render is not automatically a promoted final figure.

The real-data figure must still pass:

- scientific sentinel QA;
- layout / collision QA;
- actual PDF font-size QA;
- journal-contract validation;
- evidence-graph reintegration;
- final-size manual visual review.

Only then may it become the new accepted figure baseline.
