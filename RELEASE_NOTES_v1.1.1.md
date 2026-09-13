# top-journal-figure-pro v1.1.1

## Production-hardening release

### Added in v1.1
- semantic layout contracts;
- rendered text/drawing geometry audit;
- diagnostic overlay PDF generation;
- terminal QA orchestrator;
- synthetic geometry tests.

### Fixed in v1.1.1
- synthetic "clean" fixture now has sufficient axis-label clearance;
- geometry tests import the audit function directly instead of printing a large JSON payload through a subprocess pipe;
- CLI now prints a concise summary by default;
- full geometry report is written with `--out`;
- text-drawing review findings are capped in the in-memory payload while total counts are preserved.

## Known limitations

The geometry engine deliberately treats text-drawing intersections as REVIEW, not automatic failure.

Reason:
- axis/tick geometry may legitimately intersect or approach text bounding boxes;
- leader lines intentionally terminate near annotations;
- card borders intentionally surround text.

Hard failures should rely on:
- text-text overlap;
- explicit semantic-zone violations;
- card-boundary violations;
- protected-gutter violations;
- page clipping.

Final-size visual inspection remains mandatory.
