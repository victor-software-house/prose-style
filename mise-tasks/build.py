#!/usr/bin/env python3
#MISE description="ProseStyle.zip: the tracked ProseStyle folder and the styles upstream.toml pins"
#MISE tools = { python = "3.15.2" }
"""Build ProseStyle.zip, a package that needs no further download.

Vale fetches each name in a package's `Packages`, and their own `Packages` in
turn, so a project that synced the upstream packages got whatever release they
named. This build packs the pinned upstream styles beside ProseStyle's own, so
a project's `vale sync` makes one download and gets exactly what was tested.
"""

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import PurePosixPath

PACKAGE = "ProseStyle"
OUTPUT = "ProseStyle.zip"
# A fixed time for every entry, so the same inputs build the same bytes.
EPOCH = (1980, 1, 1, 0, 0, 0)


def github(url: str, accept: str) -> bytes:
    """Fetch from GitHub's API, with the token CI supplies when there is one."""
    headers = {"Accept": accept, "User-Agent": "prose-style-build"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()


def download(pin: dict) -> zipfile.ZipFile:
    """Download one pinned release asset through the API and check its sha256.

    The API serves assets when the release download path does not, as during
    the outage of 2026-11-08.
    """
    release = json.loads(
        github(f"https://api.github.com/repos/{pin['repo']}/releases/tags/{pin['tag']}", "application/vnd.github+json")
    )
    [asset] = [a for a in release["assets"] if a["name"] == pin["asset"]]
    data = github(asset["url"], "application/octet-stream")
    digest = hashlib.sha256(data).hexdigest()
    if digest != pin["sha256"]:
        sys.exit(f"{pin['repo']} {pin['tag']} {pin['asset']}: sha256 {digest}, upstream.toml pins {pin['sha256']}")
    return zipfile.ZipFile(io.BytesIO(data))


def upstream_files(pin: dict) -> dict[str, bytes]:
    """Map each packed path to its bytes, for every style one pin names."""
    archive = download(pin)
    files = {}
    for style in pin["styles"]:
        name = PurePosixPath(style).name
        prefix = f"{style}/"
        members = [m for m in archive.infolist() if m.filename.startswith(prefix) and not m.is_dir()]
        if not members:
            sys.exit(f"{pin['asset']} holds no {style}/")
        for member in members:
            files[f"{PACKAGE}/styles/{name}/{member.filename.removeprefix(prefix)}"] = archive.read(member)
        for legal in pin["legal"]:
            files[f"{PACKAGE}/styles/{name}/{PurePosixPath(legal).name}"] = archive.read(legal)
    return files


def own_files() -> dict[str, bytes]:
    """Map each tracked file under ProseStyle/ to its bytes."""
    listed = subprocess.run(["git", "ls-files", "-z", PACKAGE], check=True, capture_output=True).stdout
    paths = [p for p in listed.decode().split("\0") if p]
    return {path: open(path, "rb").read() for path in paths}


def check_rule_names(files: dict[str, bytes]) -> None:
    """Fail when the package config sets a rule the zip does not hold.

    Vale ignores a setting for a rule it cannot find, so a renamed rule
    would silently drop its level or its exception.
    """
    config = files[f"{PACKAGE}/.vale.ini"].decode()
    for style, rule in re.findall(r"^([A-Z][A-Za-z]*)\.([A-Za-z.]+)\s*=", config, re.MULTILINE):
        path = f"{PACKAGE}/styles/{style}/{rule.replace('.', '/')}.yml"
        if path not in files:
            sys.exit(f"{PACKAGE}/.vale.ini sets {style}.{rule}, and the zip holds no {path}")


def main() -> None:
    with open("upstream.toml", "rb") as config:
        pins = tomllib.load(config)["upstream"]
    files = own_files()
    for pin in pins:
        for path, data in upstream_files(pin).items():
            if path in files:
                sys.exit(f"{path} comes from two sources")
            files[path] = data
    check_rule_names(files)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as out:
        for path in sorted(files):
            entry = zipfile.ZipInfo(path, EPOCH)
            entry.external_attr = 0o644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(entry, files[path])
    print(f"{OUTPUT}: {len(files)} files")


main()
