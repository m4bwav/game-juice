# Changelog: juice-principles

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261128-1 · 2026-11-28 · Damage-scaled knockback and staged construction rows (1.7.3)
- because: harvest: kevintngo repo harvest 2026-11-28 (ids kevintngo-voidlight and 1y66rh1-play; github.com/kevintngo/arena-fighter has no licence and github.com/kevintngo/cinderwatch is MIT: parameters and ideas only, nothing copied)
- files: references/principles.md (parameter table)
- New rows: knockback that grows with accumulated damage, with its hitstun, hit-stop and parry start values; a structure built piece by piece that stays idle until the last piece lands. Numbers were read from code, not measured on screen. Triggers unchanged, so evals were not re-run.

### C-20261123-2 · 2026-11-23 · Chained-trigger pitch ramp and placement preview rows (1.7.2)
- because: harvest: local game harvest 2026-11-23 runners-up (Balatro and Backpack Hero notes; ideas and a few numbers only, nothing copied)
- files: references/principles.md (parameter table)
- New rows: rising pitch per chained trigger, reset per resolution, plus tally row pitch; highlight the cells a placement reads and preview the delta. Triggers unchanged, so evals were not re-run.

### C-20261123-1 · 2026-11-23 · P-30 signal a phase change with a whole-screen palette shift plus a title beat (1.7.1)
- because: harvest: local game harvest 2026-11-23 (Thronefall trailer, luminance measured from frames; idea only, nothing copied)
- files: references/principles.md (P-30)
- New principle: a mode switch reads best as a whole-frame palette and light shift with a title beat. Triggers unchanged, so evals were not re-run.

### C-20261121-3 · 2026-11-21 · Impact composite row; particle life depends on role (1.7.0)
- because: harvest: RimWorld local harvest 2026-11-21 (technique observed in RimWorld's shipped defs, 2026-11-21; idea and a few numbers only, nothing copied)
- files: references/principles.md (parameter table)
- New "Impact composite" row (single-job layers, role-based lifetimes, ranges on every value, drag and shrink on sparks, optional delayed second beat, shake for big events only); "Particles on impact" now gives life per role instead of one range. Triggers unchanged, so evals were not re-run.

### C-20261121-2 · 2026-11-21 · Card play anatomy, turn handoff and kill to reward rows; hit timing becomes a range (1.5.1)
- because: user request (technique-harvest local install harvest 2026-11: a commercial deckbuilder played live as a user and recorded at about 58 fps, tier A only, idea only, nothing copied, no game named)
- files: references/principles.md (parameter table)
- Three rows from measured frames (card play spot and discard arc that leaves input open, turn banner handoff, dim-and-fade reward after a kill); turn-based hit timing now 70-220 ms across two games; turn-based kill gains a dissolve style. Triggers unchanged, so evals were not re-run.

### C-20261121-1 · 2026-11-21 · Staggered resolution, reward reveal and turn-based kill rows (1.5.0)
- because: user request (technique-harvest local install harvest 2026-11: a commercial turn-based dice game, tier A only (its store clips and release trailer watched as a viewer, measured frame by frame), idea only, nothing copied, no game named)
- files: references/principles.md (parameter table)
- Three rows from measured frames: items resolved about 100 ms apart with a popping total, a rarity-tinted silhouette reveal of about 350 ms, and a 150-170 ms white silhouette kill with no camera shake (no shake was found in any of the measured clips). Triggers unchanged, so evals were not re-run.

### C-20261120-2 · 2026-11-20 · P-05 buffers attack and dash with per-press expiry (1.4.1)
- because: user request (book round: Campos, Game Development Patterns with Godot 4, ch. 13)
- files: references/principles.md (P-05, parameter table coyote row)
- P-05 now buffers every core action, gives each press its own expiry, ignores key-repeat echoes and asks the designer to decide whether a buffered jump must still be held at landing. Triggers unchanged, so evals were not re-run.

### C-20261120-1 · 2026-11-20 · Web-game harvest rows: transitions, streaks, haptics, timing bands, crashes, audio, turn-based feedback (1.4.0)
- because: user request (technique-harvest web-game harvest 2026-11, measured by play and written fresh, nothing copied: maumoya/boredom-blaster-play, sw897/one-tap-skyline, waleee7/peach-dash, dcjaychou/design-ridge-run, pkieltyka/zubspace, tianlinx/spire-echoes, luizbizzio/scandeck, larryzpl123/skybreak-protocol (MIT), vitaminclaude/voidstruck (PolyForm Strict, play and measure only))
- files: references/principles.md (parameter table)
- 23 parameter rows in our words with no game named: flash-cut transition, streak pitch ladder, haptics per outcome, timing bands with signed error, never-repeat-last shuffle, crash hit-stop with slowed particles, near miss and graze, stumble before death, charged action ring, plume easing, 10 Hz HUD numbers, refused actions with a reason, muzzle flash at rapid fire, invisible aim assist, chase and side-view camera numbers, additive shake with a cap and exponential decay, distance falloff and volume tiers, killing blow keeps its feedback, feedback lost to re-render, feedback keyed to damage applied, turn-based hit timing. Live timing is measured with threewright `tw feel`, not a second probe here. Triggers unchanged, so evals were not re-run.

### C-20261118-2 · 2026-11-18 · Damage through controls, shield ripples, bullet holes, audio param dedupe rows (1.3.9)
- because: user request (technique-harvest three-repos batch G: GPU-Bandits by sloppysteaks69, no licence, and voidstruck; ideas only, written fresh)
- files: references/principles.md (parameter table)
- Four parameter rows: low-health handling (steering slow-down, sine aim drift) as an alternative to shake, multi-hit shield ripples and persistent bullet holes pointing to threewright recipes, and the 1% change gate for per-frame audio params. Triggers unchanged, so evals were not re-run.

### C-20261119-2 · 2026-11-19 · Frozen feel table and launch timer resets (1.3.11)
- because: user request (technique-harvest: a commercial web platformer, idea only, nothing copied)
- files: references/principles.md (P-29, parameter table)
- P-29 teaches one frozen feel table and resetting forgiveness timers together on every launch; parameter rows for held-jump lift, launch squash and step up/down. Triggers unchanged, so evals were not re-run.

### C-20261119-1 · 2026-11-19 · Hit-stop: shake through the freeze, snap into contact (1.3.10)
- because: R-20261119-1 (technique-harvest post pa20-p5-hit-timing, user request)
- files: references/principles.md (parameter table, Hit-stop row), RESEARCH.md
- The Hit-stop notes gain shake running through the freeze (2-4 px) and an uneased snap to the contact pose. Triggers unchanged, so evals were not re-run.

### C-20261118-1 · 2026-11-18 · Frame-rate independent smooth follow row (1.3.7)
- because: user request (technique-harvest book round 21: Sung and others, Build Your Own 2D Game Engine, 2nd ed., ch. 3 and 7, whose lerp relies on a fixed update rate; measured: a 0.1 per-frame fraction reaches 79%, 96% and 100% of the way after 0.5 s at 30, 60 and 144 fps, the exp form 96% at all three)
- files: references/principles.md (parameter table)
- Adds one parameter row: smoothing by 1 - exp(-rate × dt) or in the fixed update. Triggers unchanged, so evals were not re-run.

### C-20261117-1 · 2026-11-17 · Elastic return, procedural waddle row, Godot modulate flash note
- because: R-20261117-1 (technique-harvest post yt-LhJVhk-BiIo, user request)
- files: references/principles.md (parameter table), RESEARCH.md
- Squash/stretch notes gain the 150-250 ms elastic return, a new procedural waddle or bob row, and the damage flash notes the Godot modulate caveat. Triggers unchanged, so evals were not re-run.

### C-20261110-1 · 2026-11-10 · harvest.json: technique-harvest targets for this unit
- because: user request 2026-11-10: plugins store their own technique-harvest targets (evergreen 1.1.0 harvest.json)
- files: harvest.json (new)
- Data file only; no skill text or version changed.

### C-20261109-1 · 2026-11-09 · Locomotion sync, stepped knockback, hit-stop on fast hits, wind-up start values
- because: user request (technique-harvest post 1xajfgh, idea credited, no code copied)
- files: references/principles.md (parameter table), references/lenses.md (J3), references/media/games.md (game.attack)
- Added locomotion sync, stepped knockback and wind-up/swing start rows (the last marked tune-by-eye, no published source), the hit-stop note for fast repeated hits, two J3 questions, and trails as optional. Triggers unchanged, so evals were not re-run.

### C-20261101-1 · 2026-11-01 · Game Engine Architecture 2e: P-28 bark and voice-line pools
- because: user request (everscout game-design beat, Game Engine Architecture 2e learnings approved)
- files: references/principles.md (P-28), references/sources.md (Gregory row)
- P-28 covers line pools without repeats and priority-based interruption. Triggers unchanged, so evals were not re-run.

### C-20261031-1 · 2026-10-31 · The Gamer's Brain 2e: low-health effects, camera takeover, loss-beat reappraisal
- because: user request (everscout game-design beat, The Gamer's Brain 2e learnings approved)
- files: references/principles.md (P-18, P-19)
- P-18 now covers low-health overlays hiding the threat and signalled camera takeovers (none in VR); P-19 adds the loss beat that shows what went well. Triggers unchanged, so evals were not re-run.

### C-20261030-1 · 2026-10-30 · Swink's case studies: P-23 to P-27, lenses J13-J14, feel-cases.md
- because: user request (ludowright's feel-handoff list of what Swink adds); Swink ch. 1, 5, 11, 12-16 read
- files: references/principles.md (P-23 to P-27), references/lenses.md (J13, J14), references/feel-cases.md (new), references/sources.md (Swink row), SKILL.md (description count, Step 1 row)
- Added the feel-type classifier, context fit, rules as feel, direct versus simulated mappings and bottom-up tuning as principles, two lenses, and a method-only walk of the six areas drawn from the five case studies (no per-game numbers). Triggers unchanged apart from the count, so evals were not re-run.

### C-20261026-4 · 2026-10-26 · Published as part of the public game-juice repository
- because: user request
- files: TESTS.md (T-20261026-2)
- Removed a duplicated `led to:` line. No change to what the skill does.

### C-20261026-3 · 2026-10-26 · Description asks to be used before answering from memory, and names starting numbers and flash safety
- because: T-20261026-3, L-001
- files: SKILL.md (frontmatter description)
- Added "use it first, before answering from memory", the missed asks (starting numbers for squash and stretch, hit-stop and shake; whether a flash or motion effect is safe), and shortened the rest to stay under 1,024 characters. action-1 went 0/3 to 1/3, outcome-1 stayed 0/3; both pass 3/3 with the AGENTS snippet.

### C-20261026-2 · 2026-10-26 · XAG 117 and 118 read directly; accessibility summary corrected
- because: R-20261026-6
- files: RESEARCH.md (current understanding, open questions, findings log)
- XAG 117 requires a way to turn shake, bob and blur off; sliders are its examples, not its rule. XAG 118's limits (about 3 flashes per second over about 20% of the screen) match P-18. principles.md and lenses.md needed no change.

### C-20261026-1 · 2026-10-26 · Created as an evergreen unit
- because: user request
- files: SKILL.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `slow`, interval 120d. See R-20261026-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
