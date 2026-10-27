#!/usr/bin/env python3
"""Regression check for juice_scan.py against the sample games in tests/fixtures.

Each fixture must be detected as the right engine and must report named moments
in real files and functions. Run from the repository root:
    python tests/check_scan.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.join(ROOT, "skills", "juice-scan", "scripts", "juice_scan.py")
FIX = os.path.join(ROOT, "tests", "fixtures")

EXPECT = {
    "godot-platformer": ("godot", [("jump", "scripts/player.gd", "jump"),
                                   ("hit", "scripts/player.gd", "take_damage"),
                                   ("pickup", "scripts/coin.gd", "collect"),
                                   ("score", "scripts/hud.gd", "add_score")],
                         ["no_coyote_time", "no_jump_buffer", "no_hit_stop"]),
    "roblox-obby": ("roblox", [("jump", "src/client/Controls.client.luau", "onJumpRequest"),
                               ("hit", "src/server/Lava.server.luau", "damageHumanoid"),
                               ("pickup", "src/server/Coins.server.luau", "collectCoin")],
                    ["no_coyote_time", "no_hit_stop"]),
    "phaser-shooter": ("phaser", [("hit", "src/GameScene.js", "hitEnemy"),
                                  ("attack", "src/GameScene.js", "shoot"),
                                  ("score", "src/GameScene.js", "addScore")],
                       ["no_hit_stop"]),
    "pygame-dodge": ("pygame", [("jump", "main.py", "jump"), ("hit", "main.py", "take_hit")],
                     ["no_coyote_time"]),
    "unity-brawler": ("unity", [("hit", "Assets/Scripts/Enemy.cs", "TakeDamage"),
                                ("death", "Assets/Scripts/Enemy.cs", "Die"),
                                ("attack", "Assets/Scripts/PlayerCombat.cs", "Attack")],
                      ["no_shake_toggle", "no_pitch_variation", "no_hit_stop"]),
}
EXPECT_RISKS = {"unity-brawler": ["shake_per_frame"]}


def main() -> int:
    failures = 0
    for name, (engine, moments, findings) in EXPECT.items():
        out = subprocess.run([sys.executable, SCAN, os.path.join(FIX, name)], capture_output=True, text=True)
        try:
            r = json.loads(out.stdout)
        except json.JSONDecodeError:
            print(f"FAIL {name}: output is not JSON: {out.stdout[:200]}")
            failures += 1
            continue
        problems = []
        if "error" in r:
            problems.append(r["error"])
        elif r["engine"]["engine"] != engine:
            problems.append(f"engine {r['engine']['engine']} != {engine}")
        got = {(m["moment"], m["file"], m["function"]) for m in r.get("moments", [])}
        for exp in moments:
            if exp not in got:
                problems.append(f"missing moment {exp}")
        got_f = {f["id"] for f in r.get("findings", [])}
        problems += [f"missing finding {f}" for f in findings if f not in got_f]
        got_r = {x["id"] for x in r.get("risks", [])}
        problems += [f"missing risk {x}" for x in EXPECT_RISKS.get(name, []) if x not in got_r]
        for m in r.get("moments", []):
            if not os.path.isfile(os.path.join(FIX, name, m["file"])):
                problems.append(f"reported file does not exist: {m['file']}")
        if problems:
            failures += 1
            print(f"FAIL {name}: " + "; ".join(problems))
        else:
            print(f"ok   {name}: {engine}, {len(r['moments'])} moments, findings {sorted(got_f)}")
    # fail-soft contract
    out = subprocess.run([sys.executable, SCAN, os.path.join(FIX, "does-not-exist")], capture_output=True, text=True)
    if out.returncode != 0 or '"error"' not in out.stdout:
        failures += 1
        print("FAIL fail-soft: missing directory should print an error object and exit 0")
    else:
        print("ok   fail-soft")
    print("PASS" if not failures else f"{failures} FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
