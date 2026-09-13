# Autonomous benchmark retrieval and exemplar ranking

## Goal

v1.5 makes benchmark selection an explicit research workflow rather than an informal "find a few nice figures" step.

The skill should autonomously:

1. derive search concepts from the manuscript's Methods + Results + source tables;
2. search the target journal first;
3. expand to high-quality peer journals and field-defining papers;
4. normalize and deduplicate candidate papers;
5. rank candidates by scientific and methodological relevance;
6. select a diverse benchmark set;
7. extract figure grammar and main-vs-supplement allocation;
8. stop when additional searching adds little new design/evidence grammar.

The retrieval workflow informs **figure planning**, not scientific truth.

---

## Retrieval inputs

Build a `benchmark_search_brief.yaml` from the current project.

Required concepts:

- target journal;
- article type;
- disease / scientific question;
- study design;
- data modality;
- unit of analysis;
- primary estimand / outcome;
- key methods;
- desired figure role(s);
- date window if appropriate.

Examples of desired figure roles:

- study design / provenance;
- primary effect;
- donor- or participant-level display;
- robustness / leave-one-out;
- cross-dataset replication;
- external context;
- mechanistic triangulation;
- longitudinal / survival / prediction;
- multiview / multimodal integration.

---

## Search hierarchy

### Round 1 — target journal, closest scientific match

Search combinations of:

- target journal;
- disease/topic;
- study design;
- modality;
- main method.

This round has the highest journal-fit value.

### Round 2 — target journal, closest methodological match

When exact disease/topic matches are sparse, search the same journal for:

- same modality;
- same statistical design;
- same evidence architecture;
- same article type.

### Round 3 — high-quality peer journals

Search strong peer journals for:

- same scientific question;
- same modality;
- similar sample structure;
- similar analysis type.

### Round 4 — field-defining exemplars

Use older or cross-journal exemplars only when they provide highly transferable architecture.

A field-defining paper should not outrank a recent target-journal paper merely because it is famous.

---

## Query families

Generate several distinct query families, not one long query.

### Scientific query
`<topic> <disease> <primary outcome>`

### Method query
`<method> <study design> <modality>`

### Journal-specific query
`site:<journal-domain> <topic> <method>`

### Figure-role query
`<topic> <method> robustness sensitivity`
or
`<topic> <modality> external validation`

### Article-type query
`<topic> original research <target journal>`

The agent should adapt syntax to the available search engine.

---

## Candidate inclusion rules

Prefer primary original research.

Eligible benchmark candidates should normally provide at least one of:

- highly similar scientific question;
- highly similar modality;
- highly similar study design;
- highly transferable figure/evidence architecture.

Use reviews mainly to discover primary papers, not as default figure exemplars.

Avoid selecting papers solely because:

- they are highly cited;
- the journal has a high impact factor;
- the figure is visually attractive.

---

## Candidate metadata

For every candidate record:

- benchmark ID;
- title;
- authors;
- journal;
- year;
- DOI;
- URL;
- article type;
- retrieval date;
- search query / search round;
- target-journal match;
- scientific similarity;
- method similarity;
- modality similarity;
- sample-structure similarity;
- figure-role relevance;
- main-vs-supplement relevance;
- recency;
- full-figure/legend accessibility;
- notes.

---

## Ranking dimensions

Each candidate receives 0–5 scores for:

1. scientific similarity;
2. methodological similarity;
3. modality similarity;
4. sample-structure similarity;
5. figure-role relevance;
6. journal fit;
7. main-vs-supplement transferability;
8. accessibility of figure/legend details.

Recency is handled separately and should be modestly weighted.

### Important

Relevance outweighs prestige.

A highly relevant paper in a strong peer journal may be more useful than a weakly related paper in the target journal.

---

## Diversity-aware selection

The final benchmark set should not contain ten near-duplicates.

Prefer diversity across:

- journals;
- study designs;
- evidence roles;
- chart vocabularies;
- scientific subquestions.

But diversity cannot override relevance.

Recommended default final set:
- 5–10 papers for full manuscript figure reconstruction;
- 3–6 papers for a single figure.

---

## Retrieval provenance

Every benchmark must retain:

- the URL/DOI;
- retrieval date;
- how it was found;
- why it was selected.

Do not invent:
- DOI;
- year;
- journal;
- figure content;
- benchmark relevance.

If a full figure or legend cannot be inspected, mark:

`FIGURE_DETAIL_UNVERIFIED`

and lower accessibility / transferability confidence.

---

## Search saturation

Do not search forever.

A practical stopping rule:

Stop after at least the minimum benchmark count is met **and** two consecutive search rounds add no new high-ranked candidate or no new transferable grammar pattern.

Record:

- round number;
- candidates added;
- new grammar patterns added;
- reason for stopping.

This produces an auditable search ceiling.

---

## Exemplar dossier

For each selected benchmark, create a concise dossier:

### Why selected
- scientific similarity;
- methodological similarity;
- journal relevance.

### What to learn
- figure-level question;
- anchor panel;
- evidence sequence;
- main-vs-supplement allocation;
- chart types;
- legend strategy;
- information density.

### What not to copy
- exact layout;
- artwork;
- proprietary icons;
- study-specific visual semantics that do not fit current data.

### Current-study adaptation
- DIRECTLY_AVAILABLE;
- STRUCTURALLY_ADAPTABLE;
- OPTIONAL_NEW_ANALYSIS;
- NOT_APPLICABLE.

---

## Final principle

The benchmark set is a **decision-support corpus**, not a template library.

The current study's Methods, Results, frozen analyses, and source tables retain veto power over every proposed panel.
