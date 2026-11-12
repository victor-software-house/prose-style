#!/usr/bin/env python3
#MISE description="Run Vale and hakkiri over the same files of some checkouts, write one alert table per tool, and diff them by rule"
#MISE tools = { python = "3.15.2" }
"""Compare the alerts Vale gives with the alerts hakkiri gives, on real repositories.

Run it as `mise run alerts:diff -- --repos <checkout>... --vale <binary>
--hakkiri <binary> --package <folder|zip> --out <folder>`. Every input also
reads an environment variable, and a flag wins over its variable:

    --repos     ALERTS_DIFF_REPOS     checkouts, separated like PATH
    --vale      ALERTS_DIFF_VALE      a Vale binary
    --hakkiri   ALERTS_DIFF_HAKKIRI   a hakkiri binary
    --package   ALERTS_DIFF_PACKAGE   the ProseStyle package hakkiri reads, a
                                      folder with a styles folder, or a zip
    --out       ALERTS_DIFF_OUT       where the tables and the diff go

Nothing about a repository is kept in this repository: the names, the paths and
the alerts come from the arguments and go to the output folder only.

For each checkout the files are the regular files `git ls-files` lists. Vale
runs each repository's own `.vale.ini`, after `vale sync`. hakkiri runs the
equivalent of that file, written to a temporary config in the checkout and
removed afterwards, over the package. The conversion keeps the glob sections in
order with their styles, rule settings and ignores, `MinAlertLevel`, `Vocab`
and `[formats]`, and notes every key it leaves out in `conversion.txt`.

The output folder holds `alerts-vale.tsv` and `alerts-hakkiri.tsv`, one row per
alert, and `diff.md` and `diff.tsv` once both tables exist. The diff pairs the
alerts of one rule in one file: an alert at the same line and column is the
same alert, and one with a different message or level is `changed`. A leftover
alert with the same matched text on both sides is `moved`, and what remains is
`only-vale` or `only-hakkiri`. A run with one tool writes that tool's table and
diffs against the table the other tool left in the folder, so the two sides can
run at different times.
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
import posixpath
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

COLUMNS = ["repo", "path", "line", "column", "level", "rule", "message", "match"]
LEVELS = {"suggestion", "warning", "error"}
# Files per command, so a long list stays under the argument limit.
CHUNK = 300
# Examples per rule and kind in diff.md. diff.tsv holds every row.
EXAMPLES = 8
KINDS = ["only-vale", "only-hakkiri", "moved", "changed"]


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command and keep its streams, whatever its exit status."""
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)


def tracked_files(repo: Path) -> list[str]:
    """The regular files git tracks in `repo`, as paths relative to it."""
    listed = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=True
    ).stdout.decode()
    files = []
    for name in filter(None, listed.split("\0")):
        path = repo / name
        if path.is_file() and not path.is_symlink():
            files.append(name)
    return files


def chunks(files: list[str]) -> list[list[str]]:
    return [files[start : start + CHUNK] for start in range(0, len(files), CHUNK)]


def normal(path: str) -> str:
    return posixpath.normpath(path.replace("\\", "/"))


def alert(repo: str, path: str, line: int, column: int, level: str, rule: str, message: str, match: str) -> dict[str, str]:
    return {
        "repo": repo,
        "path": normal(path),
        "line": str(line),
        "column": str(column),
        "level": level,
        "rule": rule,
        "message": message,
        "match": match,
    }


def vale_alerts(binary: Path, repo: Path, name: str, out: Path) -> list[dict[str, str]]:
    """The alerts Vale gives for the tracked files of `repo`, under its own config."""
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    synced = run([str(binary), "sync"], repo)
    (folder / "vale-sync.txt").write_text(synced.stdout + synced.stderr)
    if synced.returncode != 0:
        raise SystemExit(f"{name}: vale sync failed, see {folder / 'vale-sync.txt'}")
    found: list[dict[str, str]] = []
    errors = []
    for files in chunks(tracked_files(repo)):
        done = run([str(binary), "--output=JSON", "--no-exit", *files], repo)
        errors.append(done.stderr)
        try:
            table = json.loads(done.stdout or "{}")
        except json.JSONDecodeError as error:
            raise SystemExit(f"{name}: Vale printed no JSON ({error}): {done.stdout[:200]}{done.stderr[:200]}")
        for path, alerts in table.items():
            for each in alerts:
                span = each.get("Span") or [0, 0]
                found.append(
                    alert(
                        name, path, each["Line"], span[0], each["Severity"], each["Check"], each["Message"], each["Match"]
                    )
                )
    (folder / "vale.err.txt").write_text("".join(errors))
    return found


def package_folder(package: Path, out: Path) -> Path:
    """The folder a hakkiri `packages` entry names: the `styles` folder of the package."""
    if package.is_file():
        target = out / "package"
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(package) as archive:
            for member in archive.namelist():
                destination = (target / member).resolve()
                if not destination.is_relative_to(target.resolve()):
                    raise SystemExit(f"{package}: {member} leaves the folder it unpacks to")
            archive.extractall(target)
        tops = [entry for entry in target.iterdir() if entry.is_dir()]
        package = tops[0] if len(tops) == 1 else target
    if (package / "styles").is_dir():
        return (package / "styles").resolve()
    return package.resolve()


def words(value: str) -> list[str]:
    return [word.strip() for word in value.split(",") if word.strip()]


def setting(value: str) -> str | None:
    """hakkiri's word for a Vale rule setting, or None for one it has no word for."""
    word = value.strip()
    if word.upper() == "NO":
        return "off"
    if word.upper() == "YES":
        return "on"
    return word.lower() if word.lower() in LEVELS else None


def convert(ini: str, styles: Path) -> tuple[dict, list[str]]:
    """The hakkiri config that equals a `.vale.ini`, and a note for each key left out."""
    parser = configparser.ConfigParser(interpolation=None, strict=False, delimiters=("=",), comment_prefixes=("#", ";"))
    parser.optionxform = str
    parser.read_string("[__global__]\n" + ini)
    notes: list[str] = []
    config: dict = {}
    global_keys = parser["__global__"] if parser.has_section("__global__") else {}
    for key, value in global_keys.items():
        match key.lower():
            case "minalertlevel":
                if value.strip().lower() in LEVELS:
                    config["level"] = value.strip().lower()
                else:
                    notes.append(f"MinAlertLevel = {value}: not a level")
            case "vocab":
                config["vocab"] = words(value)
            case "stylespath" | "packages":
                notes.append(f"{key}: replaced by the package of the run")
            case _:
                notes.append(f"{key}: no hakkiri key")
    config["packages"] = [{"path": str(styles)}]
    formats: dict[str, str] = {}
    files: dict[str, dict] = {}
    for section in parser.sections():
        if section == "__global__":
            continue
        if section == "formats":
            formats.update({key: value.strip() for key, value in parser[section].items()})
            continue
        settings = files.setdefault(section, {})
        for key, value in parser[section].items():
            lowered = key.lower()
            if lowered == "basedonstyles":
                settings["styles"] = words(value)
            elif lowered == "blockignores":
                settings["block_ignores"] = words(value)
            elif lowered == "tokenignores":
                settings["token_ignores"] = words(value)
            elif lowered == "vocab":
                settings["vocab"] = words(value)
            elif "." in key and (word := setting(value)) is not None:
                settings[key] = word
            else:
                notes.append(f"[{section}] {key} = {value}: no hakkiri key or setting")
    if formats:
        config["formats"] = formats
    config["files"] = files
    return config, notes


def hakkiri_alerts(binary: Path, repo: Path, name: str, styles: Path, out: Path) -> list[dict[str, str]]:
    """The alerts hakkiri gives for the tracked files of `repo`, under the converted config."""
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    ini = repo / ".vale.ini"
    if not ini.is_file():
        raise SystemExit(f"{name}: no .vale.ini to convert")
    config, notes = convert(ini.read_text(), styles)
    (folder / "conversion.txt").write_text("\n".join(notes) + ("\n" if notes else ""))
    (folder / "hakkiri.yaml").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    # Not in `.ctl`, so the project root is the checkout, and not the repository's own hakkiri config.
    temporary = repo / ".alert-diff.hakkiri.yaml"
    env = {key: value for key, value in os.environ.items() if not key.startswith("HAKKIRI_")}
    env.update(HAKKIRI_GITIGNORE="false", HAKKIRI_ON_UNMATCHED="ignore", NO_COLOR="1")
    found: list[dict[str, str]] = []
    failures = []
    try:
        temporary.write_text(json.dumps(config, ensure_ascii=False))
        for files in chunks(tracked_files(repo)):
            command = [str(binary), "check", "--config", str(temporary), "--format", "json", "--"]
            done = run(command + [f"./{file}" if file.startswith("-") else file for file in files], repo, env)
            try:
                result = json.loads(done.stdout)
            except json.JSONDecodeError as error:
                raise SystemExit(f"{name}: hakkiri printed no JSON ({error}): {done.stdout[:200]}{done.stderr[:400]}")
            for each in result.get("alerts", []):
                found.append(
                    alert(
                        name, each["path"], each["line"], each["column"], each["level"], each["rule"], each["message"], each["match"]
                    )
                )
            failures.extend(json.dumps(each) for each in result.get("failures", []))
    finally:
        temporary.unlink(missing_ok=True)
    (folder / "hakkiri.failures.txt").write_text("".join(f"{line}\n" for line in failures))
    return found


def escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def unescape(value: str) -> str:
    out, index = [], 0
    while index < len(value):
        if value[index] == "\\" and index + 1 < len(value):
            out.append({"t": "\t", "n": "\n", "r": "\r", "\\": "\\"}.get(value[index + 1], value[index + 1]))
            index += 2
        else:
            out.append(value[index])
            index += 1
    return "".join(out)


def write_table(path: Path, alerts: list[dict[str, str]]) -> None:
    rows = sorted(alerts, key=lambda each: (each["repo"], each["path"], int(each["line"]), int(each["column"]), each["rule"]))
    lines = ["\t".join(COLUMNS)] + ["\t".join(escape(each[column]) for column in COLUMNS) for each in rows]
    path.write_text("\n".join(lines) + "\n")


def read_table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text().split("\n")
    if lines[0].split("\t") != COLUMNS:
        raise SystemExit(f"{path}: not an alert table")
    return [dict(zip(COLUMNS, map(unescape, line.split("\t")), strict=True)) for line in lines[1:] if line]


def position(each: dict[str, str]) -> tuple[int, int]:
    return int(each["line"]), int(each["column"])


def diff(vale: list[dict[str, str]], hakkiri: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, int]]:
    """The differing alerts of two tables, one row each, and the count of alerts both gave alike."""
    groups: dict[tuple[str, str, str], tuple[list, list]] = defaultdict(lambda: ([], []))
    for each in vale:
        groups[(each["repo"], each["path"], each["rule"])][0].append(each)
    for each in hakkiri:
        groups[(each["repo"], each["path"], each["rule"])][1].append(each)
    rows: list[dict[str, str]] = []
    same: dict[str, int] = defaultdict(int)

    def row(kind: str, left: dict | None, right: dict | None) -> None:
        source = left or right
        assert source is not None
        rows.append(
            {
                "kind": kind,
                "rule": source["rule"],
                "repo": source["repo"],
                "path": source["path"],
                "vale": "{}:{}".format(*position(left)) if left else "",
                "hakkiri": "{}:{}".format(*position(right)) if right else "",
                "vale_message": left["message"] if left else "",
                "hakkiri_message": right["message"] if right else "",
                "match": (left or right)["match"],  # type: ignore[index]
            }
        )

    for (_, _, rule), (left, right) in sorted(groups.items()):
        left, right = sorted(left, key=position), sorted(right, key=position)
        by_place = defaultdict(list)
        for each in right:
            by_place[position(each)].append(each)
        rest_left = []
        for each in left:
            partner = by_place[position(each)].pop(0) if by_place[position(each)] else None
            if partner is None:
                rest_left.append(each)
            elif (each["message"], each["level"]) == (partner["message"], partner["level"]):
                same[rule] += 1
            else:
                row("changed", each, partner)
        rest_right = [each for matches in by_place.values() for each in matches]
        by_match = defaultdict(list)
        for each in rest_right:
            by_match[each["match"]].append(each)
        for each in rest_left:
            partner = by_match[each["match"]].pop(0) if by_match[each["match"]] else None
            if partner is None:
                row("only-vale", each, None)
            else:
                row("moved", each, partner)
        for matches in by_match.values():
            for each in matches:
                row("only-hakkiri", None, each)
    return rows, same


DIFF_COLUMNS = ["kind", "rule", "repo", "path", "vale", "hakkiri", "vale_message", "hakkiri_message", "match"]


def write_diff(out: Path, vale: list[dict[str, str]], hakkiri: list[dict[str, str]]) -> None:
    rows, same = diff(vale, hakkiri)
    lines = ["\t".join(DIFF_COLUMNS)] + ["\t".join(escape(each[column]) for column in DIFF_COLUMNS) for each in rows]
    (out / "diff.tsv").write_text("\n".join(lines) + "\n")
    by_rule: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: {kind: [] for kind in KINDS})
    for each in rows:
        by_rule[each["rule"]][each["kind"]].append(each)
    rules = sorted(set(by_rule) | set(same), key=lambda rule: (-sum(map(len, by_rule[rule].values())), rule))
    total = {kind: sum(len(by_rule[rule][kind]) for rule in by_rule) for kind in KINDS}
    md = [
        "# Alert diff",
        "",
        f"Vale gave {len(vale)} alerts and hakkiri gave {len(hakkiri)}.",
        f"{sum(same.values())} are the same alert on both sides.",
        "The others are " + ", ".join(f"{total[kind]} {kind}" for kind in KINDS) + ".",
        "",
        "| Rule | Same | " + " | ".join(KINDS) + " |",
        "|:--|--:|" + "--:|" * len(KINDS),
    ]
    for rule in rules:
        md.append(f"| {rule} | {same.get(rule, 0)} | " + " | ".join(str(len(by_rule[rule][kind])) for kind in KINDS) + " |")
    for rule in rules:
        if not any(by_rule[rule].values()):
            continue
        md += ["", f"## {rule}"]
        for kind in KINDS:
            found = by_rule[rule][kind]
            if not found:
                continue
            md += ["", f"{kind}, {len(found)}:", ""]
            for each in found[:EXAMPLES]:
                places = f"Vale {each['vale'] or '-'}, hakkiri {each['hakkiri'] or '-'}"
                md.append(f"- {each['repo']} {each['path']}, {places}: {escape(each['match'])[:80]}")
            if len(found) > EXAMPLES:
                md.append(f"- {len(found) - EXAMPLES} more in diff.tsv")
    (out / "diff.md").write_text("\n".join(md) + "\n")


def version(binary: Path) -> str:
    done = run([str(binary), "--version"], Path.cwd())
    return (done.stdout or done.stderr).strip()


def parse(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="mise run alerts:diff --", description=__doc__.split("\n")[0])
    parser.add_argument("--repos", nargs="*", default=None)
    parser.add_argument("--vale", default=os.environ.get("ALERTS_DIFF_VALE"))
    parser.add_argument("--hakkiri", default=os.environ.get("ALERTS_DIFF_HAKKIRI"))
    parser.add_argument("--package", default=os.environ.get("ALERTS_DIFF_PACKAGE"))
    parser.add_argument("--out", default=os.environ.get("ALERTS_DIFF_OUT"))
    args = parser.parse_args(argv)
    if args.repos is None:
        args.repos = [path for path in os.environ.get("ALERTS_DIFF_REPOS", "").split(os.pathsep) if path]
    if not args.out:
        parser.error("--out or ALERTS_DIFF_OUT names where the tables go")
    if not args.vale and not args.hakkiri:
        parser.error("give --vale, --hakkiri or both")
    if args.hakkiri and not args.package:
        parser.error("hakkiri needs --package or ALERTS_DIFF_PACKAGE")
    if (args.vale or args.hakkiri) and not args.repos:
        parser.error("--repos or ALERTS_DIFF_REPOS names the checkouts")
    return args


def main(argv: list[str]) -> int:
    args = parse(argv)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    repos = [Path(path).resolve() for path in args.repos]
    names = [repo.name for repo in repos]
    if len(set(names)) != len(names):
        raise SystemExit("two checkouts share a folder name, and the tables name a repository by it")
    meta = out / "meta.txt"
    dropped = tuple(prefix for prefix, ran in (("vale ", args.vale), ("hakkiri ", args.hakkiri), ("package ", args.hakkiri)) if ran)
    notes = [line for line in (meta.read_text().splitlines() if meta.exists() else []) if not line.startswith(dropped)]
    if args.vale:
        binary = Path(args.vale).resolve()
        alerts = [each for repo in repos for each in vale_alerts(binary, repo, repo.name, out)]
        write_table(out / "alerts-vale.tsv", alerts)
        notes.append(f"vale {version(binary)}")
    if args.hakkiri:
        binary = Path(args.hakkiri).resolve()
        package = Path(args.package).resolve()
        styles = package_folder(package, out)
        alerts = [each for repo in repos for each in hakkiri_alerts(binary, repo, repo.name, styles, out)]
        write_table(out / "alerts-hakkiri.tsv", alerts)
        notes.append(f"hakkiri {version(binary)}")
        digest = hashlib.sha256(package.read_bytes()).hexdigest() if package.is_file() else "folder"
        notes.append(f"package {digest}")
    meta.write_text("\n".join(notes) + "\n")
    tables = [out / "alerts-vale.tsv", out / "alerts-hakkiri.tsv"]
    if all(table.exists() for table in tables):
        write_diff(out, read_table(tables[0]), read_table(tables[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
