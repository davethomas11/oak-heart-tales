// Transcrypt'ed from Python, 2025-12-01 10:11:31
var math = {};
var random = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_random__ from './random.js';
__nest__ (random, '', __module_random__);
import * as __module_math__ from './math.js';
__nest__ (math, '', __module_math__);
var __name__ = 'world';
export var Tile =  __class__ ('Tile', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, py_name, description, danger, safe, ascii, shop) {
		if (typeof safe == 'undefined' || (safe != null && safe.hasOwnProperty ("__kwargtrans__"))) {;
			var safe = false;
		};
		if (typeof ascii == 'undefined' || (ascii != null && ascii.hasOwnProperty ("__kwargtrans__"))) {;
			var ascii = null;
		};
		if (typeof shop == 'undefined' || (shop != null && shop.hasOwnProperty ("__kwargtrans__"))) {;
			var shop = false;
		};
		self.py_name = py_name;
		self.description = description;
		self.danger = danger;
		self.safe = safe;
		self.ascii = ascii;
		self.shop = shop;
	});},
	get to_dict () {return __get__ (this, function (self) {
		return dict ({'name': self.py_name, 'description': self.description, 'danger': self.danger, 'safe': self.safe, 'ascii': self.ascii, 'shop': self.shop});
	});},
	get from_dict () {return function (d) {
		return Tile (__kwargtrans__ ({py_name: d ['name'], description: d ['description'], danger: float ((__in__ ('danger', d) ? d ['danger'] : 0.0)), safe: bool ((__in__ ('safe', d) ? d ['safe'] : false)), ascii: d ['ascii'], shop: bool ((__in__ ('shop', d) ? d ['shop'] : false))}));
	};}
});
export var World =  __class__ ('World', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, width, height, grid, seed) {
		if (typeof seed == 'undefined' || (seed != null && seed.hasOwnProperty ("__kwargtrans__"))) {;
			var seed = null;
		};
		self.width = width;
		self.height = height;
		self.grid = grid;
		self.seed = seed;
	});},
	get get_tile () {return __get__ (this, function (self, x, y) {
		return self.grid [y] [x];
	});},
	get to_dict () {return __get__ (this, function (self) {
		return dict ({'width': self.width, 'height': self.height, 'seed': self.seed, 'grid': (function () {
			var __accu0__ = [];
			for (var row of self.grid) {
				__accu0__.append ((function () {
					var __accu1__ = [];
					for (var t of row) {
						__accu1__.append (t.to_dict ());
					}
					return __accu1__;
				}) ());
			}
			return __accu0__;
		}) ()});
	});},
	get get_size () {return __get__ (this, function (self) {
		return self.width;
	});},
	get from_dict () {return function (d) {
		var width = int (d ['width']);
		var height = int (d ['height']);
		var seed = d.py_get ('seed');
		var grid = (function () {
			var __accu0__ = [];
			for (var row of d ['grid']) {
				__accu0__.append ((function () {
					var __accu1__ = [];
					for (var td of row) {
						__accu1__.append (Tile.from_dict (td));
					}
					return __accu1__;
				}) ());
			}
			return __accu0__;
		}) ();
		return World (__kwargtrans__ ({width: width, height: height, grid: grid, seed: seed}));
	};},
	get _default_tileset () {return function () {
		var py_default = dict ({'village': dict ({'name': 'Oakheart Village', 'description': 'Your humble village. A safe haven.', 'danger': 0.0, 'safe': true}), 'tiles': [dict ({'name': 'Western Farms', 'description': 'Abandoned fields overrun with weeds.', 'danger': 0.2}), dict ({'name': 'Old Watchtower', 'description': 'A crumbling tower watches the valleys.', 'danger': 0.3}), dict ({'name': 'Frost Creek', 'description': 'Icy water murmurs over smooth stones.', 'danger': 0.35}), dict ({'name': 'Mire Flats', 'description': 'Boggy ground that sucks at your boots.', 'danger': 0.45}), dict ({'name': 'Gloomwood', 'description': 'Dark trees crowd the path. Eyes watch.', 'danger': 0.55}), dict ({'name': 'Ruined Keep', 'description': 'Broken walls hide shadows and secrets.', 'danger': 0.6}), dict ({'name': 'Northern Ridge', 'description': 'Wind-swept ridge with sparse pines.', 'danger': 0.35}), dict ({'name': 'Eastgate Road', 'description': 'A cobbled road lined with old mileposts.', 'danger': 0.25})]});
		return py_default;
	};},
	get _pseudoRandomSeed () {return __get__ (this, function (seed) {
		var x = math.sin (seed) * 10000;
		var rng = int ((x - math.floor (x)) * 1000000);
		return dict ({'choice': (function __lambda__ (lst) {
			return lst [__mod__ (rng, len (lst))];
		}), 'randrange': (function __lambda__ (a, b) {
			return a + __mod__ (rng, b - a);
		}), 'shuffle': (function __lambda__ (lst) {
			return lst.py_sort (__kwargtrans__ ({key: (function __lambda__ (_) {
				return rng;
			})}));
		})});
	});},
	get generate_random () {return function (size, tileset, seed) {
		if (typeof seed == 'undefined' || (seed != null && seed.hasOwnProperty ("__kwargtrans__"))) {;
			var seed = null;
		};
		if (tileset === null) {
			var tileset = World._default_tileset ();
		}
		if (seed === null) {
			var seed = random.randrange (1, 10000000);
		}
		var rng = World._pseudoRandomSeed (seed);
		var base_tiles = tileset ['tiles'];
		var village_def = tileset ['village'];
		var __left0__ = size;
		var width = __left0__;
		var height = __left0__;
		var cx = Math.floor (width / 2);
		var cy = Math.floor (height / 2);
		var grid = [];
		for (var y = 0; y < height; y++) {
			var row = [];
			for (var x = 0; x < width; x++) {
				if (x == cx && y == cy) {
					row.append (Tile.from_dict (village_def));
					continue;
				}
				var td = rng.choice (base_tiles);
				var dist = abs (x - cx) + abs (y - cy);
				var danger = float ((__in__ ('danger', td) ? td ['danger'] : 0.2));
				var scaled = min (0.8, max (0.0, danger + dist * 0.05));
				row.append (Tile (__kwargtrans__ ({py_name: td ['name'], description: td ['description'], danger: scaled, safe: false, ascii: td ['ascii']})));
			}
			grid.append (row);
		}
		var rng2 = World._pseudoRandomSeed (seed);
		var num_shops = max (1, Math.floor (size / 3));
		var placed = 0;
		var positions = (function () {
			var __accu0__ = [];
			for (var y = 0; y < height; y++) {
				for (var x = 0; x < width; x++) {
					if (!(x == cx && y == cy)) {
						__accu0__.append (tuple ([x, y]));
					}
				}
			}
			return __accu0__;
		}) ();
		rng2.shuffle (positions);
		for (var [sx, sy] of positions) {
			if (placed >= num_shops) {
				break;
			}
			var dist = abs (sx - cx) + abs (sy - cy);
			if (dist < 1) {
				continue;
			}
			var t = grid [sy] [sx];
			grid [sy] [sx] = Tile (__kwargtrans__ ({py_name: "Merchant's Caravan", description: 'A traveling merchant offers wares and wisdom.', danger: 0.0, safe: true, ascii: t.ascii, shop: true}));
			placed++;
		}
		return World (__kwargtrans__ ({width: width, height: height, grid: grid, seed: seed}));
	};}
});

//# sourceMappingURL=world.map