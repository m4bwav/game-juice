# Agent rules for game-juice

Rules for any AI agent (Claude Code, Copilot, Cursor, Codex, Gemini CLI) working in this repository. `CLAUDE.md` and `.github/copilot-instructions.md` only point here.

Read [README.md](README.md) first. The three skills live under [skills/](skills/). Each is an evergreen unit with its companions beside it (RESEARCH, CHANGELOG, LEARNINGS, TESTS, `evals/evals.json`, MAINTENANCE, `evergreen.json`).

## Rules

- Evergreen units in pointer mode: before editing a skill, read its `evergreen.json`. If `next_due` has passed or `contradiction` is set, say so and refresh after the task (`evergreen-refresh`). Every SKILL.md edit gets a CHANGELOG entry with its reason. Re-run that skill's evals when the change alters what it triggers on or does.
- The knowledge base is written in our own words. Never paste passages from the source books (Swink, Schell, Hodent, Rogers) into the repo. Paraphrase, cite the chapter and page, and keep quotes under about 12 words. Never commit the books or extracts of them.
- Principle IDs (`P-xx`) and lens IDs (`J-xx`) are stable. Add new ones at the end and never renumber.
- Engine API names and library versions move. Change them only with a dated `R-` entry in the skill's RESEARCH.md.
- `skills/juice-scan/scripts/juice_scan.py` is standard-library Python 3.8+, read-only, prints one JSON object, and fails soft. After changing it, run `python tests/check_scan.py` (the sample games in `tests/fixtures/`) and `python tests/check_skills.py`.
- Skills stay under 200 lines with descriptions of at most 1,024 characters, and each description names the sibling that owns nearby requests.
- Fixtures under `tests/fixtures/` are deliberately under-juiced. Don't polish them; the tests expect their gaps. Eval runs that write reports or apply changes work on a scratch copy.
- No AI attribution in commits or files. Nothing private (people, machines, absolute home paths, credentials).
## everlast (session knowledge, load on demand)

- `ai-docs/INDEX.md` lists what past sessions learned here (solutions with verified commands, decisions with reasons, plans). At the start of a task, scan it and open only the entries whose title or tags match; no line matches: `everlast.py search "<key terms>"` before concluding nothing was recorded. Read `ai-docs/HANDOFF.md` when continuing unfinished work (everlast-resume skill).
- Before acting on an entry marked `(recheck due)`, run `everlast.py recheck <entry>`, re-run its Verified-by command only when that is read-only or safe (a build, a test, a version query), then record `everlast.py verify <entry>` or `verify <entry> --failed "what broke"`; a fix that changed is superseded, never reused blindly. When an entry, or this file, disagrees with the code, follow the code, name each mismatch in your reply, and record `verify --failed` on the entry.
- Before finishing a task that hit a dead end, verified a non-obvious command, made a design choice, or taught you something about the user, record it (everlast-capture skill, or `everlast.py note` / `handoff`); rewrite `HANDOFF.md` when work is left unfinished. Say "nothing to record" when that is true.
- Anything naming a person, an internal host or name, a credential, or an opinion about people goes to the private sidecar (`--private`), never here. Lessons about the user or this machine go to the user tier (`--user`).
- Rules go in this file, system layout in CODEMAP.md; the doc set holds only what could not be re-derived from the code in a minute.
- Link documents together with relative markdown links: every markdown folder is reachable from an index whose lines say when to read each file (`ai-docs/INDEX.md` is generated from frontmatter; give entries a one-line `summary`), and an entry links the entries it relates to on a typed `Related:` line (`supersedes`, `contradicts`, `builds on`, `see also`). The set then reads as a graph for people in Obsidian and for agents alike. No wikilinks in the repo.

