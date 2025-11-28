import random
from dataclasses import asdict
from typing import List

from models import Player, Weapon, Armor, clamp, xp_to_next_level
from world import World, Tile
from combat import generate_enemy, combat, SPELLS
from ascii_renderer import render_room


class Game:
    def __init__(self, world: World, player: Player, x: int, y: int,
                 input_fn=input, print_fn=print, interactive: bool = True):
        self.world = world
        self.player = player
        self.x = x
        self.y = y
        # Injected I/O so the game can run in non-interactive environments (web)
        self.input_fn = input_fn
        self.print_fn = print_fn
        self.interactive = interactive
        # Track explored tiles as a set of (x, y)
        self.explored = set()  # type: ignore[var-annotated]
        # Mark starting position as explored
        self._mark_explored(self.x, self.y)

    @staticmethod
    def new_random(size: int, input_fn=input, print_fn=print, interactive: bool = True) -> "Game":
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
            y=cy,
            input_fn=input_fn,
            print_fn=print_fn,
            interactive=interactive
        )

    def current_tile(self) -> Tile:
        return self.world.get(self.x, self.y)

    def move(self, dx: int, dy: int) -> str:
        nx = clamp(self.x + dx, 0, self.world.width - 1)
        ny = clamp(self.y + dy, 0, self.world.height - 1)
        if nx == self.x and ny == self.y:
            return "You can't go that way."

        # Before moving, warn the player if the destination is very dangerous
        dest_tile = self.world.get(nx, ny)
        try:
            danger_threshold = 0.6  # warn for risky areas
            if self.interactive and (not dest_tile.safe and dest_tile.danger >= danger_threshold):
                self.print_fn(
                    f"Warning: '{dest_tile.name}' seems very dangerous (danger {dest_tile.danger:.2f}). Proceed? [y/N]"
                )
                try:
                    ans = self.input_fn("> ").strip().lower()
                except Exception:
                    ans = "n"
                if ans not in ("y", "yes"):
                    return "You decide it's too dangerous and turn back."
        except Exception:
            # If anything goes wrong with prompting, just continue the move
            pass

        self.x, self.y = nx, ny
        # mark explored when arriving
        self._mark_explored(self.x, self.y)
        tile = self.current_tile()
        art = render_room(tile)
        desc = f"{art}\nYou arrive at {tile.name}. {tile.description}"
        # Roll encounter
        if not tile.safe and random.random() < tile.danger:
            enemy = generate_enemy(self.player.level, self.x, self.y)
            won = combat(self.player, enemy, input_fn=self.input_fn, print_fn=self.print_fn)
            if not self.player.is_alive():
                return "Your journey ends here."
            # Enemy weapon drop chance if you won
            try:
                if won:
                    self._maybe_offer_weapon(source="the fallen foe")
            except Exception:
                pass
        # Field find chance (can find gear lying around)
        try:
            self._maybe_field_find(tile)
        except Exception:
            pass
        return desc

    def look(self) -> str:
        t = self.current_tile()
        art = render_room(t)
        return f"{art}\n{t.name}: {t.description}"

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
        )

    def shop(self) -> str:
        tile = self.current_tile()
        if not getattr(tile, "shop", False):
            return "There is no shop here."
        lines: List[str] = []
        lines.append("Merchant's Caravan — Spells for sale:")
        # Define simple spell prices; ensure only spells not yet known are shown
        prices = {
            "Firebolt": 25,
            "Heal": 30,
            "Ice Shard": 45,
            "Shock": 40,
            "Regen": 35,
            "Guard Break": 30,
        }
        available = [s for s in prices.keys() if s in SPELLS and s not in self.player.known_spells]
        if not available:
            return "The merchant smiles: 'You've learned all I can teach you for now.'"
        for idx, name in enumerate(available, 1):
            lines.append(f"  {idx}. {name} — {prices[name]}g (MP {SPELLS[name]['mp']})")
        lines.append(f"Gold: {self.player.gold}")
        lines.append("Type a number to buy, or press Enter to leave.")
        if not self.interactive:
            # Web/non-interactive mode: show summary message
            return "\n".join(lines) + "\n(Shopping is interactive in console; not available in web mode.)"
        self.print_fn("\n".join(lines))
        choice = self.input_fn("> ").strip()
        if not choice:
            return "You leave the merchant be."
        sel = None
        if choice.isdigit():
            i = int(choice) - 1
            if 0 <= i < len(available):
                sel = available[i]
        else:
            for s in available:
                if s.lower() == choice.lower():
                    sel = s
                    break
        if not sel:
            return "The merchant shrugs. 'I don't have that.'"
        price = prices[sel]
        if self.player.gold < price:
            return "You don't have enough gold."
        # purchase
        self.player.gold -= price
        # add to known spells, keep tuple as in model
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
                self.print_fn("You are ambushed in your sleep!")
                combat(self.player, enemy, input_fn=self.input_fn, print_fn=self.print_fn)
                if not self.player.is_alive():
                    return "You were slain during the ambush..."
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

    def _offer_weapon_pickup(self, found: Weapon, source: str) -> None:
        cur = self.player.weapon
        cur_bonus = cur.attack_bonus if cur else 0
        diff = found.attack_bonus - cur_bonus
        # Non-interactive: auto-equip if strictly better; otherwise skip silently
        if not self.interactive:
            if diff > 0:
                self.player.weapon = Weapon(found.name, found.attack_bonus)
            return
        self.print_fn(f"You find {found.name} (ATK +{found.attack_bonus}) from {source}.")
        if cur:
            self.print_fn(f"Current: {cur.name} (ATK +{cur.attack_bonus}).")
        note = "better" if diff > 0 else ("the same" if diff == 0 else "worse")
        self.print_fn(f"It seems {note}. Take it? [y/N]")
        ans = self.input_fn("> ").strip().lower()
        if ans in ("y", "yes"):
            self.player.weapon = Weapon(found.name, found.attack_bonus)
            if cur:
                self.print_fn(f"You swap to {found.name}. Your {cur.name} is left behind.")
            else:
                self.print_fn(f"You equip {found.name}.")
        else:
            self.print_fn("You leave it be.")

    def _maybe_field_find(self, tile: Tile) -> None:
        # Higher chance in dangerous areas; rarely in towns
        base = 0.03 if tile.safe else 0.10
        if random.random() < base:
            wpn = self._random_weapon_for_level()
            self._offer_weapon_pickup(wpn, source="the area")

    def _maybe_offer_weapon(self, source: str = "a foe") -> None:
        drop_chance = 0.25
        if random.random() < drop_chance:
            wpn = self._random_weapon_for_level()
            self._offer_weapon_pickup(wpn, source)
