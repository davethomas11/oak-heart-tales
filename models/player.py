# models/player.py
from dataclasses import dataclass
from models.utils import clamp, xp_to_next_level
from models.weapon import Weapon
from models.armor import Armor

@dataclass
class Player:
    name: str
    level: int
    hp: int
    max_hp: int
    mp: int
    max_mp: int
    attack: int
    defense: int
    potions: int
    known_spells: list
    gold: int
    weapon: Weapon
    armor: Armor
    xp: int = 0

    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount: int) -> int:
        old = self.hp
        self.hp = clamp(self.hp + amount, 0, self.max_hp)
        return self.hp - old

    def restore_mp(self, amount: int) -> int:
        old = self.mp
        self.mp = clamp(self.mp + int(amount), 0, self.max_mp)
        return self.mp - old

    def add_xp(self, amount: int):
        notes = []
        self.xp += amount
        notes.append(f"You gain {amount} XP.")
        while self.xp >= xp_to_next_level(self.level):
            self.xp -= xp_to_next_level(self.level)
            self.level += 1
            # Improve stats on level up
            hp_gain = 5 + self.level
            atk_gain = 1 + (self.level // 3)
            def_gain = 1 if self.level % 2 == 0 else 0
            self.max_hp += hp_gain
            self.attack += atk_gain
            self.defense += def_gain
            self.hp = self.max_hp
            notes.append(
                f"Level up! You are now level {self.level}. +{hp_gain} HP, +{atk_gain} ATK, +{def_gain} DEF. HP fully restored!"
            )
        return notes

    @property
    def total_attack(self):
        return self.attack + (self.weapon.attack_bonus if self.weapon else 0)

    @property
    def total_defense(self):
        return self.defense + (self.armor.defense_bonus if self.armor else 0)