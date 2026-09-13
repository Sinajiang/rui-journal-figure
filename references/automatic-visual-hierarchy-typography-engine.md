# Automatic visual hierarchy and typography engine

## Purpose

v2.4 converts scientific hierarchy into a controlled visual hierarchy.

Inputs:

- v2.2 contribution weights;
- v2.3 benchmark-derived layout grammar;
- solved panel rectangles;
- journal physical dimensions;
- panel content/label counts.

Outputs:

- hierarchy tier for every panel;
- typography budget;
- annotation budget;
- legend/direct-label strategy;
- line/marker emphasis;
- label-density warnings;
- render-spec style overrides.

The engine is designed to prevent two common failure modes:

1. visually equal treatment of scientifically unequal evidence;
2. excessive typography variation that makes a paper look stylistically inconsistent.

---

## Priority order

1. scientific correctness;
2. journal hard requirements;
3. final-size readability;
4. scientific contribution hierarchy;
5. cross-figure consistency;
6. benchmark layout grammar;
7. aesthetics.

Typography should reinforce scientific hierarchy, not become decoration.

---

## Hierarchy tiers

Recommended tiers:

### `ANCHOR`
Central result carrying the strongest Results-level claim.

### `MAJOR_SUPPORT`
Strong participant-level, replication, orthogonal, or decisive robustness evidence.

### `SUPPORT`
Useful direct/supporting evidence.

### `CONTEXT`
External context, descriptive secondary result, boundary information.

### `PROVENANCE`
Workflow, cohort provenance, methods schematic.

### `SUPPLEMENTARY`
Evidence retained outside the main figure set.

The tier derives primarily from the scientific contribution score and role.

---

## Typography principle

The manuscript should still look like one coherent paper.

Therefore:

- panel labels stay globally consistent;
- font family stays globally consistent;
- axis/tick/annotation sizes vary only within narrow bounds;
- scientific emphasis should rely more on panel area, whitespace, marker/line emphasis, and annotation priority than dramatic font changes.

Do not make an anchor panel look like a presentation slide.

---

## Physical-size budgeting

All budgets should be based on physical panel size in millimetres.

For every panel compute:

- panel width mm;
- panel height mm;
- axis-label budget;
- tick-label budget;
- annotation-line budget;
- annotation-character budget;
- legend-item budget.

A panel that is physically narrow should not be rescued by shrinking text below the minimum font floor.

Instead prefer:

1. shorten/wrap labels;
2. thin tick labels;
3. rotate labels if scientifically legible;
4. use direct labels;
5. move legend outside the data viewport;
6. enlarge panel area;
7. change chart orientation;
8. only then consider a small font reduction within the allowed floor.

---

## Operational typography floor

The skill may use a configurable operational minimum font size as a QA floor.

This is **not** a claim about a journal requirement unless that journal profile explicitly states it.

Recommended default operational floor:

`5.5 pt`

The project or journal contract may require a larger value.

---

## Emphasis mapping

A typical bounded mapping:

| Tier | Axis/tick adjustment | Marker scale | Line scale | Annotation priority |
| --- | --- | --- | --- | --- |
| ANCHOR | +0.2–0.3 pt | 1.15 | 1.12 | highest |
| MAJOR_SUPPORT | baseline | 1.05 | 1.05 | high |
| SUPPORT | baseline | 1.00 | 1.00 | moderate |
| CONTEXT | 0 to −0.1 pt | 0.95 | 0.95 | low |
| PROVENANCE | baseline | 0.95 | 0.95 | minimal |

Panel-label typography remains uniform.

---

## Annotation budget

Annotations should be treated as scarce figure real estate.

Every panel should declare:

- maximum annotation lines;
- maximum annotation characters;
- priority annotation IDs;
- optional annotation IDs;
- whether the annotation can be moved to the legend.

When a budget is exceeded:

- remove explanatory prose first;
- retain the scientific statistic that directly supports the claim;
- move methods detail to the legend;
- never remove uncertainty/statistical information merely to make the panel cleaner when it is required for interpretation.

---

## Tick-label density

The engine should estimate a physical tick-label capacity.

If observed labels exceed the budget, possible actions include:

- thinning tick positions;
- abbreviating labels;
- using grouped/faceted labels;
- switching orientation;
- moving exhaustive labels to Supplementary;
- allocating more panel width.

Do not automatically hide scientifically meaningful categories.

---

## Legend strategy

Use the benchmark grammar as a soft prior.

Possible strategies:

- direct labels;
- panel-local legend;
- shared bottom;
- shared right;
- shared top;
- no legend.

Prefer direct labels when:

- series count is small;
- labels can be placed without collision;
- benchmark grammar supports it;
- semantic colors remain clear.

Prefer a shared legend when:

- the same semantic groups recur across panels;
- multiple local legends would duplicate information.

---

## Marker and line grammar

Repeated scientific semantics should reuse:

- marker shape;
- filled/open meaning;
- line style;
- uncertainty encoding.

Anchor emphasis may use slightly stronger marker/line weight, but never change semantic meaning.

For example, if open markers mean non-significant results, an anchor panel must not use open markers merely to look visually lighter.

---

## Hierarchy inversion

Flag when a clearly higher-contribution panel receives:

- smaller effective area;
- smaller typography;
- weaker marker/line emphasis;
- lower annotation priority;

than a lower-contribution panel without an explicit density or semantic justification.

Area inversion is handled in v2.2; v2.4 adds typography/emphasis inversion checks.

---

## Cross-figure consistency

At manuscript level verify:

- same panel-label size;
- same font family;
- same semantic colors;
- similar axis/tick hierarchy;
- comparable annotation conventions;
- stable line/marker semantics.

A figure can locally differ when its data density requires it, but the exception should be declared.

---

## Render integration

v2.4 can inject a `visual_hierarchy` block into each panel of the real-data render specification.

Example:

```yaml
visual_hierarchy:
  tier: ANCHOR
  axis_label_size_pt: 6.7
  tick_label_size_pt: 5.9
  annotation_size_pt: 6.1
  marker_size_pt: 4.4
  line_width_pt: 0.9
  max_annotation_lines: 3
  max_annotation_chars: 92
  max_legend_items: 6
```

The renderer should honor these settings where applicable.

---

## Final boundary

The engine optimizes presentation hierarchy.

It does not decide:

- which result is scientifically true;
- whether a claim is causal;
- whether a result should exist;
- whether a new analysis should be run.

Those remain upstream scientific decisions.
