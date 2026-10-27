# game-juice

![A glossy red push button squashed flat by a press, with sparks bursting from its rim](.github/images/banner.jpg)

[![tests](https://github.com/m4bwav/game-juice/actions/workflows/tests.yml/badge.svg)](https://github.com/m4bwav/game-juice/actions/workflows/tests.yml)
[![release](https://img.shields.io/github/v/release/m4bwav/game-juice)](https://github.com/m4bwav/game-juice/releases/latest)
[![licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

Skills that study a game's codebase and suggest **juice**: the feedback and polish that make playing feel good without changing the rules. That covers screen shake, hit-stop, particles, squash and stretch, easing, camera kick, layered and pitch-varied sound, UI that answers input, transitions, haptics, coyote time, and input buffering. It also flags over-juicing: effects that hurt readability, accessibility, or frame time.

Works with Claude Code, Copilot, Codex, Cursor, and anything that reads Agent Skills. Each skill is an evergreen unit: it re-researches its subject on a schedule, records lessons, and carries the evals that prove it triggers and acts.

## Install

**Claude Code**

```
claude plugin marketplace add m4bwav/game-juice
claude plugin install game-juice@game-juice
```

**Copilot, Codex, Cursor, and other Agent Skills readers**: clone the repository and link each skill folder into your agent's skills folder, `~/.agents/skills` (user-wide) or `.claude/skills` in a game repo:

```
git clone https://github.com/m4bwav/game-juice
# macOS / Linux
for s in game-juice/skills/*; do ln -s "$PWD/$s" ~/.agents/skills/; done
# Windows (PowerShell)
Get-ChildItem game-juice\skills -Directory | % { New-Item -ItemType Junction -Path "$HOME\.agents\skills\$($_.Name)" -Target $_.FullName }
```

`git pull` updates them. **Release zip**: each [release](https://github.com/m4bwav/game-juice/releases/latest) carries `game-juice-<version>.zip`, a flat `game-juice.plugin` for Cowork, a mail-safe zip, and an install prompt you can hand to an agent.

Optional: in a game repo, paste [the AGENTS.md snippet](skills/juice-apply/references/AGENTS-snippet.md) so that short requests such as "add coyote time" always go through juice-apply's toggles and revert notes.

## Quick start

In a game repository, ask: **"Make my game feel better."** juice-scan runs the scanner, reads each lead, and writes `juice-report.md`. An excerpt from the report on the Godot sample game in `tests/fixtures/godot-platformer`:

```markdown
| Moment | Where | Has | Missing |
|---|---|---|---|
| input/jump | `_unhandled_input`, `jump` (scripts/player.gd:19, 24) | instant velocity | coyote time, jump buffer, variable height, stretch, sound, dust |
| hit | `take_damage` (scripts/player.gd:29) | health decrement | hit-stop, flash, shake, knockback, i-frames, sound |
| death | `die` (scripts/player.gd:35) | instant scene reload | any death beat |

### S-01 · Coyote time + jump buffer · impact 3 / effort 1
- Moment: jump · `jump` / `_unhandled_input` in scripts/player.gd:19-26
- Technique: 0.1 s grace after leaving a ledge; 0.12 s buffer for early presses. Control comes before polish (P-16, P-05).
```

Then: **"Apply S-01."** juice-apply adds the change behind a `JuiceSettings` toggle, names its constants, and logs a revert note in `juice-changes.md`. Ask juice-principles why it works: **"What is hit-stop and how long should it be?"**

## Skills

| Skill | Use it for | Produces |
|---|---|---|
| [juice-scan](skills/juice-scan/SKILL.md) | "make my game feel better", "add juice", "why does combat feel flat" | `juice-report.md`: moment map, quick wins, medium changes, signature moments, over-juice and accessibility findings. Each suggestion names the file and function, technique, principle, parameters, and an engine code sketch |
| [juice-apply](skills/juice-apply/SKILL.md) | "apply S-03", "add coyote time", "do the quick wins" | the change in your code behind a `JuiceSettings` toggle with named constants and reduce-motion, shake, and flash options, plus `juice-changes.md` with revert notes |
| [juice-principles](skills/juice-principles/SKILL.md) | "what is hit-stop?", "how much shake is too much?" | answers grounded in 22 medium-independent principles and 12 lenses, with book citations and starting parameters |

Engines in v1: **Unity (C#), Godot 4 (GDScript), Roblox (Luau), web (Phaser, PixiJS, GSAP), Pygame**, with lighter notes for LÖVE, Unreal, Defold, and GameMaker.

## How the scan works

`skills/juice-scan/scripts/juice_scan.py` (standard-library Python, read-only) detects the engine, splits the code into functions, classifies each function as a feel moment (input, movement, jump, attack, hit, death, pickup, score, UI, transition, camera), and lists the feedback it already has across seven channels: visual, motion, camera, audio, UI, haptic, and timing. It reports gaps, project-wide findings (no coyote time, no hit-stop, no shake toggle, no pitch variation), and risks (shake every frame, effects spawned per frame, frozen time scale, full-screen flashes). The agent then reads the code behind each lead, runs the lenses, and writes the report.

```
python skills/juice-scan/scripts/juice_scan.py path/to/game --md
```

## Knowledge base

Principles and lenses live in [skills/juice-principles/references/](skills/juice-principles/references/). They are summaries written in the plugin's own words, citing:

- Steve Swink, *Game Feel* (2009): the control, space, and polish model, perception thresholds, response envelopes, and the polish taxonomy.
- Jesse Schell, *The Art of Game Design* 2e (2015): the lens format and the feedback, juiciness, toy, channels, and accessibility lenses.
- Celia Hodent, *The Gamer's Brain* (2017): attention, perception, and UX. Why feedback works and when it becomes noise.
- Scott Rogers, *Level Up!* 2e (2014) and 3e (2023): practical camera, controls, HUD, audio, and combat-feedback checks.

Plus talks and articles: Jonasson & Purho's "Juice it or lose it" (2012), Nijman's "The Art of Screenshake" (2013), Eiserloh's trauma shake (2016), Thorson's "Celeste & Forgiveness" (2018), Sakurai on hit-stop, and the WCAG, Game Accessibility Guidelines, and Xbox accessibility guidance. See [sources.md](skills/juice-principles/references/sources.md) and each skill's RESEARCH.md. No book text is included.

## Beyond games

The principles (anticipation, impact, follow-through, layering, contrast, restraint) are written for any medium. [media/](skills/juice-principles/references/media/README.md) holds adapters: games in full, with stubs for web UI, video edits, and presentations that a later version will fill in.

## Development

```
python tests/check_scan.py     # scanner against five sample games (tests/fixtures)
python tests/check_skills.py   # structure, companions, manifests, links, public-safety guards
```

Both run in CI on Ubuntu and Windows with Python 3.9 and 3.13.

**How the evals were run.** Each skill's cases live in `evals/evals.json` and its runs in `TESTS.md`. They were run with `claude -p` (Claude Code 2.1.281) and `--plugin-dir` against a fresh scratch copy of a sample game per run, three runs per case, and a case passes only on evidence: the Skill call in the stream-json trace, the files and diff left in the scratch copy, and the reply checked against the case's expectations.

## Known limitations

- The scanner is heuristic. It matches function names and calls, so it finds leads, not proof; the skill reads each lead before suggesting anything, and a report can still miss a moment with an unusual name.
- Feedback wired outside code is not seen: scenes and prefabs, the Unity Inspector, animation events, audio mixers, Blueprints. Reports list these under "Not checked".
- Unreal, LÖVE, Defold, and GameMaker get short pointers, not full references. The web sketches use the Phaser 3 API and were not re-checked against Phaser 4.
- Routing depends on the model. Short requests such as "add coyote time and a jump buffer" went to juice-apply in 3 of 3 runs at release, but 0 of 4 earlier the same day. Knowledge questions that name no juice term ("starting numbers for squash and stretch", "is a full-screen flash on every hit OK?") are often answered from the model's memory without juice-principles: 1 of 3 and 0 of 3 at release. With the [AGENTS.md snippet](skills/juice-apply/references/AGENTS-snippet.md) in the game repo, all of these went 3 of 3. The two principles cases stay listed as failing in `skills/juice-principles/evergreen.json` until they pass without it.
- juice-apply cannot playtest. It runs the project's own check where one exists (compile, lint), re-runs the scanner, and leaves the feel to you.

Rules for agents working here: [AGENTS.md](AGENTS.md). Security: [SECURITY.md](SECURITY.md). Licence: MIT.

## Privacy

The skills run locally, read your project files, and send nothing anywhere. The scanner is read-only; juice-apply edits files only after you agree to the plan.
