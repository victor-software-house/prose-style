# Tasks

## 1. The rewrite

- [x] 1.1 Rewrite BareURL on the `link` scope, and keep BareURLInComment on the raw scope for Rust comments.  
  Verify `hakkiri test --coverage ProseStyle/styles` passes the cases of both rules.  
  Evidence, 2026-11-11 (UTC): both rules pass their cases on hakkiri 0.0.5 in a box.
- [x] 1.2 Show that both rules finish on the sizes that stopped Vale, and that they flag what v0.0.6 flags.  
  Verify a planted comparison and a scale run, with no failure.  
  Evidence, 2026-11-11 (UTC):
  - In a box, hakkiri 0.0.5 ran BareURL and BareURLInComment on generated files without a failure.
  - A Markdown file of 12,000 lines with 480 bare URLs took 0.67 s for the rule alone.  
    A line of 14,000 characters took 0.00 s.
  - A Rust file of 50,000 lines with 2,000 comment URLs took 0.29 s.  
    A comment line of 50,000 characters took 0.01 s.
  - The planted test used a file of 24 Markdown shapes and a Rust file.  
    Vale 3.26.0 with the v0.0.14 rules and hakkiri gave alerts on the same lines, with two exceptions.  
    The Rust alerts of `BareURLInComment` were identical.
  - hakkiri flags a URL in plain parentheses or double quotes that v0.0.14 passes.  
    And v0.0.14 flags a URL in a link title that hakkiri cannot read.
  - Both flag a URL in link text or in the alt text of an image, once the rule reads the `alt` scope.
  - The hakkiri check over 233 Markdown files printed no backtrack alert.
