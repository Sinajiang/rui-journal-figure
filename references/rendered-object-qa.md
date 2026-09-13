# Rendered-object QA

## Why v1.1 adds a second QA layer

A PDF can pass page-edge clipping checks and still fail visually.

Typical internal failures include:

- text crossing a card boundary;
- a legend entering the data viewport;
- an axis title touching a divider;
- a callout overlapping another annotation;
- a colorbar pressing against donor labels;
- a panel label intruding into a title strip;
- a repair that removes one overlap but weakens the figure hierarchy.

Therefore v1.1 separates QA into two layers:

### Layer 1 — production mechanics
Checks:
- page dimensions;
- actual PDF font size;
- page clipping;
- RGB / CMYK / raster properties;
- file integrity.

### Layer 2 — rendered-object geometry
Checks:
- panel rectangles;
- semantic zones;
- text bounding boxes;
- reserved title / data / legend / annotation regions;
- cross-panel gutter violations;
- text-text overlap;
- text-boundary crossings;
- potential text-drawing collisions.

## Semantic-zone contracts

A reliable figure should declare explicit normalized regions:

- `panel`
- `title_zone`
- `data_zone`
- `legend_zone`
- `annotation_zone`
- `colorbar_zone`
- `card_zone`

The QA engine can then test whether rendered objects remain inside their intended region.

This is stronger than trying to infer layout meaning from the PDF after export.

## Severity

### BLOCKING
- text outside page;
- text crossing a declared card boundary;
- legend text inside a protected data zone;
- panel object crossing into another panel;
- text-text overlap exceeding tolerance;
- object violates an explicit forbidden region.

### REVIEW
- potential text-line collision;
- text close to a border;
- unusually small gutter;
- dense annotation cluster;
- drawing geometry intersects a text box where semantic intent is unknown.

Review-level findings require rendered visual inspection.

## Important limitation

Automated geometry cannot reliably decide whether every text-line intersection is bad.

For example:
- a tick label is expected to sit near an axis;
- a leader line may intentionally terminate near an annotation;
- a box outline may surround text.

Therefore the tool should not blindly fail every text-drawing intersection.

Use:
- explicit semantic zones for hard rules;
- geometric heuristics for review flags;
- final-size human visual review for promotion.
