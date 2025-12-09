# test_engine_game_action.py

import unittest
from unittest.mock import MagicMock

from engine.game.action import Action, _Actions
from engine.game.game_state import GameState

class DummyPlayer:
    def __init__(self):
        self.potions = 2
        self.known_spells = ["Firebolt", "Heal"]
        self.hp = 30
        self.max_hp = 30
        self.mp = 10
        self.gold = 50

class DummyWorld:
    width = 5
    height = 5

class DummyGame:
    def __init__(self):
        self.state = GameState.COMBAT
        self.player = DummyPlayer()
        self.enemy = MagicMock()
        self.world = DummyWorld()
        self.x = 2
        self.y = 2
        self.shop_items = {"Potion": 10}
        self.shop = MagicMock()
        self.combat_attack = MagicMock(return_value="attack")
        self.combat_potion = MagicMock(return_value="potion")
        self.combat_flee = MagicMock(return_value="flee")
        self.look = MagicMock(return_value="look")
        self.stats = MagicMock(return_value="stats")
        self.spells = MagicMock(return_value="spells")
        self.rest = MagicMock(return_value="rest")
        self.map = MagicMock(return_value="map")
        self.shop_enter = MagicMock(return_value="shop_enter")
        self.current_tile = MagicMock(return_value=MagicMock(shop=True))
        self.save_game = MagicMock(return_value="save")
        self.help_text = MagicMock(return_value="help")
        self.quit_game = MagicMock(return_value="quit")
        self.get_log = MagicMock(return_value="log")
        self.load_game = MagicMock(return_value="load")
        self.restart_game = MagicMock(return_value="restart")
        self.start_new_game = MagicMock(return_value="new_game")
        self.start_load_game = MagicMock(return_value="start_load")
        self.start_quit = MagicMock(return_value="start_quit")
        self.execute_question = MagicMock(return_value="answered")

class TestAction(unittest.TestCase):
    def test_to_dict(self):
        a = Action("id", "label", ["k"], "cat", False, "reason")
        d = a.to_dict()
        self.assertEqual(d["id"], "id")
        self.assertEqual(d["label"], "label")
        self.assertEqual(d["hotkeys"], ["k"])
        self.assertEqual(d["category"], "cat")
        self.assertFalse(d["enabled"])
        self.assertEqual(d["reason"], "reason")

class TestActions(unittest.TestCase):
    def setUp(self):
        self.g = DummyGame()
        self.g.shop_exit = lambda : "shop_exit"
        self.actions = _Actions(self.g)

    def test_available_combat(self):
        self.g.state = GameState.COMBAT
        acts = self.actions.available()
        ids = [a["id"] for a in acts]
        self.assertIn("combat_attack", ids)
        self.assertIn("combat_potion", ids)
        self.assertIn("combat_flee", ids)
        self.assertIn("cast::firebolt", ids)
        self.assertIn("cast::heal", ids)

    def test_available_shop(self):
        self.g.state = GameState.SHOP
        acts = self.actions.available()
        ids = [a["id"] for a in acts]
        self.assertIn("shop_buy::potion", ids)
        self.assertIn("shop_exit", ids)
        self.assertIn("inventory", ids)

    def test_available_exploration(self):
        self.g.state = None
        acts = self.actions.available()
        ids = [a["id"] for a in acts]
        self.assertIn("move_n", ids)
        self.assertIn("look", ids)
        self.assertIn("inventory", ids)

    def test_execute_by_id(self):
        self.g.state = GameState.COMBAT
        self.actions.available()
        result = self.actions.execute("combat_attack")
        self.assertEqual(result, "attack")

    def test_execute_by_hotkey(self):
        self.g.state = GameState.COMBAT
        self.actions.available()
        result = self.actions.execute("a")
        self.assertEqual(result, "attack")

    def test_execute_invalid(self):
        self.g.state = GameState.COMBAT
        self.actions.available()
        result = self.actions.execute("not_an_action")
        self.assertIsNone(result)

    def test_execute_exception(self):
        self.g.state = GameState.COMBAT
        self.actions.available()
        self.actions._exec_map["combat_attack"] = MagicMock(side_effect=Exception("fail"))
        result = self.actions.execute("combat_attack")
        self.assertIn("Action 'combat_attack' failed", result)

if __name__ == "__main__":
    unittest.main()