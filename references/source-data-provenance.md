# Source-data provenance

Every quantitative panel should be traceable.

For each panel record:

- source file;
- rows/columns used;
- sample identifiers;
- transformations;
- plotted statistic;
- error-bar definition;
- statistical annotation source;
- exclusions;
- frozen-value sentinels.

## Sentinel values

Store several exact values that must match the scientific authority.

Examples:
- primary effect estimate;
- P value;
- FDR;
- sample size;
- number of permutations;
- one or more key gene estimates.

If a plotting script produces a sentinel mismatch, stop.

## No silent repair

Never silently:

- impute;
- filter;
- change factor order;
- change aggregation;
- drop missing observations;
- alter labels.

Any required change must be recorded.
