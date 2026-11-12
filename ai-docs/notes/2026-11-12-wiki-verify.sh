#!/bin/sh
# Re-runs every output shown on the game-juice wiki. Run from the repo root.
S=skills/juice-scan/scripts/juice_scan.py
echo "== scan godot --md"; python $S tests/fixtures/godot-platformer --md
echo "== scan godot jump moment"; python $S tests/fixtures/godot-platformer | python -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d['moments'][2],indent=1))"
echo "== scan keys"; python $S tests/fixtures/godot-platformer | python -c "import json,sys;print(' '.join(json.load(sys.stdin)))"
echo "== scan missing"; python $S does/not/exist
echo "== check_scan"; python tests/check_scan.py
echo "== check_skills"; python tests/check_skills.py
