# top-journal-figure-pro v1.7.0

## Structural prototype and automatic promotion loop

### Added
- low-cost structural prototype generator;
- non-data chart-type glyphs;
- structural visual-quality scoring;
- accepted-baseline comparison;
- surgical repair planner;
- PROMOTE / REPAIR / ROLLBACK / HOLD controller;
- prototype promotion-loop orchestrator;
- baseline and promotion-ledger templates.

### Safeguard
Prototypes are explicitly marked:

`STRUCTURAL PROTOTYPE — NO DATA`

They must never contain fabricated scientific values.

### Core loop
architecture candidate
→ structural prototype
→ visual scoring
→ accepted-baseline comparison
→ PROMOTE / REPAIR / ROLLBACK
→ real-data rendering only after architecture promotion
