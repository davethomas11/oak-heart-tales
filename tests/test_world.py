import unittest

from world import World


class TestWorld(unittest.TestCase):
    def test_generate_random_basic(self):
        size = 5
        seed = 12345
        w = World.generate_random(size=size, seed=seed)
        self.assertEqual(w.width, size)
        self.assertEqual(w.height, size)
        # Center tile is safe village
        cx, cy = size // 2, size // 2
        center = w.get(cx, cy)
        self.assertTrue(center.safe)
        # All tiles have danger within [0.0, 0.8]
        for y in range(size):
            for x in range(size):
                t = w.get(x, y)
                self.assertGreaterEqual(t.danger, 0.0)
                self.assertLessEqual(t.danger, 0.8)

    def test_deterministic_with_seed(self):
        size = 5
        seed = 999
        w1 = World.generate_random(size=size, seed=seed)
        w2 = World.generate_random(size=size, seed=seed)
        self.assertEqual(w1.to_dict(), w2.to_dict())

    def test_danger_increases_on_average_with_distance(self):
        size = 9
        seed = 42
        w = World.generate_random(size=size, seed=seed)
        cx, cy = size // 2, size // 2
        # Average danger for tiles at manhattan distance 1 vs 2
        d1 = []
        d2 = []
        for y in range(size):
            for x in range(size):
                dist = abs(x - cx) + abs(y - cy)
                if dist == 1:
                    d1.append(w.get(x, y).danger)
                elif dist == 2:
                    d2.append(w.get(x, y).danger)
        self.assertTrue(len(d1) > 0 and len(d2) > 0)
        self.assertGreaterEqual(sum(d2) / len(d2), sum(d1) / len(d1))


if __name__ == "__main__":
    unittest.main()
