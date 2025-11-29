# models/player.py
def clamp(val: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, val))

def xp_to_next_level(level: int) -> int:
    # Simple quadratic curve
    return 50 + (level * level * 25)

class Player:
    def __init__(
            self,
            name: str,
            level: int,
            hp: int,
            max_hp: int,
            mp: int,
            max_mp: int,
            attack: int,
            defense: int,
            potions: int,
            known_spells: list,
            gold: int,
            weapon,
            armor,
            xp: int = 0,
    ):
        self.name = name
        self.level = level
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.attack = attack
        self.defense = defense
        self.potions = potions
        self.known_spells = known_spells
        self.gold = gold
        self.weapon = weapon
        self.armor = armor
        self.xp = xp

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

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "attack": self.attack,
            "defense": self.defense,
            "potions": self.potions,
            "known_spells": self.known_spells,
            "gold": self.gold,
            "weapon": self.weapon.name if self.weapon else None,
            "armor": self.armor.name if self.armor else None,
            "xp": self.xp,
        }
