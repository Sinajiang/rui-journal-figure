# Prompt — automatic annotation and legend intelligence

Read the manuscript Methods and Results, source tables, evidence graph, contribution hierarchy, solved layout, journal contract, and benchmark layout/annotation grammar.

For every panel, enumerate candidate statistical/semantic annotations and assign exactly one disposition: `DIRECT`, `LEGEND`, or `SUPPRESS`.

Use this priority order:

1. scientific correctness and frozen authority;
2. claim importance;
3. statistical necessity;
4. effect magnitude and uncertainty;
5. multiplicity-aware significance;
6. benchmark support;
7. final-size legibility and annotation budget;
8. density minimization.

Specific rules:

- prefer effect size + uncertainty over significance-only decoration;
- if an authorized FDR/q/adjusted P exists for the same multiplicity-controlled inferential unit, suppress raw P unless both are explicitly necessary;
- if CI is already fully encoded by whiskers/bands, suppress repeated numeric CI text by default and define the CI once in the legend;
- put n in the legend unless varying denominators/attrition are themselves interpretive;
- suppress direction prose when direction is visually obvious;
- move methods prose out of the data viewport;
- do not use stars as the only statistical information for an anchor claim;
- do not exceed v2.4 annotation/legend budgets; restructure before shrinking fonts.

Return:

- a structured annotation candidate inventory;
- a machine-readable annotation decision plan;
- a direct-annotation list ordered by placement priority;
- a compact legend plan with shared clauses deduplicated;
- suppressed-item audit with explicit reasons;
- review flags for ambiguous or scientifically unsafe cases.
## v2.5.1 audit corrections

- Raw P may be suppressed by adjusted significance only when both refer to the same **figure, panel, and inferential unit**. A reused group name elsewhere is insufficient.
- CI candidates may carry structured `lower`, `upper`, and `interval_level` values; a CI is not assumed to be a single scalar.
- Effect candidates may carry `effect_metric` so OR/HR/beta/MD/rho or another authorized metric is preserved rather than relabeled.
- `estimate_encoded=true` now reduces redundant numeric effect labeling unless the exact magnitude is required/high-importance.
- Invalid significance values, non-positive/non-integer sample sizes, reversed CI bounds, and invalid interval levels are blocking defects.
- If legend density remains above budget after safe de-duplication, promotion blocks for restructuring. Required/high information is never silently removed merely to satisfy density.
- The approved annotation plan is automatically bound to each real-data render spec by figure + panel before rendering. This binding governs content disposition; exact geometric placement still follows the panel renderer/layout contract and final visual QA.
### Decision-preserving precision

Automatic rounding must preserve inferential interpretation around the null. For ratio measures such as OR/HR/RR the default null is 1; for difference/correlation/regression scales the default null is 0 unless an explicit `null_reference` is supplied. If nominal significant-digit rounding would move a bound or estimate onto/across the null, increase displayed precision until the original side of the null is preserved.

### Binding to real-data rendering

The approved plan is binding in the real-data workflow. It is injected into the matching figure/panel render spec automatically. `DIRECT` items are rendered in a restrained panel statistical block, `LEGEND` items are materialized as an annotation-legend fragment for manuscript reintegration, and `SUPPRESS` items are excluded from the figure annotation layer. Final-size collision and manual visual QA remain mandatory.

