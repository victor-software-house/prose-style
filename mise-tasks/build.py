#!/usr/bin/env python3
#MISE description="ProseStyle.zip, the hakkiri package, and PullRequestStyle.zip"
#MISE tools = { python = "3.15.2" }
"""Build ProseStyle.zip, the hakkiri package, and PullRequestStyle.zip, the Vale
package a pull request's text adds to the frozen v0.0.14 ProseStyle zip.

Each zip holds the tracked files of its folder and nothing else: ProseStyle's
rules, vocabulary, settings file, NOTICE and LICENSE, so a project's one
download is exactly what the tests ran on.
"""

import subprocess
import zipfile

PACKAGE = "ProseStyle"
# The Vale package of the pull request check: it holds its own files only.
PULL_REQUEST = "PullRequestStyle"
# A fixed time for every entry, so the same inputs build the same bytes.
EPOCH = (1980, 1, 1, 0, 0, 0)


def own_files(package: str) -> dict[str, bytes]:
    """Map each tracked file under one package folder to its bytes."""
    listed = subprocess.run(["git", "ls-files", "-z", package], check=True, capture_output=True).stdout
    paths = [p for p in listed.decode().split("\0") if p]
    return {path: open(path, "rb").read() for path in paths}


def write_zip(output: str, files: dict[str, bytes]) -> None:
    """Write the files with fixed times and modes, so the same inputs build the same bytes."""
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as out:
        for path in sorted(files):
            entry = zipfile.ZipInfo(path, EPOCH)
            entry.external_attr = 0o644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(entry, files[path])
    print(f"{output}: {len(files)} files")


def main() -> None:
    write_zip(f"{PACKAGE}.zip", own_files(PACKAGE))
    write_zip(f"{PULL_REQUEST}.zip", own_files(PULL_REQUEST))


main()
