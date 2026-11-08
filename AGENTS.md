# prose-style

A Vale package that flags the speech habits of AI-written text, published as `ProseStyle.zip` on each release.  
The `README.md` lists the habits it flags and how a project uses it.

## Layout

- `ProseStyle/.vale.ini`: the package configuration a project reads before its own.
- `ProseStyle/styles/ProseStyle/*.yml`: one rule per file, each with its `tests:`.
- `.github/workflows/`: `ci.yml` runs the tests; `release.yml` builds and attaches the zip on a tag.

## Writing a rule

1. Each rule catches one habit. Its comment states why, in one or two short sentences.  
   No chat quotes, no profanity, no private paths or tool names.
2. Each rule carries a case that fires and a case that must stay clean.  
   `mise run test` fails when any rule fires in no case.
3. Match the habit.  
   Let natural uses of the same word pass with `exceptions:`.  
   Check each hit on a real document before raising a level.
4. A rule's message shows what to write instead.
5. A rule's name uses words people say, such as `StockPhrases` or `LeakedChat`.  
   Never a term of art such as diction, residue or coinage.
6. Levels: `error` for a habit with no valid use, `warning` for one that needs a person's judgment, `suggestion` for a score or a style hint.

## Releases

- Tags are patch-only, from `v0.0.1`, annotated, on a `main` commit whose CI passed.  
  Never move or reuse a tag: projects pin the release URL.
- Upstream packages are pinned by release URL in `ProseStyle/.vale.ini`.  
  Std comes after Voices, so the pinned Std replaces the latest one Voices names.

## Writing in this repository

The package's own rules apply here: plain words, short sentences, no dashes as punctuation.  
A file, rule or value holds, shows, marks or matches; it never says, knows or wants.

Use word pairs that occur in ordinary English.  
Check a doubtful pair, such as "plain fix", against its alternatives in [Google Books Ngram][ngram].  
Rewrite a pair near zero when an alternative scores well: "plain fix" has 0 per billion words, "quick fix" 280.  
Books lag web and software usage, so when every choice is near zero, as with "wall of prose" and "wall of text", the counts decide nothing and the writer's wording stands.  
The JSON form returns the same counts:  
`https://books.google.com/ngrams/json?content=plain+fix,plain+words&corpus=en&year_start=2010&case_insensitive=true`.

[ngram]: https://books.google.com/ngrams
