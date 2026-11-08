# prose-style

A Vale package, published as `ProseStyle.zip` on each release.
The `README.md` holds what it turns on and how a project uses it.

## Layout

- `ProseStyle/.vale.ini`: the package configuration a project reads before its own.
- `ProseStyle/styles/ProseStyle/*.yml`: one rule per file, each with its `tests:`.
- `.github/workflows/`: `ci.yml` runs the tests; `release.yml` builds and attaches the zip on a tag.

## Rules for a rule

1. Each rule names one habit, and its comment gives the reason in one or two plain sentences.
   No chat quotes, no profanity, no private paths or tool names.
2. Each rule carries a case that fires and a case that must stay clean.
   `mise run test` fails when any rule fires in no case.
3. Match the habit, not every use of a word.
   Allow the natural uses with `exceptions:`, and check each hit on a real document before raising a level.
4. A rule's message names the fix: what to write instead.
5. Levels: `error` for a habit with no valid use, `warning` for one that needs a person's judgment, `suggestion` for a score or a style hint.

## Releases

- Tags are patch-only, from `v0.0.1`, annotated, on a `main` commit whose CI passed.
  Never move or reuse a tag: projects pin the release URL.
- Upstream packages are pinned by release URL in `ProseStyle/.vale.ini`.
  Std comes after Voices, so the pinned Std replaces the latest one Voices names.

## Writing in this repository

The package's own rules apply here: plain words, short sentences, no dashes as punctuation.
A file, rule or value holds, shows, marks or matches; it never says, knows or wants.
