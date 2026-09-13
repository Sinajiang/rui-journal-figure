# Chart selection

Choose a chart because of the estimand and data structure.

| Scientific task | Preferred chart |
|---|---|
| Compare distributions with small/moderate n | dot + box / violin |
| Paired measurements | paired slope / connected dot |
| Effect estimates with uncertainty | forest / interval plot |
| Many genes × datasets | heatmap / evidence matrix |
| DE overview | volcano / MA |
| Cross-dataset concordance | scatter + reference lines |
| Leave-one-out sensitivity | lollipop / influence plot |
| Threshold / model range | interval / dumbbell |
| Cohort composition | grouped or stacked bars |
| Study provenance | compact workflow |
| External evidence roles | routing schematic + matrix |
| Mechanism | restrained schematic with evidence labels |

## Rules

- show individual observations when n is small;
- avoid bars for continuous data when the distribution matters;
- do not use radar charts for inferential comparisons;
- avoid pie charts for scientific composition unless only a very simple descriptive proportion is needed;
- use diverging heatmaps only when zero has real semantic meaning;
- do not use UMAP/PCA merely as decoration.
