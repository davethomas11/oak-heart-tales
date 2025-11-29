import unittest

from engine.game.player import clamp, xp_to_next_level, Player


class TestModels(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-1, 0, 10), 0)
        self.assertEqual(clamp(11, 0, 10), 10)

    def test_xp_curve_increases(self):
        vals = [xp_to_next_level(l) for l in range(1, 6)]
        # strictly increasing
        self.assertTrue(all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)))

    def test_player_heal_clamps(self):
        p = Player(name="Hero", level=1, hp=10, max_hp=20, mp=10, max_mp=10, attack=5, defense=5, potions=0, known_spells=[], gold=0, weapon=None, armor=None)
        healed = p.heal(15)
        self.assertEqual(healed, 10)  # goes to 20
        self.assertEqual(p.hp, 20)
        healed = p.heal(-50)
        self.assertEqual(p.hp, 0)

    def test_level_up_increases_stats_and_resets_hp(self):
        p = Player(name="Hero", level=1, hp=20, max_hp=20, mp=10, max_mp=10, attack=5, defense=5, potions=0, known_spells=[], gold=0, weapon=None, armor=None)
        # Give enough XP for at least one level
        need = xp_to_next_level(p.level)
        notes = p.add_xp(need)
        self.assertTrue(any("Level up!" in n for n in notes))
        self.assertGreaterEqual(p.level, 2)
        self.assertEqual(p.hp, p.max_hp)


if __name__ == "__main__":
    unittest.main()
