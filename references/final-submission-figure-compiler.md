# Final submission figure compiler

## Purpose

v1.9 compiles individually promoted figures into a **manuscript-level submission figure package**.

Single-figure QA is not enough.

A manuscript can contain four individually acceptable figures that still fail as a set because:

- the same group changes color between figures;
- panel labels use different cases or sizes;
- axis typography drifts;
- one figure uses a different font family;
- one TIFF is 300 dpi while the others are 600 dpi;
- figure filenames and manuscript citations disagree;
- source-data files are incomplete;
- legends describe outdated versions;
- visual density varies so much that the manuscript feels assembled from unrelated branches.

The compiler therefore treats the complete figure set as a single submission artifact.

---

## Preconditions

Only figures with promoted status should enter the compiler.

Every figure should already have:

- scientific authority;
- promoted version;
- final PDF;
- final TIFF or required raster alternative;
- editable vector source when appropriate;
- preview PNG;
- source-data mapping;
- provenance;
- final-size visual QA;
- journal-contract QA;
- evidence-graph QA.

If a figure is still `RENDERED_PRE_PROMOTION`, it should not be compiled as final.

---

## Figure-set manifest

The compiler uses a manuscript-level manifest.

For every figure record:

- figure number;
- promoted version;
- scientific authority;
- PDF path;
- SVG path;
- TIFF path;
- preview path;
- legend file / legend text source;
- source-data directory;
- provenance file;
- semantic-color contract;
- font family;
- panel-label style;
- physical width / height;
- raster DPI;
- journal stage.

---

## Cross-figure consistency checks

### 1. Semantic colors

A semantic meaning should not change color across figures.

Examples:
- VM group;
- migraine group;
- control;
- positive direction;
- negative direction;
- missing evidence;
- contextual evidence.

The compiler should compare declared semantic colors and flag inconsistencies.

A color may differ only if:
- the semantic meaning differs;
- the figure contract explicitly declares a local exception.

### 2. Typography

Check:
- font family;
- base font size;
- panel label size;
- panel-label case;
- weight;
- mathematical notation consistency.

Do not force identical font size when one figure has a justified journal-compliant exception, but require explicit declaration.

### 3. Panel labels

Across main figures, panel labels should normally use one convention:
- uppercase A/B/C/D; or
- lowercase a/b/c/d.

Do not mix conventions accidentally.

### 4. Physical dimensions

Figure widths should follow the target journal's accepted width system.

A manuscript can legitimately mix single- and double-column figures, but the set should declare why.

### 5. Line / marker grammar

Where the same semantic encoding recurs:
- open marker;
- filled marker;
- significance marker;
- reference line;
- uncertainty interval;
should remain stable or be explicitly explained.

### 6. Visual hierarchy

Review manuscript-level balance:
- figure count;
- panel count distribution;
- average density;
- schematic fraction;
- anchor-panel prominence.

This is partly automated and partly manual.

---

## Legend synchronization

The compiler should verify:

- Figure 1 legend maps to Figure 1 final panel architecture;
- panel order matches artwork;
- statistical definitions match current figure;
- source / cohort naming is current;
- no retired panel descriptions remain;
- Supplementary numbering remains stable.

A legend mismatch is a blocking submission defect.

---

## Source-data package

The compiler should assemble:

```text
SOURCE_DATA/
├── Figure_1/
│   ├── Figure_1_Panel_B_source_data.tsv
│   └── ...
├── Figure_2/
└── ...
```

Each main quantitative panel should resolve to a source-data extract.

The package should not contain:
- unrelated participant variables;
- unused source tables;
- superseded source files unless explicitly retained for reproducibility.

---

## Contact sheet

Create a manuscript-level contact sheet containing all promoted figure previews.

Purpose:

- inspect cross-figure typography;
- inspect color semantics;
- inspect density;
- inspect visual hierarchy;
- catch one figure that visually belongs to a different design branch.

A contact sheet is a QA artifact, not a submission figure.

---

## Cross-figure visual QA

Manual review should answer:

- Do all figures look like they belong to the same paper?
- Is the strongest result visually prominent?
- Are workflow/schematic panels proportionate?
- Is any figure obviously more crowded or more decorative than the others?
- Does the color language remain stable?
- Are repeated scientific concepts encoded consistently?
- Does figure progression support the manuscript argument?

A compiler should not auto-fix global style inconsistencies without review.

---

## Submission package layout

Recommended output:

```text
FINAL_SUBMISSION_FIGURES/
├── Figure_1.pdf
├── Figure_1.tiff
├── Figure_2.pdf
├── Figure_2.tiff
└── ...

EDITABLE/
├── Figure_1.svg
└── ...

PREVIEWS/
├── Figure_1_preview.png
└── ...

SOURCE_DATA/
├── Figure_1/
└── ...

LEGENDS/
├── Figure_1_legend.txt
└── ...

PROVENANCE/
├── Figure_1_provenance.json
└── ...

QA/
├── cross_figure_consistency.json
├── figure_set_contact_sheet.png
├── file_integrity.json
└── final_submission_figure_qa.md

MANIFEST_SHA256.json
```

The target journal may require different upload organization.
The compiler should preserve journal-specific filenames if explicitly required.

---

## Exact-version integrity

Every compiled package should record:

- exact promoted figure version;
- SHA-256 for every deliverable;
- source authority;
- compilation timestamp;
- target journal;
- journal profile retrieval date.

If any final figure is changed after compilation, regenerate the package and hashes.

---

## Blocking failures

Do not mark the figure package submission-ready when:

- an unpromoted figure is included;
- a required final PDF/TIFF is missing;
- semantic colors conflict without an exception;
- figure numbering is duplicated or discontinuous;
- a final legend is missing;
- a quantitative figure lacks source-data mapping;
- final file hash cannot be computed;
- a required journal format fails;
- final-size visual review is incomplete.

---

## Final state

Successful compilation yields:

`FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION`

It becomes:

`FIGURE_PACKAGE_SUBMISSION_READY`

only after:
- automated cross-figure gates pass;
- manual contact-sheet review passes;
- manuscript figure citations / legends pass reintegration QA;
- target-journal upload contract is confirmed.
