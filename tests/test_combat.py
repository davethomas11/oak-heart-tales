import unittest
import random

from combat import calc_damage, generate_enemy, depth_from_pos


class TestCombat(unittest.TestCase):
    def test_calc_damage_bounds(self):
        # Try a range of atk/def values and ensure damage is at least 1 and not absurdly high
        for atk in range(1, 15):
            for df in range(0, 10):
                # run multiple trials due to randomness
                for _ in range(20):
                    dmg = calc_damage(atk, df)
                    self.assertGreaterEqual(dmg, 1)
                    # Upper bound: base + 2 (per implementation); base may be negative but upper should be <= atk - df + 2
                    self.assertLessEqual(dmg, max(1, atk - df + 2))

    def test_generate_enemy_level_bounds(self):
        random.seed(123)
        pl = 4
        x, y = 2, 3
        e = generate_enemy(pl, x, y)
        depth = depth_from_pos(x, y)
        self.assertGreaterEqual(e.level, 1)
        self.assertLessEqual(e.level, pl + 3)
        self.assertIn("Lv", e.name)
        self.assertGreater(e.max_hp, 0)
        self.assertEqual(e.hp, e.max_hp)
        self.assertGreater(e.attack, 0)
        self.assertGreaterEqual(e.defense, 0)
        self.assertGreater(e.xp_reward, 0)
        self.assertGreater(e.gold_reward, 0)


if __name__ == "__main__":
    unittest.main()
