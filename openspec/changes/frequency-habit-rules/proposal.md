## Why

The package's rules come from habits readers noticed, and nothing measures how much more often agents use them than people do.  
[research.md][research] counts both sides: agent docs use semicolons 7.3 times as often as pre-2022 design docs, colons inside a sentence 4.0 times, and ", not the" contrasts 7.7 times.  
A linear model that sees no topic words tells agent sentences from human ones with a held-out ROC AUC of 0.958 to 0.987 on sources it never trained on, so the habits are real and measurable.

## What Changes

- Add rules for the candidates in [research.md][research] that score high on both ratio and spread: semicolons and colons inside a sentence, ", not the" contrasts, three-item lists, "so the" opening a clause, verbs that make a thing act, stock adjectives and adverbs, and four phrases.
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
