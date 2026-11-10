# prose-style

A [Vale] package that flags the speech habits of AI-written text.

## Setup

Add the release zip to `Packages` in a project's `.vale.ini`, then run `vale sync`:

```ini
StylesPath = .vale/styles
MinAlertLevel = warning
Packages = https://github.com/victor-software-house/prose-style/releases/download/v0.0.1/ProseStyle.zip
```

The package's own `.vale.ini` turns the rules on for `*.{md,mdx,rs}` and reads Rust doc comments as Markdown.  
In a Rust file, `BareURLInComment` and `BareWorkItemInComment` take the place of `BareURL` and `BareWorkItem`.  
They read comments only, so a URL or a code such as `#123` in a string literal passes.  
A project adds sections only for other file types or its own exceptions.

The zip holds every style the rules use, so `vale sync` makes one download.  
Ignore the synced styles in Git: `vale sync` rebuilds them from `Packages`.

## Styles

The build packs the upstream styles that [`upstream.toml`][upstream] pins by sha256, with their licenses.

| Style | Source | Rules |
|:--|:--|:--|
| `ProseStyle` | this repository | every rule in [`ProseStyle/styles/ProseStyle`][rules] |
| `Voices` | [Voices v0.2.0][voices] | all, except `ColonReveal`; the noun `harness` passes `Banned` |
| `Direct` | [Voices v0.2.0][voices] | all, `Length` as a warning, except `Ease` |
| `Readability` | [Readability v0.2.0][readability] | `FleschKincaid`, as a suggestion |
| `Std` | [Std v0.2.0][std] | `Latin`, `Spacing`, `GenderedPronouns`, `GenderedTerms`, as suggestions |

Sentences warn at 25 words (`Direct.Length`) and fail at 40 (`ProseStyle.LongSentence`).  
The rules from `NounStack` to `HardBreak` are suggestions, except `ContrastInTitle`, `Slang`, `OneTermTwoWays` and `VagueLinkText`, which warn.  
`ThingsSpeakNoun` warns like `ThingsSpeak`.  
A project sees the suggestions when its `MinAlertLevel` is `suggestion`.  
The part-of-speech rules need Vale 3.20 or later: `NounStack` and `PrepositionChain` use `min`, and `ThingsSpeakNoun` uses `exceptions`.  
The repository pins Vale 3.26.0.

## Habits

| Habit | Example | Rule |
|:--|:--|:--|
| Stock phrases | `load-bearing`, `crucially`, `at its core`, `smoking gun` | `StockPhrases` |
| Leaked chat replies | `You're right`, `Great question`, `Want me to fix it?` | `LeakedChat` |
| Lingo and slang | `seams`, `on the wire`, `wire format`, `doctrine` | `Lingo` |
| Made-up words | `top-to-bottomness`, `bullets-versus-numbered-paragraphs` | `MadeUpWords` |
| Things that speak or think | `the log says`, `the adapter knows`, `the request asks` | `ThingsSpeak`, `ThingsSpeakNoun` |
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
| Bare links and codes | a pasted URL, `#123`, `EVO-9673` | `BareURL`, `BareURLInComment`, `BareWorkItem`, `BareWorkItemInComment` |
| Profanity | profanity in a tracked file, the sign of a pasted message | `Profanity` |
| Walls of prose | sentences over 40 words, paragraphs and list items over 60 | `LongSentence`, `Paragraph`, `ListItem`, `TableRow` |
| Noun stacks | `session lake store path` | `NounStack` |
| Chained prepositions | `the handling of errors in the parser of the daemon` | `PrepositionChain` |
| Contrast frames | `, not the`, a heading that ends `, not the disk` | `ContrastNot`, `ContrastInTitle` |
| Clause chains | `waits for the host; the host sits idle, which is slow` | `ClauseChain` |
| Stock words | `durable`, `verbatim`, `byte for byte` | `StockWords` |
| Things that act | `the store owns`, `the daemon waits` | `ThingsAct` |
| Hyphen chains | `claude-code-source-recovery` in running prose | `HyphenChain` |
| Slang | `gonna`, `awesome`, `janky` | `Slang` |
| Monotone rhythm | three sentences that open alike, five of near-equal length | `SameSentenceStart`, `FlatRhythm` |
| One term two ways | `email` and `e-mail` in one file | `OneTermTwoWays` |
| Acronyms with no definition | `DAFB` before `Data Analysis Facility Base (DAFB)` | `UndefinedAcronym` |
| Vague or unpinned links | `[here](…)`, a link to `blob/main` | `VagueLinkText`, `UnpinnedCodeLink` |
| Markdown line breaks | two sentences on one line, a continued line with no two trailing spaces | `SentencePerLine`, `HardBreak` |

## Development

[mise] pins Vale and Python and holds the tasks.

| Task | Runs |
|:--|:--|
| `mise run test` | The three test tasks below |
| `mise run test:rules` | `vale test --coverage`: every rule's cases, and every rule must fire in one |
| `mise run test:package` | The package cases on the built zip |
| `mise run test:messages` | Every rule's message, linted through the built zip |
| `mise run build` | `ProseStyle.zip` from the tracked `ProseStyle/` folder and the upstream styles, downloaded through the GitHub API |

Each rule carries its cases under `tests:`.  
A tag `v0.0.N` on `main` publishes `ProseStyle.zip` as a release asset.

[Vale]: https://vale.sh
[mise]: https://mise.jdx.dev
[rules]: ProseStyle/styles/ProseStyle
[upstream]: upstream.toml
[voices]: https://github.com/jdkato/voices/releases/tag/v0.2.0
[readability]: https://github.com/vale-cli/Readability/releases/tag/v0.2.0
[std]: https://github.com/vale-cli/Std/releases/tag/v0.2.0
