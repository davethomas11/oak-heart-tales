# models/weapon.py
class Weapon:
    def __init__(self, name, attack_bonus):
        self.name = name
        self.attack_bonus = attack_bonus

    def __str__(self):
        return f"Weapon(name={self.name}, attack_bonus={self.attack_bonus})"