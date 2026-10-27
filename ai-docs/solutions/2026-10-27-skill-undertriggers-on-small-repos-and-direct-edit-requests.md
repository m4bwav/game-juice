---
title: Skill undertriggers on small repos and direct edit requests
kind: solution
status: active
date: 2026-10-27
verified: 2026-10-27
stale_after: 2027-01-25
tags: [skills, triggering, evals, agents-md]
aliases: [undertrigger, skill not invoked, model edits directly]
entities: [juice-apply, juice-principles, juice-scan, AGENTS.md]
summary: "read when a skill is skipped and the model does the work itself: short edit requests, tiny repos, knowledge questions"
agent: copilot
---

# Skill undertriggers on small repos and direct edit requests

## Problem

Agent skills that should own a request were skipped and the model did the work itself:

- juice-scan (before C-20261026-2): "why does combat feel flat... take a look at the code" in a tiny sample game was answered by reading the code directly.
- juice-apply trigger-2: "add coyote time and a jump buffer to my player" went 0/4 twice, the model editing `player.gd` directly, skipping the toggles, constants and revert note.
- juice-principles action-1 and outcome-1: "starting numbers for squash and stretch on a jump landing" and "is it OK to flash the whole screen white on every hit" were answered from memory with no tool call: 0/3 each.

The pattern: a small repo, a short direct request, or a question that sounds like general knowledge with no juice term in it. The model judges the task small enough to do itself.

## Dead ends

- Listing more trigger phrases alone did not move juice-apply trigger-2 (0/4 before and after).
- "Use it first, before ... even for a one-line change" in the description fixed juice-scan's case but not juice-apply's on the same day, and moved juice-principles only from 0/3 to 1/3 on action-1 and 0/3 to 0/3 on outcome-1.
- Judging a trigger from an empty scratch folder: the principles cases fail there for a second reason (no project context); run trigger evals in a copy of a real fixture.

## Fix

1. Keep the description pattern that helps: lead with the user's own complaint words, say "use it first, before reading code / answering from memory", and name the exact asks that were missed. Stay under 1,024 characters (check_skills enforces it).
2. Add a standing rule in the target repo's instructions: `skills/juice-apply/references/AGENTS-snippet.md`, pasted into the game repo's `AGENTS.md` with `CLAUDE.md` importing it. It routes feel edits to juice-apply, audits to juice-scan, and feel questions to juice-principles.
3. Measure three runs per case with and without the snippet, and keep a case in `tests.failing` until it passes without the snippet. Document the numbers in the README's Known limitations.

## Verified by

`claude -p` 2.1.281 with `--plugin-dir <repo> --output-format stream-json --permission-mode bypassPermissions --max-turns 6`, one fresh scratch copy of `tests/fixtures/godot-platformer` per run, evidence from the Skill call in the trace (2026-10-27): with the snippet, juice-apply trigger-2 3/3, juice-principles action-1 3/3 (principles.md read, P-03 cited) and outcome-1 3/3 (P-15, P-18, 3-per-second limit); without it, trigger-2 3/3, action-1 1/3, outcome-1 0/3. Logged as T-20261026-3 in each skill's TESTS.md.

Related: see also [the publication decision](../decisions/2026-10-27-publish-game-juice-as-a-public-repository.md)
