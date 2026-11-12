---
title: GitHub wiki and social preview
summary: Wiki pages for 1.3.5, how they were verified, and how to update them at the next release
---

# GitHub wiki (2026-11-12, v1.3.5)

Wiki: https://github.com/m4bwav/game-juice/wiki. Working copy: sibling folder `game-juice.wiki`.

Pages: Home, Getting-Started, The-Skills, The-Scanner, Toggles-and-Accessibility, Works-With, FAQ, Versions-And-Upgrading, Development, _Sidebar, _Footer.

Verified: every output block comes from `2026-11-12-wiki-verify.sh` (scanner on the Godot fixture, the fail-soft case, both test scripts), saved in `2026-11-12-wiki-verify.out.txt`. wikiwright `check`, `outputs` (6 checked, 0 missing) and `live` (9 pages, 0 failures) all passed.

Works with: game-juice's page covers sfxwright, ludowright, grindwright, madnesswright, unity-agent and roblox-agent. A game-juice section was added to the Works-with pages of the sfxwright, ludowright and madnesswright wikis, and a "feel" row to grindwright's lane table. unity-agent and roblox-agent have no wikis.

Social preview: `.github/images/social-preview.jpg` (1280x640, the banner cropped with the title), uploaded in repository settings; `usesCustomOpenGraphImage` is true.

## Inaccuracies in shipped docs

1. README says 27 principles; principles.md now has 28 (P-01 to P-28).

## Updating at the next release

Run the verify script from the repo root, diff with `wikiwright.py diffout`, fix pages. Pages that name the version: Home, Versions-And-Upgrading (add a row), _Footer. Add any new partner plugin to Works-With and to that plugin's own Works-with page.
