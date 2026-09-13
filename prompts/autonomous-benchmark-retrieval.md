# Prompt — autonomous benchmark retrieval

Use the current project's Methods, Results, source tables, scientific authority, target journal, and intended figure roles.

## 1. Build search brief
Extract:
- disease/topic;
- study design;
- modality;
- unit of analysis;
- primary outcome/estimand;
- key methods;
- target journal;
- desired figure roles.

## 2. Search in rounds
Search:
1. target journal + closest scientific match;
2. target journal + closest methodological match;
3. high-quality peer journals with similar design/modality;
4. field-defining exemplars only if needed.

Use several query families rather than one oversized query.

## 3. Verify metadata
For every candidate verify:
- title;
- journal;
- year;
- DOI when available;
- URL;
- article type;
- primary-research status;
- figure/legend accessibility.

If figure details were not inspected, label:
`FIGURE_DETAIL_UNVERIFIED`.

## 4. Rank by relevance
Score:
- scientific similarity;
- method similarity;
- modality similarity;
- sample-structure similarity;
- figure-role relevance;
- journal fit;
- main-vs-supplement transferability;
- figure-detail accessibility;
- recency.

Relevance outranks prestige.

## 5. Select a diverse set
Prefer 5–10 strong benchmarks for whole-manuscript planning.
Avoid near-duplicate benchmark sets.

## 6. Extract benchmark grammar
For each selected paper record:
- why selected;
- figure-level scientific questions;
- anchor-panel pattern;
- evidence sequence;
- chart vocabulary;
- legend strategy;
- main-vs-supplement allocation;
- transferable principles;
- what must not be copied.

## 7. Stop at saturation
Stop when:
- minimum benchmark count has been met; and
- two consecutive search rounds add no new high-ranked candidate and no new transferable grammar.

## Boundary
Do not allow benchmark literature to create panels unsupported by the current study.
