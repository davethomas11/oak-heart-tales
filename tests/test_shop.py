from engine.game.shop import Shop
import unittest

class TestShop(unittest.TestCase):
    class DummyPlayer:
        def __init__(self):
            self.known_spells = []
            self.weapon = None
            self.armor = None
            self.gold = 100
            self.potions = 0

    class DummyEventManager:
        def __init__(self):
            self.events = []
        def emit(self, event):
            self.events.append(event)

    def setUp(self):
        self.player = self.DummyPlayer()
        self.event_manager = self.DummyEventManager()
        self.shop = Shop(self.player, self.event_manager)
        self.shop.set_shop_items(["Firebolt"], ["Wooden Sword"], ["Dragon Scale Mail"])

    def test_shop_show_items(self):
        result = self.shop.shop("")
        self.assertIn("Merchant's Caravan", result)
        self.assertIn("Potion", result)

    def test_shop_buy_spell(self):
        self.player.gold = 100
        result = self.shop.shop("Firebolt")
        self.assertIn("You acquire the spell Firebolt", result)
        self.assertIn("Firebolt", self.player.known_spells)

    def test_shop_buy_weapon(self):
        self.player.gold = 100
        result = self.shop.shop("Wooden Sword")
        self.assertIn("You acquire the weapon Wooden Sword", result)
        self.assertEqual(self.player.weapon.name, "Wooden Sword")

    def test_shop_buy_armor(self):
        self.player.gold = 100
        result = self.shop.shop("Dragon Scale Mail")
        self.assertIn("You acquire the armor Dragon Scale Mail", result)
        self.assertEqual(self.player.armor.name, "Dragon Scale Mail")

    def test_shop_buy_potion(self):
        self.player.gold = 100
        result = self.shop.shop("Potion")
        self.assertIn("You acquire the potion Potion", result)
        self.assertEqual(self.player.potions, 1)

    def test_shop_not_enough_gold(self):
        self.player.gold = 0
        result = self.shop.shop("Firebolt")
        self.assertIn("You don't have enough gold", result)

    def test_shop_item_not_found(self):
        result = self.shop.shop("Nonexistent")
        self.assertIn("I don't have that", result)

if __name__ == "__main__":
    unittest.main()