# top-journal-figure-pro v1.8.1

## Real-data production engine — tested release

v1.8.0 was an internal development snapshot and was not promoted because the new sentinel validator failed test collection due to a Python reserved-keyword syntax error.

v1.8.1 fixes the sentinel validator and re-runs the complete regression suite.

### Production engine capabilities
- declarative real-data render specifications;
- frozen sentinel validation;
- explicit source-table filters;
- panel-specific source-data exports;
- PDF/SVG/TIFF/PNG output;
- provenance logging;
- pre-promotion PDF QA;
- hard stop on sentinel mismatch.

### Governance
A render that passes the engine is still `RENDERED_PRE_PROMOTION` until manual final-size visual review and the broader journal/evidence QA stack pass.
