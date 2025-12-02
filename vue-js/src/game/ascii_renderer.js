// Transcrypt'ed from Python, 2025-12-01 16:29:57
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {Tile} from './world.js';
var __name__ = 'ascii_renderer';
export var _box = function (text, title) {
	if (typeof title == 'undefined' || (title != null && title.hasOwnProperty ("__kwargtrans__"))) {;
		var title = null;
	};
	var lines = (text ? text.splitlines () : []);
	var width = max ((function () {
		var __accu0__ = [];
		for (var l of lines) {
			__accu0__.append (len (l));
		}
		return __accu0__;
	}) () + (title ? [len (title)] : [0, 0]));
	var border = ('+' + '-' * (width + 2)) + '+';
	var out = [border];
	if (title) {
		out.append (('| ' + title.ljust (width)) + ' |');
		out.append (('| ' + '-' * width) + ' |');
	}
	for (var l of lines) {
		out.append (('| ' + l.ljust (width)) + ' |');
	}
	out.append (border);
	return '\n'.join (out);
};
export var render_room = function (tile, text_loader) {
	try {
		var fname = tile.ascii;
		if (!(fname)) {
			var fname = tile.py_name.lower ().py_replace (' ', '_') + '.txt';
		}
		var art = text_loader.load (fname);
		if (art) {
			return art;
		}
		return _box ('', __kwargtrans__ ({title: tile.py_name}));
	}
	catch (__except0__) {
		return _box ('', __kwargtrans__ ({title: tile.py_name}));
	}
};

//# sourceMappingURL=ascii_renderer.map