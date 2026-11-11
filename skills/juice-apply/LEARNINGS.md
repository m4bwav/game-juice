# Learnings: juice-apply

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-001 · 2026-10-26 · A direct request to add one named technique is treated as a routine edit and skips the skill
- Trigger: trigger-2 ("add coyote time and a jump buffer to my player") ran 0/4 before and 0/4 after the description said "even for a one-line change". The action case with a longer request ("add hit-stop and screen shake to take_damage, with a way to turn shake off") did invoke the skill. A later run the same day (T-20261026-3), with no SKILL.md change, went 3/3 without help and 3/3 with the AGENTS snippet.
- Hypothesis: a short, specific edit request sits on the line between the model's built-in editing behaviour and the skill, so routing varies from run to run. Mentioning settings, toggles or accessibility pulls toward the skill; a standing rule in the repo's own instructions removes the variance.
- Rule: keep the "use it first, even for a one-line change" description, and offer the game repo the AGENTS.md snippet (`references/AGENTS-snippet.md`, linked from the README) so feel edits are routed by a standing rule, not by the description alone. Re-run trigger-2 at every refresh; a regression without the snippet is expected noise only if the snippet run still passes.
- Evidence: T-20261026-2, T-20261026-3, C-20261026-2, C-20261026-3
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-26

### L-002 · 2026-11-11 · Juice for a mod or level with no game code: build it from the level's own data objects
- Trigger: the "game" is a map or mod for someone else's engine (a MADNESS: Project Nexus SceneTools level), so there is no code to add hit-stop, shake or particles to.
- Rule: look for the engine's data-driven feedback objects (destructibles, togglables, sound names, flash on hit) and juice the set with them: shootable glass, lamps and screens that swap to a broken state with a built-in sound and a hit flash. Keep it cosmetic (bullets pass through, no damage bar, no popup, no explosion) so fights play the same, put the toggle and hit counts as named constants in the level generator, and pick only props the source material already has. Ask for one play that checks sound, flash, swap, no marker icon, and bullets still reaching enemies behind.
- Evidence: madnesswright examples/NexusProminence `Breakable` and juice-changes.md; owner play 2026-11-11 passed ("play test went well"), log clean; released to Steam Workshop the same day. madnesswright L-20261111-3 `shootable-set-pieces`.
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-11-11
