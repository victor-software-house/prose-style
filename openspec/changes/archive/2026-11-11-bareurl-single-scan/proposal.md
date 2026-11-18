## Why

[BareURL][bareurl] and [BareURLInComment][bareurlincomment] use lookbehinds to check whether a URL sits in a fenced block or a code span.
In BareURL the fence lookbehind reads from the top of the file, one loop step per line.

Since v0.0.8, in BareURLInComment it reads back only to the first line of the URL's comment block.
That works because a fence in a doc comment cannot span a line of code.

The code-span lookbehinds read the URL's line, one loop step per character.
[regexp2][regexp2-limit] gives a match 100,000 backtracking slots, and Vale panics when a match runs out.

So the whole Vale run stops on a URL in a Markdown file of about 12,000 lines.
In either format, a line of about 14,000 characters with a URL stops it too.

A test took 870 Rust files from a large crate and planted URLs in their comments, code and strings.
It planted them on one line in 25, and on every line over 14,000 characters.
Release v0.0.6 panicked on 14 files.

Then the comment bodies in BareURLInComment became runs of characters other than `*`.
After that change, 11 files still panicked:

- 6 files of 12,800 to 57,500 lines
- 4 files with lines of 41,000 to 51,000 characters
- a synthetic file with lines of 20,000 characters

At each URL, the fence lookbehind also scans back to the top of the file.
So the time grows with the number of URLs times the length of the file.
With a URL on every line, each generated file took over 10 minutes.
A project avoids the panic only by leaving such files out, as the template's `generated_paths` answer does.

## What Changes

- Markdown: replace BareURL's raw-scope regex with a rule on the `link` scope.
  Vale renders Markdown with [goldmark and GitHub Flavored Markdown][vale-md], which turns a bare URL into a link, and [maps `a` to `link`][vale-ast].
  A bare URL or an autolink then shows as a link whose text is its URL.
  Fenced code and code spans never reach that scope.
- Rust comments: Vale 3.26.0 reads only [line comments][vale-rs] as Markdown, so the `link` scope misses `/* */` blocks.
  Check them with a [Tengo script][vale-script] rule that scans the file once, or keep raw scope for block comments only.
- Each candidate flags exactly what v0.0.6 flags on every file where v0.0.6 finishes, with no panics.
  The same comparison with planted URLs proves it.

## Capabilities

### New Capabilities

- `bare-urls`: which URLs the package flags as bare, in Markdown and in Rust comments, and the file sizes the check handles.

### Modified Capabilities

None.

## Impact

- `BareURL.yml` and `BareURLInComment.yml` change scope or kind; their tests keep every current case.
- Projects that leave large generated files out for this reason can lint them again.

[bareurl]: ../../../../ProseStyle/styles/ProseStyle/BareURL.yml
[bareurlincomment]: ../../../../ProseStyle/styles/ProseStyle/BareURLInComment.yml
[regexp2-limit]: https://github.com/jdkato/regexp2/blob/af31cb0c57f76300c511ddf59009a2b27c2ade4b/options.go#L8
[vale-md]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/lint/md.go#L20-L22
[vale-ast]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/lint/ast.go#L41
[vale-rs]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/lint/code/rs.go
[vale-script]: https://github.com/vale-cli/vale/blob/e2d4374b1c66c8a1dd6d912bebc135040d8833fa/internal/check/script.go
