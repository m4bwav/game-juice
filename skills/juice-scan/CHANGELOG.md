# Changelog: juice-scan

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261026-4 · 2026-10-26 · Published as part of the public game-juice repository
- because: user request
- files: RESEARCH.md (R-20261026-1 wording), TESTS.md (T-20261026-1)
- Generalized one phrase for the public repository (sources written "from general engine knowledge") and removed a duplicated `led to:` line. No change to what the skill does.

### C-20261026-3 · 2026-10-26 · Engine references checked against primary docs; Roblox pop uses UIScale
- because: R-20261026-4, R-20261026-5, R-20261026-6, R-20261026-7, R-20261026-8; user request (pop sketch)
- files: references/engines/roblox.md (settings hook, pickup pop, haptics), references/engines/godot.md (hit-stop, Godot traps), references/engines/web.md (PixiJS and GSAP sketches), RESEARCH.md (open questions, findings log)
- Roblox: `GuiService.ReducedMotionEnabled` confirmed; `pop(gui)` now tweens a `UIScale` child instead of resizing `Size`; haptics lead with the `HapticEffect` instance, which the docs say supersedes `HapticService`. Godot: `create_timer` argument order confirmed; `Tween.set_ignore_time_scale` corrected from 4.3+ to 4.4+, with the fallback for older versions. Web: GSAP licence confirmed on gsap.com and its one restriction noted; the Arcade `timeScale` direction was already right.

### C-20261026-2 · 2026-10-26 · Description claims feel complaints first, even for tiny projects; scanner sees indirect hit-stop calls
- because: T-20261026-1, L-001; T-20261026-2 (juice-apply re-scan)
- files: SKILL.md (frontmatter description), scripts/juice_scan.py (FEEDBACK timing and PROJECT_CHECKS hit_stop patterns)
- The description now says to use the skill first, before reading any game code, even for a tiny project. It leads with complaint words (flat, floaty, weak, stiff, unsatisfying), and the engine list is shorter to stay under 1,024 characters. The scanner also counts `.freeze(` and `Freeze*(` calls as timing feedback, so a hit-stop moved into a settings helper is still recognized.

### C-20261026-1 · 2026-10-26 · Created as an evergreen unit
- because: user request
- files: SKILL.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `moderate`, interval 30d. See R-20261026-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
