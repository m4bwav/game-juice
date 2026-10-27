# Learnings: juice-scan

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-001 · 2026-10-26 · On a small repo the model reads the code itself unless the description says "first, even for tiny projects"
- Trigger: trigger-3 ("why does combat feel flat... take a look at the code") ran 0/4 against a three-file Godot fixture. The first tool was Bash `find`/`cat`.
- Hypothesis: when the whole codebase fits in two reads, the model rates the skill as overhead. Prompts that name the code ("take a look at the code") pull it toward reading directly.
- Rule: keep "use it first, before reading any game code yourself, even for a tiny project" and the reason (principles, parameters, engine traps) in the description. Test triggers on the small fixtures, the hardest case.
- Evidence: T-20261026-1 (0/4), C-20261026-2, T-20261026-2 (4/4)
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-26