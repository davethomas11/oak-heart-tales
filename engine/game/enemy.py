# models/enemy.py
class Enemy:
    def __init__(
            self,
            name: str,
            ascii: str,
            level: int,
            max_hp: int,
            hp: int,
            attack: int,
            defense: int,
            xp_reward: int,
            gold_reward: int,
            direction: int = 0,
    ):
        self.name = name
        self.ascii = ascii
        self.level = level
        self.max_hp = max_hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.direction = direction

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

    @staticmethod
    def from_dict(data: dict) -> 'Enemy':
        return Enemy(
            name=data.get("name", "Unknown"),
            ascii=data.get("ascii", "(?)"),
            level=data.get("level", 1),
            max_hp=data.get("max_hp", 10),
            hp=data.get("hp", 10),
            attack=data.get("attack", 5),
            defense=data.get("defense", 2),
            xp_reward=data.get("xp_reward", 0),
            gold_reward=data.get("gold_reward", 0),
        )
