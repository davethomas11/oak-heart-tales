# models/enemy.py
from dataclasses import dataclass

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

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ascii": self.ascii,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "xp_reward": self.xp_reward,
            "gold_reward": self.gold_reward,
        }