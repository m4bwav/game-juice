# Security policy

## Reporting a problem

Open an issue or a pull request and I'll take a look. A pull request with the fix is the quickest route.

You can also report privately: open the repository's **Security** tab and choose **Report a vulnerability**.

This is a one-person project with no bug bounty and no response deadline. I'll reply when I can and say what I plan to do. Good-faith testing on your own copy is welcome.

## Supported versions

Only the latest release on the default branch gets fixes.

## Scope

The skills' instructions and the scanner run on your machine with your agent's permissions. The scanner (`skills/juice-scan/scripts/juice_scan.py`) only reads the project's files and prints JSON (or writes it to the file you name with `--out`); it never runs project code or opens the network. juice-scan writes one file, `juice-report.md`. juice-apply edits your game's files only after you agree to its plan, and logs each change in `juice-changes.md`.

In scope: anything that leads the agent to run commands, write files, fetch URLs or share data beyond what a skill says it does. That includes instructions planted in a game's source files or comments that the skills read (prompt injection). Out of scope: bugs in the agent tool itself (Claude Code, Copilot, Codex, Cursor); report those to their makers.
