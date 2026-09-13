# top-journal-figure-pro v1.5.0

## Autonomous benchmark retrieval and exemplar ranking

### Added
- benchmark search brief;
- query-family generator;
- benchmark candidate provenance schema;
- DOI/title normalization and deduplication;
- relevance-weighted benchmark ranking;
- diversity-aware benchmark selection;
- provenance audit;
- search-saturation audit;
- benchmark dossier builder;
- retrieval prompt and checklist.

### Ranking principle
Relevance > prestige.

Scientific similarity, methodological similarity, modality, and figure-role relevance carry more weight than target-journal identity alone.

### Verification principle
Unverified figure details reduce benchmark confidence.

### Search stopping rule
Stop after the minimum benchmark set is reached and two consecutive search rounds add no new high-ranked benchmark or transferable grammar pattern.
