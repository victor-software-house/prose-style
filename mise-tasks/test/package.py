#!/usr/bin/env python3
#MISE description="Unpack the built ProseStyle.zip into test/ as a project does, then run the project cases"
#MISE depends=["build"]
#MISE tools = { python = "3.15.2" }
"""Unpack ProseStyle.zip into test/package and run test/package.test.yml on it.

test/.ctl/hakkiri.yaml lists the unpacked styles folder, so hakkiri reads the
package settings beside it as it does for a project that pins the release.
"""

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PACKAGE = Path("test/package")


def main() -> int:
    shutil.rmtree(PACKAGE, ignore_errors=True)
    with zipfile.ZipFile("ProseStyle.zip") as archive:
        archive.extractall(PACKAGE)
    return subprocess.run(["hakkiri", "test", "package.test.yml"], cwd="test").returncode


if __name__ == "__main__":
    sys.exit(main())
