# Evidence-aware figure intelligence

## Purpose

A figure can be visually excellent yet still be manuscript-inconsistent.

Common failures include:

- the Results section cites the wrong panel;
- the legend describes an older panel architecture;
- a panel contains evidence that is never discussed;
- a Results claim has no corresponding figure or table;
- a figure implies a stronger claim than the mapped source data support;
- Supplementary numbering drifts after figure replacement;
- a source-data file no longer matches the promoted panel.

v1.3 introduces a structured evidence graph linking:

> manuscript claim → figure → panel → source data → statistic → legend → manuscript citation

The graph is bidirectional. Every promoted panel should be explainable from the manuscript, and every manuscript figure claim should resolve back to a panel and source.

## Core entities

### Claim
A manuscript-level scientific statement.

Required metadata:
- stable claim ID;
- section;
- sentence / paragraph locator;
- claim strength;
- evidence status;
- linked figure/panel.

### Panel
A visual evidence unit.

Required metadata:
- figure;
- panel label;
- role;
- source-data ID;
- plotted statistic;
- linked legend clause;
- linked manuscript claims.

### Source
The data or frozen result object underlying a panel.

Required metadata:
- path or stable identifier;
- scientific authority;
- transformation;
- sentinels;
- whether re-analysis is allowed.

### Legend clause
A minimal description of:
- what is shown;
- sample / unit;
- statistic;
- uncertainty;
- model or adjustment where needed.

## Evidence status

Use explicit statuses:

- `DIRECT` — panel directly tests the claim.
- `SUPPORTING` — panel supports but does not directly test the claim.
- `CONTEXTUAL` — external disease/state context only.
- `ROBUSTNESS` — sensitivity / perturbation / alternate model.
- `MECHANISTIC` — mechanistic evidence.
- `BOUNDARY` — limitation or evidence ceiling.
- `UNSUPPORTED` — claim currently exceeds available evidence.

Do not silently upgrade a contextual or robustness panel into direct replication.

## Claim strength

Recommended controlled vocabulary:

- descriptive;
- association;
- differential;
- predictive;
- replication;
- mechanistic;
- causal.

The audit should flag:
- `replication` claim linked only to contextual evidence;
- `mechanistic` claim linked only to descriptive association;
- `causal` claim without explicitly declared causal evidence.

These are review flags unless the project defines them as hard failures.

## Bidirectional integrity rules

### Manuscript → figure
Every figure citation in Results should resolve to:
- an existing figure;
- an existing panel if a panel is specified.

### Figure → manuscript
Every main-figure panel should have:
- at least one linked claim or a declared non-claim role such as workflow/provenance.

### Panel → source
Every quantitative panel must map to:
- source data;
- statistic;
- authority.

### Legend → panel
Legend architecture must contain exactly the promoted panel set unless the journal uses a different convention.

### Supplementary integrity
Supplementary figures/tables should have:
- sequential identifiers;
- matching mentions;
- no duplicate numbering.

## Important boundary

Scripts can validate structure and explicit mappings.

They cannot independently determine scientific truth from prose.

The AI/human review layer must create the evidence graph from the actual manuscript, methods, results, legends, and source data. The scripts then test whether that declared mapping is internally coherent.
