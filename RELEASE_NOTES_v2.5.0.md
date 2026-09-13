# top-journal-figure-pro v2.5.0

## Automatic annotation and legend intelligence

Adds a scientific-information placement engine that assigns every candidate item to `DIRECT`, `LEGEND`, or `SUPPRESS` using benchmark priors, claim importance, statistical necessity, physical annotation capacity, and redundancy rules.

Key additions:

- effect-size / uncertainty-first annotation hierarchy;
- multiplicity-aware P / adjusted P / FDR / q handling;
- automatic suppression of raw P when a superior adjusted statistic represents the same inferential unit;
- CI de-duplication when uncertainty is already graphically encoded;
- sample-size placement logic;
- direction-prose suppression when direction is visually encoded;
- legend density limits and shared-clause de-duplication;
- controlled numerical precision;
- annotation-plan audit and render-spec injection;
- benchmark annotation-statistic priors;
- unified-workflow `ANNOTATION_INTELLIGENCE` stage.
