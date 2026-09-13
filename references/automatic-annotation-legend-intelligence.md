# Automatic annotation and legend intelligence

## Purpose

v2.5 decides **what statistical information deserves scarce figure real estate** and whether each item belongs as a direct annotation, in the figure legend, or nowhere in the final figure package.

This layer sits after contribution-aware layout/typography and before prototype rendering. It does not change scientific results. It changes only the placement, redundancy, precision, and density of already-authorized information.

## Inputs

The engine uses four evidence classes:

1. **Internal scientific authority** — Results, Methods, source tables, evidence graph, frozen sentinels.
2. **Claim importance** — anchor/support/context role and contribution score.
3. **Statistical necessity** — whether interpretation requires effect magnitude, uncertainty, multiplicity information, sample size, or direction.
4. **Benchmark grammar** — how closely matched high-quality papers distribute direct labels, legends, uncertainty and significance information.

Benchmark behavior is a soft prior. It never overrides scientific correctness, journal rules, or final-size legibility.

## The three-way decision

Every candidate annotation must receive exactly one disposition:

- `DIRECT` — printed in or immediately adjacent to the data viewport;
- `LEGEND` — retained in the panel/figure legend but removed from the plot body;
- `SUPPRESS` — removed because it is redundant, visually encoded already, statistically inferior to a preferred quantity, or irrelevant to the claim.

`SUPPRESS` never means deleting required information from the scientific record. Required detail may remain in source data, Methods, Results, table, or Supplementary material.

## Information hierarchy

Default information priority:

1. effect magnitude;
2. uncertainty / confidence interval;
3. multiplicity-aware significance (`FDR`, `q`, adjusted P);
4. raw P when it is the authorized primary inferential quantity and no superior adjusted measure applies;
5. sample size and denominator context;
6. direction text;
7. methods prose.

This is not a universal statistical ranking. It is a **figure-real-estate priority** designed for biomedical results figures.

## Effect size

Directly annotate an effect estimate when all of the following are substantially true:

- the panel carries an anchor or major-support claim;
- the exact magnitude materially affects interpretation;
- the estimate is not already obvious from a labeled axis/table-like encoding;
- the label can be placed collision-free at final size.

When the effect estimate is already the plotted coordinate in an effect/forest plot, avoid repeating the same number on every mark unless the benchmark grammar strongly supports numeric columns and the panel remains visually restrained.

Effect size normally outranks a significance label.

## Confidence intervals

If the CI is already shown graphically with whiskers/bands/error bars, the default is:

- keep the uncertainty encoding;
- define the interval once in the legend (for example, `95% CI`);
- suppress repeated numeric CI text from the data viewport.

Direct numeric CI text is justified when the exact interval bounds are essential to the claim, the interval is not otherwise visible, or a journal/benchmark convention strongly favors a compact numeric effect-plus-CI column.

## P values, adjusted P, FDR and q values

When multiplicity correction applies, prefer the authorized adjusted quantity. Do not mechanically show raw P and FDR/q side by side for the same comparison.

Default placement:

- anchor, sparse primary comparison: direct adjusted significance may be justified;
- multiple endpoints/features: legend or encoded significance, with exact values in source data/table where needed;
- context/secondary panels: direct P labels require stronger justification;
- raw P is suppressed when an authorized adjusted value for the same inferential unit is already shown, unless both are scientifically necessary.

Stars may be used as a compact secondary encoding only when exact statistical reporting exists elsewhere. Stars must never be the only statistical reporting for an anchor claim.

## Sample size (`n`)

Sample size is usually legend context, not a repeated plot annotation.

Place `n` directly only when:

- denominators vary materially across displayed groups/time points;
- attrition/missingness is part of the scientific interpretation;
- the panel itself is a participant-flow or denominator panel;
- benchmark/journal convention and legibility support direct `n` labels.

Repeated identical `n` labels across panels should collapse to one legend clause.

## Direction annotations

Words such as `higher`, `lower`, `increased`, `decreased`, `positive`, or `negative` should be suppressed when direction is already clear from position, sign, axis, arrow, or stable semantic color.

Direction text is retained directly only when the visual encoding is genuinely ambiguous or the panel is categorical/qualitative rather than metric.

## Legend density

A figure legend is not a second Results section.

The engine should separate legend content into:

- statistical definitions shared once per figure;
- panel-specific statistical clauses;
- method/encoding clauses;
- sample-size/denominator clauses.

Repeated definitions such as `error bars indicate 95% CI` should appear once. Repeated group-color definitions should use a shared semantic key when possible. Panel legends should not restate values already visible in the panel.

## Precision policy

Precision should reflect inferential need rather than source-table decimal noise.

Defaults:

- P/FDR/q: three decimals; values below 0.001 use inequality notation unless an exact small value is required for reproducibility or a prespecified threshold;
- effect sizes and CI: generally two meaningful decimal places/significant digits, adapted to scale;
- n: integers;
- percentages: precision consistent with denominator size and source authority.

Never create apparent precision that exceeds the underlying measurement or model output.

## Benchmark integration

Benchmark extraction should record, where feasible:

- fraction of effect sizes directly printed;
- fraction of CIs numerically printed vs graphically encoded;
- direct P/FDR/q usage;
- direct `n` usage;
- direction-text usage;
- significance style (`exact`, `threshold`, `stars`, `none`);
- legend statistical density.

These become weighted priors. Strong benchmark support can resolve a close `DIRECT` vs `LEGEND` decision, but cannot rescue a scientifically redundant label.

## Density control

The planner must honor the v2.4 physical annotation budget. If the scientifically justified direct annotations exceed capacity:

1. keep required effect/uncertainty information;
2. move significance details to the legend;
3. move repeated n/method detail to shared legend text;
4. suppress direction prose that the graphic already conveys;
5. enlarge/restructure the panel before reducing font below the operational floor.

## Audit failures

Blocking or review conditions include:

- both raw P and adjusted P/FDR/q shown for the same inferential unit without explicit justification;
- numeric CI repeated directly despite a complete CI graphical encoding and no exact-bound justification;
- required uncertainty omitted from an effect claim;
- method prose occupying the data viewport;
- repeated identical `n` labels across multiple panels;
- direct direction prose duplicating obvious visual direction;
- anchor claim represented only by significance stars;
- legend density exceeding the declared budget;
- a suppressed item marked `required` without an alternative authorized location.

## Final boundary

The engine governs **presentation**, not inferential authority. It must never recalculate, reinterpret, or replace frozen statistical results.
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

