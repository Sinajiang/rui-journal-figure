# top-journal-figure-pro v1.3.0

## Evidence-aware figure intelligence

### Added
- bidirectional evidence graph;
- figure/panel citation extraction;
- evidence-graph audit;
- legend-architecture audit;
- supplementary numbering audit;
- manuscript–figure reintegration QA orchestrator;
- claim-strength / evidence-status review flags.

### Core model
manuscript claim → figure → panel → source data → statistic → legend → citation

### Governance
The structural scripts do not replace scientific judgment. They verify declared mappings and expose inconsistencies.

### Typical use
After a figure redesign:
1. update promoted panel architecture;
2. rebuild or update evidence graph;
3. run citation/legend/supplementary audits;
4. make the minimum manuscript edits;
5. lock the exact manuscript + figure + legend version.
