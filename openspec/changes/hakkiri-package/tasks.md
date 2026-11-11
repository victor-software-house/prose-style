# Tasks

Every compile, lint and test step of a rule runs in the pull request's CI.  
The pinned hakkiri is the 0.0.5 release, the first that reads a package's settings, so tasks 2 to 5 wait for it.

## 1. Write the rules

- [ ] 1.1 Add the six native script rules, each with the cases of `v0.0.14` and a case for each difference in the design, and delete the six `.tengo` files.  
  Verify `hakkiri test --coverage ProseStyle/styles` passes them, and a project that lists the unpacked zip prints no `failed` line.
- [ ] 1.2 Add the 17 ports and the 14 opt-in rules under their names, each with its cases, the `FleschKincaid` rule with a case that fires and one that stays clean, and the `SentenceLength` rule with the body of its parent.  
  Verify `hakkiri test --coverage ProseStyle/styles` passes and no file name repeats.
- [ ] 1.3 Close the two overlaps and rename the three comments, in `StockPhrases`, `FormalWords`, `StrawMan` and `LongSentence`.  
  Verify the two cases of "One fault draws one alert" pass.

- [ ] 1.4 Rewrite `BareURL` on the `link` scope and keep every current case.  
  Verify the cases pass, and `hakkiri check` over the Markdown files of this repository and of hakkiri prints no backtrack-limit alert.

## 2. Ship the settings and the credits

- [ ] 2.1 Write `ProseStyle/.ctl/hakkiri.yaml` and delete `ProseStyle/.vale.ini`.  
  Verify the cases of "The settings file ships the package's switches" pass in the consumer project.
- [ ] 2.2 Write `NOTICE` and `LICENSE` in `ProseStyle/`.  
  Verify each port named in the design appears once in `NOTICE`.

## 3. Build and test

- [ ] 3.1 Reduce `mise-tasks/build.py` to the tracked folder, and delete `upstream.toml`.  
  Verify the zip holds the style, `config`, the settings file, `NOTICE` and `LICENSE`, and two builds give the same bytes.
- [ ] 3.2 Pin hakkiri 0.0.5 in `mise.toml`, regenerate `mise.lock` for `linux-x64` and `macos-arm64`, and move the three test tasks and `test/` to hakkiri.  
  Verify `mise run test` passes in CI on the pinned release.

## 4. Release and describe

- [ ] 4.1 Print the `packages:` entry in the release notes and attach the zip as the one asset.  
  Verify a tag on a branch of the fork shows the block with the hash of the uploaded file.
- [ ] 4.2 Rewrite `README.md` and `AGENTS.md` for the hakkiri package, and close `bareurl-single-scan` once `BareURL` is rewritten.  
  Verify the lint of the repository's own Markdown passes.

## 5. Gate

- [ ] 5.1 An alert diff against Vale with `v0.0.14` over the public repositories shows only the intended differences.  
  Verify the diff lists each difference of the design and no other.
- [ ] 5.2 Pull request CI passes on the head of the pull request.  
  Verify the checks of the head commit pass in the run on the pull request.
