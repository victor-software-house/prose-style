# Design

## Decisions

### 1. One style holds every rule

All rules sit in `ProseStyle/styles/ProseStyle/`, and none copies an upstream folder.  
The 17 ports and the 14 opt-in rules take the renames the operator chose (operator, 2026-11-11).

| Upstream rule | Rule in ProseStyle | Check type | Level |
|:--|:--|:--|:--|
| `Voices.Banned` | `SlopWords` | `existence` | error |
| `Voices.BinaryContrast` | `BinaryContrast` | `existence` | error |
| `Voices.InflatedWords` | `InflatedWords` | `substitution` | error |
| `Voices.Puffery` | `Puffery` | `existence` | error |
| `Voices.Recap` | `RecapOpener` | `existence` | error |
| `Voices.SuperficialAnalysis` | `SuperficialAnalysis` | `existence` | error |
| `Voices.ThroatClearing` | `ThroatClearing` | `existence` | error |
| `Voices.WeakVerbs` | `WeakVerbs` | `substitution` | error |
| `Voices.Weasel` | `VagueAttribution` | `existence` | error |
| `Direct.Hedging` | `Hedging` | `existence` | error |
| `Direct.Length`, and `Std.Readability.SentenceLength` it extends | `SentenceLength` | `occurrence` | suggestion |
| `Direct.Preamble` | `Preamble` | `existence` | error |
| `Readability.FleschKincaid` | `GradeLevel` | `metric` | suggestion |
| `Std.Abbreviations.Latin` | `LatinAbbreviation` | `substitution` | suggestion |
| `Std.Punctuation.Spacing` | `SentenceSpacing` | `existence` | suggestion |
| `Std.Usage.GenderedPronouns` | `GenderedPronouns` | `existence` | suggestion |
| `Std.Usage.GenderedTerms` | `GenderedTerms` | `substitution` | suggestion |

The 14 opt-in rules keep their upstream names: `AutomatedReadability`, `ColemanLiau`, `FleschReadingEase`, `GunningFog`, `LIX`, `SMOG`, `Polysyllables`, `PassiveVoice`, `OxfordComma`, `Contractions`, `FirstPersonPlural`, `FirstPersonSingular`, `DateFormat` and `TimeFormat`.  
Their levels stay those of their rule files.

None of the 31 new names equals one of the 44 existing names, which a comparison of the file names showed.  
`SentenceLength` takes the level and the 25-word limit of `Direct.Length`, and the body of `Std.Readability.SentenceLength`, so the parent folder goes.  
The fields `action: replace` of four substitution rules stay: hakkiri loads them and applies none until `HKR-011`.

Alternative: keep the four upstream styles beside `ProseStyle`.  
It lost because the operator ruled that ProseStyle owns its rules, and a copy of a style the package does not own drifts from its source with no way to fix it here.

The rules the package leaves out are `Voices.ColonReveal` and `Direct.Ease`, which its own `.vale.ini` turned off, `Std.Abbreviations.Acronyms`, which `UndefinedAcronym` covers with a wider test and a longer list, and `Std.Punctuation.Ellipses`, which flags the `…` that `Emoji` allows.

### 2. The six script rules become native rules

A probe in hakkiri `main` rewrote the six rules from their Tengo source and ran the 18 cases of `v0.0.14`: all 18 pass, after one fixture input changed.

| Rule | Check type | Scope |
|:--|:--|:--|
| `FlatRhythm` | `metric`, `sentence_length_sd` with `sentences >= 5` | `paragraph` |
| `BareWorkItem` | `existence`, lookaround pattern for the code and the standard names | `text & ~code & ~link` |
| `SameSentenceStart` | `existence`, backreference and lookahead | `paragraph` |
| `HardBreak` | `existence`, a newline not preceded by two spaces or a backslash | `text.md` |
| `SentencePerLine` | `existence`, abbreviation lookbehinds | `text & ~heading & ~table & ~code & ~link` |
| `PrepositionChain` | `existence`, chain of three prepositions | `sentence` |

The rules differ from the scripts in these ways, and each gets a case:

- `SameSentenceStart` marks the first of the three openings, and the script marked the third.
- `HardBreak` reads the Markdown tree.  
  It flags a continuation line inside a block quote, which the script skipped.  
  It skips a setext heading and an indented code block, which the script flagged.
- `PrepositionChain` drops a chain that overlaps a code span, where the script restarted after the span.
- `FlatRhythm` counts words and sentences as hakkiri does, not with the script's own pattern.
- `BareWorkItem` is `text`, so it also reads comments in a Rust file, where `BareWorkItemInComment` reads them already; the Rust switch below keeps one alert.

The sizes were measured on one file of 8,000 lines with 16,000 codes: all six rules ran over it in 0.96 s.  
An alert diff against Vale over the public repositories is the proof that remains, and `HKR-008` names it.

Alternative: wait for hakkiri to run Tengo (`HKR-036`).  
It lost because the operator ruled the rules native, and the interpreter has to run faster than Vale before it ships.

### 3. The settings file ships the switches of the `.vale.ini`

`ProseStyle/.ctl/hakkiri.yaml` sits beside `ProseStyle/styles/`, where the operator chose it and where Vale keeps a package's `.vale.ini`.

| `.vale.ini` | `.ctl/hakkiri.yaml` |
|:--|:--|
| `Vocab = ProseStyle` | `vocab: [ProseStyle]` |
| `[*.{md,mdx,rs}] BasedOnStyles = ProseStyle, Voices, Direct` | `'*.{md,mdx,rs}': {styles: [ProseStyle]}` |
| `Voices.ColonReveal = NO`, `Direct.Ease = NO` | none: both rules are gone |
| `Direct.Length`, `Readability.FleschKincaid` and four `Std` rules set to `suggestion` | the level in each rule file |
| `[formats] rs = md` | none: hakkiri reads Rust comments as Markdown |
| `[*.rs]` with six rules `NO` | `'*.rs'` with the same six rules `off` |
| `[**/openspec/changes/**/*.md] StaleWords = NO` | the same glob with `ProseStyle.StaleWords: off` |
| none | the 14 opt-in rules `off` under the first glob |

The six rules off in Rust files are `BareURL`, `BareWorkItem`, `SentencePerLine`, `HardBreak`, `VagueLinkText` and `UnpinnedCodeLink`.  
`SentencePerLine` and `HardBreak` read Markdown only now, so their switch is redundant and stays for safety until a Rust case shows it is not needed.

A project turns an opt-in rule on with `ProseStyle.PassiveVoice: on` under its own glob, which wins over the package.

Alternative: ship no settings and have each project copy them.  
It lost because the 14 opt-in rules would then run for every project, and `HKR-040` exists to avoid that.

### 4. The build packs the tracked folder

`mise-tasks/build.py` zips `ProseStyle/`, including `NOTICE`, `LICENSE` and `.ctl/hakkiri.yaml`, with dated entries as it does now, so the same inputs give the same bytes.  
`upstream.toml`, `download`, `upstream_files` and the sha256 check go.  
`check_rule_names` goes with `ProseStyle/.vale.ini`: hakkiri refuses a rule key that names no rule, so the tests catch a rename.  
The six `.tengo` files go, and `config/vocabularies/ProseStyle/accept.txt` stays inside `styles/`.

### 5. `NOTICE` and `LICENSE`

The package credits the MIT sources of the ports (operator, 2026-11-11), rule by rule:

| Source | Copyright | Ports |
|:--|:--|:--|
| [no-ai-slop][no-ai-slop] | 2026 Peter Yang | `SlopWords`, `InflatedWords`, `BinaryContrast`, `ThroatClearing`, `Puffery`, `VagueAttribution`, `RecapOpener`, `SuperficialAnalysis`, `WeakVerbs`, through Voices |
| [Vale Voices][voices] | 2026 Joseph Kato and contributors | the nine rules above, and `Hedging`, `SentenceLength` and `Preamble` |
| [`awesome-claude-output-styles`][aco-styles] | 2026 Serge Shima | `Hedging`, `SentenceLength` and `Preamble`, shaped after its entry |
| [errata-ai/Google][std] | Joseph Kato | `GenderedPronouns`, and the base of `LatinAbbreviation` and `GenderedTerms`; the opt-in `PassiveVoice`, `OxfordComma`, `FirstPersonPlural`, `DateFormat` and `TimeFormat` |
| [errata-ai/Microsoft][std] | 2018 to 2019 Joseph Kato | `SentenceSpacing`, entries of `GenderedTerms`; the opt-in `FirstPersonSingular` and `Contractions` |
| [errata-ai/IBM][std] | Joseph Kato | `SentenceLength`, entries of `LatinAbbreviation` |
| [Vale Readability][readability] | 2026 Joseph Kato | `GradeLevel`; the six opt-in scores, and `Polysyllables` as a native port of its script |

The three upstream licence files are the MIT text with a different copyright line, so one `LICENSE` holds the text and the lines above.

### 6. The tests run on a pinned hakkiri

`mise.toml` pins hakkiri 0.0.6 from its GitHub release, the first that holds the settings, the block ignores and the plain-text default this package needs, with an exact version and a lock file for `linux-x64` and `macos-arm64`, the two assets a release holds.

| Task | Now | After |
|:--|:--|:--|
| `test:rules` | `vale test --coverage ProseStyle/styles/ProseStyle` | `hakkiri test --coverage ProseStyle/styles` |
| `test:package` | `vale sync`, then `vale test package.test.yml` | unpack the zip into `test/package`, then `hakkiri test` in `test/` |
| `test:messages` | `vale --output JSON` over a page of messages | `hakkiri check --format json` over the same page |

- `test/.vale.ini` becomes `test/.ctl/hakkiri.yaml` with `packages: [{path: package/ProseStyle/styles}]`.  
  The consumer then reads the unpacked zip and its settings file as a project does.
- The cases in `test/package.test.yml` take the new names and use `format: rs` and `format: txt` in place of `.rs` and `.txt`.  
  The cases that name `Voices.ColonReveal` and `Direct.Ease` go.
- `test:messages` reads `level`, `rule` and `line` of the JSON in place of `Severity`, `Check` and `Line`.  
  Its list of page-level checks names `GradeLevel`.

Alternative: run the tests on a hakkiri built from source.  
It lost because a pin by exact release is what a project does.

### 7. The release prints a `packages:` entry

A tag builds both zips and publishes them.
`ProseStyle.zip` is the one asset of the hakkiri package, and `PullRequestStyle.zip` is the Vale package of the pull request check.  
The release notes hold a block a project pastes into `.ctl/hakkiri.yaml`:

```yaml
packages:
  - url: https://github.com/victor-software-house/prose-style/releases/download/<tag>/ProseStyle.zip
    sha256: <the hash of the zip>
```

The job computes the hash from the zip it uploads.  
The old line, `Packages = <url>`, goes.  
The README names `v0.0.14` as the last release a Vale project can pin.

### 8. Two overlaps close

- `StockPhrases` loses `harness(?:es)? the (?:full )?(?:power|potential)`, which `SlopWords` covers with `harness(?:es|ed|ing)?`.  
  The vocabulary entry for the noun `harness` stays.
- `FormalWords` flags `stands as`, which draws a second alert on `stands as a testament`.  
  The swap becomes `stands as(?! a testament)`, so only `Puffery` fires there.

The comments that name `Voices.InflatedWords`, `Voices.BinaryContrast` and `Direct.Length` in `FormalWords`, `StrawMan` and `LongSentence` take the new names.  
`SentenceLength` at 25 words beside `LongSentence` at 40 stays, so a sentence over 40 words draws a suggestion and an error, by design.

### 9. `BareURL` is rewritten on the `link` scope

`BareURL` finds a URL outside fences and code spans with a raw-scope pattern that holds lookbehinds.  
In hakkiri 0.0.4 that pattern reached the backtrack limit of 1,000,000 steps on 131 of the 165 Markdown files of hakkiri's own documents.  
Each of those files draws an error in place of an alert.  
`bareurl-single-scan` describes the same limit in Vale's engine.

A probe rule on the `link` scope, with `raw: '^https?://\S+$'`, flagged a bare URL, an autolink in angle brackets and a link whose text is its URL.  
It passed a link with words as text, a URL in a code span and a URL in a fenced block.  
The rule reads the `link` and `alt` scopes with the pattern `https?://[^\s<>]+`, so a URL in link text or in the alt text of an image draws an alert too.
A planted comparison with Vale at `v0.0.14` gave alerts on the same lines, except that hakkiri flags a URL in plain parentheses or double quotes and cannot read a link's title attribute.
So the rewrite is the first change of that open change, and it stands on its own.  
`BareURLInComment` ran on the Rust files with no limit alert and stays as it is.

Alternative: raise the limit in hakkiri.  
It lost because the time of the pattern grows with the file's length times the number of URLs, and a limit only moves the failure to longer files.

## Risks

- A project that names a dropped or renamed rule fails to load.  
  The change cannot see those configs, and the tag notes list every rename.

## Open decisions

1. **The tag.** The tag is `v0.0.16`, because `v0.0.15` went to `PullRequestStyle` (operator, 2026-11-11), and it stays a patch while the alert diff shows the same or better alerts than Vale with `v0.0.14`.
2. **The mirror.** The CI downloads tools through a mirror, and nothing here shows that the mirror serves a release of another repository.

The open change `bareurl-single-scan` closed with decision 9, and its spec is `bare-urls`.

[aco-styles]: https://github.com/smixs/awesome-claude-output-styles
[no-ai-slop]: https://github.com/petergyang/no-ai-slop
[readability]: https://github.com/vale-cli/Readability/releases/tag/v0.2.0
[std]: https://github.com/vale-cli/Std/releases/tag/v0.2.0
[voices]: https://github.com/jdkato/voices/releases/tag/v0.2.0
