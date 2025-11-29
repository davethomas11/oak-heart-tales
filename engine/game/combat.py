import random
from .enemy import Enemy

# Constants for magic numbers
# Critical and graze chances
CRIT_CHANCE = 0.08
GRAZE_CHANCE = 0.13
ENEMY_CRIT_CHANCE = 0.06
ENEMY_GRAZE_CHANCE = 0.11

# Defend and potion values
DEFEND_REDUCTION_BASE = 3
REGEN_POTION_BASE = 12

# Flee chances
FLEE_CHANCE = 0.5
FLEE_CHANCE_STRONG_ENEMY = 0.3


def depth_from_pos(x: int, y: int) -> int:
    # deeper towards bottom-right; simple heuristic
    return x + y


def generate_enemy(enemy_archetypes: list, player_level: int, x: int, y: int) -> Enemy:
    depth = depth_from_pos(x, y)
    available = enemy_archetypes[: min(3 + depth, len(enemy_archetypes))]
    archetype = random.choice(available)
    lvl = max(1, min(player_level + 3, player_level + random.choice([-1, 0, 0, 1]) + depth // 2))
    max_hp = archetype["base_hp"] + lvl * 3 + random.randint(0, 3)
    atk = archetype.get("base_attack", 3) + lvl + random.randint(0, 2)
    defense = archetype["base_defense"] + (lvl // 3)
    xp_reward = archetype["xp_reward"] + lvl * 10 + random.randint(0, 10)
    gold_reward = archetype["gold_reward"] + lvl * 3 + random.randint(0, 6)
    return Enemy(
        name=f"{archetype['name']} (Lv {lvl})",
        ascii=archetype.get("ascii", "???"),
        level=lvl,
        max_hp=max_hp,
        hp=max_hp,
        attack=atk,
        defense=defense,
        xp_reward=xp_reward,
        gold_reward=gold_reward
    )


def calc_damage(attacker_atk: int, defender_def: int) -> int:
    base = attacker_atk - defender_def
    roll = random.randint(-1, 2)
    return max(1, base + roll)


# Simple built-in spell catalog
# Keep minimal and inline to avoid new files; effects implemented in-code
SPELLS = {
    # name: {mp: cost, pow: base power (damage or heal)}
    "Firebolt": {"mp": 4, "pow": 6},  # single-target damage
    "Heal": {"mp": 5, "pow": 10},  # heal self
    "Ice Shard": {"mp": 7, "pow": 9},  # stronger damage
    # Quick wins: a few more simple spells
    "Shock": {"mp": 6, "pow": 5},  # small dmg, chance to stun
    "Regen": {"mp": 5, "pow": 3},  # heal over time (per turn amount)
    "Guard Break": {"mp": 4, "pow": 2},  # reduce enemy defense temporarily
}
