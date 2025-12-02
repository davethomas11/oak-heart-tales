// Transcrypt'ed from Python, 2025-12-01 16:29:57
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
var __name__ = 'player';
export var clamp = function (val, lo, hi) {
	return max (lo, min (hi, val));
};
export var xp_to_next_level = function (level) {
	return 50 + (level * level) * 25;
};
export var Player =  __class__ ('Player', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, py_name, level, hp, max_hp, mp, max_mp, attack, defense, potions, known_spells, gold, weapon, armor, xp) {
		if (typeof xp == 'undefined' || (xp != null && xp.hasOwnProperty ("__kwargtrans__"))) {;
			var xp = 0;
		};
		self.py_name = py_name;
		self.level = level;
		self.hp = hp;
		self.max_hp = max_hp;
		self.mp = mp;
		self.max_mp = max_mp;
		self.attack = attack;
		self.defense = defense;
		self.potions = potions;
		self.known_spells = known_spells;
		self.gold = gold;
		self.weapon = weapon;
		self.armor = armor;
		self.xp = xp;
	});},
	get is_alive () {return __get__ (this, function (self) {
		return self.hp > 0;
	});},
	get heal () {return __get__ (this, function (self, amount) {
		var old = self.hp;
		self.hp = clamp (self.hp + amount, 0, self.max_hp);
		return self.hp - old;
	});},
	get restore_mp () {return __get__ (this, function (self, amount) {
		var old = self.mp;
		self.mp = clamp (self.mp + int (amount), 0, self.max_mp);
		return self.mp - old;
	});},
	get add_xp () {return __get__ (this, function (self, amount) {
		var notes = [];
		self.xp += amount;
		notes.append ('You gain {} XP.'.format (amount));
		while (self.xp >= xp_to_next_level (self.level)) {
			self.xp -= xp_to_next_level (self.level);
			self.level++;
			var hp_gain = 5 + self.level;
			var atk_gain = 1 + Math.floor (self.level / 3);
			var def_gain = (__mod__ (self.level, 2) == 0 ? 1 : 0);
			self.max_hp += hp_gain;
			self.attack += atk_gain;
			self.defense += def_gain;
			self.hp = self.max_hp;
			notes.append ('Level up! You are now level {}. +{} HP, +{} ATK, +{} DEF. HP fully restored!'.format (self.level, hp_gain, atk_gain, def_gain));
		}
		return notes;
	});},
	get _get_total_attack () {return __get__ (this, function (self) {
		return self.attack + (self.weapon ? self.weapon.attack_bonus : 0);
	});},
	get _get_total_defense () {return __get__ (this, function (self) {
		return self.defense + (self.armor ? self.armor.defense_bonus : 0);
	});},
	get to_dict () {return __get__ (this, function (self) {
		return dict ({'name': self.py_name, 'level': self.level, 'hp': self.hp, 'max_hp': self.max_hp, 'mp': self.mp, 'max_mp': self.max_mp, 'attack': self.attack, 'defense': self.defense, 'potions': self.potions, 'known_spells': self.known_spells, 'gold': self.gold, 'weapon': (self.weapon ? self.weapon.py_name : null), 'armor': (self.armor ? self.armor.py_name : null), 'xp': self.xp});
	});}
});
Object.defineProperty (Player, 'total_defense', property.call (Player, Player._get_total_defense));
Object.defineProperty (Player, 'total_attack', property.call (Player, Player._get_total_attack));;

//# sourceMappingURL=player.map