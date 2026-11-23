"""countup_plan.py: the timeline of a staged score reveal (P-08), as JSON, for a value and its parts.

Stages: each component pops in with a decaying stagger, a short gather beat, the total counts up with a quartic
ease-out whose length grows by size tier, a hit-stop and shake scaled by tier, then the target's health readout
counts down while a ghost bar catches up. The whole timeline is compressed to fit a cap so long combos never drag.

Usage:
  countup_plan.py --value N [--target HP] [--components a,b,c] [--fps 60] [--cap-ms 6000] [--frames]
                  [--triggers N] [--tally-rows N]

--triggers N adds a chained-trigger pitch ramp (one resolution, reset per call); --tally-rows N adds tally
row pitches.

Numbers come from a measured technique harvest of a shipped game (2026-11-21) and are defaults, not
rules: tune them in the game. Standard-library Python 3.8+. Prints one JSON object.
"""
import argparse, json, math, sys

TIERS = (150, 2500, 40000)          # below each bound: tier 0, 1, 2; above the last: tier 3
BASE_MS, PER_TIER_MS = 300, 300     # count-up length = 300 ms + 300 ms per tier
HITSTOP_MS = (40, 90, 160, 320)
STAGGER_MS, STAGGER_DECAY, STAGGER_FLOOR_MS = 240, 0.93, 90
GATHER_MS = 260
HEALTH_MS, GHOST_DELAY_MS = 500, 380
RAMP_BASE, RAMP_STEP, JIGGLE_DECAY = 0.86, 0.016, 5.0  # pitch per trigger rises ~1.5%; jiggle decays at 5/s
TALLY_BASE, TALLY_STEP = 0.95, 0.06


def trigger_ramp(n, base=RAMP_BASE, cap_ms=6000):
    """Pitch ramp for n chained triggers inside one resolution. Starts fresh on every call (reset per resolution)."""
    waits = [max(STAGGER_FLOOR_MS, STAGGER_MS * STAGGER_DECAY ** i) for i in range(n)]
    scale = min(1.0, cap_ms / sum(waits)) if waits else 1.0
    out, now = [], 0.0
    for i, w in enumerate(waits):
        out.append({"i": i, "t_ms": round(now), "pitch": round(base * (1 + RAMP_STEP * i), 4),
                    "jiggle_add": 1.0, "jiggle_decay_per_s": JIGGLE_DECAY})
        now += w * scale
    return out


def tally_rows(n):
    return [{"row": i, "pitch": round(TALLY_BASE + TALLY_STEP * i, 4)} for i in range(n)]


def tier(value, target=None):
    t = sum(value >= b for b in TIERS)
    if target and value >= 150 and value >= 3 * target:  # overkill reads one size bigger
        t += 1
    return min(t, 3)


def ease_out_quart(x):
    return 1 - (1 - x) ** 4


def trauma(value):
    if value <= 0:
        return 0.0
    return round(min(max((math.log10(value) - 1.2) / 6.2, 0.12), 1.0), 3)


def plan(value, target=None, components=(), fps=60, cap_ms=6000, frames=False):
    t = tier(value, target)
    count_ms = 0 if value <= 0 else BASE_MS + PER_TIER_MS * t
    waits = [max(STAGGER_FLOOR_MS, STAGGER_MS * STAGGER_DECAY ** i) for i in range(len(components))]
    fixed = (GATHER_MS if components else 0) + count_ms + HITSTOP_MS[t] + HEALTH_MS
    scale = 1.0
    if waits and sum(waits) + fixed > cap_ms:  # shorten only the staggers, so every stage stays readable
        scale = max(cap_ms - fixed, 0) / sum(waits)
    stages, now = [], 0.0
    for c, w in zip(components, waits):
        stages.append({"stage": "component", "value": c, "at_ms": round(now)})
        now += w * scale
    if components:
        stages.append({"stage": "gather", "at_ms": round(now), "ms": GATHER_MS})
        now += GATHER_MS
    count = {"stage": "count_up", "at_ms": round(now), "ms": count_ms, "ease": "quartic ease-out", "tier": t}
    if frames and count_ms:
        n = max(1, round(count_ms * fps / 1000))
        count["frames"] = [round(value * ease_out_quart(k / n)) for k in range(1, n + 1)]
    stages.append(count)
    now += count_ms
    stages.append({"stage": "hit_stop", "at_ms": round(now), "ms": HITSTOP_MS[t], "trauma": trauma(value)})
    now += HITSTOP_MS[t]
    stages.append({"stage": "health", "at_ms": round(now), "ms": HEALTH_MS, "ghost_at_ms": round(now + GHOST_DELAY_MS)})
    now += HEALTH_MS
    return {"value": value, "target": target, "tier": t, "stagger_scale": round(scale, 3),
            "total_ms": round(now), "stages": stages}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--value", type=float, required=True)
    ap.add_argument("--target", type=float)
    ap.add_argument("--components", default="")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--cap-ms", type=int, default=6000)
    ap.add_argument("--frames", action="store_true", help="list the shown value for every frame of the count-up")
    ap.add_argument("--triggers", type=int, default=0, help="emit a chained-trigger pitch ramp for N triggers")
    ap.add_argument("--tally-rows", type=int, default=0, help="emit rising pitches for N tally rows")
    a = ap.parse_args(argv)
    comps = [float(x) for x in a.components.split(",") if x.strip()]
    out = plan(a.value, a.target, comps, a.fps, a.cap_ms, a.frames)
    if a.triggers:
        out["trigger_ramp"] = trigger_ramp(a.triggers, cap_ms=a.cap_ms)
    if a.tally_rows:
        out["tally_rows"] = tally_rows(a.tally_rows)
    json.dump(out, sys.stdout)
    print()


if __name__ == "__main__":
    main()
