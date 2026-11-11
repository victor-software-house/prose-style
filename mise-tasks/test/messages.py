#!/usr/bin/env python3
#MISE description="Lint every rule's message with the built package, so the package's own words pass its rules"
#MISE depends=["test:package"]
#MISE tools = { python = "3.15.2" }
"""Lint each rule's message as a Markdown paragraph through test/.vale.ini.

`test:package` syncs the built zip into test/styles first. A rule file with no
one-line `message:` fails, so a message this script cannot read is never skipped.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RULES = [Path("ProseStyle/styles/ProseStyle"), Path("PullRequestStyle/styles/PullRequestStyle")]
MESSAGE = re.compile(r'^message: "(.*)"$', re.MULTILINE)
VERB = re.compile(r"%(?:\[\d+\])?[sd]")
# Checks that read line layout or compare paragraphs, which a one-line message
# shown on its own has neither of. Every other alert, at any level, fails.
PAGE_CHECKS = {
    "ProseStyle.FlatRhythm",
    "ProseStyle.HardBreak",
    "ProseStyle.OneTermTwoWays",
    "ProseStyle.SameSentenceStart",
    "ProseStyle.SentencePerLine",
    "Readability.FleschKincaid",
}


def alerts_of(report: object) -> list[dict] | None:
    """Every alert in a Vale JSON report, or None for a report of another shape."""
    if not isinstance(report, dict):
        return None
    files = list(report.values())
    if not all(isinstance(file, list) and all(isinstance(a, dict) for a in file) for file in files):
        return None
    return [a for file in files for a in file]


def main() -> int:
    paragraphs = []
    for rule in sorted(path for folder in RULES for path in folder.glob("*.yml")):
        found = MESSAGE.findall(rule.read_text())
        if len(found) != 1:
            print(f"{rule}: expected one message line, found {len(found)}")
            return 1
        paragraphs.append((rule.stem, VERB.sub("x", found[0])))

    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp, "messages.md")
        page.write_text("".join(f"{text}\n\n" for _, text in paragraphs))
        run = subprocess.run(
            ["vale", "--config", "test/.vale.ini", "--output", "JSON", str(page)],
            capture_output=True,
            text=True,
        )
    # Vale prints a JSON object of alert lists by file, {} with no alerts, and
    # exits 1 only on an error-level alert. A runtime error exits 2 with an
    # object of another shape. Anything else is a failed run, not a clean one.
    try:
        report = json.loads(run.stdout)
    except json.JSONDecodeError:
        report = None
    alerts = alerts_of(report)
    errors = alerts is not None and any(a.get("Severity") == "error" for a in alerts)
    if alerts is None or run.returncode not in (0, 1) or (run.returncode == 1) != errors:
        print(f"vale exited {run.returncode} with an unexpected report", file=sys.stderr)
        print(run.stderr, end="", file=sys.stderr)
        return run.returncode or 1

    failed = [a for a in alerts if a["Check"] not in PAGE_CHECKS]
    for alert in failed:
        rule, _ = paragraphs[(alert["Line"] - 1) // 2]
        print(f"{rule}: {alert['Check']}: {alert['Message']}")
    print(f"{len(paragraphs)} messages, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
