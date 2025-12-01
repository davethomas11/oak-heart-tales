// Transcrypt'ed from Python, 2025-12-01 10:11:31
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
var __name__ = 'enemy';
export var Enemy =  __class__ ('Enemy', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, py_name, ascii, level, max_hp, hp, attack, defense, xp_reward, gold_reward) {
		self.py_name = py_name;
		self.ascii = ascii;
		self.level = level;
		self.max_hp = max_hp;
		self.hp = hp;
		self.attack = attack;
		self.defense = defense;
		self.xp_reward = xp_reward;
		self.gold_reward = gold_reward;
	});},
	get is_alive () {return __get__ (this, function (self) {
		return self.hp > 0;
	});},
	get to_dict () {return __get__ (this, function (self) {
		return dict ({'name': self.py_name, 'ascii': self.ascii, 'level': self.level, 'max_hp': self.max_hp, 'hp': self.hp, 'attack': self.attack, 'defense': self.defense, 'xp_reward': self.xp_reward, 'gold_reward': self.gold_reward});
	});}
});

//# sourceMappingURL=enemy.map