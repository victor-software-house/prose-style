# Proposal

Queue row: `HKR-008` in the [hakkiri ledger][hkr-008].
It builds on `HKR-040`, package settings, which [PR 87][pr-87] merged.

## Motivation

`ProseStyle.zip` is a Vale package today.
It contains 44 rules of its own and 36 rule files copied from three upstream packages.
Six of its rules run as Tengo scripts, and a `.vale.ini` turns it all on.
hakkiri replaces Vale for it, and hakkiri runs none of those three things as they stand:

- it loads a Vale style folder, but it rejects a script rule until the config turns it `off`, so six of the 44 do not run;
- it reads no `.vale.ini`, so no rule is on and the settings of the package do not apply;
- it runs the 36 copied rules, but the package owns none of them, and 19 of them no project turned on.

The operator made three decisions (operator, 2026-11-11):

- ProseStyle owns its rules.
- From its next release, the zip is the hakkiri package.
- The hakkiri package is one asset.


`PullRequestStyle.zip`, the Vale package of the pull request check, stays beside it.

## Changes

- The six script rules become native rules: five `existence` rules and one `metric` rule.
  A probe passed the 18 cases of the six rules from `v0.0.14`, after one fixture input changed, with the differences the design lists.
- 17 upstream rules join the style as they are or renamed, 14 more join as opt-in rules that ship off, and 4 are dropped.
  The style then contains 75 rules.
- The package ships `ProseStyle/.ctl/hakkiri.yaml` beside `ProseStyle/styles/`.
  It turns the style on for Markdown, MDX (Markdown with components) and Rust files, and switches the 14 opt-in rules off.
  It keeps the switches that the `.vale.ini` contains.
- `upstream.toml`, the download in `mise-tasks/build.py` and every copied style folder go.
  `NOTICE` and `LICENSE` credit the MIT sources of the ports.
- The tests run on a pinned hakkiri release, `hakkiri test` and `hakkiri check` in place of `vale test` and `vale`.
- The release notes print a `packages:` entry with the `url` and the `sha256` of the zip.
- `README.md` and `AGENTS.md` describe the hakkiri package.
- `BareURL` becomes a rule on the `link` scope.
  In a probe, the raw pattern failed on 131 of 165 files.
- Two overlaps close: `harness the power` leaves `StockPhrases`, and `stands as a testament` draws one alert.

## Capabilities

### New Capabilities

- `hakkiri-package`: what the zip contains, the settings it ships, and how it is built, tested and released.

### Modified Capabilities

None.

## Impact

- Projects that pin `v0.0.14` keep Vale.
  Projects that pin the next release run hakkiri, and Vale cannot read it.
- A project's config may use a rule of an upstream style, such as `Voices.ColonReveal` or `Direct.Length`.
  That project must rename the rule, since hakkiri rejects a key that matches no rule.
  The templates repository contains the projects' configs, so that is where to look.
- `BareURL` reaches hakkiri's backtrack limit on most Markdown files.
  So it is rewritten on the `link` scope, the first change of the open `bareurl-single-scan`.

[hkr-008]: https://github.com/victor-software-house/hakkiri/blob/21425fba51ef099fc6c3ffbc638bc13379a3a737/tasks.yaml
[pr-87]: https://github.com/victor-software-house/hakkiri/pull/87
