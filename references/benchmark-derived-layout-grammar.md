# Benchmark-derived layout grammar engine

v2.3 learns quantified layout priors from the final selected benchmark corpus.

It records normalized panel rectangles, topology, anchor-panel share, workflow share,
white-space fraction, legend placement, direct-label usage, text density, and role-specific
panel areas. These are aggregated with benchmark relevance weights and combined with the
v2.2 scientific contribution weights.

Priority order:
1. scientific correctness;
2. evidence availability;
3. journal hard requirements;
4. final-size legibility;
5. contribution hierarchy;
6. benchmark layout grammar;
7. aesthetic preference.

The engine learns distributions, never exact benchmark artwork. Any divergence from benchmark
medians is allowed when scientifically or visually justified and should be documented.
