# models/armor.py
class Armor:
    def __init__(self, name, defense_bonus):
        self.name = name
        self.defense_bonus = defense_bonus

    def __str__(self):
        return f"Armor(name={self.name}, defense_bonus={self.defense_bonus})"