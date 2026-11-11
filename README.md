# prose-style

A [hakkiri] package that flags the speech habits of AI-written text.

## Setup

Pin the release in a project's `.ctl/hakkiri.yaml` by `url` and `sha256`.
The release notes print the entry:

```yaml
packages:
  - url: https://github.com/victor-software-house/prose-style/releases/download/<tag>/ProseStyle.zip
    sha256: <the hash in the release notes>
```

The package's own `.ctl/hakkiri.yaml` turns the style on for `*.{md,mdx,rs}`.
It names the vocabulary `ProseStyle`, and hakkiri reads a Rust comment as Markdown.
In a Rust file, `BareURLInComment` and `BareWorkItemInComment` take the place of `BareURL` and `BareWorkItem`.
They read comments only, so a URL or a code such as `#123` in a string literal passes.
A project adds globs only for other file types or its own exceptions, and its settings win over the package's.

The zip holds the whole style, so hakkiri makes one download and caches it.
`v0.0.14` is the last release a Vale project can pin: from the next release the zip is a hakkiri package, and Vale reads it no more.

## Style

The one style `ProseStyle` holds every rule, in [`ProseStyle/styles/ProseStyle`][rules].
Seventeen of its rules are ports of rules from [Vale Voices][voices], [Std][std] and [Readability][readability], renamed and kept native: `SlopWords`, `BinaryContrast`, `InflatedWords`, `Puffery`, `RecapOpener`, `SuperficialAnalysis`, `ThroatClearing`, `WeakVerbs`, `VagueAttribution`, `Hedging`, `SentenceLength`, `Preamble`, `GradeLevel`, `LatinAbbreviation`, `SentenceSpacing`, `GenderedPronouns` and `GenderedTerms`.
[`NOTICE`][notice] credits each source rule by rule, and [`LICENSE`][license] holds the MIT text.

Fourteen more ship off, for a project to turn on with `ProseStyle.<Rule>: on` under a glob of its own:

| Rules | Reads |
|:--|:--|
| `AutomatedReadability`, `ColemanLiau`, `FleschReadingEase`, `GunningFog`, `LIX`, `SMOG`, `Polysyllables` | a readability score per file |
| `PassiveVoice`, `OxfordComma`, `Contractions` | grammar and punctuation habits |
| `FirstPersonPlural`, `FirstPersonSingular` | the person of the text |
| `DateFormat`, `TimeFormat` | how dates and times are written |

A rule that catches an AI speech habit fails as an error.
Rules on length and sentence shape warn, because a long table row or three sentences that open alike can be right: `Paragraph`, `ListItem`, `TableRow`, `ClauseChain`, `NounStack`, `PrepositionChain`, `SameSentenceStart` and `FlatRhythm`.
`StockWords` and `StaleWords` warn too, because their words have plain uses a person has to judge.
`UndefinedAcronym`, `SentencePerLine`, `HardBreak`, `GradeLevel`, `SentenceLength`, `LatinAbbreviation`, `SentenceSpacing`, `GenderedPronouns` and `GenderedTerms` are suggestions.
A sentence fails at 40 words (`LongSentence`), and `SentenceLength` hints at 25 as a suggestion.
A project sees the suggestions when its `level` is `suggestion`.
The repository pins hakkiri 0.0.5.

## Habits

| Habit | Example | Rule |
|:--|:--|:--|
| Stock phrases | `load-bearing`, `crucially`, `at its core`, `smoking gun` | `StockPhrases` |
| Leaked chat replies | `You're right`, `Great question`, `Want me to fix it?` | `LeakedChat` |
| Lingo and slang | `seams`, `on the wire`, `wire format`, `doctrine` | `Lingo` |
| Made-up words | `top-to-bottomness`, `bullets-versus-numbered-paragraphs`, `greppability` | `MadeUpWords`, `MadeUpNouns` |
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

## Pull requests

The organization's required `PR prose` check lints each pull request's title and description.  
It runs on Vale, and reads the `v0.0.14` `ProseStyle.zip`, then `PullRequestStyle.zip`, with the same levels in every repository.  
It writes the title to a `.pr-title` file and the description to a `.pr-body` file, so every setting for pull request text sits in sections for those two extensions and never reaches a project's docs.

| File | Rules |
|:--|:--|
| `.pr-title` | `PullRequestStyle.ConventionalTitle`, then the prose rules on the subject after the type and scope |
| `.pr-body` | the prose rules, with `HardBreak` off: GitHub shows a line break in a description as a break |

The check writes each reference GitHub links as a link before it lints: an issue or pull request number, and an id an [autolink reference][autolinks] covers.  
`BareWorkItem` then flags only what GitHub leaves as plain text.  
A repository makes its own ids pass by adding an autolink reference for their prefix.

A repository cannot change a level for its pull requests until the check moves to hakkiri (operator, 2026-11-11).

[autolinks]: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/configuring-autolinks-to-reference-external-resources

## Line breaks

`SentencePerLine` and `HardBreak` read every Markdown file, since a rendered page drops a single line break.  
A file that wraps at a column turns them off for itself, at its top:

```markdown
<!-- hakkiri ProseStyle.SentencePerLine: off -->
<!-- hakkiri ProseStyle.HardBreak: off -->
```

The hakkiri release after 0.0.5 reads these comments, and Vale's own `<!-- vale ... -->` form.

## Development

[mise] pins hakkiri, Vale and Python and holds the tasks.
Vale runs only the pull request package.

| Task | Runs |
|:--|:--|
| `mise run test` | The four test tasks below |
| `mise run test:rules` | `hakkiri test --coverage`: every rule's cases, and every rule must fire in one |
| `mise run test:package` | The package cases on the built zip, unpacked and listed as a project does |
| `mise run test:messages` | Every rule's message, linted through the built zip |
| `mise run test:pull-request` | The pull request package's rules and cases, on Vale |
| `mise run build` | `ProseStyle.zip` from the tracked `ProseStyle/` folder, and `PullRequestStyle.zip` from `PullRequestStyle/` |

Each rule carries its cases under `tests:`.  
A tag `v0.0.N` on `main` publishes `ProseStyle.zip` and `PullRequestStyle.zip` as release assets, and the release notes print the `packages:` entry for the first.

[hakkiri]: https://github.com/victor-software-house/hakkiri
[license]: ProseStyle/LICENSE
[mise]: https://mise.jdx.dev
[notice]: ProseStyle/NOTICE
[rules]: ProseStyle/styles/ProseStyle
[voices]: https://github.com/jdkato/voices/releases/tag/v0.2.0
[readability]: https://github.com/vale-cli/Readability/releases/tag/v0.2.0
[std]: https://github.com/vale-cli/Std/releases/tag/v0.2.0
