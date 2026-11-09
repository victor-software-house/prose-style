## ADDED Requirements

### Requirement: The bare URL check finishes on any file

BareURL and BareURLInComment SHALL finish on a file of any line count and any line length, without a Vale panic.

#### Scenario: A large generated file

- **WHEN** a Rust file of 50,000 lines, or with a line of 50,000 characters, holds a URL in a comment
- **THEN** Vale reports the bare URL and exits without a panic

### Requirement: The rewrite flags what v0.0.6 flags

A rewrite of the bare URL check SHALL flag the same URLs as release v0.0.6 on every file where v0.0.6 finishes.

#### Scenario: The planted comparison

- **WHEN** both versions run on Rust and Markdown files with URLs planted in comments, code, strings, links, code spans and fenced blocks
- **THEN** each file where v0.0.6 finishes gets the same alerts from both
