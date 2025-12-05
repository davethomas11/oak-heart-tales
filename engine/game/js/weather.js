// Transcrypt'ed from Python, 2025-12-04 16:09:33
var time = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_time__ from './time.js';
__nest__ (time, '', __module_time__);
var __name__ = 'weather';
export var Weather =  __class__ ('Weather', [object], {
	__module__: __name__,
	TYPES: ['Sunny', 'Rainy', 'Stormy', 'Foggy', 'Snowy'],
	get __init__ () {return __get__ (this, function (self) {
		self.current = self._choice (self.TYPES);
	});},
	get _choice () {return __get__ (this, function (self, py_items) {
		var t = int (time.time () * 1000);
		var idx = __mod__ (t, len (py_items));
		return py_items [idx];
	});},
	get change () {return __get__ (this, function (self) {
		self.current = self._choice (self.TYPES);
	});},
	get effect () {return __get__ (this, function (self) {
		var effects = dict ({'Sunny': dict ({}), 'Rainy': dict ({'visibility': 0.2}), 'Stormy': dict ({'encounter_rate': +(0.2)}), 'Foggy': dict ({'visibility': 0.4}), 'Snowy': dict ({'movement_penalty': +(1)})});
		return effects.py_get (self.current, dict ({}));
	});},
	get stuck_message () {return __get__ (this, function (self) {
		var messages = dict ({'Snowy': 'Snowdrifts block your path '});
		return messages.py_get (self.current, 'The weather is unusual.');
	});},
	get describe () {return __get__ (this, function (self) {
		var descriptions = dict ({'Sunny': 'The sun is shining brightly.', 'Rainy': "It's raining steadily.", 'Stormy': 'A fierce storm is raging.', 'Foggy': 'Thick fog reduces visibility.', 'Snowy': 'Snow is falling gently.'});
		return descriptions.py_get (self.current, 'The weather is indescribable.');
	});}
});

//# sourceMappingURL=weather.map