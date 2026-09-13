# Prompt — real-data figure production

The architecture has already been promoted.

Use only the declared real source data.

## 1. Build render specification
For every panel declare:
- source table;
- mapped columns;
- filters;
- transformations;
- chart type;
- ordering;
- uncertainty;
- statistical annotations;
- semantic colors;
- layout position.

Do not infer missing mappings.

## 2. Lock sentinels
Declare exact frozen sentinels before rendering.

At minimum include:
- relevant row/sample count;
- one or more key effect/statistical values;
- critical category/status sets when applicable.

## 3. Validate
Run:
- render-spec validation;
- sentinel validation;
- source-path / column validation.

Any sentinel failure blocks rendering promotion.

## 4. Render
Export:
- PDF
- SVG
- TIFF
- preview PNG
- panel source-data TSVs
- provenance JSON

## 5. QA
Run:
- actual PDF font audit;
- geometry/collision audit;
- layout-contract audit where available;
- journal contract validation;
- final-size visual review.

## 6. Reintegration
After figure promotion:
- update manuscript panel citations;
- update legend;
- verify evidence graph;
- rebuild exact submission package.

Do not change scientific values in order to improve visual appearance.
