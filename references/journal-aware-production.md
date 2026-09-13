# Journal-aware figure production

Journal specifications are external contracts and can change.

## Rule

Never hard-code a journal requirement from memory when the task is current submission preparation.

Use:
1. official author-guidelines pages;
2. a retrieval date;
3. a versioned journal profile;
4. stage-specific constraints.

## Unknown means unknown

If the official page does not state:
- figure width,
- font size,
- color mode,
- line width,
or another production value,

store it as `null` / unknown.

Do not infer a number from another journal or publisher-wide rule unless the journal explicitly incorporates that rule.

## Hard requirements vs recommendations

Profiles should distinguish:
- `min`, `max`, `required`, `not_allowed` → hard or near-hard checks;
- `preferred`, `recommended` → warnings;
- editorial design advice → notes.

## Benchmarking

Use recent benchmark papers to learn:
- evidence sequencing;
- figure density;
- chart vocabulary;
- visual restraint.

Do not use benchmark articles to override the journal's official technical requirements.
