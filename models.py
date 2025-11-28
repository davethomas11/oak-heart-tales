from dataclasses import dataclass


def clamp(val: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, val))


def xp_to_next_level(level: int) -> int:
    # Simple quadratic curve
    return 50 + (level * level * 25)

class Weapon:
    def __init__(self, name, attack_bonus):
        self.name = name
        self.attack_bonus = attack_bonus

    def __str__(self):
        return f"Weapon(name={self.name}, attack_bonus={self.attack_bonus})"

class Armor:
    def __init__(self, name, defense_bonus):
        self.name = name
        self.defense_bonus = defense_bonus

    def __str__(self):
        return f"Armor(name={self.name}, defense_bonus={self.defense_bonus})"

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


@dataclass
class Enemy:
    name: str
    ascii: str
    level: int
    max_hp: int
    hp: int
    attack: int
    defense: int
    xp_reward: int
    gold_reward: int

    def is_alive(self) -> bool:
        return self.hp > 0
