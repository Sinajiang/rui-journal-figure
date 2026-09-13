# v2.5 automatic annotation / legend checklist

- [ ] Every candidate item is `DIRECT`, `LEGEND`, or `SUPPRESS`.
- [ ] Anchor claims show effect magnitude and uncertainty when required.
- [ ] Multiplicity-aware statistics outrank redundant raw P values.
- [ ] Numeric CI is not repeated when graphical CI already communicates the interval, unless exact bounds matter.
- [ ] `n` is direct only when denominator variation/attrition is interpretive.
- [ ] Direction prose is removed when direction is visually obvious.
- [ ] Method prose does not occupy the data viewport.
- [ ] Repeated statistical definitions are collapsed to shared legend clauses.
- [ ] Repeated group semantics use one shared key where possible.
- [ ] No anchor claim relies on stars alone.
- [ ] Precision does not imply unsupported measurement/model accuracy.
- [ ] Direct annotations fit the v2.4 physical annotation budget.
- [ ] Legend density fits the declared legend budget.
- [ ] Suppressed `required` information has an authorized alternative location.
- [ ] Benchmark conventions are treated as soft priors, never as vetoes over science.
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

