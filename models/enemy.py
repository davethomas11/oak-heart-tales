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