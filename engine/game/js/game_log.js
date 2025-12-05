// Transcrypt'ed from Python, 2025-12-04 16:09:33
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {datetime} from './datetime.js';
var __name__ = 'game_log';
export var GameLog =  __class__ ('GameLog', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, max_size) {
		if (typeof max_size == 'undefined' || (max_size != null && max_size.hasOwnProperty ("__kwargtrans__"))) {;
			var max_size = 10;
		};
		self.entries = [];
		self.max_size = max_size;
	});},
	get add_entry () {return __get__ (this, function (self, entry) {
		var timestamp = datetime.now ().strftime ('%Y-%m-%d %H:%M:%S');
		self.entries.append (tuple ([timestamp, entry]));
		if (len (self.entries) > self.max_size) {
			self.entries.py_pop (0);
		}
		return entry;
	});},
	get get_recent_entries () {return __get__ (this, function (self, count) {
		if (typeof count == 'undefined' || (count != null && count.hasOwnProperty ("__kwargtrans__"))) {;
			var count = 10;
		};
		return (function () {
			var __accu0__ = [];
			for (var [ts, msg] of self.entries.__getslice__ (-(count), null, 1)) {
				__accu0__.append ('{} - {}'.format (ts, msg));
			}
			return __accu0__;
		}) ();
	});},
	get py_clear () {return __get__ (this, function (self) {
		self.entries.py_clear ();
	});},
	get __str__ () {return __get__ (this, function (self) {
		return '\n'.join ((function () {
			var __accu0__ = [];
			for (var [ts, msg] of self.entries) {
				__accu0__.append ('{} - {}'.format (ts, msg));
			}
			return py_iter (__accu0__);
		}) ());
	});}
});

//# sourceMappingURL=game_log.map