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
    "web-platformer": ("phaser", [("jump", "src/Player.js", "jump")],
                       ["scattered_feel_constants", "launch_without_timer_reset"]),
    "unity-deckbuilder": ("unity", [("card_play", "Assets/Scripts/HandView.cs", "OnCardPlayed"),
                                    ("card_draw", "Assets/Scripts/HandView.cs", "AnimateSingleDraw"),
                                    ("turn", "Assets/Scripts/HandView.cs", "OnTurnEnded")],
                          []),
    "godot-wave-hero": ("godot", [("attack", "scripts/hero.gd", "attack")],
                        ["hit_stop_ignores_hit_rate", "anim_speed_not_tied_to_move_speed"]),
    "unity-wave-hero": ("unity", [("hit", "Assets/Scripts/Hero.cs", "OnSwordHit")], []),
}
EXPECT_RISKS = {"unity-brawler": ["shake_per_frame"]}
# Findings that must not fire: the tuned hero scales its freeze by time since the last hit and sets clip speed.
EXPECT_FINDING_ABSENT = {"unity-wave-hero": ["hit_stop_ignores_hit_rate", "anim_speed_not_tied_to_move_speed"],
                         "godot-platformer": ["anim_speed_not_tied_to_move_speed"]}
# The numbers behind a finding: (fixture, finding id, key, expected value).
EXPECT_NUMBERS = [("godot-wave-hero", "hit_stop_ignores_hit_rate", "freeze_s", 0.12),
                  ("godot-wave-hero", "hit_stop_ignores_hit_rate", "gap_s", 0.2),
                  ("godot-wave-hero", "hit_stop_ignores_hit_rate", "share", 0.6),
                  ("godot-wave-hero", "anim_speed_not_tied_to_move_speed", "max_move_speed", 9.5)]


def check_rate_rules() -> list:
    """Unit checks on the hit-rate and locomotion rules, on inputs written here."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("juice_scan", SCAN)
    js = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(js)
    problems = []
    if abs(js._seconds("HIT_STOP_FRAMES", 6) - 0.1) > 1e-9:
        problems.append("6 hit-stop frames should be 0.1 s")
    if abs(js._seconds("hitStopMs", 80) - 0.08) > 1e-9:
        problems.append("80 ms should be 0.08 s")
    if abs(js._interval_seconds("fire_rate", 10) - 0.1) > 1e-9:
        problems.append("fire_rate 10 should be a 0.1 s gap")
    if abs(js._interval_seconds("fireRate", 0.15) - 0.15) > 1e-9:
        problems.append("fireRate 0.15 should stay 0.15 s")
    ids = lambda fs: {f["id"] for f in fs}
    slow = js.rate_and_locomotion_findings(["a.gd:1"], [(0.08, "a.gd:1")], [(0.8, "a.gd:2")], [], [], [], [])
    if "hit_stop_ignores_hit_rate" in ids(slow):
        problems.append("an 80 ms freeze on 0.8 s swings (10%) should pass")
    fast = js.rate_and_locomotion_findings(["a.gd:1"], [(0.03, "a.gd:1")], [(0.1, "a.gd:2")], [], [], [], [])
    if not any(f["id"] == "hit_stop_ignores_hit_rate" and f["severity"] == "medium" for f in fast):
        problems.append("a fixed 30 ms freeze at 10 hits/s should be flagged medium")
    scaled = js.rate_and_locomotion_findings(["a.gd:1"], [(0.12, "a.gd:1")], [(0.1, "a.gd:2")], ["a.gd:5 f"], [], [], [])
    if scaled:
        problems.append("a freeze that scales with the hit rate should pass")
    synced = js.rate_and_locomotion_findings([], [], [], [], ["a.gd:9"], ["a.gd:10"], [])
    if synced:
        problems.append("a run clip with speed_scale set should pass")
    if not js.hitstop_scales_with_rate("float f = sinceLastHit < 0.3f ? hitStopDuration * 0.25f : hitStopDuration;"):
        problems.append("camelCase since-last-hit scaling not seen")
    if js.hitstop_scales_with_rate("await get_tree().create_timer(hit_stop_time).timeout"):
        problems.append("create_timer must not count as a rate")
    return problems
# Functions and folders that must never be reported: predicates, tests, editor-only tools.
EXPECT_ABSENT = {"unity-deckbuilder": ["HasPendingDamageReveal", "TakeDamage_ReducesHp", "OnImportButtonPressed"]}


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
        problems += [f"unexpected finding {f}" for f in EXPECT_FINDING_ABSENT.get(name, []) if f in got_f]
        for fx, fid, key, val in EXPECT_NUMBERS:
            if fx == name:
                nums = next((f.get("numbers", {}) for f in r.get("findings", []) if f["id"] == fid), {})
                if nums.get(key) != val:
                    problems.append(f"{fid}.{key} = {nums.get(key)}, expected {val}")
        got_r = {x["id"] for x in r.get("risks", [])}
        problems += [f"missing risk {x}" for x in EXPECT_RISKS.get(name, []) if x not in got_r]
        got_fn = {m["function"] for m in r.get("moments", [])}
        problems += [f"reported excluded function {fn}" for fn in EXPECT_ABSENT.get(name, []) if fn in got_fn]
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
    rule_problems = check_rate_rules()
    if rule_problems:
        failures += 1
        print("FAIL rate rules: " + "; ".join(rule_problems))
    else:
        print("ok   rate rules: hit-stop share and gap, clip speed sync, unit conversion")
    print("PASS" if not failures else f"{failures} FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
