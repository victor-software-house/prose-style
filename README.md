# prose-style

A [Vale] package that flags the speech habits of AI-written text.

## Setup

Add the release zip to `Packages` in a project's `.vale.ini`, then run `vale sync`:

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

## Styles

| Style | Source | Rules |
|:--|:--|:--|
| `ProseStyle` | this repository | every rule in [`ProseStyle/styles/ProseStyle`][rules] |
| `Voices` | [Voices v0.2.0][voices] | all, except `ColonReveal` |
| `Direct` | ships inside Voices | all, `Length` as a warning, except `Ease` |
| `Readability` | [Readability v0.2.0][readability] | `FleschKincaid`, as a suggestion |
| `Std` | [Std v0.2.0][std] | `Latin`, `Spacing`, `GenderedPronouns`, `GenderedTerms`, as suggestions |

Sentences warn at 25 words (`Direct.Length`) and fail at 40 (`ProseStyle.LongSentence`).

## Habits

| Habit | Example | Rule |
|:--|:--|:--|
| Stock phrases | `load-bearing`, `crucially`, `at its core`, `smoking gun` | `StockPhrases` |
| Leaked chat replies | `You're right`, `Great question`, `Want me to fix it?` | `LeakedChat` |
| Lingo and slang | `seams`, `on the wire`, `wire format`, `doctrine` | `Lingo` |
| Made-up words | `top-to-bottomness`, `bullets-versus-numbered-paragraphs` | `MadeUpWords` |
| Things that speak or think | `the log says`, `the adapter knows`, `the request asks` | `ThingsSpeak` |
| Jargon | `land the PR`, `gate on CI`, `surfaces the error` | `Jargon` |
| Formal words | `prior to`, `obtain`, `serves as`, `boasts` | `FormalWords` |
| Filler | `simply`, `basically`, `of course` | `Filler` |
| Straw-man contrasts | `a document, not a transcript`, `not because X, but Y` | `StrawMan` |
| Dashes between clauses | `real — so we wait`, `runs -- then stops` | `Dashes` |
| Emoji and exclamation marks | `Done ✅`, `It works!` | `Emoji`, `Exclamation` |
| Words that go stale | `currently`, `previously`, `was renamed` | `StaleWords` |
| "Kind" as a noun | `each kind`, `per kind`, `an unknown kind` | `KindAsNoun` |
| Chatty headings | `Use it`, `What it turns on`, `How it works` | `ChattyHeadings` |
| Generic table headers | `Details`, `Info`, `Kind` | `GenericHeaders` |
| Bare links and codes | a pasted URL, `#123`, `EVO-9673` | `BareURL`, `BareWorkItem` |
| Profanity | profanity in a tracked file, the sign of a pasted message | `Profanity` |
| Walls of prose | sentences over 40 words, paragraphs and list items over 60 | `LongSentence`, `Paragraph`, `ListItem`, `TableRow` |

## Development

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
