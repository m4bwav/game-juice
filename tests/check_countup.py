"""Tests for juice-apply's countup_plan.py. Run: python tests/check_countup.py"""
import pathlib, sys, unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "skills" / "juice-apply" / "scripts"))
import countup_plan as cp  # noqa: E402


def stage(p, name):
    return next(s for s in p["stages"] if s["stage"] == name)


class CountupPlan(unittest.TestCase):
    def test_tiers_and_lengths(self):
        self.assertEqual(stage(cp.plan(52, 460), "count_up")["ms"], 300)
        self.assertEqual(stage(cp.plan(256), "count_up")["ms"], 600)
        self.assertEqual(stage(cp.plan(1824, 2000), "count_up")["ms"], 600)
        self.assertEqual(stage(cp.plan(600, 150), "count_up")["ms"], 900)  # overkill bumps a tier
        self.assertEqual(cp.tier(10 ** 6, 1), 3)  # capped
        self.assertEqual(stage(cp.plan(0), "count_up")["ms"], 0)

    def test_frames_rise_and_ease(self):
        f = stage(cp.plan(1000, frames=True, fps=60), "count_up")["frames"]
        self.assertEqual(f, sorted(f))
        self.assertEqual(f[-1], 1000)
        self.assertAlmostEqual(cp.ease_out_quart(0.5), 0.9375)

    def test_stagger_floor_and_cap(self):
        p = cp.plan(500, components=[10] * 12)
        at = [s["at_ms"] for s in p["stages"] if s["stage"] == "component"]
        self.assertTrue(all(b - a >= 89 for a, b in zip(at, at[1:])))
        big = cp.plan(5000, components=[1] * 200)
        self.assertLessEqual(big["total_ms"], 6000)
        self.assertLess(big["stagger_scale"], 1)

    def test_trauma(self):
        self.assertEqual(cp.trauma(5), 0.12)
        self.assertEqual(cp.trauma(10 ** 9), 1.0)

    def test_trigger_ramp_and_tally(self):
        r = cp.trigger_ramp(10)
        pitches = [e["pitch"] for e in r]
        self.assertTrue(all(b > a for a, b in zip(pitches, pitches[1:])))
        self.assertEqual(pitches[0], 0.86)
        self.assertEqual(cp.trigger_ramp(10)[0]["pitch"], 0.86)  # reset per resolution
        self.assertLessEqual(cp.trigger_ramp(200)[-1]["t_ms"], 6000)
        self.assertEqual([t["pitch"] for t in cp.tally_rows(3)], [0.95, 1.01, 1.07])


if __name__ == "__main__":
    unittest.main()
