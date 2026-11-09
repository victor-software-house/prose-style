## Why

[BareURL][bareurl] and [BareURLInComment][bareurlincomment] decide whether a URL sits in a fenced block or a code span with lookbehinds.  
The fence lookbehind reads from the top of the file, one loop step per line.  
The code-span lookbehinds read the URL's line, one loop step per character.  
[regexp2][regexp2-limit] gives a match 100,000 backtracking slots, and Vale panics when a match runs out.  
So a URL in a file of about 12,000 lines, or on a line of about 14,000 characters, stops the whole Vale run.

A test planted URLs in comments, code and strings of 870 Rust files from a large crate, on one line in 25 and on every line over 14,000 characters.  
Release v0.0.6 panicked on 14 files.  
After the comment bodies in BareURLInComment became runs of characters other than `*`, 11 files still panicked: 6 files of 12,800 to 57,500 lines, 4 files with lines of 41,000 to 51,000 characters, and a synthetic file with lines of 20,000.  
The fence lookbehind also scans from the top of the file at each URL, so the time grows with the URL count times the file length: a URL on every line took over 10 minutes per generated file.  
A project avoids the panic only by leaving such files out, as the template's `generated_paths` answer does.

## What Changes

- Markdown: replace BareURL's raw-scope regex with a rule on the `link` scope.  
  Vale renders Markdown with [goldmark and GFM][vale-md], which turns a bare URL into a link, and [maps `a` to `link`][vale-ast].  
  A bare URL or an autolink then shows as a link whose text is its URL, and fenced code and code spans never reach that scope.
- Rust comments: Vale 3.26.0 reads only [line comments][vale-rs] as Markdown, so the `link` scope misses `/* */` blocks.  
  Check them with a [Tengo script][vale-script] rule that scans the file once, or keep raw scope for block comments only.
- Each candidate flags exactly what v0.0.6 flags on every file where v0.0.6 finishes, proved by the same planted-URL comparison, with no panics.

## Capabilities

### New Capabilities

- `bare-urls`: which URLs the package flags as bare, in Markdown and in Rust comments, and the file sizes the check handles.

### Modified Capabilities

None.

## Impact

- `BareURL.yml` and `BareURLInComment.yml` change scope or kind; their tests keep every current case.
- Projects that leave large generated files out for this reason can lint them again.

[bareurl]: ../../../ProseStyle/styles/ProseStyle/BareURL.yml
[bareurlincomment]: ../../../ProseStyle/styles/ProseStyle/BareURLInComment.yml
[regexp2-limit]: https://github.com/jdkato/regexp2/blob/af31cb0c57f76300c511ddf59009a2b27c2ade4b/options.go#L8
[vale-md]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/lint/md.go#L20-L22
[vale-ast]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/lint/ast.go#L41
[vale-rs]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/lint/code/rs.go
[vale-script]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/check/script.go
