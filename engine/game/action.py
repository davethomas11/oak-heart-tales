from .game_state import GameState
from .combat import SPELLS

#__pragma__('skip')
import traceback
#__pragma__('noskip')

class Action:
    def __init__(
            self,
            id: str,
            label: str,
            hotkeys: list,
            category: str = "general",
            enabled: bool = True,
            reason: str = None
    ):
        self.id = id
        self.label = label
        self.hotkeys = hotkeys
        self.category = category
        self.enabled = enabled
        self.reason = reason

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "hotkeys": self.hotkeys,
            "category": self.category,
            "enabled": self.enabled,
            "reason": self.reason,
        }


class _Actions:
    """
    Decoupled actions provider/executor so any interface (CLI/Web/etc.) can query
    available actions and invoke them without hardcoding game logic.
    """

    def __init__(self, game) -> None:
        self.g = game
        # map action id -> callable returning text
        self._exec_map = {}
        # also map hotkeys to ids for convenience
        self._key_to_id = {}

    def available(self) -> list:
        g = self.g
        w = g.world
        x, y = g.x, g.y

        actions = []

        # Branch by game state
        if g.state == GameState.COMBAT:
            enemy = g.enemy
            # Combat actions
            actions.extend(
                [
                    Action("combat_attack", "Attack", ["attack", "a"], "combat"),
                    Action("combat_potion", "Use Potion", ["potion", "p"], "combat",
                           enabled=g.player.potions > 0,
                           reason=None if g.player.potions > 0 else "No potions"),
                    Action("combat_flee", "Flee", ["flee", "run", "f"], "combat"),
                    Action("look", "Examine Enemy", ["look", "l"], "combat"),
                    Action("stats", "Stats", ["stats", "s"], "combat"),
                ]
            )
            # Spells known/affordable become actions
            for sp in g.player.known_spells:
                if sp in SPELLS:
                    cost = int(SPELLS[sp]["mp"])
                    actions.append(
                        Action(
                            id=f"cast::{sp.lower()}",
                            label=f"Cast {sp} (MP {cost})",
                            hotkeys=[f"cast {sp}".lower()],
                            category="combat",
                            enabled=g.player.mp >= cost,
                            reason=None if g.player.mp >= cost else "Not enough MP",
                        )
                    )


            # Build exec map for combat
            self._exec_map = {
                "combat_attack": g.combat_attack,
                "combat_potion": g.combat_potion,
                "combat_flee": g.combat_flee,
                "look": g.look,
                "stats": g.stats,
            }
            # Add cast actions
            for sp in g.player.known_spells:
                if sp in SPELLS:
                    self._exec_map[f"cast::{sp.lower()}"] = (lambda s=sp: g.combat_cast(s))
        elif g.state == GameState.GAME_OVER:
            # Game over actions
            actions.extend(
                [
                    Action("game_over_load", "Load Game", ["load", "l"], "game_over"),
                    Action("game_over_restart", "Restart Game", ["restart", "r"], "game_over"),
                ]
            )
            # Build exec map for game over
            self._exec_map = {
                "game_over_load": g.load_game,
                "game_over_restart": g.restart_game,
            }
        elif g.state == GameState.SHOP:
            shop = g.shop_items

            # Shop actions
            index = 1
            for item in shop.keys():
                actions.append(
                    Action(
                        id=f"shop_buy::{item}",
                        label=f"Buy {item} (Gold {shop[item]})",
                        hotkeys=[f"buy {item}".lower(), f"{index}", item],
                        category="shop"
                    )
                )
                index += 1
            actions.append(Action("shop_exit", "Exit Shop", ["exit", "e"], "shop"))
            actions.append(Action("look", "View Shop", ["look", "l"], "shop"))
            actions.append(Action("stats", "Stats", ["stats", "s"], "shop"))
            # Build exec map for shop
            self._exec_map = {
                # **{f"shop_buy::{item.lower()}": (lambda it=item: g.shop(it)) for item in shop.keys()},
                "shop_exit": g.shop_exit,
                "look": g.look,
                "stats": g.stats,
            }
            for item in shop.keys():
                self._exec_map[f"shop_buy::{item.lower()}"] = (lambda it=item: g.shop(it))


        elif g.state == GameState.START_MENU:
            # Start menu actions
            actions.extend(
                [
                    Action("start_new_game", "New Game", ["new", "n"], "start_menu"),
                    Action("start_load_game", "Load Game", ["load", "l"], "start_menu"),
                    Action("start_quit", "Quit", ["quit", "q"], "start_menu"),
                ]
            )
            # Build exec map for start menu
            self._exec_map = {
                "start_new_game": g.start_new_game,
                "start_load_game": g.start_load_game,
                "start_quit": g.start_quit,
            }
        elif g.state == GameState.ASKING_QUESTION:
            actions.extend([
                Action("answer_yes", "Yes", ["yes", "y"], "question"),
                Action("answer_no", "No", ["no", "n"], "question"),
                Action("look", "Examine", ["look", "l"], "question"),
                Action("stats", "Stats", ["stats", "s"], "question"),
            ])
            self._exec_map = {
                "answer_yes": lambda: g.execute_question(True),
                "answer_no": lambda: g.execute_question(False),
                "look": g.look,
                "stats": g.stats,
            }
        else:
            # Exploration/default actions
            # Movement actions (n,s,e,w), disabled at edges with reason
            def can_go(nx: int, ny: int) -> (bool, str):
                if nx < 0 or ny < 0 or nx >= w.width or ny >= w.height:
                    return False, "Edge of the world"
                return True, None

            dirs = [
                ("move_n", "North", "travel", (0, -1), ["n", "north", "ArrowUp"]),
                ("move_s", "South", "travel", (0, 1), ["s", "south", "ArrowDown"]),
                ("move_w", "West", "travel", (-1, 0), ["w", "west", "ArrowLeft", "a"]),
                ("move_e", "East", "travel", (1, 0), ["e", "east", "ArrowRight", "d"]),
            ]
            for aid, label, cat, (dx, dy), keys in dirs:
                ok, reason = can_go(x + dx, y + dy)
                actions.append(Action(id=aid, label=label, hotkeys=keys, category=cat, enabled=ok, reason=reason))

            # Basic actions
            actions.extend(
                [
                    Action("look", "Look", ["look", "l"], "info"),
                    Action("map", "Map", ["map", "m"], "info"),
                    Action("stats", "Stats", ["stats", "character", "c"], "info"),
                    Action("rest", "Rest", ["rest", "r"], "camp"),
                    Action("shop", "Shop", ["shop"], "town", enabled=bool(getattr(g.current_tile(), "shop", False)),
                           reason=None if getattr(g.current_tile(), "shop", False) else "No merchant here"),
                    Action("inventory", "Inventory", ["inv", "inventory", "i"], "info"),
                ]
            )

            # Build exec map for exploration
            self._exec_map = {
                "move_n": lambda: g.move(0, -1),
                "move_s": lambda: g.move(0, 1),
                "move_w": lambda: g.move(-1, 0),
                "move_e": lambda: g.move(1, 0),
                "look": g.look,
                "map": g.map,
                "stats": g.stats,
                "rest": g.rest,
                "shop": g.shop_enter,
                "inventory": lambda: f"Inventory: Potions x{g.player.potions}; Gold {g.player.gold}",
            }

        actions.extend(
            [
                Action("save_game", "Save Game", ["save", "!"], "system"),
                Action("help", "Help", ["help", "h", "?"], "system"),
                Action("quit_game", "Quit Game", ["quit", "q"], "system"),
                Action("log", "Show Log", ["log", "g"], "system"),
            ]
        )

        self._exec_map.update({
            "save_game": g.save_game,
            "help": g.help_text,
            "quit_game": g.quit_game,
            "log": g.get_log,
        })

        # Map hotkeys for quick execute
        self._key_to_id = {}
        for a in actions:
            for k in a.hotkeys:
                self._key_to_id[k.lower()] = a.id

        # Return simple dicts for portability/serialization
        return [a.to_dict() for a in actions]

    def execute(self, action_id_or_key: str) -> str:
        if not action_id_or_key:
            return None
        key = action_id_or_key.strip().lower()
        # Ensure command maps are built for current state
        if not self._exec_map:
            self.available()
        aid = key
        if aid not in self._exec_map:
            aid = self._key_to_id.get(key, key)
        fn = self._exec_map.get(aid)
        if not fn:
            return None
        try:
            return fn()
        except Exception:
            reason = ""
            #__pragma__('skip')
            reason = traceback.format_exc()
            #__pragma__('noskip')
            return f"Action '{aid}' failed: \n{reason}"