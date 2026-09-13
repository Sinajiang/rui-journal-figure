# top-journal-figure-pro v1.4.0

## Benchmark-informed automatic figure planning

### Core change
Figure planning now requires a dual evidence base:

**Methods + Results + source tables + frozen science + top-journal / benchmark papers**

### Added
- internal evidence inventory schema;
- benchmark manifest;
- benchmark-to-study mapping;
- candidate figure-plan schema;
- source-table inspector;
- manuscript section extractor;
- benchmark manifest validator;
- candidate plan validator;
- weighted candidate-plan scorer;
- candidate-plan comparison;
- benchmark-informed planning prompt and checklist.

### Key safeguard
Benchmark-derived panels are classified as:
- DIRECTLY_AVAILABLE
- STRUCTURALLY_ADAPTABLE
- OPTIONAL_NEW_ANALYSIS
- NOT_APPLICABLE

Unavailable evidence cannot enter the promoted plan.

### Intended workflow
internal evidence inventory
→ benchmark search
→ benchmark grammar extraction
→ benchmark-to-study mapping
→ candidate architectures
→ scoring
→ expert promotion
→ figure generation
→ geometry/journal/evidence QA
