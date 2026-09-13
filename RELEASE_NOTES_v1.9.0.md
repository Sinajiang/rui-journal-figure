# top-journal-figure-pro v1.9.0

## Final submission figure compiler

### Added
- manuscript-level figure-set manifest;
- cross-figure semantic-color audit;
- font/panel-label consistency audit;
- raster DPI audit;
- manuscript-level contact sheet;
- final figure/source-data/legend/provenance compiler;
- SHA-256 package manifest;
- figure-package promotion controller.

### New states
- FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION
- FIGURE_PACKAGE_BLOCKED
- FIGURE_PACKAGE_SUBMISSION_READY

### Principle
Passing single-figure QA is necessary but insufficient. The complete figure set must also pass manuscript-level visual and semantic consistency review.
