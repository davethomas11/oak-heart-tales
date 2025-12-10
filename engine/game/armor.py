# models/armor.py
class Armor:
    def __init__(self, name, defense_bonus):
        self.name = name
        self.defense_bonus = defense_bonus

    def __str__(self):
        return f"Armor(name={self.name}, defense_bonus={self.defense_bonus})"

    def to_dict(self):
        return {"name": self.name, "defense_bonus": self.defense_bonus}

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["defense_bonus"])

def armor_pool():
    return [
        Armor("Cloth Tunic", 1),
        Armor("Leather Armor", 2),
        Armor("Chainmail", 3),
        Armor("Plate Armor", 4),
        Armor("Dragon Scale Mail", 5),
        Armor("Mage Robe", 2),
    ]