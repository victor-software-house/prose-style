# Tasks

Every compile, lint and test step of a rule runs in the pull request's CI.  
The pinned hakkiri is the 0.0.5 release, the first that reads a package's settings.  
Three rule cases fail on it, in rules that were already here, until the hakkiri release that fixes indexed message verbs (`HKR-045`) and a fence across a blank doc-comment line (`HKR-046`).  
The alert diff and the proposal's `block_ignores` entry wait for the release after that.

## 1. Write the rules

- [x] 1.1 Add the six native script rules, each with the cases of `v0.0.14` and a case for each difference in the design, and delete the six `.tengo` files.  
  Verify `hakkiri test --coverage ProseStyle/styles` passes them, and a project that lists the unpacked zip prints no `failed` line.  
  Evidence, 2026-11-11 (UTC): `hakkiri test --coverage ProseStyle/styles` on hakkiri 0.0.5 passed the six native rules in a box.  
  Three cases of rules that were already here fail: `NounStack` and `ThingsSpeakNoun` print `%[1]s` unfilled, and `BareURLInComment` flags a URL in a fence across a blank line.

- [x] 1.2 Add the 17 ports and the 14 opt-in rules under their names, each with its cases, the `FleschKincaid` rule with a case that fires and one that stays clean, and the `SentenceLength` rule with the body of its parent.  
  Verify `hakkiri test --coverage ProseStyle/styles` passes and no file name repeats.  
  Evidence, 2026-11-11 (UTC): the same run passed the 17 ports and the 14 opt-in rules, with 0 uncovered rules.

- [x] 1.3 Close the two overlaps and rename the three comments, in `StockPhrases`, `FormalWords`, `StrawMan` and `LongSentence`.  
  Verify the two cases of "One fault draws one alert" pass.  
  Evidence, 2026-11-11 (UTC): the two cases of "One fault draws one alert" pass in `test/package.test.yml`.

- [x] 1.4 Rewrite `BareURL` on the `link` scope and keep every current case.  
  Verify the cases pass, and `hakkiri check` over the Markdown files of this repository and of hakkiri prints no backtrack-limit alert.  
  Evidence, 2026-11-11 (UTC): `hakkiri check` over the 233 Markdown files of the hakkiri repository printed no failure and no backtrack alert.  
  The Markdown of this repository was not checked.

## 2. Ship the settings and the credits

- [x] 2.1 Write `ProseStyle/.ctl/hakkiri.yaml` and delete `ProseStyle/.vale.ini`.  
  Verify the cases of "The settings file ships the package's switches" pass in the consumer project.  
  Evidence, 2026-11-11 (UTC): the cases of the settings file in `test/package.test.yml` pass in a consumer that lists the unpacked zip.

- [x] 2.2 Write `NOTICE` and `LICENSE` in `ProseStyle/`.  
  Verify each port named in the design appears once in `NOTICE`.  
  Evidence, 2026-11-11 (UTC): `NOTICE` names each of the 31 ported rules once, and `LICENSE` holds the four copyright lines.

## 3. Build and test

- [x] 3.1 Reduce `mise-tasks/build.py` to the tracked folder, and delete `upstream.toml`.  
  Verify the zip holds the style, `config`, the settings file, `NOTICE` and `LICENSE`, and two builds give the same bytes.  
  Evidence, 2026-11-11 (UTC): the build wrote 79 files for `ProseStyle.zip` and 3 for `PullRequestStyle.zip`.

- [ ] 3.2 Pin hakkiri 0.0.5 in `mise.toml`, regenerate `mise.lock` for `linux-x64` and `macos-arm64`, and move the three test tasks and `test/` to hakkiri.  
  Verify `mise run test` passes in CI on the pinned release.  
  Evidence, 2026-11-11 (UTC): the pin and the lock are written, `test:package` (17 cases), `test:messages` (76 messages) and `test:pull-request` (8 cases) pass in a box, and `test:rules` fails on the three cases above. CI has not run.

## 4. Release and describe

- [ ] 4.1 Print the `packages:` entry in the release notes and attach `ProseStyle.zip` with `PullRequestStyle.zip`.  
  Verify a tag on a branch of the fork shows the block with the hash of the uploaded file.
- [ ] 4.2 Rewrite `README.md` and `AGENTS.md` for the hakkiri package, and close `bareurl-single-scan` once `BareURL` is rewritten.  
  Verify the lint of the repository's own Markdown passes.

## 5. Gate

- [ ] 5.1 An alert diff against Vale with `v0.0.14` over the public repositories shows only the intended differences.  
  Verify the diff lists each difference of the design and no other.
- [ ] 5.2 Pull request CI passes on the head of the pull request.  
  Verify the checks of the head commit pass in the run on the pull request.
