# top-journal-figure-pro v2.5.1

## Corrective audit release for automatic annotation and legend intelligence

This release corrects issues found during post-release audit of v2.5.0. No v2.4 layout, contribution-weighting, or visual-hierarchy science is changed.

Corrections:

- scope raw-P suppression to the same **figure + panel + inferential unit**, preventing an adjusted statistic in another panel from suppressing an unrelated raw P;
- support structured confidence intervals with `lower`, `upper`, and `interval_level` rather than treating CI as a single scalar only;
- support explicit effect-size metric labels (`OR`, `HR`, `beta`, `MD`, `rho`, etc.) and avoid duplicated prefixes;
- preserve the side of the inferential null during automatic rounding (ratio-scale null 1; difference/correlation/regression-scale null 0 unless explicitly overridden);
- make `estimate_encoded` operational so visually encoded effect magnitudes reduce redundant numeric labeling unless the value is claim-critical;
- prioritize effect magnitude and uncertainty when the direct-annotation physical budget forces demotion;
- validate P/FDR/q/adjusted-P range, positive integer n, ordered CI bounds, and valid interval level;
- treat unresolved legend over-density as a blocking restructure requirement rather than allowing a nominal PASS;
- treat repeated required information collapsed to an authorized shared legend clause as a valid alternative representation;
- scope render-spec injection by **figure + panel**, preventing same-named panels in different figures from receiving the wrong plan;
- automatically bind the approved annotation plan to each real-data render spec inside the unified workflow before rendering; DIRECT items are rendered as a restrained panel statistical block and LEGEND items are materialized as a legend fragment;
- replace the awkward repeated-n phrase with `n=... throughout unless otherwise indicated`;
- update release metadata and add regression tests for the audit findings.
