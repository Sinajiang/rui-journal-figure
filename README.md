# top-journal-figure-pro

A contract-first, evidence-architecture, collision-free workflow for generating submission-grade scientific figures for high-impact biomedical journals.

## Purpose

`top-journal-figure-pro` is designed for manuscript main figures, Extended Data / Supplementary figures, study-design schematics, cross-dataset evidence maps, mechanistic diagrams, and graphical-abstract drafts.

The skill is intentionally stricter than a generic plotting workflow. It treats a scientific figure as four coupled products:

1. **Scientific evidence object** — the figure must support a specific manuscript claim.
2. **Visual communication object** — the claim must be legible at the journal's final physical size.
3. **Reproducible data object** — every quantitative element must map back to source data.
4. **Submission artifact** — the exported PDF/SVG/TIFF must survive journal upload and manuscript integration.

## Core rule

> One figure should answer one Results-level scientific question.  
> Each panel must contribute a distinct piece of evidence.

## Design philosophy

The workflow is built around five principles:

- **Contract before drawing**: define the scientific claim, evidence roles, data sources, and journal constraints first.
- **Evidence architecture before aesthetics**: choose panels because they answer different inferential subquestions.
- **Visual restraint**: high-impact figures should be information-dense, not poster-like or decorative.
- **Baseline lock + surgical repair**: once a scientifically strong layout exists, repair local defects without casually rebuilding the entire figure.
- **Rendered visual QA is mandatory**: automated checks are necessary but never sufficient.

## Why this skill exists

Common failure modes in iterative manuscript-figure work include:

- text looks fine in code but overlaps after PDF/TIFF export;
- legends invade the data viewport;
- fixing one collision creates another;
- panel layouts become progressively weaker after repeated “cleanup”;
- AI-generated raster previews look attractive, but submission files render poorly;
- flow diagrams become visually dominant while quantitative evidence becomes secondary;
- a figure passes page-edge clipping checks but still has internal text/line/annotation collisions.

This skill explicitly treats those as **blocking defects**, not cosmetic issues.

## Workflow

### Phase 0 — Authority and data lock

Before figure work begins:

- identify the scientific authority / frozen analysis version;
- identify the manuscript version;
- identify the source-data files;
- define whether re-analysis is permitted;
- create immutable sentinels for key numerical results.

No plotting script may silently alter:

- sample size,
- gene/feature selection,
- statistical model,
- threshold,
- normalization,
- P value / FDR,
- effect direction,
- subgroup definition,
- evidence-status semantics.

### Phase 1 — Figure contract

Create a contract using `templates/figure_contract.yaml`.

Required fields:

- figure-level claim;
- target journal;
- physical width / height;
- primary evidence panel;
- supporting evidence panels;
- source-data map;
- frozen numerical sentinels;
- panel-specific scientific roles;
- allowed transformations;
- forbidden changes.

### Phase 2 — Evidence architecture

Use `references/evidence-architecture.md`.

For each panel define one role:

- anchor / primary result;
- direct replication;
- orthogonal support;
- robustness / sensitivity;
- participant-level support;
- disease or state context;
- mechanism;
- boundary / limitation;
- workflow / provenance.

If two panels answer the same question with no added inferential value, one should normally be removed or moved to Supplementary / Extended Data.

### Phase 3 — Chart selection

Use `references/chart-selection.md`.

Default mapping:

- individual-level distributions → dot + box / violin / raincloud;
- paired data → paired slope / connected dot;
- effect estimates → forest / interval plot;
- many genes × datasets → heatmap / evidence matrix;
- differential-expression overview → volcano / MA;
- cross-dataset agreement → scatter with identity/reference lines;
- donor sensitivity → leave-one-out lollipop / influence plot;
- categorical provenance → grouped bars / compact cohort diagram;
- workflow → compact schematic;
- mechanism → schematic only when supported by evidence.

### Phase 4 — Baseline generation

The first serious version should establish:

- global layout;
- group colors;
- panel order;
- typographic hierarchy;
- legend strategy;
- axis conventions;
- annotation density;
- source-data traceability.

Do not over-optimize micro-spacing before the architecture is correct.

### Phase 5 — Baseline lock

When the scientific and visual hierarchy is strong, create a baseline lock using `checklists/baseline-lock.md`.

After baseline lock:

- prefer **surgical repair** over complete rebuild;
- change only the defective panel or local object;
- preserve accepted visual hierarchy unless the defect is structural;
- keep a repair ledger.

### Phase 6 — Collision-free repair

Every modification must be followed by:

1. final-size render;
2. visual inspection;
3. geometric collision audit;
4. actual PDF-font-size audit;
5. panel alignment audit.

A figure is blocked if any reliable collision exists between:

- text ↔ text;
- text ↔ line / curve;
- text ↔ marker;
- legend ↔ data viewport;
- annotation ↔ axis label;
- panel label ↔ title;
- card text ↔ card boundary;
- colorbar ↔ donor/axis labels;
- panel content ↔ neighboring panel gutter.

### Phase 7 — Terminal visual QA

The final decision is made on **rendered final files**, not code or previews.

Review at:

- 100% final physical size;
- reduced manuscript-view size;
- high-resolution zoom.

Automated QA passing does not equal visual acceptance.

### Phase 8 — Submission integration

Only after figure lock:

- replace manuscript upload figures;
- verify figure citations;
- verify legends;
- verify supplementary numbering;
- regenerate portal package;
- inspect manuscript proof / portal-rendered preview.

## Output contract

A complete figure-delivery package should contain:

- `Figure_X.pdf` — preferred editable/vector submission version;
- `Figure_X.svg` — editable source when appropriate;
- `Figure_X.tiff` — journal-ready raster fallback;
- `Figure_X_preview.png` — review-only preview;
- source-data table;
- panel evidence map;
- figure contract;
- collision audit JSON;
- alignment audit JSON;
- PDF font audit;
- visual QA checklist;
- change ledger;
- manifest with SHA-256 hashes.

## Hard gates

A figure cannot be promoted when any of the following is true:

### Scientific gate
- number does not match source data;
- sample size differs from locked analysis;
- statistical annotation is unsupported;
- visual encoding changes the meaning of the result;
- figure implies replication or mechanism not supported by data.

### Structural gate
- figure-level claim is unclear;
- multiple panels are redundant;
- anchor panel is visually subordinate to low-value schematic content;
- main figure contains material better suited to Supplementary.

### Visual gate
- overflow;
- overlap;
- clipping;
- line-through-text;
- labels touching markers;
- excessive legend density;
- unreadable text at final size;
- panel imbalance;
- uncontrolled whitespace;
- poster-like decoration.

### Submission gate
- wrong width;
- wrong resolution;
- incorrect color mode;
- non-editable raster when vector is expected;
- legend embedded when journal requires separate legend;
- file naming or numbering mismatch;
- source-data provenance missing.

## High-impact visual style

Default style:

- white background;
- sparse borders;
- restrained color;
- color meaning fixed across all figures;
- clear anchor panel;
- direct labeling when it reduces legend burden;
- data points shown when sample size is small or moderate;
- uncertainty displayed explicitly;
- avoid 3D effects, shadows, gradients, decorative icons, and unnecessary boxes.

## AI-generated imagery

AI images may be used for:

- concept ideation;
- graphical-abstract drafts;
- non-quantitative schematic exploration.

AI images must **not** be treated as:

- raw data;
- microscopy;
- quantitative experimental evidence;
- a substitute for measured observations.

Any AI-assisted schematic should be scientifically verified, redrawn when needed, and checked against the target journal's current policy.

## Recommended usage

Examples:

- “Use top-journal-figure-pro to redesign these four manuscript figures without changing frozen statistics.”
- “Create a Figure 3 evidence architecture from this Results section and source data.”
- “Audit this PDF for collisions, actual font sizes, and submission readiness.”
- “Keep the current visual baseline and perform surgical repair only.”
- “Compare the current figure against high-impact journal exemplars, but adapt structure rather than copy artwork.”

## Package structure

```text
top-journal-figure-pro/
├── SKILL.md
├── README.md
├── requirements.txt
├── references/
│   ├── evidence-architecture.md
│   ├── chart-selection.md
│   ├── visual-system.md
│   ├── collision-engineering.md
│   ├── source-data-provenance.md
│   └── journal-contracts.md
├── scripts/
│   ├── validate_figure.py
│   ├── audit_pdf_text.py
│   ├── audit_panel_alignment.py
│   ├── audit_figure_collisions.py
│   ├── figure_safety.py
│   ├── render_preview.py
│   └── build_contact_sheet.py
├── templates/
│   ├── figure_contract.yaml
│   ├── panel_evidence_map.tsv
│   ├── source_data_map.tsv
│   ├── visual_qa.yaml
│   └── change_ledger.md
├── checklists/
│   ├── baseline-lock.md
│   ├── panel-review.md
│   ├── terminal-visual-qa.md
│   └── submission-qa.md
├── prompts/
│   ├── figure-planning.md
│   ├── surgical-repair.md
│   ├── hostile-visual-review.md
│   └── journal-benchmarking.md
└── examples/
    └── biomedical-four-figure-plan.md
```


## v2.2 contribution-weighted autonomous workflow

v1.1 adds a semantic geometry layer so collision QA no longer depends only on page clipping or text-text overlap.

New components:

- `templates/layout_contract.yaml`
- `scripts/audit_pdf_geometry.py`
- `scripts/audit_layout_contract.py`
- `scripts/make_diagnostic_overlay.py`
- `scripts/terminal_qa.py`
- `references/rendered-object-qa.md`
- synthetic geometry tests

The intended workflow is now:

> **figure contract → evidence architecture → baseline → layout contract → render → geometry audit → diagnostic overlay → surgical repair → terminal visual QA**

The layout contract makes explicit what the PDF itself cannot reliably infer: which region is a title strip, which region is a data viewport, which whitespace is a protected gutter, and which text must remain inside a card.

## Reference basis

The architecture is informed by the public `nature-figure` skill from Yuan1z0825/nature-skills, especially its emphasis on:

- figure-level claims and panel evidence roles;
- final-size alignment and collision auditing;
- source-data traceability;
- vector-first output;
- actual PDF font-size checks;
- rendered visual review after automated QA.

This package is an original implementation and does not copy third-party assets or templates.


## Production-hardening QA philosophy

`audit_pdf_geometry.py` intentionally distinguishes:

- **BLOCKING**: reliable geometry failures such as text-text overlap.
- **REVIEW**: possible text-drawing interactions that cannot be judged safely without semantic context.

Use `layout_contract.yaml` to convert important semantic expectations into hard rules.  
Use the diagnostic overlay for localization.  
Use manual final-size visual review for the promotion decision.


## v2.2 contribution-weighted autonomous workflow

v1.2 adds versioned, stage-specific external contracts for figure production.

Bundled profiles:
- Nature
- Headache: The Journal of Head and Face Pain
- Brain Communications

Each profile records:
- retrieval date;
- official source URLs;
- stage-specific dimensions;
- font constraints or recommendations;
- resolution;
- preferred formats;
- panel-label rules;
- journal-specific visual guidance.

Important: profiles intentionally preserve unknowns. If an official source does not state a value, the skill must not invent one.

New workflow:

> official journal guidelines → journal profile → figure contract → evidence architecture → baseline → geometry QA → journal validation → terminal visual QA

A benchmark-grammar module is also included. It learns transferable design principles from exemplary papers without copying exact layouts or artwork.


## v2.2 contribution-weighted autonomous workflow

v1.3 closes the gap between a visually correct figure and a manuscript-consistent figure.

New bidirectional evidence model:

> manuscript claim → figure → panel → source data → statistic → legend → manuscript citation

New automated checks:
- figure/panel citations resolve to promoted artwork;
- promoted evidence panels map to claims and sources;
- legends match the actual promoted panel architecture;
- supplementary numbering remains sequential;
- replication/mechanistic/causal language receives evidence-status review flags;
- post-figure-replacement manuscript drift is detected before submission packaging.

The scripts validate explicit mappings. They do not silently infer scientific truth from prose.


## v2.2 contribution-weighted autonomous workflow

v1.4 upgrades planning from manuscript-only reasoning to a dual-evidence system:

> **Methods + Results + source tables + frozen authority + top-journal / benchmark papers**

The skill first inventories the current study's real evidence, then searches and studies benchmark papers to learn:
- which scientific questions strong papers promote to main figures;
- what evidence types are expected;
- how main vs Supplementary material is allocated;
- which panel architectures and chart grammars are transferable.

Benchmark-derived ideas are classified as:
- `DIRECTLY_AVAILABLE`
- `STRUCTURALLY_ADAPTABLE`
- `OPTIONAL_NEW_ANALYSIS`
- `NOT_APPLICABLE`

Only available evidence can enter the promoted figure plan.

The planner can generate multiple candidate architectures, score them, and recommend the strongest one while separately listing optional analyses suggested by the benchmark literature.


## v2.2 contribution-weighted autonomous workflow

v1.5 makes benchmark acquisition itself part of the audited workflow.

The skill now:

1. derives search concepts from Methods + Results + source tables;
2. generates several benchmark-search query families;
3. searches target-journal papers first;
4. expands to peer journals and field-defining papers;
5. records retrieval provenance;
6. normalizes DOI/title metadata and removes duplicates;
7. ranks candidates by relevance rather than prestige;
8. selects a diverse benchmark set;
9. builds an exemplar dossier;
10. applies a search-saturation stopping rule.

The ranking system explicitly down-weights unverified figure detail. A paper whose metadata is known but whose figure/legend could not be inspected cannot receive the same confidence as a fully verified benchmark.


## v2.2 contribution-weighted autonomous workflow

v1.6 uses the internal evidence inventory and the v1.5 benchmark dossier to search across alternative main-figure architectures.

It can compare 3-, 4-, and 5-figure solutions, optimize main-vs-Supplementary allocation, quantify panel redundancy, and recommend panel-level actions such as PROMOTE, MERGE, DEMOTE, or REPAIR.

The benchmark literature contributes a **soft architecture prior**. It cannot force an unavailable analysis into the promoted figure set.


## v2.2 contribution-weighted autonomous workflow

v1.7 adds an explicit visual-prototyping stage between architecture optimization and final data rendering.

Candidate architectures can now be rendered as **NO-DATA structural prototypes** and compared with the accepted visual baseline before costly final plotting.

The decision engine supports:
- PROMOTE
- REPAIR
- ROLLBACK
- HOLD

A candidate is rolled back when a local fix solves one problem but creates a meaningful global visual regression.


## v2.2 contribution-weighted autonomous workflow

v1.8 converts a promoted architecture into real PDF/SVG/TIFF figure files from explicitly mapped source data.

The renderer uses declarative panel specifications, frozen sentinels, source-data extracts, and provenance logging.

It deliberately refuses to infer scientific column mappings or transformations. Scientific semantics remain upstream decisions.


v1.8.1 is the tested production-engine release; the untested v1.8.0 development snapshot should not be used.


## v2.2 contribution-weighted autonomous workflow

v1.9 compiles promoted figures into a manuscript-level submission package and audits cross-figure consistency.

It checks semantic colors, typography, panel-label conventions, raster properties, legends, source-data presence, exact versions, and package hashes, then builds a contact sheet for mandatory whole-manuscript visual review.


## v2.2 contribution-weighted autonomous workflow

v2.0 adds one resumable controller over the full pipeline.

Users can now provide a project config and run:

```bash
python scripts/run_top_journal_figure_workflow.py workflow_project.yaml --resume
```

The workflow advances automatically through deterministic stages and stops at the first scientific, agent, or human gate that cannot be safely crossed.

It records every stage in `WORKFLOW_STATE.json`.


## v2.1 domain-adaptive scientific figure grammar

v2.1 allows the unified workflow to switch scientific figure grammar according to study type.

Supported profiles:
- bulk transcriptomics;
- single-cell;
- clinical cohort;
- survival/longitudinal;
- prediction modeling;
- meta-analysis;
- multimodal clinical.

The domain profile is selected from Methods/Results/source data and is audited before architecture optimization. It improves benchmark retrieval, panel planning, chart selection, main-vs-Supplementary allocation, and hostile visual review.


## v2.2 evidence-density and contribution optimizer

v2.2 maps scientific contribution and rendering density to visual area. It identifies anchor panels, caps workflow/provenance panels, expands dense high-value evidence, flags contribution-area inversions, and can recommend main-vs-Supplementary actions before final rendering.

The unified workflow now includes:

`ARCHITECTURE → VISUAL_WEIGHTING → PROTOTYPE`

## v2.3 benchmark-derived layout grammar

Learns quantified layout priors from selected benchmark figures and combines them with v2.2 contribution weights without copying exact layouts.

## v2.4 automatic visual hierarchy and typography

Maps scientific contribution and physical panel size to bounded typography, marker/line emphasis, annotation budgets, label-density limits, and render-spec style overrides. Panel labels and font family remain globally consistent; scientific hierarchy is expressed without turning figures into slide-like graphics.

## v2.5 — automatic annotation and legend intelligence

v2.5 adds a semantic placement layer between visual hierarchy and prototype rendering. It converts authorized candidate statistics and labels into a three-way plan: **DIRECT**, **LEGEND**, or **SUPPRESS**.

The planner uses scientific claim importance, statistical necessity, benchmark-derived annotation conventions, multiplicity status, graphical encodings, and the v2.4 physical density budget. It is designed to keep anchor figures evidence-dense without turning them into posters or numeric tables.

Primary entry points:

- `scripts/derive_annotation_legend_plan.py`
- `scripts/audit_annotation_legend_plan.py`
- `scripts/apply_annotation_plan_to_render_spec.py`
- `references/automatic-annotation-legend-intelligence.md`
- `templates/annotation_candidate_inventory.tsv`
- `templates/annotation_intelligence_contract.yaml`
