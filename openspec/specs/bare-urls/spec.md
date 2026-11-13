# bare-urls Specification

## Purpose

BareURL and BareURLInComment flag a URL written bare, and they finish on files of any size.
The size limits come from the files that stopped Vale at release v0.0.6.

## Requirements

### Requirement: The bare URL check finishes on any file

BareURL and BareURLInComment SHALL finish on a file of any line count and any line length, without a limit alert or a panic.

#### Scenario: A large generated file

- **WHEN** a Rust file of 50,000 lines, or with a comment line of 50,000 characters, holds a URL in a comment
- **THEN** hakkiri reports the bare URL, prints no failure, and exits

#### Scenario: A long Markdown file

- **WHEN** a Markdown file of 12,000 lines, or with a line of 14,000 characters, holds a bare URL
- **THEN** hakkiri reports it with no failure

### Requirement: The rewrite flags what v0.0.6 flags

A rewrite of the bare URL check SHALL flag the same URLs as release v0.0.6 on every file where v0.0.6 finishes.  
It SHALL also flag a URL in plain parentheses or in double quotes, and a reference definition that continues a paragraph, which v0.0.6 passes.  
It SHALL NOT flag a URL in the title attribute of a link, which v0.0.6 flags, because no scope hakkiri reads holds a title.

#### Scenario: The planted comparison

- **WHEN** both versions run on Rust and Markdown files with URLs planted in comments, code, strings, links, code spans and fenced blocks
- **THEN** each file gets the same alerts from `BareURLInComment`, and the Markdown file gets the same alerts from `BareURL` except for the shapes below

#### Scenario: A URL in parentheses or double quotes

- **WHEN** a Markdown paragraph holds `(https://l.example/x)` or `"https://m.example/y"`
- **THEN** the rewrite flags the URL, and v0.0.6 passes it because its lookbehind reads the character before it

#### Scenario: A definition line that continues a paragraph

- **WHEN** the line `[ref]: https://h.example/x` follows a line of text with no blank line between
- **THEN** the rewrite flags the URL, because CommonMark reads that line as paragraph text, and v0.0.6 passes it

#### Scenario: A URL in a link title

- **WHEN** a Markdown paragraph holds `[t](https://a.example/a "see https://b.example/b")`
- **THEN** the rewrite flags nothing in the title, and v0.0.6 flags `https://b.example/b`, a gap of the scopes hakkiri reads
