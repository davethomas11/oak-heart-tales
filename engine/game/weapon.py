# models/weapon.py
class Weapon:
    def __init__(self, name, attack_bonus):
        self.name = name
        self.attack_bonus = attack_bonus

    def __str__(self):
        return f"Weapon(name={self.name}, attack_bonus={self.attack_bonus})"

    def to_dict(self):
        return {"name": self.name, "attack_bonus": self.attack_bonus}

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["attack_bonus"])

def weapon_pool():
    return [
        Weapon("Rusty Dagger", 1),
        Weapon("Wooden Sword", 2),
        Weapon("Iron Sword", 3),
        Weapon("Steel Axe", 4),
        Weapon("Knight's Blade", 5),
        Weapon("Runed Spear", 6),
    ]