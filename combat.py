import random
import json
import os
from typing import Tuple, List, Dict, Callable

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

from models import Enemy, Player

def depth_from_pos(x: int, y: int) -> int:
    # deeper towards bottom-right; simple heuristic
    return x + y

# Load enemy archetypes from JSON
def load_enemy_archetypes():
    path = os.path.join("data", "enemies.json")
    with open(path, "r") as f:
        return json.load(f)

ENEMY_ARCHETYPES = load_enemy_archetypes()

def generate_enemy(player_level: int, x: int, y: int) -> Enemy:
    depth = depth_from_pos(x, y)
    available = ENEMY_ARCHETYPES[: min(3 + depth, len(ENEMY_ARCHETYPES))]
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
SPELLS: Dict[str, Dict[str, int]] = {
    # name: {mp: cost, pow: base power (damage or heal)}
    "Firebolt": {"mp": 4, "pow": 6},      # single-target damage
    "Heal": {"mp": 5, "pow": 10},         # heal self
    "Ice Shard": {"mp": 7, "pow": 9},    # stronger damage
    # Quick wins: a few more simple spells
    "Shock": {"mp": 6, "pow": 5},        # small dmg, chance to stun
    "Regen": {"mp": 5, "pow": 3},        # heal over time (per turn amount)
    "Guard Break": {"mp": 4, "pow": 2},  # reduce enemy defense temporarily
}


def _cast_spell(player: Player, enemy: Enemy, spell_name: str, print_fn: Callable[[str], None]) -> Dict[str, int]:
    spec = SPELLS.get(spell_name)
    if not spec:
        print_fn("You don't know that spell.")
        return {}
    cost = spec["mp"]
    if player.mp < cost:
        print_fn("Not enough MP!")
        return {}
    player.mp -= cost
    power = spec["pow"]
    if spell_name == "Heal":
        healed = player.heal(power + player.level)
        print_fn(f"You cast Heal and restore {healed} HP.")
        return {}
    elif spell_name == "Regen":
        # apply a 3-turn regeneration effect
        print_fn(f"You cast Regen. A gentle aura will heal you for {power} HP over the next 3 turns.")
        return {"regen_turns": 3, "regen_amount": power}
    elif spell_name == "Shock":
        # small damage and 25% chance to stun for 1 turn
        dmg = max(1, power + (player.level // 3) + random.randint(0, 2) - (enemy.defense // 4))
        enemy.hp = max(0, enemy.hp - dmg)
        stunned = 1 if random.random() < 0.25 else 0
        if stunned:
            print_fn(f"You cast Shock! It jolts the {enemy.name} for {dmg} damage and stuns it!")
        else:
            print_fn(f"You cast Shock! It jolts the {enemy.name} for {dmg} damage.")
        return {"enemy_stunned": stunned}
    elif spell_name == "Guard Break":
        # reduce enemy defense temporarily
        # magnitude scales a bit with player level
        debuff = power + (player.level // 4)
        print_fn(f"You cast Guard Break! The {enemy.name}'s defenses falter (-{debuff} DEF for 2 turns).")
        return {"enemy_def_down": debuff, "enemy_def_turns": 2}
    else:
        # offensive spell: scale slightly with level and attack
        dmg = max(1, power + (player.level // 2) + (player.attack // 4) + random.randint(0, 3) - (enemy.defense // 3))
        enemy.hp = max(0, enemy.hp - dmg)
        print_fn(f"You cast {spell_name}! It hits the {enemy.name} for {dmg} damage.")
        return {}


def combat(player: Player, enemy: Enemy, input_fn=input, print_fn=print) -> bool:
    # Clear the screen for a cleaner combat UI
    try:
        print_fn("\033[2J\033[H")
    except Exception:
        pass
    print_fn(f"A wild {enemy.name} appears! Prepare for battle.")
    art = enemy.ascii
    if art:
        print_fn(art)
    defending = False
    # Lightweight status tracking
    regen_turns = 0
    regen_amount = 0
    enemy_stunned = 0
    enemy_def_down_turns = 0
    enemy_def_down_amt = 0
    while player.is_alive() and enemy.is_alive():
        # Start of round effects (Player regen)
        if regen_turns > 0 and player.is_alive():
            healed = player.heal(regen_amount)
            print_fn(f"Regen restores {healed} HP.")
            regen_turns -= 1

        print_fn("-" * 50)
        print_fn(f"Your HP: {player.hp}/{player.max_hp} | MP: {player.mp}/{player.max_mp} | Potions: {player.potions}")
        print_fn(f"{enemy.name} HP: {enemy.hp}/{enemy.max_hp}")
        print_fn("Choose an action: [a]ttack, [d]efend, [p]otion, [s]pell, [f]lee")
        choice = input_fn("> ").strip().lower()
        if choice in ("a", "attack"):
            # consider temporary defense debuff
            eff_enemy_def = max(0, enemy.defense - (enemy_def_down_amt if enemy_def_down_turns > 0 else 0))
            dmg = calc_damage(player.total_attack, eff_enemy_def)
            # apply crit/graze
            crit = False
            graze = False
            r = random.random()
            if r < CRIT_CHANCE:
                dmg = max(1, int(dmg * 2))
                crit = True
            elif r < GRAZE_CHANCE:  # next 5%
                dmg = max(1, max(1, dmg // 2))
                graze = True
            enemy.hp = max(0, enemy.hp - dmg)
            if crit:
                print_fn(f"Critical hit! You strike the {enemy.name} for {dmg} damage!")
            elif graze:
                print_fn(f"Glancing blow. You strike the {enemy.name} for {dmg} damage.")
            else:
                print_fn(f"You strike the {enemy.name} for {dmg} damage!")
            defending = False
        elif choice in ("d", "defend"):
            mp_restored = player.restore_mp(1)
            mp_note = f" You also regain {mp_restored} MP." if mp_restored > 0 else ""
            print_fn("You brace for impact. Incoming damage reduced this turn." + mp_note)
            defending = True
        elif choice in ("p", "potions", "potion"):
            if player.potions > 0:
                player.potions -= 1
                healed = player.heal(REGEN_POTION_BASE + player.level * 2)
                print_fn(f"You quaff a potion and heal {healed} HP.")
            else:
                print_fn("You have no potions left!")
            defending = False
        elif choice in ("s", "spell", "spells"):
            # show known spells
            known = [s for s in player.known_spells if s in SPELLS]
            if not known:
                print_fn("You don't know any spells.")
                defending = False
            else:
                print_fn("Known spells:")
                for idx, sname in enumerate(known, 1):
                    spec = SPELLS[sname]
                    print_fn(f"  {idx}. {sname} (MP {spec['mp']})")
                print_fn("Cast which? (number or name, blank to cancel)")
                sel = input_fn("> ").strip()
                if not sel:
                    defending = False
                else:
                    chosen = None
                    if sel.isdigit():
                        i = int(sel) - 1
                        if 0 <= i < len(known):
                            chosen = known[i]
                    else:
                        for sname in known:
                            if sname.lower() == sel.lower():
                                chosen = sname
                                break
                    if chosen:
                        effects = _cast_spell(player, enemy, chosen, print_fn)
                        # merge effects into local state
                        if effects.get("regen_turns"):
                            regen_turns = effects.get("regen_turns", regen_turns)
                            regen_amount = effects.get("regen_amount", regen_amount)
                        if effects.get("enemy_stunned"):
                            enemy_stunned = max(enemy_stunned, effects.get("enemy_stunned", 0))
                        if effects.get("enemy_def_down"):
                            enemy_def_down_amt = max(enemy_def_down_amt, effects.get("enemy_def_down", 0))
                            enemy_def_down_turns = max(enemy_def_down_turns, effects.get("enemy_def_turns", 0))
                    else:
                        print_fn("No such spell.")
                    defending = False
        elif choice in ("f", "flee", "run"):
            chance = FLEE_CHANCE if enemy.level <= player.level else FLEE_CHANCE_STRONG_ENEMY
            if random.random() < chance:
                print_fn("You slip away into the shadows. You fled successfully!")
                return False
            else:
                print_fn("You failed to flee!")
            defending = False
        else:
            print_fn("Invalid action. You hesitate...")
            defending = False

        # decrement enemy debuffs at end of player's action
        if enemy_def_down_turns > 0:
            enemy_def_down_turns -= 1
            if enemy_def_down_turns == 0 and enemy_def_down_amt > 0:
                print_fn(f"The {enemy.name} regains its guard (+{enemy_def_down_amt} DEF).")
                enemy_def_down_amt = 0

        if enemy.is_alive():
            if enemy_stunned > 0:
                print_fn(f"The {enemy.name} is stunned and cannot act!")
                enemy_stunned -= 1
                # defending falls off after enemy turn regardless
                defending = False
                continue
            dmg = calc_damage(enemy.attack, player.total_defense)
            # apply crit/graze to enemy as well
            r2 = random.random()
            if r2 < ENEMY_CRIT_CHANCE:  # slightly lower enemy crit chance
                dmg = max(1, int(dmg * 2))
                enemy_msg_tag = " (critical!)"
            elif r2 < ENEMY_GRAZE_CHANCE:
                dmg = max(1, max(1, dmg // 2))
                enemy_msg_tag = " (glancing)"
            else:
                enemy_msg_tag = ""
            if defending:
                dmg = max(0, dmg - (DEFEND_REDUCTION_BASE + player.level // 2))
            player.hp = max(0, player.hp - dmg)
            if dmg > 0:
                print_fn(f"The {enemy.name} hits you for {dmg} damage!{enemy_msg_tag}")
            else:
                print_fn(f"You block the {enemy.name}'s attack!")

    if player.is_alive():
        print_fn(f"You defeated the {enemy.name}!")
        player.gold += enemy.gold_reward
        print_fn(f"You loot {enemy.gold_reward} gold.")
        level_notes = player.add_xp(enemy.xp_reward)
        for note in level_notes:
            print_fn(note)
        # Pause after potential level-up so messages aren't cleared by the overworld UI
        try:
            if input_fn is input:
                input_fn("\nPress Enter to continue...")
        except Exception:
            pass
        return True
    else:
        print_fn("You have fallen in battle...")
        # Pause so the player can read the death message before the screen clears
        try:
            if input_fn is input:
                input_fn("\nPress Enter to continue...")
        except Exception:
            pass
        return False
