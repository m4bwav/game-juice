# Handoff

## Current state

- Published 2026-10-27 as github.com/m4bwav/game-juice, version 1.0.0: one scrubbed commit, tag v1.0.0 for the release workflow (zip, `.plugin`, mail zip, install prompt from `scripts/pack.py`).
- Evals (T-20261026-3 in each skill's TESTS.md): juice-scan 9/9 plus spot checks; juice-apply 6/6; juice-principles 4/6, with action-1 and outcome-1 passing only when the game repo carries the AGENTS.md snippet (`skills/juice-apply/references/AGENTS-snippet.md`). README "Known limitations" states the numbers.
- API claims verified against primary docs (juice-scan R-20261026-4 to -8, juice-principles R-20261026-6); Godot `Tween.set_ignore_time_scale` corrected to 4.4+; Roblox haptics now lead with `HapticEffect`.
- Next due: juice-scan and juice-apply 2026-11-25, juice-principles 2027-02-23.

## In progress

- 2026-10-28: the first field test on the Unity deckbuilder produced 1.1.0. The scanner gained card_play, card_draw and turn moments, and it now skips tests, Unity Editor folders and predicate helpers (juice-scan L-002, L-003, T-20261028-1). The report lives at that game's root as juice-report.md. The next field step is juice-apply on S-05 (the settings toggle), then S-01.

## Decisions made this session

- Publish in the unity-agent shape, release from `scripts/pack.py`, private check in the vault with a local pre-push hook: [decision](decisions/2026-10-27-publish-game-juice-as-a-public-repository.md).

## Dead ends hit

- More description wording does not fix a skipped skill on short requests and memory-answerable questions; a repo-level AGENTS.md rule does: [solution](solutions/2026-10-27-skill-undertriggers-on-small-repos-and-direct-edit-requests.md).
- Trigger evals in an empty scratch folder fail for a second reason (no project); use a fixture copy.

## Next single action

Tune juice-principles action-1 and outcome-1 so they pass without the AGENTS snippet (try a juice-scan or juice-apply hand-off line that loads principles.md, then re-run 3x each in a godot-platformer scratch copy), and check the web.md sketches against Phaser 4.