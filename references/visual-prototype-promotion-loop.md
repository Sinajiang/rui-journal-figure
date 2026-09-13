# Visual prototype generation and promote / repair / rollback loop

## Purpose

v1.7 closes the loop between architecture planning and final figure production.

Before investing in full scientific rendering, the skill can build a **low-cost structural prototype** of a proposed figure architecture.

The prototype is used to test:

- panel balance;
- anchor-panel prominence;
- panel density;
- label / legend reserve;
- schematic-to-quantitative ratio;
- global white-space balance;
- likely collision pressure;
- whether the architecture is visually feasible at the journal's physical size.

The prototype must never be mistaken for data.

Every prototype should carry an explicit marker:

> STRUCTURAL PROTOTYPE — NO DATA

---

## Why prototypes are needed

A figure architecture can score well scientifically but still fail visually.

Common examples:

- four equally sized panels when one result should dominate;
- workflow panel consuming too much area;
- too many narrow panels requiring unreadably small text;
- dense external-evidence matrix placed in a half-width slot;
- legends forced into data viewports;
- a local repair fixing overlap while weakening the overall composition.

A low-cost prototype catches these failures before final data rendering.

---

## Promotion states

Every figure or figure-set candidate can occupy one of four states:

### PROMOTE
The candidate improves or preserves:

- scientific fidelity;
- evidence coverage;
- contribution visibility;
- rendered visual quality;
- journal compliance.

### REPAIR
The architecture is scientifically acceptable, but one or more local rendered defects remain.

Repair should be surgical whenever possible.

### ROLLBACK
The candidate is worse than the accepted baseline in a meaningful way.

Typical reasons:
- lower visual hierarchy;
- lower information efficiency;
- new crowding;
- reduced anchor-panel visibility;
- worse claim coverage;
- journal contract regression.

### HOLD
Evidence or QA is incomplete.
No promotion decision should be made yet.

---

## Baseline governance

A promoted baseline should record:

- baseline version;
- architecture score;
- visual QA score;
- hard-gate state;
- accepted figure count;
- accepted panel structure;
- source authority;
- journal profile;
- date of acceptance.

A new branch must compare against the current accepted baseline.

Do not compare only against the immediately previous failed attempt.

---

## Prototype requirements

The structural prototype should show:

- figure number;
- panel letters;
- panel role;
- chart type;
- claim IDs;
- relative panel area;
- reserved legend / annotation zones where relevant;
- visual-density estimate.

It should not show:
- invented data points;
- fabricated effect sizes;
- fake P values;
- fake heatmap values;
- simulated significance.

Simple chart glyphs may be used only as **type icons**, not as quantitative evidence.

---

## Prototype visual metrics

Useful metrics include:

### Panel balance
Penalize:
- extremely tiny panels;
- excessive area inequality without an anchor rationale;
- anchor panels that are not larger than low-value workflow panels.

### Density pressure
Estimate pressure from:
- panel count;
- visual-density scores;
- text reserve;
- narrow aspect ratios.

### White-space efficiency
Too much unused space weakens information density.
Too little increases collision risk.

### Anchor visibility
The highest-contribution panel should usually have:
- sufficient area;
- high positional salience;
- clean neighboring whitespace.

### Schematic ratio
Benchmark grammar may suggest a typical schematic fraction.
This is a soft prior.

### Layout feasibility
A candidate should fit within:
- journal width;
- journal height;
- final-size font floor;
- panel-count constraints.

---

## Decision logic

### Hard vetoes
ROLLBACK if:
- scientific hard gate fails;
- unavailable evidence is promoted;
- must-main evidence is lost;
- target-journal hard requirement fails;
- source traceability is broken.

### Visual repair
REPAIR if:
- science passes;
- architecture passes;
- final-size visual QA has local blocking defects;
- the defects appear surgically repairable.

### Promotion
PROMOTE if:
- hard gates pass;
- candidate architecture score is at least acceptable;
- rendered prototype quality is not worse than baseline beyond tolerance;
- no new global hierarchy defect appears.

### Rollback on visual regression
Even if a local overlap is fixed, ROLLBACK if:
- global balance becomes meaningfully worse;
- anchor visibility drops;
- whitespace becomes pathological;
- panel density becomes unreadable;
- the candidate loses the accepted visual character.

---

## Surgical repair planning

For each repair issue record:

- defect;
- panel / object;
- severity;
- local fix;
- protected baseline elements;
- expected side effects;
- re-QA requirements.

Preferred order:

1. move object into dedicated whitespace;
2. enlarge local container;
3. redistribute panel area;
4. wrap or shorten text;
5. move legend;
6. change chart orientation;
7. only then reduce font size.

---

## Final production transition

A prototype can only authorize **architecture promotion**.

It cannot authorize final figure files.

After architecture promotion:

1. render real source data;
2. run scientific sentinels;
3. run geometry / collision QA;
4. run journal validation;
5. run evidence-graph reintegration;
6. perform final-size visual inspection;
7. promote final figure version separately.

---

## Key principle

> Prototype early, compare against the accepted baseline, and rollback aggressively when global visual quality worsens.
