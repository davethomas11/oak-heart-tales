import random
from dataclasses import asdict
from typing import List, Optional

from models import Player, Weapon, Armor, clamp, xp_to_next_level
from world import World, Tile
from combat import generate_enemy, SPELLS, calc_damage
from ascii_renderer import render_room
from game.util import _hp_line, _clamp_int, _enemy_defense_effect
from game.game_state import GameState
from game.action import _Actions
from persistence import save_game as save, SAVE_FILE
from game.game_log import GameLog

class Game:
    def __init__(self, world: World, player: Player, x: int, y: int):
        self.world = world
        self.player = player
        self.x = x
        self.y = y
        # Track explored tiles as a set of (x, y)
        self.explored = set()  # type: ignore[var-annotated]
        # Mark starting position as explored
        self._mark_explored(self.x, self.y)
        # Actions interface for UIs
        self.actions = _Actions(self)
        # Game state & combat fields
        self.state: str = GameState.EXPLORING
        self.enemy = None  # type: ignore[assignment]
        self._combat_log: List[str] = []
        self._player_regen_turns: int = 0
        self._player_regen_amount: int = 0
        self._enemy_stunned_turns: int = 0
        self._enemy_def_down: int = 0
        self._enemy_def_turns: int = 0
        self.pending_move = None
        self.question = ""
        self.found_weapon = None
        self.ended = False
        self.log = GameLog()
        self.shop_items = None
        self.save_file = SAVE_FILE

    @staticmethod
    def new_random(size: int) -> "Game":
        w = World.generate_random(size=size)
        # Start in center
        cx = w.width // 2
        cy = w.height // 2
        return Game(
            world=w,
            player=Player(
                name="Hero",
                level=1,
                xp=0,
                gold=50,
                max_hp=20,
                hp=20,
                max_mp=10,
                mp=10,
                attack=5,
                defense=2,
                potions=1,
                known_spells=[],
                weapon=Weapon(name="Wooden Sword", attack_bonus=2),
                armor=Armor(name="Cloth Armor", defense_bonus=1)
            ),
            x=cx,
            y=cy
        )

    def help_text(self) -> str:
        actions = self.available_actions()
        lines = ["Available actions:"]
        for act in actions:
            label = act.get("label", act.get("id", ""))
            hotkeys = f" [{', '.join(act.get('hotkeys', []))}]" if act.get("hotkeys") else ""
            enabled = "" if act.get("enabled", True) else " (disabled)"
            reason = f" — {act['reason']}" if not act.get("enabled", True) and act.get("reason") else ""
            lines.append(f"  - {label}{hotkeys}{enabled}{reason}")
        return "\n".join(lines)

    def get_log(self) -> str:
        return f"{self.log}"

    def save_game(self, filename: str = None) -> str:
        file = filename if filename else self.save_file
        save(self.to_dict(), file)
        message = f"Game saved to {file}."
        return message

    def restart_game(self) -> str:
        fresh = Game.new_random(size=self.world.get_size())
        self.copy_from(fresh)
        message = "Game restarted."
        return message

    def load_game(self, filename: str = None) -> str:
        from persistence import load_game
        loaded = load_game(filename if filename else self.save_file)
        if loaded:
            self.copy_from(Game.from_dict(loaded))
            message = "Game loaded."
        else:
            message = "No save found or save file invalid."
        return message

    def quit_game(self) -> str:
        self.ended = True
        message = "Game ended by player."
        return message

    def current_tile(self) -> Tile:
        return self.world.get(self.x, self.y)

    def execute_question(self, answer: bool) -> str:
        if self.state != GameState.ASKING_QUESTION or not hasattr(self, "pending_move"):
            return "No question pending."
        if self.pending_move:
            return self.execute_pending_move(answer)
        else:
            return "No question pending."

    def move(self, dx: int, dy: int, ask: bool = True) -> str:
        self.log.add_entry(f"Attempting to move from ({self.x},{self.y}) by delta ({dx},{dy})")
        nx = clamp(self.x + dx, 0, self.world.width - 1)
        ny = clamp(self.y + dy, 0, self.world.height - 1)
        if nx == self.x and ny == self.y:
            return "You can't go that way."

        # Before moving, warn the player if the destination is very dangerous
        dest_tile = self.world.get(nx, ny)
        try:
            danger_threshold = 0.6  # warn for risky areas
            if (not dest_tile.safe and dest_tile.danger >= danger_threshold) and ask:
                self.change_state(GameState.ASKING_QUESTION)
                self.pending_move = (nx, ny)
                self.question = f"Warning: '{dest_tile.name}' seems very dangerous (danger {dest_tile.danger:.2f}). Proceed? [y/N]"
                return self.question
        except Exception:
            # If anything goes wrong with prompting, just continue the move
            pass

        self.change_state(GameState.EXPLORING)
        self.x, self.y = nx, ny
        # mark explored when arriving
        self._mark_explored(self.x, self.y)
        tile = self.current_tile()
        art = render_room(tile)
        desc = f"{art}\nYou arrive at {tile.name}. {tile.description}"
        if tile.shop:
            desc += "\nYou see a merchant here (type shop to enter)."

        # Roll encounter -> switch to action-driven combat
        if not tile.safe and random.random() < tile.danger:
            enemy = generate_enemy(self.player.level, self.x, self.y)
            intro = self.enter_combat(enemy)
            return desc + "\n\n" + intro
        # Field find chance (can find gear lying around)
        try:
            found = self._maybe_field_find(tile)
            if found:
                desc += "\n\n" + found
        except Exception:
            pass
        return desc

    def execute_pending_move(self, confirm: bool) -> str:
        if self.state != GameState.ASKING_QUESTION or not hasattr(self, "pending_move"):
            return "No move pending confirmation."
        if confirm:
            nx, ny = self.pending_move
            del self.pending_move
            self.change_state(GameState.EXPLORING)
            return self.move(nx - self.x, ny - self.y, ask=False)
        else:
            del self.pending_move
            self.change_state(GameState.EXPLORING)
            return "You decide not to proceed there."

    def look(self) -> str:
        if self.state == GameState.COMBAT:
            return self._combat_status()
        if self.state == GameState.SHOP:
            return self.shop()
        if self.state == GameState.ASKING_QUESTION:
            return self.question
        if self.state == GameState.GAME_OVER:
            return "Game Over. You can load a saved game or restart."
        t = self.current_tile()
        art = render_room(t)
        return f"{art}\n{t.name}: {t.description} \n{'You see a merchant here (type shop to enter).' if t.shop else ''}"

    # --- Actions facade for interfaces ---
    def available_actions(self) -> List[dict]:
        """
        Return a simple, serializable list of available actions for the current state.
        Each item contains: id, label, enabled, reason (optional), category, hotkeys.
        """
        return self.actions.available()

    def execute_action(self, action_id_or_key: str) -> Optional[str]:
        """Execute an action by id or key; returns output text or None if unknown."""
        log = self.actions.execute(action_id_or_key)
        self.log.add_entry(log)
        return log

    def _mark_explored(self, x: int, y: int) -> None:
        try:
            self.explored.add((int(x), int(y)))
        except Exception:
            # Be resilient to any odd inputs
            pass

    def map(self) -> str:
        # Render a simple ASCII map of explored tiles
        rows = []
        for y in range(self.world.height):
            line_chars = []
            for x in range(self.world.width):
                if x == self.x and y == self.y:
                    ch = "@"  # player
                elif (x, y) in self.explored:
                    ch = "."  # explored
                else:
                    ch = "?"  # unexplored
                line_chars.append(ch)
            rows.append("".join(line_chars))
        title = f"Map ({self.world.width}x{self.world.height}) — @ you, . explored, ? unknown"
        return title + "\n" + "\n".join(rows)

    def stats(self) -> str:
        p = self.player
        return (
            f"{p.name} Lv {p.level}\n"
            f"XP: {p.xp}/{xp_to_next_level(p.level)} | Gold: {p.gold}\n"
            f"HP: {p.hp}/{p.max_hp} | MP: {p.mp}/{p.max_mp} | ATK: {p.attack} | DEF: {p.defense} | Potions: {p.potions} | Spells: {len([s for s in p.known_spells if s in SPELLS])}"
            f"\nWeapon: {p.weapon if p.weapon else 'None'}\nArmor: {p.armor if p.armor else 'None'}"
            f"\nSpells Known: {', '.join(p.known_spells) if p.known_spells else 'None'}"
            f"\nLocation: ({self.x},{self.y}) - {self.current_tile().name}"
            f"\nState: {self.state}"
        )

    def shop_exit(self) -> str:
        self.change_state(GameState.EXPLORING)
        return "You leave the shop.\n" + self.look()

    def shop_enter(self) -> str:
        return "You enter the shop!\n" + self.shop()

    def shop(self, selection: Optional[str] = None) -> str:

        tile = self.current_tile()
        if not getattr(tile, "shop", False):
            return "There is no shop here."
        spells = {
            "Firebolt": 25,
            "Heal": 30,
            "Ice Shard": 45,
            "Shock": 40,
            "Regen": 35,
            "Guard Break": 30,
        }
        available = [s for s in spells.keys() if s in SPELLS and s not in self.player.known_spells]
        self.shop_items = {s: spells[s] for s in available}
        self.change_state(GameState.SHOP)

        if not available:
            return "The merchant smiles: 'You've learned all I can teach you for now.'"
        if selection is None:
            lines = ["\nMerchant's Caravan — Spells for sale:"]
            for idx, name in enumerate(available, 1):
                lines.append(f"  {idx}. {name} — {spells[name]}g (MP {SPELLS[name]['mp']})")
            lines.append(f"Player gold: {self.player.gold}")
            lines.append("Type a number or spell name to buy, or press Enter to leave.")
            return "\n".join(lines)
        sel = None
        if selection.isdigit():
            i = int(selection) - 1
            if 0 <= i < len(available):
                sel = available[i]
        else:
            for s in available:
                if s.lower() == selection.lower():
                    sel = s
                    break
        if not sel:
            return "The merchant shrugs. 'I don't have that.'"
        price = spells[sel]
        if self.player.gold < price:
            return "You don't have enough gold."
        self.player.gold -= price
        self.player.known_spells = list(self.player.known_spells) + [sel]
        return f"You learn the spell {sel}!"

    def rest(self) -> str:
        tile = self.current_tile()
        if tile.safe:
            healed = self.player.heal(8 + self.player.level * 2)
            # chance to receive a free potion in town occasionally
            if random.random() < 0.15:
                self.player.potions += 1
                return f"You rest at the village and heal {healed} HP. The healer gifts you a potion."
            return f"You rest at the village and heal {healed} HP."
        else:
            healed = self.player.heal(4 + self.player.level)
            note = f"You rest cautiously and heal {healed} HP."
            # Resting in dangerous areas may trigger an ambush
            if random.random() < min(0.2 + tile.danger / 2, 0.75):
                enemy = generate_enemy(self.player.level, self.x, self.y)
                note += "\nYou are ambushed in your sleep!"
                intro = self.enter_combat(enemy)
                return note + "\n\n" + intro
            return note

    def debug_pos(self) -> str:
        return f"Pos: ({self.x},{self.y})"

    def to_dict(self) -> dict:
        p = self.player
        return {
            "player": {
                "name": p.name,
                "level": p.level,
                "xp": p.xp,
                "gold": p.gold,
                "max_hp": p.max_hp,
                "hp": p.hp,
                "max_mp": p.max_mp,
                "mp": p.mp,
                "attack": p.attack,
                "defense": p.defense,
                "potions": p.potions,
                "known_spells": list(p.known_spells),
                "weapon": (
                    {"name": p.weapon.name, "attack_bonus": p.weapon.attack_bonus}
                    if p.weapon else None
                ),
                "armor": (
                    {"name": p.armor.name, "defense_bonus": p.armor.defense_bonus}
                    if p.armor else None
                ),
            },
            "world": self.world.to_dict(),
            "pos": {"x": self.x, "y": self.y},
            "explored": [[x, y] for (x, y) in sorted(self.explored)],
            "state": str(self.state),
            # Persist minimal combat snapshot if in combat
            "combat": (
                {
                    "enemy": asdict(self.enemy) if self.enemy else None,
                    "regen_turns": self._player_regen_turns,
                    "regen_amount": self._player_regen_amount,
                    "enemy_stunned": self._enemy_stunned_turns,
                    "enemy_def_down": self._enemy_def_down,
                    "enemy_def_turns": self._enemy_def_turns,
                }
                if self.state == GameState.COMBAT
                else None
            ),
        }

    @staticmethod
    def from_dict(d: dict) -> "Game":
        from models import Player as PlayerModel  # avoid circular import types
        w = World.from_dict(d["world"])
        pd = d["player"]
        # Reconstruct weapon/armor objects if present
        wpn_d = pd.get("weapon")
        arm_d = pd.get("armor")
        wpn_obj = Weapon(name=wpn_d["name"], attack_bonus=int(wpn_d["attack_bonus"])) if isinstance(wpn_d, dict) else None
        arm_obj = Armor(name=arm_d["name"], defense_bonus=int(arm_d["defense_bonus"])) if isinstance(arm_d, dict) else None
        p = PlayerModel(
            name=pd["name"],
            level=int(pd["level"]),
            xp=int(pd["xp"]),
            gold=int(pd["gold"]),
            max_hp=int(pd["max_hp"]),
            hp=int(pd["hp"]),
            max_mp=int(pd.get("max_mp", 10)),
            mp=int(pd.get("mp", pd.get("max_mp", 10))),
            attack=int(pd["attack"]),
            defense=int(pd["defense"]),
            potions=int(pd.get("potions", 0)),
            known_spells=pd.get("known_spells", ()),
            weapon=wpn_obj,
            armor=arm_obj,
        )
        pos = d.get("pos", {"x": 0, "y": 0})
        x = int(pos.get("x", 0))
        y = int(pos.get("y", 0))
        g = Game(world=w, player=p, x=x, y=y)
        # restore explored if present
        explored_list = d.get("explored") or []
        try:
            for item in explored_list:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    gx, gy = int(item[0]), int(item[1])
                    if 0 <= gx < w.width and 0 <= gy < w.height:
                        g._mark_explored(gx, gy)
        except Exception:
            # ignore malformed explored data
            pass
        # Ensure current tile is always considered explored
        g._mark_explored(g.x, g.y)
        # Load state (backward-compatible)
        g.state = str(d.get("state") or GameState.EXPLORING)
        # Restore combat snapshot if present
        cmb = d.get("combat") or None
        try:
            if isinstance(cmb, dict) and cmb.get("enemy"):
                ed = cmb["enemy"]
                from models import Enemy as EnemyModel
                g.enemy = EnemyModel(
                    name=ed["name"], ascii=ed["ascii"], level=int(ed["level"]), max_hp=int(ed["max_hp"]),
                    hp=int(ed["hp"]), attack=int(ed["attack"]), defense=int(ed["defense"]),
                    xp_reward=int(ed["xp_reward"]), gold_reward=int(ed["gold_reward"]) )
                g._player_regen_turns = int(cmb.get("regen_turns", 0))
                g._player_regen_amount = int(cmb.get("regen_amount", 0))
                g._enemy_stunned_turns = int(cmb.get("enemy_stunned", 0))
                g._enemy_def_down = int(cmb.get("enemy_def_down", 0))
                g._enemy_def_turns = int(cmb.get("enemy_def_turns", 0))
        except Exception:
            pass
        return g

    def copy_from(self, other: "Game") -> None:
        self.world = other.world
        self.player = other.player
        self.x = other.x
        self.y = other.y
        # copy explored set
        try:
            self.explored = set(other.explored)
        except Exception:
            self.explored = {(self.x, self.y)}
        # copy state/combat snapshot
        self.state = other.state
        self.enemy = other.enemy
        self._player_regen_turns = other._player_regen_turns
        self._player_regen_amount = other._player_regen_amount
        self._enemy_stunned_turns = other._enemy_stunned_turns
        self._enemy_def_down = other._enemy_def_down
        self._enemy_def_turns = other._enemy_def_turns
        self.available_actions()

    def change_state(self, state: str):
        self.state = state
        self.actions.available()

    # --- Loot and discovery helpers ---
    def _weapon_pool(self) -> List[Weapon]:
        # Simple tiered weapons; bonuses are small to moderate
        return [
            Weapon("Rusty Dagger", 1),
            Weapon("Wooden Sword", 2),
            Weapon("Iron Sword", 3),
            Weapon("Steel Axe", 4),
            Weapon("Knight's Blade", 5),
            Weapon("Runed Spear", 6),
        ]

    def _random_weapon_for_level(self) -> Weapon:
        pool = self._weapon_pool()
        # bias selection by player level
        idx = min(len(pool) - 1, max(0, (self.player.level - 1) // 2 + random.randint(-1, 1)))
        # jitter around idx
        choices = pool[max(0, idx - 1): min(len(pool), idx + 2)] or pool
        return random.choice(choices)

    def _offer_weapon_pickup(self, found: Weapon, source: str) -> str:
        cur = self.player.weapon
        cur_bonus = cur.attack_bonus if cur else 0
        diff = found.attack_bonus - cur_bonus
        self.change_state(GameState.ASKING_QUESTION)
        self.question = f"You find {found.name} (ATK +{found.attack_bonus}) from {source}."
        self.question += f"\nCurrent: {cur.name} (ATK +{cur.attack_bonus})." if cur else "\nYou have no weapon equipped."
        self.question += f"\nIt seems {'better' if diff > 0 else ('the same' if diff == 0 else 'worse')}. Take it? [y/N]"
        return self.question

    def _maybe_field_find(self, tile: Tile) -> str:
        # Higher chance in dangerous areas; rarely in towns
        base = 0.03 if tile.safe else 0.10
        if random.random() < base:
            wpn = self._random_weapon_for_level()
            return self._offer_weapon_pickup(wpn, source="the area")
        return ""

    def _maybe_offer_weapon(self, source: str = "a foe") -> None:
        drop_chance = 0.25
        if random.random() < drop_chance:
            wpn = self._random_weapon_for_level()
            self._offer_weapon_pickup(wpn, source)

    # --- Combat entry/turns and actions ---
    def enter_combat(self, enemy) -> str:
        self.change_state(GameState.COMBAT)
        self.enemy = enemy
        self._combat_log = []
        # Reset temporary effects
        self._enemy_stunned_turns = 0
        self._enemy_def_down = 0
        self._enemy_def_turns = 0
        intro = f"A {enemy.name} appears! Prepare for battle."
        return intro + "\n" + self._combat_status()

    def _combat_status(self) -> str:
        if not self.enemy:
            return ""
        e = self.enemy
        lines = [
            _hp_line("You", self.player.hp, self.player.max_hp) + f" | MP {self.player.mp}/{self.player.max_mp}",
            _hp_line(e.name, e.hp, e.max_hp),
            f"\n{e.ascii}\n",
            f"[Enemy Stats] ATK: {e.attack} | DEF: {e.defense}"
            ]
        return "\n".join(lines)

    def _end_combat(self, victory: bool) -> str:
        out_lines: List[str] = []
        if victory:
            e = self.enemy
            if e:
                self.player.gold += max(0, int(e.gold_reward))
                out_lines.append(f"You defeated {e.name}! You loot {e.gold_reward} gold.")
                # Award XP and level-up notes
                notes = self.player.add_xp(max(0, int(e.xp_reward)))
                out_lines.extend(notes)
                try:
                    self._maybe_offer_weapon(source="the fallen foe")
                except Exception:
                    pass
        else:
            out_lines.append("You were defeated...")

        # Clear combat state
        self.enemy = None
        self._player_regen_turns = 0
        self._player_regen_amount = 0
        self._enemy_stunned_turns = 0
        self._enemy_def_down = 0
        self._enemy_def_turns = 0

        if not self.player.is_alive():
            self.change_state(GameState.GAME_OVER)
            return "\n".join(out_lines)
        # Return to exploring
        self.change_state(GameState.EXPLORING)
        return "\n".join(out_lines)

    def _player_regen_tick(self) -> Optional[str]:
        if self._player_regen_turns > 0 and self._player_regen_amount > 0:
            healed = self.player.heal(self._player_regen_amount)
            self._player_regen_turns -= 1
            return f"Regen restores {healed} HP."
        return None

    def _enemy_turn(self) -> List[str]:
        msgs: List[str] = []
        if not self.enemy:
            return msgs
        e = self.enemy
        if self._enemy_stunned_turns > 0:
            msgs.append(f"{e.name} is stunned and cannot act!")
            self._enemy_stunned_turns -= 1
        else:
            # Enemy attacks
            dmg = calc_damage(int(e.attack), int(self.player.total_defense))
            dmg = max(1, dmg)
            self.player.hp = _clamp_int(self.player.hp - dmg, 0, self.player.max_hp)
            msgs.append(f"{e.name} strikes you for {dmg} damage.")
        # Decay enemy defense debuff
        if self._enemy_def_turns > 0:
            self._enemy_def_turns -= 1
            if self._enemy_def_turns == 0 and self._enemy_def_down > 0:
                msgs.append("The enemy's defenses recover.")
                self._enemy_def_down = 0
        # Regen tick after enemy turn
        reg = self._player_regen_tick()
        if reg:
            msgs.append(reg)
        # Check death
        if not self.player.is_alive():
            msgs.append(self._end_combat(victory=False))
        return msgs

    # --- Player combat actions ---
    def combat_attack(self) -> str:
        if self.state != GameState.COMBAT or not self.enemy:
            return "There's nothing to attack."
        e = self.enemy
        eff_def = _enemy_defense_effect(int(e.defense), self._enemy_def_down, self._enemy_def_turns)
        dmg = calc_damage(int(self.player.total_attack), eff_def)
        e.hp = _clamp_int(e.hp - dmg, 0, e.max_hp)
        msgs = [f"You strike the {e.name} for {dmg} damage."]
        if e.hp <= 0:
            msgs.append(self._end_combat(victory=True))
            return "\n".join([m for m in msgs if m])
        # Enemy responds
        msgs.extend(self._enemy_turn())
        msgs.append(self._combat_status())
        return "\n".join([m for m in msgs if m])

    def combat_cast(self, spell: str) -> str:
        if self.state != GameState.COMBAT or not self.enemy:
            return "You can't cast that now."
        if spell not in SPELLS:
            return "You don't know that spell."
        cost = int(SPELLS[spell]["mp"])
        if self.player.mp < cost:
            return "Not enough MP!"
        self.player.mp -= cost
        e = self.enemy
        msgs: List[str] = []
        power = int(SPELLS[spell]["pow"])
        if spell == "Heal":
            healed = self.player.heal(power + self.player.level)
            msgs.append(f"You cast Heal and restore {healed} HP.")
        elif spell == "Regen":
            self._player_regen_turns = 3
            self._player_regen_amount = power
            msgs.append(f"You cast Regen. You'll recover {power} HP for 3 turns.")
        elif spell == "Guard Break":
            self._enemy_def_down = power + (self.player.level // 4)
            self._enemy_def_turns = 2
            msgs.append("You cast Guard Break! The enemy's defenses falter.")
        else:
            # Damage spell
            dmg = max(1, power + (self.player.level // 2) + random.randint(0, 2) - (int(e.defense) // 4))
            e.hp = _clamp_int(e.hp - dmg, 0, e.max_hp)
            msgs.append(f"You cast {spell}! It hits {e.name} for {dmg} damage.")
            if e.hp <= 0:
                msgs.append(self._end_combat(victory=True))
                return "\n".join([m for m in msgs if m])
        # Enemy turn
        msgs.extend(self._enemy_turn())
        msgs.append(self._combat_status())
        return "\n".join([m for m in msgs if m])

    def combat_potion(self) -> str:
        if self.state != GameState.COMBAT:
            return "You don't need to use a potion now."
        if self.player.potions <= 0:
            return "You have no potions."
        self.player.potions -= 1
        healed = self.player.heal(12 + self.player.level)
        msgs = [f"You quaff a potion and recover {healed} HP."]
        msgs.extend(self._enemy_turn())
        msgs.append(self._combat_status())
        return "\n".join([m for m in msgs if m])

    def combat_flee(self) -> str:
        if self.state != GameState.COMBAT or not self.enemy:
            return "There is nothing to flee from."
        # Base chance
        chance = 0.5
        try:
            if self.enemy.level > self.player.level:
                chance = 0.35
        except Exception:
            pass
        if random.random() < chance:
            self.change_state(GameState.EXPLORING)
            self.enemy = None
            self._player_regen_turns = 0
            self._player_regen_amount = 0
            self._enemy_stunned_turns = 0
            self._enemy_def_down = 0
            self._enemy_def_turns = 0
            return "You successfully flee back to safety."
        else:
            msgs = ["You fail to flee!"]
            msgs.extend(self._enemy_turn())
            msgs.append(self._combat_status())
            return "\n".join([m for m in msgs if m])