#!/usr/bin/env python3
#MISE description="The alert diff task: the .vale.ini conversion, the pairing of alerts, and a run with stand-in tools"
#MISE tools = { python = "3.15.2" }
"""Test mise-tasks/alerts/diff.py on made-up repositories and stand-in binaries."""

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "alerts" / "diff.py"
spec = importlib.util.spec_from_file_location("alerts_diff", SCRIPT)
diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diff)

INI = """\
StylesPath = .vale/styles
MinAlertLevel = warning
Packages = https://example.test/Package.zip
Vocab = Words

[formats]
rs = md

[*.{md,mdx,rs}]
BasedOnStyles = Style, Other
Style.Loud = NO
Style.Quiet = YES
Other.Mild = suggestion
BlockIgnores = (?s)BEGIN.*?END, (?m)^## Why$
TokenIgnores = ({{.*?}})

[generated/**]
BasedOnStyles =

[*.md]
Odd = 3
Style.Odd = maybe
"""


def row(path, line, column, rule, message="m", match="x", level="warning"):
    return diff.alert("repo", path, line, column, level, rule, message, match)


class Convert(unittest.TestCase):
    def test_a_vale_ini_becomes_a_hakkiri_config(self):
        config, notes = diff.convert(INI, Path("/package/styles"))
        self.assertEqual(
            config,
            {
                "level": "warning",
                "vocab": ["Words"],
                "packages": [{"path": "/package/styles"}],
                "formats": {"rs": "md"},
                "files": {
                    "*.{md,mdx,rs}": {
                        "styles": ["Style", "Other"],
                        "Style.Loud": "off",
                        "Style.Quiet": "on",
                        "Other.Mild": "suggestion",
                        "block_ignores": ["(?s)BEGIN.*?END", "(?m)^## Why$"],
                        "token_ignores": ["({{.*?}})"],
                    },
                    "generated/**": {"styles": []},
                    "*.md": {},
                },
            },
        )
        self.assertEqual(
            notes,
            [
                "StylesPath: replaced by the package of the run",
                "Packages: replaced by the package of the run",
                "[*.md] Odd = 3: no hakkiri key or setting",
                "[*.md] Style.Odd = maybe: no hakkiri key or setting",
            ],
        )


class Diff(unittest.TestCase):
    def test_alerts_pair_by_place_then_by_match(self):
        vale = [
            row("a.md", 1, 1, "S.One"),
            row("a.md", 2, 5, "S.One", message="old"),
            row("a.md", 3, 1, "S.One", match="moved"),
            row("a.md", 9, 1, "S.One", match="gone"),
            row("b.md", 1, 1, "S.Two"),
        ]
        hakkiri = [
            row("a.md", 1, 1, "S.One"),
            row("a.md", 2, 5, "S.One", message="new"),
            row("a.md", 4, 2, "S.One", match="moved"),
            row("a.md", 7, 1, "S.One", match="extra"),
        ]
        rows, same = diff.diff(vale, hakkiri)
        self.assertEqual(dict(same), {"S.One": 1})
        self.assertEqual(
            sorted((each["kind"], each["rule"], each["path"], each["vale"], each["hakkiri"]) for each in rows),
            [
                ("changed", "S.One", "a.md", "2:5", "2:5"),
                ("moved", "S.One", "a.md", "3:1", "4:2"),
                ("only-hakkiri", "S.One", "a.md", "", "7:1"),
                ("only-vale", "S.One", "a.md", "9:1", ""),
                ("only-vale", "S.Two", "b.md", "1:1", ""),
            ],
        )

    def test_a_table_reads_back_what_it_wrote(self):
        hard = [row("a b.md", 1, 1, "S.One", message="tab\there\nline \\ end", match="x\ny")]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "t.tsv"
            diff.write_table(path, hard)
            self.assertEqual(diff.read_table(path), hard)


STAND_IN = """#!/bin/sh
{script}
"""


class Run(unittest.TestCase):
    def test_both_tools_run_and_the_diff_names_each_difference(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "checkout"
            repo.mkdir()
            git = lambda *args: subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
            git("init", "-q")
            (repo / ".vale.ini").write_text(INI)
            (repo / "one.md").write_text("one\n")
            (repo / "two.md").write_text("two\n")
            git("add", "-A")
            vale_json = json.dumps(
                {
                    "one.md": [
                        {"Line": 1, "Span": [1, 3], "Severity": "warning", "Check": "S.One", "Message": "m", "Match": "one"}
                    ],
                    "two.md": [
                        {"Line": 2, "Span": [4, 6], "Severity": "error", "Check": "S.Two", "Message": "m", "Match": "two"}
                    ],
                }
            )
            hakkiri_json = json.dumps(
                {
                    "alerts": [
                        {"path": "one.md", "line": 1, "column": 1, "level": "warning", "rule": "S.One", "message": "m", "match": "one"}
                    ],
                    "failures": [],
                    "files": 2,
                }
            )
            vale = root / "vale"
            vale.write_text(STAND_IN.format(script=f'[ "$1" = sync ] && exit 0\n[ "$1" = --version ] && echo vale 1 && exit 0\ncat <<\'EOF\'\n{vale_json}\nEOF'))
            hakkiri = root / "hakkiri"
            hakkiri.write_text(STAND_IN.format(script=f'[ "$1" = --version ] && echo hakkiri 1 && exit 0\ncat <<\'EOF\'\n{hakkiri_json}\nEOF'))
            for binary in (vale, hakkiri):
                binary.chmod(0o755)
            package = root / "package"
            (package / "styles").mkdir(parents=True)
            out = root / "out"
            self.assertEqual(
                diff.main(
                    ["--repos", str(repo), "--vale", str(vale), "--hakkiri", str(hakkiri), "--package", str(package), "--out", str(out)]
                ),
                0,
            )
            self.assertEqual(len(diff.read_table(out / "alerts-vale.tsv")), 2)
            self.assertEqual(len(diff.read_table(out / "alerts-hakkiri.tsv")), 1)
            table = (out / "diff.tsv").read_text().splitlines()
            self.assertEqual(len(table), 2)
            self.assertTrue(table[1].startswith("only-vale\tS.Two\tcheckout\ttwo.md\t2:4"))
            self.assertIn("Odd = 3", (out / "checkout" / "conversion.txt").read_text())
            self.assertFalse((repo / ".alert-diff.hakkiri.yaml").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
