#!/usr/bin/env python3
"""Pack game-juice the way evergreen-pack packs evergreen.

Writes to dist/ (or --out):
  game-juice-<version>.zip     folder inside, for backup, 7-Zip, `claude plugin install`
  game-juice.plugin            flat, for Cowork's Save plugin
  game-juice-<version>-mail.zip  email-safe: .py stored as .py.txt (rename back after unzipping)
Each archive carries INSTALL-PROMPT.txt. Excludes .git, caches, dist/, eval scratch and generated reports.
"""
import argparse
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "evals_scratch"}
EXCLUDE_FILES = {"juice-report.md", "juice-changes.md", ".DS_Store"}
EXCLUDE_EXT = (".pyc", ".zip", ".plugin", ".7z")

PROMPT = """Install the game-juice plugin from the archive {name}.
(Or skip the archive: in Claude Code run `claude plugin marketplace add m4bwav/game-juice` then
`claude plugin install game-juice@game-juice`; elsewhere clone https://github.com/m4bwav/game-juice.)

1. Unzip it (the folder inside is game-juice/). If this is the -mail.zip, rename every *.py.txt file back to *.py.
2. Claude Code: run `claude plugin marketplace add <path to game-juice>` then `claude plugin install game-juice@game-juice`,
   or load it for one session with `claude --plugin-dir <path to game-juice>`.
   Copilot, Codex, Cursor and other Agent Skills readers: link or copy game-juice/skills/* into the tool's skill folder
   (for example ~/.agents/skills/ or .claude/skills/).
3. Check it: `python game-juice/tests/check_skills.py` and `python game-juice/tests/check_scan.py` should both pass.
4. The skills are evergreen units (pointer mode): with the evergreen plugin installed, its session-start audit
   will list them and refresh them when due.
Then try: "make my game feel better" in a game repository.
"""


def git_ignored():
    """Untracked files git ignores (local notes, scratch); empty when git is unavailable."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files", "--others", "--ignored", "--exclude-standard"],
                             capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    return {line.rstrip("/") for line in out.splitlines() if line}


def files():
    ignored = git_ignored()
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(d for d in dns if d not in EXCLUDE_DIRS and not (dp == ROOT and d == "evals"))
        for f in sorted(fns):
            if f in EXCLUDE_FILES or f.endswith(EXCLUDE_EXT):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            if rel in ignored:
                continue
            yield full, rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    a = ap.parse_args()
    ver = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))["version"]
    os.makedirs(a.out, exist_ok=True)
    made = []
    for kind in ("zip", "plugin", "mail"):
        name = {"zip": f"game-juice-{ver}.zip", "plugin": "game-juice.plugin", "mail": f"game-juice-{ver}-mail.zip"}[kind]
        path = os.path.join(a.out, name)
        n = 0
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for full, rel in files():
                arc = rel if kind == "plugin" else f"game-juice/{rel}"
                if kind == "mail" and arc.endswith(".py"):
                    arc += ".txt"
                z.write(full, arc)
                n += 1
            z.writestr("INSTALL-PROMPT.txt", PROMPT.format(name=name))
        made.append((path, n, os.path.getsize(path)))
    with open(os.path.join(a.out, f"game-juice-{ver}-INSTALL-PROMPT.txt"), "w", encoding="utf-8") as fh:
        fh.write(PROMPT.format(name=f"game-juice-{ver}.zip"))
    for p, n, size in made:
        print(f"{p}  {n} files  {size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
