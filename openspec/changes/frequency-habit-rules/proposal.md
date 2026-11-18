## Why

The package's rules come from habits that readers noticed.
Nothing measures how much more often agents use them than people do.

[research.md][research] counts both sides.
Agent docs use semicolons 7.3 times as often as design docs from before 2022.
They use colons inside a sentence 4.0 times as often, and `, not the` contrasts 7.7 times.

A linear model that sees no topic words can tell agent sentences from human ones.
On held-out sources it never trained on, it scores 0.958 to 0.987.
The score is the area under the curve (AUC) of the receiver operating characteristic (ROC).
So the habits are real and measurable.

## What Changes

- Add rules for the candidates in [research.md][research] that score high on both ratio and spread:
  - semicolons and colons inside a sentence
  - `, not the` contrasts
  - lists of three items
  - `so the` at the start of a clause
  - verbs that make a thing act
  - stock adjectives and adverbs
  - four phrases
- Give each new rule the measured ratio and source counts in its test fixtures' notes, so a later change can re-measure it.
- Keep the method's scripts outside the package; [research.md][research] records the method, corpora, pins and numbers needed to repeat it.

## Capabilities

### New Capabilities

- `habit-rules`: which speech habits the package flags, at what level, and the measured evidence each rule rests on.

### Modified Capabilities

None.

## Impact

- New rule files in `ProseStyle/styles/ProseStyle/`, each with tests.
- Repositories that sync ProseStyle get the new rules with the next release; a rate-based rule can raise new warnings in docs that passed before.

[research]: research.md
