# prose-style

A [Vale] package for plain, short, literal technical prose.  
It flags stock phrases, chat residue, dashes, long sentences and paragraphs, coined jargon, and verbs that give things speech or thought.

## Use it

Name the release zip in a project's `.vale.ini`, then run `vale sync`:

```ini
StylesPath = .vale/styles
MinAlertLevel = warning
Packages = https://github.com/victor-software-house/prose-style/releases/download/v0.0.1/ProseStyle.zip
```

The package's own `.vale.ini` turns the rules on for `*.{md,mdx,txt}`.  
A project adds sections only for other file types or its own exceptions:

```ini
# Rust doc comments are Markdown.
[formats]
rs = md

[*.rs]
BasedOnStyles = ProseStyle, Direct
```

Ignore the synced styles in Git: `vale sync` rebuilds them from `Packages`.

## What it turns on

| Style | Source | Rules |
|:--|:--|:--|
| `ProseStyle` | this repository | every rule in [`ProseStyle/styles/ProseStyle`][rules] |
| `Voices` | [Voices v0.2.0][voices] | all, except `ColonReveal` |
| `Direct` | ships inside Voices | all, `Length` as a warning, except `Ease` |
| `Readability` | [Readability v0.2.0][readability] | `FleschKincaid`, as a suggestion |
| `Std` | [Std v0.2.0][std] | `Latin`, `Spacing`, `GenderedPronouns`, `GenderedTerms`, as suggestions |

Sentences warn at 25 words (`Direct.Length`) and fail at 40 (`ProseStyle.LongSentence`).

## Develop

[mise] pins Vale and holds the tasks.

| Task | Runs |
|:--|:--|
| `mise run test` | `vale test --coverage`: every rule's cases, and every rule must fire in one |
| `mise run build` | `ProseStyle.zip` from the committed `ProseStyle/` folder |

Each rule carries its cases under `tests:`.  
A tag `v0.0.N` on `main` publishes `ProseStyle.zip` as a release asset.

[Vale]: https://vale.sh
[mise]: https://mise.jdx.dev
[rules]: ProseStyle/styles/ProseStyle
[voices]: https://github.com/jdkato/voices/releases/tag/v0.2.0
[readability]: https://github.com/vale-cli/Readability/releases/tag/v0.2.0
[std]: https://github.com/vale-cli/Std/releases/tag/v0.2.0
