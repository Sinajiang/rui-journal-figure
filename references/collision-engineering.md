# Collision engineering

## Why collision QA is difficult

Page-edge clipping is only one failure mode. Many serious defects occur entirely inside the page:

- legend over data;
- annotation over marker;
- title over top strip;
- card text over card border;
- colorbar over labels;
- two text blocks overlapping;
- decorative divider pressing against axis title.

## Required checks

### Text-text
Detect or inspect:
- title vs panel label;
- legend vs annotation;
- labels in compact cards;
- multi-line text with insufficient line spacing.

### Text-geometry
Detect or inspect:
- text vs plotted lines;
- text vs arrow connectors;
- text vs card borders;
- text vs colorbar.

### Panel-panel
Detect or inspect:
- labels crossing gutters;
- legends extending into neighboring axes;
- shared annotation bands.

## Repair strategy

Prefer in this order:

1. move object into dedicated whitespace;
2. widen/tall the container;
3. reduce wording;
4. break title intentionally;
5. move legend outside data viewport;
6. enlarge the entire panel;
7. only then reduce font size.

Do not shrink text below the readable floor merely to make a crowded design fit.

## Surgical repair principle

If the visual architecture is good, do not rebuild the whole figure.

Repair only:
- the panel;
- the label;
- the legend;
- the card;
- the annotation zone;
that actually fails.
