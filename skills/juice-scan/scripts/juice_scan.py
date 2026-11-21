#!/usr/bin/env python3
"""juice_scan.py - map a game's feel moments and the feedback each one already has.

Usage:
  python juice_scan.py <project-root> [--md] [--out FILE] [--max-files N] [--include-vendor] [--audio]

Inline <script> blocks of .html/.htm files are scanned as JavaScript with line
numbers kept as in the HTML file. --audio adds an "audio" section: every sound
play call with its literal volume, and findings for world sounds without
distance falloff, looped sounds restarted every frame, and flat effect volumes.

Prints one JSON object (or a Markdown moment map with --md). Pure standard
library, read-only, fails soft: on any error it still prints a JSON object
with an "error" field and exits 0. The output is the raw material for the
juice-scan skill's report; it guesses from names and calls, so every finding
is a lead to read, not a verdict.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime

VERSION = "1.4.0"

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "Library", "Temp", "Logs", "obj", "bin",
    "Build", "Builds", "build", "dist", "out", ".godot", ".import", "__pycache__",
    "venv", ".venv", "env", "Packages", "UserSettings", "Intermediate", "Binaries",
    "DerivedDataCache", "Saved", ".idea", ".vs", ".vscode", "coverage", "Pods",
    # Test suites and Unity editor-only code never reach the player.
    "Tests", "tests", "test", "Test", "__tests__", "spec", "Editor",
}
TEST_FILE = re.compile(r"(Tests?\.cs|_test\.(py|gd|lua)|\.(test|spec)\.(js|ts|jsx|tsx)|\.spec\.luau?)$|^test_\w+\.py$")
# Queries and helpers that only name a moment (HasPendingDamageReveal, GetImpactPosition, HitTest)
# are not the moment itself.
PREDICATE_NAME = re.compile(r"^(Has|Is|Can|Get|Should|Meets|Find|Compute|Calc|Count)[A-Z]|^(has|is|can|get|should|find)_|[Hh]it_?[Tt]est|^Hits$")
VENDOR_DIRS = {"Plugins", "addons", "ThirdParty", "vendor", "Vendor", "lib", "libs", "Packages"}

LANG_BY_EXT = {
    ".cs": "csharp", ".gd": "gdscript", ".lua": "lua", ".luau": "lua",
    ".js": "js", ".mjs": "js", ".ts": "js", ".jsx": "js", ".tsx": "js",
    ".py": "python", ".cpp": "cpp", ".h": "cpp", ".hpp": "cpp",
    ".html": "js", ".htm": "js",
}
HTML_EXT = (".html", ".htm")
SCRIPT_TAG_RX = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.I | re.S)
# A type= attribute that is not JavaScript (JSON, ld+json, importmap, shader source, templates).
JS_SCRIPT_TYPE = re.compile(r"""(?i)\btype\s*=\s*["']?\s*(?!(?:text/javascript|application/javascript|module|text/babel)\b)""")

# --- engine detection ------------------------------------------------------

def detect_engine(root: str, files: list[str]) -> dict:
    def exists(*p):
        return os.path.exists(os.path.join(root, *p))

    evidence = []
    engine = "unknown"
    lang = None
    if exists("ProjectSettings", "ProjectVersion.txt") or (exists("Assets") and any(f.endswith(".cs") for f in files)):
        engine, lang = "unity", "csharp"
        evidence.append("ProjectSettings/ProjectVersion.txt" if exists("ProjectSettings", "ProjectVersion.txt") else "Assets/ with .cs")
    elif exists("project.godot"):
        engine, lang = "godot", "gdscript"
        evidence.append("project.godot")
    elif any(n.endswith(".uproject") for n in os.listdir(root)):
        engine, lang = "unreal", "cpp"
        evidence.append("*.uproject")
    elif exists("default.project.json") or exists("rokit.toml") or exists("wally.toml") or any(f.endswith(".luau") for f in files):
        engine, lang = "roblox", "lua"
        evidence.append(next((m for m in ("default.project.json", "rokit.toml", "wally.toml") if exists(m)), ".luau files"))
    elif exists("main.lua") and _contains(os.path.join(root, "main.lua"), r"\blove\."):
        engine, lang = "love2d", "lua"
        evidence.append("main.lua uses love.*")
    elif exists("game.project"):
        engine, lang = "defold", "lua"
        evidence.append("game.project")
    elif exists("package.json"):
        pkg = _read(os.path.join(root, "package.json"))
        for name, eng in (("phaser", "phaser"), ("pixi.js", "pixijs"), ("kaboom", "kaboom"),
                          ("kaplay", "kaplay"), ("excalibur", "excalibur"), ("three", "threejs")):
            if f'"{name}"' in pkg:
                engine, lang = eng, "js"
                evidence.append(f"package.json depends on {name}")
                break
        if engine == "unknown":
            engine, lang = "web", "js"
            evidence.append("package.json")
    if engine == "unknown":
        for f in files:
            if f.endswith(".py") and _contains(f, r"^\s*import pygame|^\s*from pygame"):
                engine, lang = "pygame", "python"
                evidence.append(os.path.relpath(f, root) + " imports pygame")
                break
    if engine == "unknown":
        for f in files:
            if f.lower().endswith(HTML_EXT) and _source(f).strip():
                src = _source(f)
                engine = next((e for rx, e in ((r"new Phaser\.Game", "phaser"), (r"\bPIXI\.", "pixijs"),
                                                (r"\bTHREE\.", "threejs")) if re.search(rx, src)), "web")
                lang = "js"
                evidence.append(os.path.relpath(f, root).replace("\\", "/") + " inline <script>")
                break
    if engine == "unknown":
        for f in files:
            if f.endswith((".js", ".ts")) and _contains(f, r"new Phaser\.Game|from ['\"]phaser['\"]"):
                engine, lang = "phaser", "js"
                evidence.append(os.path.relpath(f, root))
                break
            if f.endswith((".js", ".ts")) and _contains(f, r"PIXI\.|from ['\"]pixi\.js['\"]"):
                engine, lang = "pixijs", "js"
                evidence.append(os.path.relpath(f, root))
                break
    return {"engine": engine, "language": lang, "evidence": evidence}


LIBRARY_PATTERNS = [
    ("DOTween", r"using DG\.Tweening|\bDOTween\b"),
    ("Feel (MMFeedbacks)", r"MoreMountains\.Feedbacks|MMF_Player|MMFeedbacks"),
    ("PrimeTween", r"using PrimeTween|\bTween\.(Position|Scale|ShakeCamera|PunchScale)"),
    ("LitMotion", r"using LitMotion|LMotion\."),
    ("LeanTween", r"\bLeanTween\."),
    ("Cinemachine Impulse", r"CinemachineImpulseSource|GenerateImpulse"),
    ("Godot Tween", r"create_tween\(|\bTween\.TRANS_|set_trans\("),
    ("Roblox TweenService", r"TweenService"),
    ("GSAP", r"\bgsap\.|from ['\"]gsap['\"]"),
    ("Phaser tweens", r"this\.tweens\.add|tweens\.chain"),
    ("Phaser camera FX", r"cameras\.main\.(shake|flash|fade)"),
    ("PixiJS particle-emitter", r"particle-emitter|new Emitter\("),
    ("tween.js", r"TWEEN\.Tween|@tweenjs"),
    ("pytweening", r"import pytweening"),
    ("flux/tween.lua (LOVE)", r"require\s*\(?['\"](flux|tween)['\"]"),
]

# --- function splitting ----------------------------------------------------

CS_FUNC = re.compile(
    r"^\s*(?:\[[^\]]*\]\s*)*(?:(?:public|private|protected|internal|static|override|virtual|async|sealed|abstract|new|unsafe|extern)\s+)*"
    r"(?:[\w<>\[\],.?]+\s+)(\w+)\s*\([^;{]*\)?\s*(?:where\s+[^{]*)?\{?\s*$")
GD_FUNC = re.compile(r"^\s*(?:static\s+)?func\s+(\w+)")
LUA_FUNC = [
    re.compile(r"^\s*(?:local\s+)?function\s+([\w.:]+)\s*\("),
    re.compile(r"^\s*(?:local\s+)?([\w.]+)\s*=\s*function\s*\("),
    re.compile(r"([\w.]+)\s*:\s*Connect\(\s*function"),
]
JS_FUNC = [
    re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)\s*\("),
    re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|\w+\s*=>)"),
    re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|override\s+)*(\w+)\s*\([^)]*\)\s*(?::\s*[\w<>\[\]| ]+)?\s*\{\s*$"),
    re.compile(r"^\s*(\w+)\s*:\s*(?:async\s*)?function\s*\("),
]
PY_FUNC = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")
CPP_FUNC = re.compile(r"^\s*[\w:<>*&\s]+?\b(\w+)::(\w+)\s*\([^;]*\)\s*(?:const)?\s*(?:override)?\s*\{?\s*$")
NOT_FUNC = {"if", "for", "foreach", "while", "switch", "return", "catch", "using", "lock", "else", "new",
            "function", "elseif", "with", "typeof", "sizeof", "nameof", "base", "this", "get", "set"}


def split_functions(lines: list[str], lang: str) -> list[tuple[str, int, int]]:
    """Return (name, start_line_1based, end_line_exclusive_1based)."""
    starts: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        name = None
        if lang == "csharp":
            m = CS_FUNC.match(line)
            if m and m.group(1) not in NOT_FUNC and "=" not in line.split("(")[0]:
                name = m.group(1)
        elif lang == "gdscript":
            m = GD_FUNC.match(line)
            name = m.group(1) if m else None
        elif lang == "lua":
            for rx in LUA_FUNC:
                m = rx.search(line)
                if m:
                    name = m.group(1) + (" handler" if "Connect" in rx.pattern else "")
                    break
        elif lang == "js":
            for rx in JS_FUNC:
                m = rx.match(line)
                if m and m.group(1) not in NOT_FUNC:
                    name = m.group(1)
                    break
        elif lang == "python":
            m = PY_FUNC.match(line)
            name = m.group(1) if m else None
        elif lang == "cpp":
            m = CPP_FUNC.match(line)
            if m and m.group(2) not in NOT_FUNC:
                name = f"{m.group(1)}::{m.group(2)}"
        if name:
            starts.append((name, i + 1))
    out = []
    for idx, (name, start) in enumerate(starts):
        end = starts[idx + 1][1] if idx + 1 < len(starts) else len(lines) + 1
        out.append((name, start, end))
    return out

# --- moments and feedback --------------------------------------------------

# (moment, name regex, body regex). Name matches weigh 3, body matches 1.
MOMENTS = [
    ("jump", r"jump|leap|hop", r"\bjump|is_on_floor|isGrounded|IsGrounded|JumpPower|Humanoid\.Jump|velocity\.y\s*=\s*-|\.Jump\b"),
    ("attack", r"attack|shoot|fire|swing|slash|strike|cast|punch|melee|bullet", r"Instantiate\(.*(bullet|projectile)|spawn_?bullet|projectile|\bfire\b"),
    ("hit", r"hit|damage|hurt|takedamage|take_damage|on_?hit|impact|collide|collision", r"health\s*-=|hp\s*-=|lives\s*-=|TakeDamage|take_damage|take_hit|\bdamage\b|Health\s*=\s*.*-|colliderect|OnCollisionEnter|OnTriggerEnter"),
    ("death", r"die\b|^die|death|dead|kill|gameover|game_over|explode|destroy", r"Destroy\(gameObject|queue_free\(\)|:Destroy\(\)|health\s*<=\s*0|hp\s*<=\s*0|game_?over"),
    ("pickup", r"pickup|pick_up|collect|coin|gem|item|powerup|power_up|loot", r"coins?\s*\+=|collect|pickup|:Destroy\(\).*coin"),
    ("score", r"score|points|combo|addscore|add_score", r"score\s*\+=|Score\s*\+=|score\s*=\s*score\s*\+|leaderstats"),
    ("ui_button", r"onclick|on_click|button|pressed|menu|onpointer|mousebutton1click|hover", r"onClick|\.pressed\.connect|MouseButton1Click|addEventListener\(['\"](click|pointerdown)|setInteractive|on\(['\"]pointerdown"),
    ("transition", r"loadscene|load_scene|change_scene|transition|fade|nextlevel|next_level|restart|teleport", r"SceneManager\.LoadScene|change_scene_to|scene\.start|TeleportAsync|location\.href"),
    ("camera", r"camera|cam\b|follow", r"Camera\.main|camera\.|Camera2D|CurrentCamera|cameras\.main"),
    ("card_play", r"playcard|play_card|cardplayed|card_played|tryplay|castcard|cast_card", r"OnCardPlayed|card_played|PlayCard\(|play_card\(|discardPile|discard_pile"),
    ("card_draw", r"drawcard|draw_card|carddraw|dealcard|deal_card|drawsequence|singledraw|drawhand|draw_hand", r"DrawCard\(|draw_card\(|hand\.Add\(|hand\.append\(|hand\.push\(|deck\.Draw"),
    ("turn", r"endturn|end_turn|turnended|turn_ended|nextturn|next_turn|startturn|turnstarted|newround|new_round", r"OnTurnEnded|turn_ended|EndTurn\(|end_turn\(|turnNumber\s*\+\+|turn\s*\+=\s*1"),
    ("movement", r"^move|movement|walk|run\b|dash", r"velocity|move_and_slide|MoveTo|AddForce|\.Move\(|transform\.position\s*\+=|rect\.(x|y)\s*[+-]="),
    ("input", r"input|keydown|keypressed|keypress|onmove|onjump|_unhandled_input", r"Input\.Get|InputAction|UserInputService|ContextActionService|is_action_just_pressed|KEYDOWN|keyboard\.|love\.keypressed|addEventListener\(['\"]key"),
]
MOMENT_NAME_RX = [(m, re.compile(n, re.I), re.compile(b)) for m, n, b in MOMENTS]

FEEDBACK = {
    "visual": r"Particle|particle|emitter|Emitter|\bflash|Flash|tint|modulate\b|\.color\s*=|Color\s*=|vfx|VFX|\bfx\b|explosion|Explosion|spawn_?effect|trail|Trail|dust|sparks?",
    "motion": r"DOTween|\.DO[A-Z]\w*\(|\btween|Tween|[Ll]erp\(|ease|Ease|SmoothDamp|AnimationCurve|squash|stretch|PunchScale|DOPunch|scale\s*=|localScale\s*=",
    "camera": r"[Ss]hake|Impulse|trauma|cameras\.main\.(shake|flash|zoom)|FieldOfView|\bfov\b|zoom|camera.*offset|Camera.*Offset",
    "audio": r"AudioSource|PlayOneShot|AudioStreamPlayer|\bSound\b|:Play\(\)|sound|Sound|sfx|SFX|audio|Audio|mixer\.|love\.audio|playSound|createOscillator|createBufferSource|\.play\(\s*['\"]",
    "ui": r"setText\(|popup|Popup|DamageNumber|damage_number|floating_?text|FloatingText|\bText\b|\.text\s*=|Label|label\.|HUD|hud|TextLabel",
    "haptic": r"SetMotorSpeeds|[Vv]ibrat|Haptic|rumble|Rumble|start_joy_vibration|navigator\.vibrate|SetMotor",
    "timing": r"hit_?stop|HitStop|hitStop|freeze_?frame|\.freeze\(|[Ff]reeze[A-Z_]\w*\(|timeScale|time_scale|Engine\.time_scale|coyote|Coyote|jump_?buffer|JumpBuffer|inputBuffer|input_buffer|grace|slow_?mo|SlowMo",
    "animation": r"Animator|SetTrigger|AnimationPlayer|\.play\(\"|LoadAnimation|anims\.play|:Play\(\)|animation\.play|AnimatedSprite",
}
FEEDBACK_RX = {k: re.compile(v) for k, v in FEEDBACK.items()}

# What a well-fed moment usually has. A gap is a lead, not a rule (see juice-principles).
EXPECTED = {
    "jump": ["motion", "audio", "visual", "timing"],
    "attack": ["audio", "visual", "camera", "animation"],
    "hit": ["timing", "visual", "camera", "audio", "ui", "haptic"],
    "death": ["visual", "audio", "camera", "timing"],
    "pickup": ["audio", "visual", "motion", "ui"],
    "score": ["ui", "motion", "audio"],
    "ui_button": ["motion", "audio"],
    "transition": ["motion", "audio"],
    "camera": ["motion"],
    "movement": ["visual", "motion", "audio"],
    "input": ["timing"],
    "card_play": ["motion", "audio", "visual"],
    "card_draw": ["motion", "audio"],
    "turn": ["motion", "audio", "ui"],
}

PROJECT_CHECKS = {
    "pitch_variation": r"pitch\s*=\s*.*[Rr]andom|Random\.Range\([^)]*\).*pitch|pitch_scale\s*=\s*rand|randf_range|PlaybackSpeed\s*=\s*.*random|setRate|detune|rate\s*:\s*Phaser\.Math|pitch.*random\.uniform",
    "reduce_motion_toggle": r"reduce_?motion|reduceMotion|ReduceMotion|prefers-reduced-motion|screen_?shake_?(enabled|intensity|strength|scale)|ScreenShake(Enabled|Intensity|Scale)|shakeEnabled|shake_enabled|camera_?shake_?(enabled|scale)",
    "flash_limit": r"flash_?limit|max_?flash|photosensitiv|epilep|flashes_per_second|FlashLimit",
    "coyote_time": r"coyote|Coyote",
    "jump_buffer": r"jump_?buffer|JumpBuffer|jumpBuffer|input_?buffer|InputBuffer",
    "hit_stop": r"hit_?stop|HitStop|hitStop|freeze_?frame|\.freeze\(|FreezeFrame|hit_?pause|HitPause",
    "screen_shake": r"[Ss]hake|Impulse|trauma",
}
PROJECT_RX = {k: re.compile(v) for k, v in PROJECT_CHECKS.items()}

# Feel constants written as bare literals: a name that tunes feel, assigned a number.
FEEL_LITERAL_RX = re.compile(
    r"(?i)\b\w*(coyote|jump_?buffer|squash|stretch|jump_?(?:velocity|force|speed|height|lift)|"
    r"hold_?lift|step_?(?:up|down)|hit_?stop|shake)\w*\s*[:=]\s*-?\d*\.?\d+\b")
# Launch events: anything besides the plain jump that throws the player upward.
LAUNCH_NAME_RX = re.compile(r"(?i)spring|bounce|launch|stomp|trampoline|jump_?pad|boost")
UPWARD_RX = re.compile(r"(?i)velocity\.y|vel\.y|\bvy\b|velocity_y|setVelocityY|AssemblyLinearVelocity|\.velocity\s*=")

# Hit-stop against hit rate (idea from technique-harvest post 1xajfgh: fixed freezes read as stutter on fast
# weapons). Durations: literals named for hit-stop, or the first number passed to a hit-stop call.
_TYPED_ASSIGN = r"\s*(?::\s*[\w.]+\s*)?(?::=|=|:)\s*"
HITSTOP_LIT_RX = re.compile(r"(?i)\b(\w*(?:hit_?stop|hit_?pause|freeze_?frame|freeze_?time|freeze_?duration)\w*)" + _TYPED_ASSIGN + r"(\d*\.?\d+)(f|ms)?\b")
HITSTOP_CALL_RX = re.compile(r"(?i)\b(\w*(?:hit_?stop|hit_?pause|freeze_?frame|freeze))\s*\(\s*(\d*\.?\d+)(f|ms)?\s*[,)]")
HITSTOP_NOT_DURATION = re.compile(r"(?i)enabled|scale|strength|count|chance|max_?stack")
# Time between hits: cooldowns, fire rates, attack intervals.
INTERVAL_LIT_RX = re.compile(
    r"(?i)\b(\w*(?:fire_?rate|rate_?of_?fire|attack_?(?:cooldown|interval|delay|rate)|shot_?(?:cooldown|delay|interval)|"
    r"fire_?(?:delay|interval|cooldown)|swing_?(?:cooldown|interval)|time_?between_?(?:shots|attacks|hits|swings)|"
    r"weapon_?cooldown|shoot_?cooldown|hit_?cooldown)\w*)" + _TYPED_ASSIGN + r"(\d*\.?\d+)(f|ms)?\b")
# A hit-stop that already scales with the rate of hits names one of these on a line that sets or calls the
# freeze. Lines are matched after snake-casing (sinceLastHit -> since_last_hit), so words need a boundary.
HITSTOP_SCALE_RX = re.compile(r"(?<![a-z])(combo|consecutive|last_hit|since_last|streak|hit_count|in_a_row|rate|cooldown|"
                              r"interval|attack_speed|final_hit|is_final|finisher|recent)")
HITSTOP_ANY_RX = re.compile(r"hit_?stop|hit_?pause|freeze_?frame|freeze\w*\s*\(|\bfreeze\b")


def _snake(line: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", line).lower()


def hitstop_scales_with_rate(body: str) -> bool:
    """True when a line naming the freeze also names the rate of hits (combo, cooldown, time since last hit)."""
    for line in body.splitlines():
        n = _snake(line)
        if HITSTOP_ANY_RX.search(n) and HITSTOP_SCALE_RX.search(n):
            return True
    return False
# Rule numbers (start values, tune by eye): a freeze longer than a quarter of the gap between hits, or any fixed
# freeze at 4+ hits a second, stacks into stutter.
HITSTOP_MAX_SHARE = 0.25
FAST_HIT_GAP_S = 0.25

# Locomotion: a walk or run clip played at a fixed rate while the body's speed changes slides the feet.
WALK_ANIM_RX = re.compile(
    r"""(?i)(?:\bplay\w*|\btravel|crossfade\w*|setbool|settrigger|playanimation)\s*\(\s*["'][\w/ ]*?(walk|run|jog|sprint|locomotion)\w*["']"""
    r"""|\banimation\s*=\s*["'](walk|run|jog|sprint)\w*["']""")
ANIM_SYNC_RX = re.compile(
    r"""(?i)speed_scale\s*=|playback_?(?:speed|rate)|\banimator\.speed\s*=|\banim\w*\.speed\s*=|setfloat\(\s*["']\w*(?:speed|velocity|move)"""
    r"""|adjustspeed\(|anims\.timescale|msperframe|blend_position|blend_amount|blendspace|applyrootmotion|root_?motion|foot_?ik"""
    r"""|setikposition|stride|\bplay\(\s*["']\w+["']\s*,\s*-?[\d.]+\s*,\s*[a-z_]""")
MOVE_SPEED_LIT_RX = re.compile(r"(?i)\b(\w*(?:move|walk|run|max|sprint)_?speed\w*|speed)" + _TYPED_ASSIGN + r"(\d*\.?\d+)f?\b")
# Playback rate outside this band of the clip's authored speed looks wrong; blend to the next clip instead.
ANIM_RATE_BAND = (0.8, 1.25)


def _seconds(name: str, value: float, suffix: str = "") -> float:
    """Convert a duration literal to seconds from its name, suffix and size."""
    n = name.lower()
    if re.search(r"frames", n):
        return value / 60.0
    if suffix.lower() == "ms" or re.search(r"(^|_)ms$|_ms_|ms$|millis|msec", n) or value > 10:
        return value / 1000.0
    return value


def _interval_seconds(name: str, value: float, suffix: str = "") -> float:
    """A 'rate' above 1 is hits per second; everything else is seconds (or ms) between hits."""
    n = name.lower()
    if "rate" in n and not re.search(r"interval|delay|cooldown", n) and value > 1 and suffix.lower() != "ms":
        return 1.0 / value
    return _seconds(name, value, suffix)


# Over-juice / risk heuristics, checked line by line.
RISKS = [
    ("timescale_zero", r"(timeScale|time_scale)\s*=\s*0(\.0)?\b", "Time is frozen here; confirm it is restored on every path (including scene change and pause) or the game can lock."),
    ("spawn_in_update", None, "Effects are instantiated inside a per-frame function; pool them or rate-limit to avoid GC spikes and visual noise."),
    ("shake_per_frame", None, "Camera shake is triggered from a per-frame function; continuous shake reads as noise and causes motion sickness."),
    ("full_screen_flash", r"cameras\.main\.flash|FullScreenFlash|screen_?flash|ScreenFlash|flash_?screen", "Full-screen flash: keep it under 3 flashes per second and offer a way to turn it off (WCAG 2.3.1, photosensitivity)."),
]
PER_FRAME = re.compile(r"^(Update|LateUpdate|FixedUpdate|_process|_physics_process|update|love\.update|Heartbeat handler|RenderStepped handler|Stepped handler|tick|Tick)$")
SPAWN_RX = re.compile(r"Instantiate\(|\.instantiate\(\)|Instance\.new\(\s*['\"](ParticleEmitter|Part)|createEmitter|add\.particles|new Emitter\(")
SHAKE_CALL = re.compile(r"[Ss]hake\(|GenerateImpulse\(|cameras\.main\.shake\(|add_trauma\(|AddTrauma\(")
AUDIO_CALL = re.compile(FEEDBACK["audio"])
JITTER_RX = re.compile(r"(position|offset|Position|Offset|CFrame)\s*[+*]?=\s*.*(Random\.(insideUnit\w+|Range)|randf|rand_range|math\.random|Math\.random|random\.uniform)")

# --- helpers ---------------------------------------------------------------

def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def _html_scripts(html: str) -> str:
    """Inline JavaScript of an HTML page, everything else blanked to newlines so line numbers match the file.
    Scripts with src= and non-JS types (JSON, ld+json, importmap, shaders, templates) are skipped."""
    parts, pos = [], 0
    for m in SCRIPT_TAG_RX.finditer(html):
        attrs, body = m.group(1), m.group(2)
        parts.append("\n" * html.count("\n", pos, m.start(2)))
        is_js = not re.search(r"(?i)\bsrc\s*=", attrs) and not JS_SCRIPT_TYPE.search(attrs)
        parts.append(body if is_js else "\n" * body.count("\n"))
        pos = m.end(2)
    parts.append("\n" * html.count("\n", pos))
    return "".join(parts)


def _source(path: str) -> str:
    """The scannable code of a file: the file itself, or the inline scripts of an HTML page."""
    text = _read(path)
    return _html_scripts(text) if path.lower().endswith(HTML_EXT) else text


def _contains(path: str, rx: str) -> bool:
    return re.search(rx, _read(path), re.M) is not None


def walk(root: str, include_vendor: bool, max_files: int) -> tuple[list[str], list[str]]:
    files, vendor = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        keep = []
        for d in dirnames:
            if d in SKIP_DIRS or d.startswith("."):
                continue
            if not include_vendor and d in VENDOR_DIRS:
                vendor.append(os.path.relpath(os.path.join(dirpath, d), root))
                continue
            keep.append(d)
        dirnames[:] = keep
        for f in filenames:
            if TEST_FILE.search(f):
                continue
            if os.path.splitext(f)[1].lower() in LANG_BY_EXT:
                files.append(os.path.join(dirpath, f))
                if len(files) >= max_files:
                    return files, vendor
    return files, vendor


def classify(name: str, body: str, rel: str = "", nlines: int = 0) -> list[tuple[str, int]]:
    scores = []
    short = name.split(".")[-1].split(":")[-1]
    per_frame = bool(PER_FRAME.match(short) or PER_FRAME.match(name))
    # Long game-loop functions often hold several moments inline; accept weaker evidence there.
    threshold = 1 if nlines >= 25 else 2
    camera_file = "camera" in os.path.basename(rel).lower()
    if PREDICATE_NAME.search(short):
        return []
    for moment, name_rx, body_rx in MOMENT_NAME_RX:
        s = 0
        if name_rx.search(name.replace(" handler", "")):
            s += 3
        hits = len(body_rx.findall(body))
        s += min(hits, 3)
        if per_frame and moment == "movement" and hits:
            s += 1
        if camera_file and moment == "camera":
            s += 3
        if s >= threshold:
            scores.append((moment, s))
    scores.sort(key=lambda t: -t[1])
    return scores


def scan(root: str, include_vendor: bool = False, max_files: int = 4000, audio: bool = False) -> dict:
    root = os.path.abspath(root)
    files, vendor = walk(root, include_vendor, max_files)
    eng = detect_engine(root, files)
    libs: set[str] = set()
    project_flags = {k: [] for k in PROJECT_CHECKS}
    moments = []
    risks = []
    func_count = 0
    feel_literal_files = []
    launches = []
    hitstop_durations: list[tuple[float, str]] = []
    hit_intervals: list[tuple[float, str]] = []
    hitstop_scaled: list[str] = []
    walk_anims: list[str] = []
    anim_synced: list[str] = []
    move_speeds: list[tuple[float, str]] = []
    texts: list[tuple[str, str]] = []
    funcs: list[tuple[str, str, int, str]] = []  # (file, name, line, body)

    for path in files:
        rel = os.path.relpath(path, root).replace("\\", "/")
        lang = LANG_BY_EXT[os.path.splitext(path)[1].lower()]
        text = _source(path)
        if not text.strip():
            continue
        texts.append((rel, text))
        for lib, rx in LIBRARY_PATTERNS:
            if re.search(rx, text):
                libs.add(lib)
        for k, rx in PROJECT_RX.items():
            m = rx.search(text)
            if m and len(project_flags[k]) < 5:
                line = text.count("\n", 0, m.start()) + 1
                project_flags[k].append(f"{rel}:{line}")
        if FEEL_LITERAL_RX.search(text):
            feel_literal_files.append(rel)
        collect_rate_and_locomotion(text, rel, hitstop_durations, hit_intervals, walk_anims, anim_synced, move_speeds)
        lines = text.splitlines()
        for name, start, end in split_functions(lines, lang):
            func_count += 1
            body = "\n".join(lines[start - 1:end - 1])
            funcs.append((rel, name, start, body))
            short = name.split(".")[-1].split(":")[-1]
            # risks
            for rid, rx, why in RISKS:
                if rx and re.search(rx, body):
                    risks.append({"id": rid, "file": rel, "function": name, "line": start, "why": why})
            if PER_FRAME.match(short) or PER_FRAME.match(name):
                if SPAWN_RX.search(body):
                    risks.append({"id": "spawn_in_update", "file": rel, "function": name, "line": start, "why": RISKS[1][2]})
                if (SHAKE_CALL.search(body) or JITTER_RX.search(body)) and not re.search(r"\bif\b", body):
                    risks.append({"id": "shake_per_frame", "file": rel, "function": name, "line": start, "why": RISKS[2][2]})
            if LAUNCH_NAME_RX.search(short) and UPWARD_RX.search(body):
                resets = [k for k in ("coyote", "buffer") if re.search(k, body, re.I)]
                launches.append({"file": rel, "function": name, "line": start, "resets": resets})
            if hitstop_scales_with_rate(body):
                hitstop_scaled.append(f"{rel}:{start} {name}")
            cls = classify(name, body, rel, end - start)
            if not cls:
                continue
            feedback = {}
            for cat, rx in FEEDBACK_RX.items():
                found = sorted(set(m.group(0) for m in rx.finditer(body)))[:4]
                if found:
                    feedback[cat] = found
            primary = cls[0][0]
            expected = EXPECTED.get(primary, [])
            gaps = [c for c in expected if c not in feedback]
            moments.append({
                "moment": primary,
                "also": [m for m, _ in cls[1:3]],
                "file": rel,
                "function": name,
                "line": start,
                "lines": end - start,
                "language": lang,
                "feedback": feedback,
                "gaps": gaps,
                "confidence": "high" if cls[0][1] >= 4 else "medium" if cls[0][1] >= 3 else "low",
            })

    # project-level findings
    findings = []
    if project_flags["screen_shake"] and not project_flags["reduce_motion_toggle"]:
        findings.append({"id": "no_shake_toggle", "severity": "high",
                         "why": "Screen shake exists but no reduce-motion or shake-intensity setting was found (accessibility: motion sickness, vestibular disorders).",
                         "where": project_flags["screen_shake"]})
    has_audio = any("audio" in m["feedback"] for m in moments)
    if has_audio and not project_flags["pitch_variation"]:
        findings.append({"id": "no_pitch_variation", "severity": "medium",
                         "why": "Sounds play but no pitch randomization was found; repeated identical samples fatigue the ear (machine-gun effect)."})
    # Coyote time and a jump buffer only matter when the player presses jump (not when "jump" is airtime state).
    jump_inputs = find_jump_inputs(texts)
    if any(m["moment"] == "jump" for m in moments) and jump_inputs:
        if not project_flags["coyote_time"]:
            findings.append({"id": "no_coyote_time", "severity": "medium", "why": "Jumping exists but no coyote-time grace window was found."})
        if not project_flags["jump_buffer"]:
            findings.append({"id": "no_jump_buffer", "severity": "medium", "why": "Jumping exists but no jump/input buffer was found."})
    if any(m["moment"] == "hit" for m in moments) and not project_flags["hit_stop"]:
        findings.append({"id": "no_hit_stop", "severity": "medium", "why": "Hits exist but no hit-stop / freeze-frame was found."})

    if len(feel_literal_files) >= 2:
        findings.append({"id": "scattered_feel_constants", "severity": "low",
                         "why": "Feel numbers (coyote, buffer, squash, jump lift, step, shake) are set as literals in several files; gather them in one frozen tuning table (P-29).",
                         "where": feel_literal_files[:8]})
    if project_flags["coyote_time"] or project_flags["jump_buffer"]:
        leaky = [f"{x['file']}:{x['line']} {x['function']}" for x in launches if len(x["resets"]) < 2]
        if leaky:
            findings.append({"id": "launch_without_timer_reset", "severity": "medium",
                             "why": "A spring, bounce or launch path sets upward velocity without clearing both the coyote and jump-buffer timers, so a buffered jump can fire on top of it (P-29).",
                             "where": leaky[:8]})

    findings += rate_and_locomotion_findings(project_flags["hit_stop"], hitstop_durations, hit_intervals,
                                             hitstop_scaled, walk_anims, anim_synced, move_speeds)
    findings += streak_findings(texts, has_audio or bool(project_audio(texts)))
    findings += dodge_findings(texts, funcs)
    findings += stagger_findings(funcs)
    findings += reduce_motion_findings(texts, funcs, project_flags["reduce_motion_toggle"])

    by_moment: dict[str, int] = {}
    for m in moments:
        by_moment[m["moment"]] = by_moment.get(m["moment"], 0) + 1
    order = {"high": 0, "medium": 1, "low": 2}
    moments.sort(key=lambda m: (order[m["confidence"]], -len(m["gaps"]), m["file"], m["line"]))

    result = {
        "tool": "juice_scan.py", "version": VERSION,
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "root": root,
        "engine": eng,
        "libraries": sorted(libs),
        "files_scanned": len(files),
        "functions_seen": func_count,
        "vendor_dirs_skipped": vendor[:20],
        "moment_counts": by_moment,
        "moments": moments,
        "project_flags": project_flags,
        "findings": findings,
        "risks": risks,
        "jump_inputs": jump_inputs[:5],
        "note": "Heuristic map from names and calls. Read each function before suggesting; confidence=low entries are often false positives.",
    }
    if audio:
        result["audio"] = audio_scan(texts, funcs)
    return result


def collect_rate_and_locomotion(text, rel, durations, intervals, walk_anims, synced, speeds) -> None:
    """Gather hit-stop durations, gaps between hits, walk/run plays, speed sync and move speeds in one file."""
    def where(m):
        return f"{rel}:{text.count(chr(10), 0, m.start()) + 1}"
    for rx in (HITSTOP_LIT_RX, HITSTOP_CALL_RX):
        for m in rx.finditer(text):
            if HITSTOP_NOT_DURATION.search(m.group(1)):
                continue
            secs = _seconds(m.group(1), float(m.group(2)), m.group(3) or "")
            if 0 < secs <= 1.0:
                durations.append((round(secs, 4), where(m)))
    for m in INTERVAL_LIT_RX.finditer(text):
        secs = _interval_seconds(m.group(1), float(m.group(2)), m.group(3) or "")
        if 0 < secs <= 5.0:
            intervals.append((round(secs, 4), where(m)))
    for m in WALK_ANIM_RX.finditer(text):
        walk_anims.append(where(m))
    for m in ANIM_SYNC_RX.finditer(text):
        synced.append(where(m))
    for m in MOVE_SPEED_LIT_RX.finditer(text):
        v = float(m.group(2))
        if v > 0:
            speeds.append((v, where(m)))


def rate_and_locomotion_findings(hit_stop_flags, durations, intervals, scaled, walk_anims, synced, speeds) -> list:
    """hit_stop_ignores_hit_rate and anim_speed_not_tied_to_move_speed, with the numbers behind each."""
    out = []
    if (hit_stop_flags or durations) and not scaled:
        freeze = max(durations)[0] if durations else None
        gap = min(intervals)[0] if intervals else None
        share = round(freeze / gap, 2) if freeze and gap else None
        fast = gap is not None and gap < FAST_HIT_GAP_S
        if share is not None and (share >= HITSTOP_MAX_SHARE or fast):
            severity = "high" if share >= 2 * HITSTOP_MAX_SHARE else "medium"
        elif gap is None:
            severity = "low"
        else:
            severity = None  # slow hits: a fixed freeze is fine
        if severity:
            nums = []
            if freeze is not None:
                nums.append(f"longest freeze {round(freeze * 1000)} ms")
            if gap is not None:
                nums.append(f"shortest gap between hits {round(gap * 1000)} ms")
            if share is not None:
                nums.append(f"freeze is {round(share * 100)}% of that gap")
            out.append({
                "id": "hit_stop_ignores_hit_rate", "severity": severity,
                "why": ("Hit-stop is a fixed length and nothing near it reads the rate of hits (combo, cooldown, time since "
                        "the last hit), so fast weapons stack freezes into stutter. Keep the freeze under "
                        f"{round(HITSTOP_MAX_SHARE * 100)}% of the gap between hits; at {round(1 / FAST_HIT_GAP_S)}+ hits a "
                        "second cut it to 30 ms or less, or freeze only the last hit of a combo"
                        + (" (" + "; ".join(nums) + ")." if nums else ". No attack rate was found; check the fastest weapon.")),
                "numbers": {"freeze_s": freeze, "gap_s": gap, "share": share,
                            "max_share": HITSTOP_MAX_SHARE, "fast_gap_s": FAST_HIT_GAP_S},
                "where": ([w for _, w in sorted(durations, reverse=True)[:3]] + [w for _, w in sorted(intervals)[:3]])
                         or hit_stop_flags[:5],
            })
    if walk_anims and not synced:
        top = max(speeds)[0] if speeds else None
        lo, hi = ANIM_RATE_BAND
        out.append({
            "id": "anim_speed_not_tied_to_move_speed", "severity": "medium",
            "why": ("A walk or run clip plays at a fixed rate and nothing sets its playback speed, blend or root motion from "
                    "the body's speed, so the feet slide. Set playback rate = ground speed / the clip's authored stride speed; "
                    f"keep it within {lo}-{hi}x and blend to the next clip outside that band, or drive the body by root motion "
                    "or foot IK" + (f" (move speeds up to {top:g} found)." if top is not None else ".")),
            "numbers": {"rate_band": [lo, hi], "max_move_speed": top},
            "where": walk_anims[:8],
        })
    return out


# --- jump bound to an input ---------------------------------------------------
# A line that reads a key, button or action, and a jump call or action name on it or within two lines after.
INPUT_LINE_RX = re.compile(
    r"(?i)keydown|keyup|keypress|\bK_(SPACE|UP|w)\b|\bkey\s*===?|\.key\b|\.code\b|keyCode|is_action_(just_)?pressed|"
    r"GetButton|GetKey|Input\.Get|InputAction|UserInputService|ContextActionService|JustDown|\.isDown|"
    r"pointerdown|touchstart|mousedown|_unhandled_input|func _input|love\.keypressed|wasPressedThisFrame|\bbtnp?\(")
JUMP_PRESS_RX = re.compile(
    r"""(?i)\bjump\w*\s*\(|["']jump["']|\bjump\w*\s*=\s*true\b|\.Jump\s*=\s*true|JumpRequest|\bjump_?(pressed|queued|requested)\b""")


def find_jump_inputs(texts) -> list:
    """file:line of each place a jump is bound to an input (a key, button or action)."""
    out = []
    for rel, text in texts:
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if INPUT_LINE_RX.search(line):
                for j in range(i, min(i + 3, len(lines))):
                    if JUMP_PRESS_RX.search(lines[j]):
                        out.append(f"{rel}:{j + 1}")
                        break
    return sorted(set(out), key=out.index)


# --- streak pitch ladder (idea: a one-tap stacking game, technique-harvest 2026-11) ----------------
STREAK_INC_RX = re.compile(r"(?i)\b(\w*(?:combo|streak|chain|perfects?|in_?a_?row)\w*)\s*(?:\+\+|\+=\s*1\b|=\s*\1\s*\+\s*1\b)")
PROJECT_AUDIO_RX = re.compile(
    r"AudioContext|createOscillator|new Audio\(|playSound|play_sound|PlayOneShot|AudioSource|AudioStreamPlayer|"
    r"pygame\.mixer|love\.audio|SoundService|\bHowl\b|\bsfx\w*\s*\(")
PITCH_WORD_RX = re.compile(r"(?i)pitch|playback_?rate|\brate\b|frequency|freq\b|detune|semitone")
SEMITONE_RX = re.compile(r"2\s*\*\*\s*\(|Math\.pow\(\s*2\s*,|\bpow\(\s*2(\.0)?\s*,|1\.059|semitone")
# Start values: warm-up of 2 steps, +1 semitone a step, cap at +4.
LADDER = {"warmup_steps": 2, "semitones_per_step": 1, "cap_semitones": 4}


def project_audio(texts) -> list:
    return [rel for rel, text in texts if PROJECT_AUDIO_RX.search(text)]


def streak_findings(texts, has_audio: bool) -> list:
    """streak_without_pitch_ladder: a combo or streak counter climbs, sounds play, and no pitch follows the counter."""
    counters, where = set(), []
    for rel, text in texts:
        for m in STREAK_INC_RX.finditer(text):
            counters.add(m.group(1))
            where.append(f"{rel}:{text.count(chr(10), 0, m.start()) + 1}")
    if not counters or not has_audio:
        return []
    names = re.compile(r"\b(" + "|".join(re.escape(c) for c in counters) + r")\b|combo|streak|chain", re.I)
    for _, text in texts:
        for line in text.splitlines():
            if SEMITONE_RX.search(line) or (PITCH_WORD_RX.search(line) and names.search(line)):
                return []
    return [{
        "id": "streak_without_pitch_ladder", "severity": "low",
        "why": ("A streak or combo counter climbs and sounds play, but no pitch, rate or frequency follows the counter, so "
                "the run sounds the same at step 2 and step 20. Raise the cue 1 semitone a step (factor 2 ** (n / 12)) "
                "from the 3rd step, cap at +4, shift both notes of a two-note cue, and reset with the streak (P-11)."),
        "numbers": dict(LADDER, counters=sorted(counters)),
        "where": where[:8],
    }]


# --- near miss and graze margin (idea: a lane runner, technique-harvest 2026-11) ------------------------
OBSTACLE_RX = re.compile(r"(?<![a-z])(obstacle|hazard|barrier|spike|asteroid|lane|enemy_?bullet|incoming)")
COLLIDE_RX = re.compile(r"(?i)collid|collision|overlap|intersect|colliderect|hit_?test|\baabb\b|OnTriggerEnter|"
                        r"OnCollisionEnter|body_entered|Touched|Math\.hypot\([^)]*\)\s*<|\bdist\w*\s*<")
NEAR_MISS_RX = re.compile(r"near_?miss|near_?pass|graze|close_?call|clearance|min_?gap|closest_?pass")
MARGIN_RX = re.compile(r"graze|margin|forgiv|stumble|tolerance|epsilon|lenien|hitbox_?(scale|shrink|inset)")
RUN_END_RX = re.compile(r"(?i)game_?over|\bdie\s*\(|\bdead\s*=\s*true|\blives\s*(-=|--)|\bhp\s*=\s*0\b|\bhealth\s*=\s*0\b|"
                        r"restart\s*\(|end_?run|\bcrash\s*\(|running\s*=\s*false|alive\s*=\s*false")


def dodge_findings(texts, funcs) -> list:
    """no_near_miss and no_graze_margin for games where the player dodges obstacles."""
    obstacles = [f"{rel}:{_snake(t).count(chr(10), 0, m.start()) + 1}" for rel, t in texts
                 for m in [OBSTACLE_RX.search(_snake(t))] if m]
    hits = [(rel, name, line, body) for rel, name, line, body in funcs if COLLIDE_RX.search(body)]
    if not obstacles or not hits:
        return []
    snaked = "\n".join(_snake(t) for _, t in texts)
    out = []
    if not NEAR_MISS_RX.search(snaked):
        out.append({
            "id": "no_near_miss", "severity": "medium",
            "why": ("Obstacles are dodged but close passes earn nothing. Track the smallest clearance per obstacle while "
                    "it passes and reward passes under about a quarter of a lane (a whoosh, a short slow-down, points)."),
            "numbers": {"reward_clearance_lanes": 0.25},
            "where": (obstacles + [f"{r}:{ln} {n}" for r, n, ln, _ in hits])[:8],
        })
    enders = [f"{r}:{ln} {n}" for r, n, ln, b in hits if RUN_END_RX.search(b)]
    if enders and not MARGIN_RX.search(snaked):
        out.append({
            "id": "no_graze_margin", "severity": "low",
            "why": ("A collision ends the run or kills at once with no graze margin or stumble tier. Shrink the hurt box "
                    "a little below the art, and let a glancing hit cost speed (a stumble) the first time, so only a "
                    "second hit inside about 5 s ends the run."),
            "numbers": {"stumble_window_s": 5.5},
            "where": enders[:8],
        })
    return out


# --- staggered resolution (idea: a turn-based dice game, technique-harvest 2026-11, measured from its store clips) ---
BATCH_LOOP_RX = re.compile(r"(?i)(?:\bfor\s*\(?[^\n]*?\b(?:in|of)\b|\bforeach\s*\(|\.forEach\s*\(|\bfor\s+\w+\s+in\b)"
                           r"[^\n]*?\b\w*(dice|die|cards?|hand|rewards?|loot|rolls?|relics?|tiles|matches|results|"
                           r"slots|pieces)\b")
BATCH_FEEDBACK_RX = re.compile(r"(?i)\.play\s*\(|play_?sound|playOneShot|\bsfx|spawn|Instantiate\s*\(|particle|"
                               r"\bflash|\bpop\s*\(|\bpunch|DO(Scale|Move|Punch|Shake|Fade)|tween|animate|"
                               r"show_?number|damage_?number|float_?text|\.reveal\s*\(")
STAGGER_RX = re.compile(r"(?i)\byield\b|\bawait\b|WaitForSeconds|setTimeout|SetDelay|AppendInterval|\bdelay\b|"
                        r"stagger|create_timer|task\.wait|\bwait\s*\(|\bsleep\s*\(|\b(i|idx|index|n|k)\s*\*\s*\d")
STAGGER = {"step_ms": 100, "max_total_ms": 600}


def stagger_findings(funcs) -> list:
    """batch_resolve_without_stagger: a loop over dice, cards or rewards fires feedback for every item in one frame."""
    where = []
    for rel, name, line, body in funcs:
        m = BATCH_LOOP_RX.search(body)
        if not m or STAGGER_RX.search(body):
            continue
        if BATCH_FEEDBACK_RX.search(body[m.end():]):
            where.append(f"{rel}:{line + body.count(chr(10), 0, m.start())} {name}")
    if not where:
        return []
    return [{
        "id": "batch_resolve_without_stagger", "severity": "low",
        "why": ("A loop over dice, cards or rewards plays its feedback for every item in the same frame, so five "
                "results read as one blur. Resolve them one at a time about 100 ms apart (cap the whole run near "
                "600 ms, or step faster for long runs), pop the running total on each step, and save the biggest "
                "response for the last item (P-03, P-11, P-23)."),
        "numbers": dict(STAGGER),
        "where": where[:8],
    }]


# --- reduce motion read where shake is applied (idea: a side-view vehicle game, technique-harvest 2026-11) ----
SHAKE_FUNC_NAME = re.compile(r"(?i)shake|trauma|camera|cam\b")
REDUCE_READ_RX = re.compile(PROJECT_CHECKS["reduce_motion_toggle"] + r"|reduced_?motion|motion_?scale|motionScale")
REDUCE_ASSIGN_RX = re.compile(r"\b(\w+)\s*(?:=|:)\s*[^;\n]*(?:" + PROJECT_CHECKS["reduce_motion_toggle"] + r")")


def reduce_motion_findings(texts, funcs, toggle_flags) -> list:
    """reduce_motion_not_applied: a reduce-motion setting exists, but no function that writes shake reads it."""
    if not toggle_flags:
        return []
    shakers = [(rel, name, line, body) for rel, name, line, body in funcs
               if SHAKE_CALL.search(body) or (SHAKE_FUNC_NAME.search(name) and re.search(r"[Ss]hake|trauma", body))]
    if not shakers:
        return []
    names = {m.group(1) for _, t in texts for m in REDUCE_ASSIGN_RX.finditer(t)} - {"var", "let", "const", "if"}
    alias = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b") if names else None
    for _, _, _, body in shakers:
        if REDUCE_READ_RX.search(body) or (alias and alias.search(body)):
            return []
    return [{
        "id": "reduce_motion_not_applied", "severity": "medium",
        "why": ("A reduce-motion or shake setting exists, but none of the functions that add or apply shake read it, so "
                "the setting does nothing in play. Read it where the shake offset is written: scale the amplitude by "
                "the setting (0 when reduce motion is on) (P-18, J12)."),
        "where": toggle_flags[:3] + [f"{r}:{ln} {n}" for r, n, ln, _ in shakers[:5]],
    }]


# --- audio pass (--audio; idea: a networked arena shooter, technique-harvest 2026-11) -------------------
PLAY_CALL_RX = re.compile(
    r"(?i)\b(?:play_?one_?shot|play_?clip_?at_?point|play_?sound|play_?sfx|sfx)\s*\(|(?<!anims)\.play\s*\(|"
    r"\b(?:src|source|osc\w*|node|voice)\.start\s*\(|:Play\(\)")
VOLUME_LIT_RX = re.compile(r"(?i)\b(?:volume|vol|gain(?:\.value)?)\s*(?:[:=]|\.setValueAtTime\(|\()\s*(\d*\.?\d+)\b"
                           r"|\bplay_?(?:sound|sfx)\s*\(\s*[\"'][^\"']*[\"']\s*,\s*(\d*\.?\d+)\b")
WORLD_HANDLER_RX = re.compile(r"(?i)enemy|remote|other|opponent|explo|world|spawn|impact|monster|npc|bot\b")
WORLD_ARGS_RX = re.compile(r"(?i)\b(?:play\w*|sfx)\s*\([^)]*\b(?:x|pos|position|global_position|transform\.position)\b")
DISTANCE_RX = re.compile(r"(?i)\bdist\w*|hypot|falloff|attenuat|rolloff|spatial|panner|AudioStreamPlayer[23]D|"
                         r"refDistance|maxDistance|max_distance|unit_size|\b1\s*-\s*d\s*/")
SPATIAL_PLAYER_RX = re.compile(r"createPanner|new PannerNode|AudioStreamPlayer[23]D|spatialBlend\s*=\s*1|\.pos\(|RollOffMode")
LOOPED_SET_RX = re.compile(r"\b([\w.$]+?)\.loop\s*=\s*(?:true|True)\b")
LOOPED_NAME_RX = re.compile(r"(?i)loop|engine|thrust|motor|hum\b|ambien|drone|wind\b|music|siren|alarm")
PLAYING_GUARD_RX = re.compile(r"(?i)is_?playing|\.playing\b|\.paused\b|playing\s*[!=]=|started\b|is_on\b|already|_active\b")
HANDLER_RX = re.compile(r"(?i)^(on_?message|onmessage|handle\w*message|on_?packet|on_?data|on_?state|on_?snapshot)$")
LOOP_PLAY_RX = re.compile(r"""([\w.$]+?)\s*\.\s*(?:play|Play|start)\s*\(|\$([\w/]+)\.play\(""")
TIERS = {"tiers": [0.18, 0.38], "falloff": "1 - d / r, r = half the larger screen side"}


def audio_scan(texts, funcs) -> dict:
    """List every play call with its literal volume and flag falloff, loop restarts and flat volumes."""
    plays, volumes = [], []
    for rel, text in texts:
        for i, line in enumerate(text.splitlines(), 1):
            if PLAY_CALL_RX.search(line):
                plays.append(f"{rel}:{i}")
            for m in VOLUME_LIT_RX.finditer(line):
                v = float(m.group(1) or m.group(2))
                if 0 <= v <= 4:
                    volumes.append((v, f"{rel}:{i}"))
    findings = []
    spatial = any(SPATIAL_PLAYER_RX.search(t) for _, t in texts)
    flat_world = []
    for rel, name, line, body in funcs:
        if not PLAY_CALL_RX.search(body):
            continue
        world = WORLD_HANDLER_RX.search(name) or WORLD_ARGS_RX.search(body)
        if world and not spatial and not DISTANCE_RX.search(body):
            flat_world.append(f"{rel}:{line} {name}")
    if flat_world:
        findings.append({
            "id": "audio_no_falloff", "severity": "medium",
            "why": ("Sounds from enemies, other players or world positions play at one volume however far away they are, "
                    "so a far shot is as loud as your own. Scale by distance: gain = base x max(0, 1 - d / r), r about "
                    "half the larger screen side, or use a 2D/3D spatial player."),
            "numbers": TIERS, "where": flat_world[:8],
        })
    looped = {m.group(1).split(".")[-1] for _, t in texts for m in LOOPED_SET_RX.finditer(t)}
    restarts = []
    for rel, name, line, body in funcs:
        short = name.split(".")[-1].split(":")[-1]
        if not (PER_FRAME.match(short) or HANDLER_RX.match(short)):
            continue
        for m in LOOP_PLAY_RX.finditer(body):
            target = (m.group(1) or m.group(2) or "").split(".")[-1].split("/")[-1]
            if (target in looped or LOOPED_NAME_RX.search(target)) and not PLAYING_GUARD_RX.search(body):
                restarts.append(f"{rel}:{line + body.count(chr(10), 0, m.start())} {name}")
                break
    if restarts:
        findings.append({
            "id": "audio_loop_restart", "severity": "medium",
            "why": ("A looped sound is started inside a per-frame or per-message function with no is-playing check, so it "
                    "restarts every frame and stutters. Keep a small state machine: start the ignition once on the edge, "
                    "then a sustain loop that keeps playing until the input ends."),
            "where": restarts[:8],
        })
    vals = [v for v, _ in volumes]
    if vals and (min(vals) >= 1.0 or (len(vals) >= 3 and max(vals) == min(vals))):
        findings.append({
            "id": "audio_no_headroom", "severity": "low",
            "why": ("Every literal effect volume is the same (or full scale), so nothing sits above anything else and "
                    "stacked effects clip. Tier them: frequent and remote effects about 0.18, your own weapon 0.24-0.28, "
                    "rare big moments 0.32-0.38, times a user slider per bus, leaving headroom for many at once."),
            "numbers": dict(TIERS, volumes=sorted(set(vals))),
            "where": [w for _, w in volumes[:8]],
        })
    return {"plays": plays[:60], "volumes": sorted(set(vals)), "findings": findings}


def to_markdown(r: dict) -> str:
    out = [f"# Juice scan: {os.path.basename(r['root'])}", "",
           f"Engine: **{r['engine']['engine']}** ({', '.join(r['engine']['evidence']) or 'no marker'}). "
           f"Files: {r['files_scanned']}, functions: {r['functions_seen']}. "
           f"Libraries: {', '.join(r['libraries']) or 'none found'}.", "",
           "| Moment | File | Function | Line | Has | Gaps | Conf. |", "|---|---|---|---|---|---|---|"]
    for m in r["moments"]:
        out.append(f"| {m['moment']} | {m['file']} | `{m['function']}` | {m['line']} | "
                   f"{', '.join(m['feedback']) or '-'} | {', '.join(m['gaps']) or '-'} | {m['confidence']} |")
    if r["findings"]:
        out += ["", "## Project findings", ""] + [f"- **{f['id']}** ({f['severity']}): {f['why']}" for f in r["findings"]]
    au = r.get("audio")
    if au:
        out += ["", "## Audio", "", f"{len(au['plays'])} play calls; literal volumes: "
                f"{', '.join(str(v) for v in au['volumes']) or 'none'}."]
        out += [f"- **{f['id']}** ({f['severity']}): {f['why']} ({', '.join(f['where'][:4])})" for f in au["findings"]]
    if r["risks"]:
        out += ["", "## Risks (possible over-juicing or bugs)", ""] + [
            f"- **{x['id']}** `{x['function']}` in {x['file']}:{x['line']}: {x['why']}" for x in r["risks"]]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--md", action="store_true", help="print a Markdown moment map instead of JSON")
    ap.add_argument("--out", help="also write the output to this file")
    ap.add_argument("--max-files", type=int, default=4000)
    ap.add_argument("--include-vendor", action="store_true", help="scan Plugins/, addons/, vendor/ too")
    ap.add_argument("--audio", action="store_true", help="add the audio pass: play calls, volumes, falloff, loop restarts, headroom")
    a = ap.parse_args(argv)
    try:
        if not os.path.isdir(a.root):
            raise FileNotFoundError(f"not a directory: {a.root}")
        result = scan(a.root, a.include_vendor, a.max_files, a.audio)
        text = to_markdown(result) if a.md else json.dumps(result, indent=2)
    except Exception as exc:  # fail soft
        text = json.dumps({"tool": "juice_scan.py", "version": VERSION, "error": f"{type(exc).__name__}: {exc}"})
    if a.out:
        try:
            with open(a.out, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as exc:
            sys.stderr.write(f"could not write {a.out}: {exc}\n")
    sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
