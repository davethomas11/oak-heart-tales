// Transcrypt'ed from Python, 2025-12-04 16:09:33
var random = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {Enemy} from './enemy.js';
import * as __module_random__ from './random.js';
__nest__ (random, '', __module_random__);
var __name__ = 'combat';
export var CRIT_CHANCE = 0.08;
export var GRAZE_CHANCE = 0.13;
export var ENEMY_CRIT_CHANCE = 0.06;
export var ENEMY_GRAZE_CHANCE = 0.11;
export var DEFEND_REDUCTION_BASE = 3;
export var REGEN_POTION_BASE = 12;
export var FLEE_CHANCE = 0.5;
export var FLEE_CHANCE_STRONG_ENEMY = 0.3;
export var depth_from_pos = function (x, y) {
	return x + y;
};
export var generate_enemy = function (enemy_archetypes, player_level, x, y) {
	var depth = depth_from_pos (x, y);
	var available = enemy_archetypes.__getslice__ (null, min (3 + depth, len (enemy_archetypes)), 1);
	var archetype = random.choice (available);
	var lvl = max (1, min (player_level + 3, (player_level + random.choice ([-(1), 0, 0, 1])) + Math.floor (depth / 2)));
	var max_hp = (archetype ['base_hp'] + lvl * 3) + random.randint (0, 3);
	var atk = (archetype ['base_attack'] + lvl) + random.randint (0, 2);
	var defense = archetype ['base_defense'] + Math.floor (lvl / 3);
	var xp_reward = (archetype ['xp_reward'] + lvl * 10) + random.randint (0, 10);
	var gold_reward = (archetype ['gold_reward'] + lvl * 3) + random.randint (0, 6);
	return Enemy ('{} (Lv {})'.format (archetype ['name'], lvl), archetype ['ascii'], lvl, max_hp, max_hp, atk, defense, xp_reward, gold_reward);
};
export var calc_damage = function (attacker_atk, defender_def) {
	var base = attacker_atk - defender_def;
	var roll = random.randint (-(1), 2);
	return max (1, base + roll);
};
export var SPELLS = dict ({'Firebolt': dict ({'mp': 4, 'pow': 6}), 'Heal': dict ({'mp': 5, 'pow': 10}), 'Ice Shard': dict ({'mp': 7, 'pow': 9}), 'Shock': dict ({'mp': 6, 'pow': 5}), 'Regen': dict ({'mp': 5, 'pow': 3}), 'Guard Break': dict ({'mp': 4, 'pow': 2})});

//# sourceMappingURL=combat.map