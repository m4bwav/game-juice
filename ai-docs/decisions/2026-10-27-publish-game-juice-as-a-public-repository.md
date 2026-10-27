---
title: Publish game-juice as a public repository
kind: decision
status: active
date: 2026-10-27
verified: 2026-10-27
stale_after: 2027-04-25
tags: [release, repo, privacy, pattern]
entities: [github, pack.py, check_skills.py]
summary: read before changing the repo layout, the workflows, pack.py or the manifests, or before a first push from a fresh clone
agent: copilot
---

# Publish game-juice as a public repository

## Context

game-juice was built in a local folder with one local commit and tag (v1.0.0), never pushed. The three skills were linked into the agent skill folders and registered with the evergreen plugin, so the folder could not move. Before going public, the open eval cases, the API claims marked unverified, and a privacy and copyright pass were still outstanding.

## Decision

game-juice is published as the public repository github.com/m4bwav/game-juice in the shape of the published sibling unity-agent: MIT with the author credit only; `AGENTS.md` as the source of truth with `CLAUDE.md` importing it through Claude Code's import line and `.github/copilot-instructions.md` pointing at it; `.claude-plugin/plugin.json` (icon, repository, homepage, documentation, support and privacy URLs) plus `marketplace.json`, with the root `plugin.json` kept in step; a tests workflow (Ubuntu and Windows, Python 3.9 and 3.13, `tests/check_skills.py` and `tests/check_scan.py`); a release workflow on `v*` tags that checks the tag against `plugin.json`, runs both checks and `scripts/pack.py`, and attaches all four `dist/` files; `SECURITY.md` with private vulnerability reporting on; an `ai-docs/` doc set in committed mode; and one scrubbed first commit at version 1.0.0.

## Reasons

- Clone plus links is the whole install, `git pull` the update, and each evergreen refresh lands as a commit.
- The release carries `scripts/pack.py`'s output (zip, flat `.plugin`, mail-safe zip, install prompt) rather than a zip built in the workflow, so the published archives match what a local pack produces.
- `tests/check_skills.py` and `scripts/pack.py` skip files git ignores, so a local, ignored note in the folder can neither fail CI-equivalent checks locally nor leak into `dist/`. Local-only ignores go in `.git/info/exclude`, so the public `.gitignore` names nothing private.
- The private denylist stays in the vault sidecar and runs from an uncommitted `.git/hooks/pre-push`, as for unity-agent and roblox-agent.

## Alternatives rejected

- Shipping with the trigger gaps hidden: the README "Known limitations" states the routing numbers, and `tests.failing` stays set for juice-principles' action-1 and outcome-1.
- Another round of description tweaks for juice-apply trigger-2: a repo-level AGENTS.md snippet was tried instead (it routes 3/3), and the case also passed 3/3 without it on the release day.
- Keeping the pre-publish history: it was one unpushed commit; the published history starts with the scrubbed tree.

## Consequences

The local folder is the clone. A fresh clone needs the pre-push hook re-created from the vault sidecar before its first push. Phaser 4 is now the current major; the web sketches still use the Phaser 3 API (open question in juice-scan's RESEARCH).

Related: builds on the unity-agent publication decision (sibling repository, ai-docs/decisions/2026-09-22-publish-unity-agent-as-a-public-repository-in-the-sibling-pl.md); see also [the undertrigger solution](../solutions/2026-10-27-skill-undertriggers-on-small-repos-and-direct-edit-requests.md)
