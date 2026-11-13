## ADDED Requirements

### Requirement: The zip holds one style of native rules

`ProseStyle.zip` SHALL hold one top folder, `ProseStyle`, whose `styles` folder holds the style `ProseStyle` and the folder `config`, and no other style.  
No rule of the style SHALL extend `script`, and no file of the zip SHALL come from a download made at build time.

#### Scenario: A run with no failed rule

- **WHEN** a project lists the unpacked zip and runs `hakkiri check` on a Markdown file
- **THEN** hakkiri prints no `failed` line for a rule it cannot run, and exits 0 or 1 by the alerts

#### Scenario: One style folder

- **WHEN** the zip is listed
- **THEN** `ProseStyle/styles` holds `ProseStyle` and `config`, and `ProseStyle/.ctl/hakkiri.yaml` sits beside it

### Requirement: The style holds 75 rules

The style SHALL hold the 44 rules of `v0.0.14`, the 17 ports and the 14 opt-in rules named in the design, each in a file of its own with `tests`.  
A rule SHALL flag nothing outside its own cases' reach: `hakkiri test --coverage` SHALL pass.

#### Scenario: The names

- **WHEN** the rule files of `styles/ProseStyle` are listed
- **THEN** 75 names show, `SlopWords`, `RecapOpener`, `VagueAttribution`, `LatinAbbreviation`, `SentenceSpacing`, `SentenceLength` and `GradeLevel` among them, and no upstream style name

#### Scenario: A renamed rule

- **WHEN** `Direct.Length` is written in a project's config
- **THEN** hakkiri refuses the key, since no rule has that name

### Requirement: The six script rules run natively

`FlatRhythm`, `BareWorkItem`, `SameSentenceStart`, `HardBreak`, `SentencePerLine` and `PrepositionChain` SHALL be `existence` or `metric` rules that pass the cases of `v0.0.14` and the cases the design adds for each difference.

#### Scenario: Three sentences that open alike

- **WHEN** a Markdown file holds `The worker reads the cache. The cache holds one file. The file keeps one record.`
- **THEN** `ProseStyle.SameSentenceStart` reports `Three sentences in a row open with 'The': change the opening of one.`

#### Scenario: A continued line in a block quote

- **WHEN** a Markdown file holds `> First line` and `> Second line`
- **THEN** `ProseStyle.HardBreak` reports the first line

### Requirement: The settings file ships the package's switches

`ProseStyle/.ctl/hakkiri.yaml` SHALL turn the style on for `*.md`, `*.mdx` and `*.rs`, and SHALL set the 14 opt-in rules `off`.  
It SHALL switch `BareURL`, `BareWorkItem`, `SentencePerLine`, `HardBreak`, `VagueLinkText` and `UnpinnedCodeLink` off for `*.rs`, and `StaleWords` off for `**/openspec/changes/**/*.md`.  
It SHALL name the vocabulary `ProseStyle`.

#### Scenario: An opt-in rule off

- **WHEN** a project lists the zip and no more, and a Markdown file holds `The cache was bought by the team.`
- **THEN** `ProseStyle.PassiveVoice` reports nothing, and with `ProseStyle.PassiveVoice: on` under a glob of the project it reports `'was bought' looks like passive voice.`

#### Scenario: A Rust file

- **WHEN** a Rust file holds the doc comment `/// Fixed in EVO-9673.`
- **THEN** `ProseStyle.BareWorkItemInComment` reports it and `ProseStyle.BareWorkItem` reports nothing

#### Scenario: The vocabulary

- **WHEN** a Markdown file holds `The freshness harness writes to stdout.`
- **THEN** `ProseStyle.SlopWords` reports nothing, and `They harnessed the cache.` draws `Inflated word: 'harnessed'. Say the plain thing.`

### Requirement: One fault draws one alert

A text SHALL draw one alert from `SlopWords` and none from `StockPhrases` for `harness the power`, and one from `Puffery` and none from `FormalWords` for `stands as a testament`.

#### Scenario: A power phrase

- **WHEN** a Markdown file holds `Harness the power of the cache.`
- **THEN** one alert shows, from `ProseStyle.SlopWords`

#### Scenario: A testament phrase

- **WHEN** a Markdown file holds `This stands as a testament to the team.`
- **THEN** one alert shows, from `ProseStyle.Puffery`

### Requirement: The package credits its sources

The zip SHALL hold `ProseStyle/NOTICE` and `ProseStyle/LICENSE`.  
`NOTICE` SHALL name each MIT source, its copyright line and the rules ported from it.

#### Scenario: A listed source

- **WHEN** `NOTICE` is read
- **THEN** it names no-ai-slop with Peter Yang, Vale Voices with Joseph Kato, `awesome-claude-output-styles` with Serge Shima, and the Google, Microsoft and IBM styles and the Readability style with Joseph Kato, and each port appears once

### Requirement: The release prints a packages entry

The release notes SHALL hold a `packages:` block with the `url` of the zip and its `sha256`, and the release SHALL attach `ProseStyle.zip` as the hakkiri package, beside `PullRequestStyle.zip`.

#### Scenario: A release

- **WHEN** the tag job finishes
- **THEN** the notes hold a `url` that ends in `/ProseStyle.zip` and the 64 hex digits of the hash of the uploaded file, and the release holds `PullRequestStyle.zip` and no other asset

### Requirement: BareURL runs on every Markdown file

`BareURL` SHALL read the `link` scope.  
It SHALL flag a bare URL, an autolink and a link whose text is its URL.  
It SHALL pass a link with words as text, a URL in a code span and a URL in a fenced block.  
No file SHALL draw a backtrack-limit alert from it.

#### Scenario: A bare URL beside a fence

- **WHEN** a Markdown file holds a fenced block, then `See https://x.example now.`
- **THEN** `ProseStyle.BareURL` reports `Bare URL 'https://x.example': put the link on the words that name it.` once, and no alert names a backtrack limit

#### Scenario: A URL in code

- **WHEN** a Markdown file holds `Use `https://code.example/five` here.`
- **THEN** `ProseStyle.BareURL` reports nothing
