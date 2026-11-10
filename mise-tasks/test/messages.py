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

RULES = Path("ProseStyle/styles/ProseStyle")
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


def main() -> int:
    paragraphs = []
    for rule in sorted(RULES.glob("*.yml")):
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
    # Vale prints a JSON object, {} with no alerts, and exits 1 only on an
    # error-level alert. Anything else is a failed run, not a clean one.
    try:
        report = json.loads(run.stdout)
    except json.JSONDecodeError:
        report = None
    alerts = [a for file in (report or {}).values() for a in file]
    errors = any(a["Severity"] == "error" for a in alerts)
    if not isinstance(report, dict) or run.returncode not in (0, 1) or (run.returncode == 1) != errors:
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
