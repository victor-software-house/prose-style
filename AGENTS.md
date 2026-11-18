# prose-style

A hakkiri package that flags the speech habits of AI-written text, published as `ProseStyle.zip` on each release.  
The `README.md` lists the habits it flags and how a project uses it.

## Layout

- `ProseStyle/.ctl/hakkiri.yaml`: the package settings that hakkiri applies before a project's own.  
  They turn the style on for Markdown, MDX (Markdown with components) and the comments of Rust, Swift, Go, TypeScript, JavaScript, YAML, TOML and Shell files.  
  They also turn the 14 opt-in rules off, and set the switches for source files and OpenSpec.
- `ProseStyle/renames.tsv`: each Vale rule of `v0.0.14` beside the rule that replaces it, or `-` when the package drops it.  
  The task that diffs alerts reads this file.
- `ProseStyle/NOTICE` and `ProseStyle/LICENSE`: the credits and the MIT text for the rules ported from other projects.
- `ProseStyle/styles/ProseStyle/*.yml`: one rule per file, each with its `tests:`.
- `ProseStyle/styles/config/vocabularies/ProseStyle/accept.txt`: words an upstream rule flags that have a plain technical use, such as the noun `harness`.  
  hakkiri reads each entry as an exception, so `SlopWords` lets the noun pass and still flags `harnessed` and `harnessing`.
- `PullRequestStyle/`: the Vale package the organization's pull request check reads after the frozen `v0.0.14` ProseStyle zip.  
  Its `.vale.ini` sets the rules for the `.pr-title` and `.pr-body` files that check writes, and its style has the rules only pull request text needs.
- `mise-tasks/build.py`: zips the tracked `ProseStyle/` folder and the tracked `PullRequestStyle/` folder, with fixed times, so the same inputs give the same bytes.
- `mise-tasks/alerts/diff.py`: `mise run alerts:diff` runs Vale and hakkiri over the files of some checkouts and diffs their alerts by rule.  
  Its arguments give the checkouts, the binaries and the package, and the tables go to an output folder.  
  So this repository stores nothing from the projects it runs on.
- `test/`: a hakkiri consumer project that unpacks the built `ProseStyle.zip` and runs `package.test.yml`, and `test/pull-request/`, a Vale project for the pull request package.
- `.github/workflows/`: `ci.yml` runs the tests; `release.yml` builds and attaches both zips on a tag, and prints the `packages:` entry in the release notes.

## Writing a rule

1. Each rule catches one habit.  
   Its comment states why, in one or two short sentences.  
   No chat quotes, no profanity, no private paths or tool names.
2. Each rule carries a case that fires and a case that must stay clean.  
   `mise run test` fails when any rule fires in no case, and `hakkiri test --coverage` checks it.
3. Match the habit.  
   Let natural uses of the same word pass with `exceptions:`.  
   Check each hit on a real document before raising a level.
4. A rule's message is the shortest command that shows the writer exactly what to change.  
   It passes the package's own rules.  
   Good messages:
   - `Write '%s' instead of '%s'.`
   - `Cut '%s'.`
   - `Reword one of these three sentences so it does not start with '%s'.`

   A message never opens with a category label and never uses a figure of speech.  
   It never uses a verb too vague to act on, such as vary, address or improve.  
   `mise run test:messages` lints every message through the built zip.

   A rule is a native hakkiri rule: no script rule, because hakkiri runs none.
5. A rule's name uses words people say, such as `StockPhrases` or `LeakedChat`.  
   Never a term of art such as diction, residue or coinage.
6. Each rule has one of three levels:
   - `error` for an AI speech habit, even when a rare valid use exists (operator, 2026-11-10).  
     Examples are a thing that speaks, a contrast frame or a made-up word.
   - `warning` for length and sentence shape, and for words with plain uses a person has to judge.
   - `suggestion` for a score or a hint whose fit depends on the file.

## Releases

- Tags are patch-only, from `v0.0.1`, annotated, on a `main` commit whose CI passed.  
  Never move or reuse a tag: projects pin the release URL.
- The package owns its rules, and nothing is copied at build time.  
  A rule ported from another project names its source in a header comment, and `ProseStyle/NOTICE` credits it.
- `v0.0.14` is the last release a Vale project can pin.  
  A release from `v0.0.16` on is a hakkiri package: the release notes print the `packages:` entry with its `sha256`.

## Writing in this repository

The package's own rules apply here: plain words, short sentences, no dashes as punctuation.  
A file, rule or value contains, shows, returns or matches; it never says, knows or wants.  
`mise run lint:prose` checks this repository and the rule comments with the package's own rules, at every level.

Use word pairs that occur in ordinary English.  
Check a doubtful pair, such as `plain fix`, against its alternatives in [Google Books Ngram][ngram].  
Rewrite a pair near zero when an alternative scores well: `plain fix` has 0 per billion words, `quick fix` 280.

Books lag web and software usage.  
When every choice is near zero, as with "wall of prose" and "wall of text", the counts decide nothing and the writer's wording stands.  
The JSON form returns the same counts:  
`https://books.google.com/ngrams/json?content=plain+fix,plain+words&corpus=en&year_start=2010&case_insensitive=true`.

[ngram]: https://books.google.com/ngrams
