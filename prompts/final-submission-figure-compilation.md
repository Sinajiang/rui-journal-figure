# Prompt — final submission figure compilation

All individual figures have passed final promotion.

Now treat the complete figure set as one manuscript-level artifact.

## 1. Build figure-set manifest
Record:
- exact promoted version;
- scientific authority;
- PDF/TIFF/SVG/preview;
- legend;
- source-data directory;
- provenance;
- style contract.

## 2. Cross-figure audit
Check:
- figure numbering;
- promoted-only status;
- semantic colors;
- font family;
- panel-label case;
- raster resolution;
- legend presence;
- source-data presence.

## 3. Build contact sheet
Inspect the entire set together.

Ask:
- do all figures look like the same manuscript?
- are repeated semantic colors stable?
- is one figure unusually crowded?
- is one workflow disproportionately large?
- does evidence progression match the Results argument?

## 4. Compile package
Create:
- FINAL_SUBMISSION_FIGURES/
- EDITABLE/
- PREVIEWS/
- SOURCE_DATA/
- LEGENDS/
- PROVENANCE/
- QA/
- SHA-256 manifest.

## 5. Reintegration gate
Re-run:
- manuscript figure/panel citations;
- legend architecture;
- Supplementary numbering;
- journal upload contract.

## 6. Promote
Only after automated and manual gates pass may the state become:

`FIGURE_PACKAGE_SUBMISSION_READY`
