import random
from .weapon import weapon_pool
from .armor import armor_pool
from .combat import SPELLS

class Character:
    def __init__(self, name, role, dialog, spells=None, item=None, type=None):
        self.name = name
        self.role = role  # e.g., 'wizard', 'helper', 'villager'
        self.dialog = dialog
        self.spells = spells or []
        self.type = type or ""
        self.item = item  # e.g., weapon or armor
        self.question = None

    def interact(self, player):
        output = [f"You meet {self.name}, a {self.role}.", f'\n"{self.dialog}"\n']
        if self.role == "wizard" and self.spells:
            for spell in self.spells:
                if spell not in player.known_spells:
                    output.append(f"{self.name} knows the spell, {spell}, and offers to teach you!")
                    self.question = {
                        "type": "spell_learn",
                        "spell": spell,
                        "character": self.name,
                        "ask": f"Do you want to learn the spell {spell}?",
                        "action": lambda choice: player.known_spells.append(spell) if choice else None
                    }
                break
        elif self.role == "helper" and self.item:
            if self.type == "weapon" and self.item.attack_bonus > (player.weapon.attack_bonus if player.weapon else 0):
                output.append(f"{self.name} gives you a weapon: {self.item.name}!")
                self.question = {
                    "type": "weapon_find",
                    "item": self.item,
                    "character": self.name,
                    "ask": "Do you want to equip this new weapon?",
                    "action": lambda choice: setattr(player, 'weapon', self.item) if choice else None
                }
            elif self.type == "armor" and self.item.defense_bonus > (player.armor.defense_bonus if player.armor else 0):
                output.append(f"{self.name} gives you armor: {self.item.name}!")
                self.question = {
                    "type": "armor_find",
                    "item": self.item,
                    "character": self.name,
                    "ask": "Do you want to equip this new armor?",
                    "action": lambda choice: setattr(player, 'armor', self.item) if choice else None
                }
            else:
                output.append(f"{self.name} offers you a {self.item.name}, but it's not better than your current gear.")
        else:
            output.append(f"You have a pleasant conversation with {self.name}.")
        return "\n".join(output)

# Example list of characters
CHARACTERS = [
    Character(
        name="Eldrin the Wise",
        role="wizard",
        dialog="Greetings, traveler. Magic is the key to survival in these lands.",
        spells=[random.choice(list(SPELLS.keys()))]
    ),
    Character(
        name="Mira the Brave",
        role="helper",
        dialog="Take this, it will help you on your journey!",
        type="weapon",
        item=random.choice(weapon_pool())
    ),
    Character(
        name="Thorn the Ranger",
        role="helper",
        dialog="Here, wear this armor to protect yourself.",
        type="armor",
        item=random.choice(armor_pool())
    ),
    Character(
        name="Old Man Willow",
        role="villager",
        dialog="The woods are dangerous at night. Stay safe, friend."
    )
]