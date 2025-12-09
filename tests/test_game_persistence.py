import unittest

from engine.game import Game


class TestGamePersistence(unittest.TestCase):
    def test_round_trip(self):
        tiles = {
            "village": {"name": "Test Village", "description": "A test village.", "danger": 0.0, "safe": True, "ascii": "."},
            "tiles": [
                {"name": "Plains", "description": "Open plains.", "danger": 0.1, "safe": False, "ascii": "."},
                {"name": "Forest", "description": "Dense forest.", "danger": 0.3, "safe": False, "ascii": "."},
                {"name": "Mountain", "description": "Rocky mountain.", "danger": 0.5, "safe": False, "ascii": "."},
            ],
        }
        g1 = Game.new_random(size=5, tileset=tiles)
        # mutate some player fields predictably
        p = g1.player
        p.name = "Tester"
        p.gold = 42
        p.potions = 3
        # move position within bounds
        g1.x = 1
        g1.y = 2

        data = g1.to_dict()
        g2 = Game.from_dict(data)

        self.assertEqual(g2.player.name, "Tester")
        self.assertEqual(g2.player.gold, 42)
        self.assertEqual(g2.player.potions, 3)
        self.assertEqual(g2.x, 1)
        self.assertEqual(g2.y, 2)
        # World dimensions preserved
        self.assertEqual(g2.world.width, g1.world.width)
        self.assertEqual(g2.world.height, g1.world.height)


if __name__ == "__main__":
    unittest.main()
