from .event import GameEvent, EventManager
from .player import Player
from .combat import SPELLS
from .weapon import Weapon, weapon_pool
from .armor import Armor, armor_pool
import time

spells = {
    "Firebolt": 25,
    "Heal": 30,
    "Ice Shard": 45,
    "Shock": 40,
    "Regen": 35,
    "Guard Break": 30,
}

weapon_items = weapon_pool()
weapons = {w.name: w.attack_bonus * 20 for w in weapon_items}
armor_items = armor_pool()
armor = {a.name: a.defense_bonus * 20 for a in armor_items}
potion_price = 5

class Shop:
    def __init__(self, player: Player, event_manager: EventManager):
        self.player = player
        self.event_manager = event_manager
        self.shop_items = None

    def _choice(self, items):
        # Simple pseudo-random choice using time
        t = int(time.time() * 1000)
        idx = t % len(items)
        return items[idx]

    def generate_items(self):
        # Randomize available spells (up to 3)
        available_spells = [self._choice([s for s in spells if s in SPELLS and s not in self.player.known_spells])
                            for _ in range(min(3, len([s for s in spells if s in SPELLS and s not in self.player.known_spells])))]
        # Remove duplicates if any
        available_spells = list(dict.fromkeys(available_spells))

        # Randomize available weapons and armor (up to 2 each)
        available_weapons = [self._choice(list(weapons.keys()))] if weapons else []
        available_armor = [self._choice(list(armor.keys()))] if armor else []

        return self.set_shop_items(available_spells, available_weapons, available_armor)

    def set_shop_items(self, spells_list: list, weapons_list: list, armor_list: list):
        items = {}
        for s in spells_list:
            if s in SPELLS:
                items[s] = spells[s]
        for w in weapons_list:
            if w in weapons:
                items[w] = weapons[w]
        for a in armor_list:
            if a in armor:
                items[a] = armor[a]
        items["Potion"] = potion_price
        self.shop_items = items
        return self.shop_items

    def shop(self, selection: str) -> str:

        if not self.shop_items:
            self.generate_items()

        available_spells = [s for s in self.shop_items if s in SPELLS and s not in self.player.known_spells]
        available_weapons = [w for w in self.shop_items if w not in SPELLS and w in weapons and (w != self.player.weapon.name)]
        available_armor = [a for a in self.shop_items if a not in SPELLS and a in armor and (a != self.player.armor.name)]

        self.set_shop_items(available_spells, available_weapons, available_armor)

        if not self.shop_items:
            self.event_manager.emit(GameEvent(GameEvent.SHOP_EMPTY, {
                "message": "Shop is empty, all items learned or bought."
            }))
            return "The merchant smiles: 'You've learned all I can teach and bought all I can offer for now.'"

        if selection is None or selection == "":
            lines = ["\nMerchant's Caravan — Items for sale:"]
            idx = 1
            for name in available_spells:
                lines.append(f"  {idx}. {name} (Spell) — {spells[name]}g (MP {SPELLS[name]['mp']})")
                idx += 1
            for name in available_weapons:
                lines.append(f"  {idx}. {name} (Weapon) — {weapons[name]}g")
                idx += 1
            for name in available_armor:
                lines.append(f"  {idx}. {name} (Armor) — {armor[name]}g")
                idx += 1
            if "Potion" in self.shop_items:
                lines.append(f"  {idx}. Potion — {potion_price}g (Restores HP)")
                idx += 1
            lines.append(f"Player gold: {self.player.gold}")
            lines.append("Type a number or item name to buy.")
            return "\n".join(lines)

        sel = None
        items_list = list(self.shop_items.keys())
        if selection.isdigit():
            i = int(selection) - 1
            if 0 <= i < len(items_list):
                sel = items_list[i]
        else:
            for s in items_list:
                if s.lower() == selection.lower():
                    sel = s
                    break

        if not sel:
            self.event_manager.emit(GameEvent(GameEvent.SHOP_ITEM_NOT_FOUND, {
                "message": f"Shop item not found: {selection}",
                "selection": selection,
                "available_items": self.shop_items
            }))
            return "The merchant shrugs. 'I don't have that.'"

        price = self.shop_items[sel]
        if self.player.gold < price:
            self.event_manager.emit(GameEvent(GameEvent.SHOP_NOT_ENOUGH_GOLD, {
                "message": f"Not enough gold for {sel}.",
                "selection": sel,
                "price": price,
                "player_gold": self.player.gold
            }))
            return "You don't have enough gold."

        self.player.gold -= price
        if sel in spells:
            self.player.known_spells = list(self.player.known_spells) + [sel]
            item_type = "spell"
        elif sel in weapons:
            self.player.weapon = weapon_items[[w.name for w in weapon_items].index(sel)]
            item_type = "weapon"
        elif sel in armor:
            self.player.armor = armor_items[[a.name for a in armor_items].index(sel)]
            item_type = "armor"
        elif sel == "Potion":
            self.player.potions += 1
            item_type = "potion"
        else:
            item_type = "item"

        self.event_manager.emit(GameEvent(GameEvent.BOUGHT_ITEM, {
            "message": f"Player bought {item_type} {sel}.",
            "item": sel,
            "type": item_type,
            "price": price,
            "player_gold": self.player.gold
        }))
        return f"You acquire the {item_type} {sel}!"