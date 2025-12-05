// Transcrypt'ed from Python, 2025-12-04 16:09:33
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {SPELLS} from './combat.js';
import {GameState} from './game_state.js';
var __name__ = 'action';
export var Action =  __class__ ('Action', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, id, label, hotkeys, category, enabled, reason) {
		if (typeof category == 'undefined' || (category != null && category.hasOwnProperty ("__kwargtrans__"))) {;
			var category = 'general';
		};
		if (typeof enabled == 'undefined' || (enabled != null && enabled.hasOwnProperty ("__kwargtrans__"))) {;
			var enabled = true;
		};
		if (typeof reason == 'undefined' || (reason != null && reason.hasOwnProperty ("__kwargtrans__"))) {;
			var reason = null;
		};
		self.id = id;
		self.label = label;
		self.hotkeys = hotkeys;
		self.category = category;
		self.enabled = enabled;
		self.reason = reason;
	});},
	get to_dict () {return __get__ (this, function (self) {
		return dict ({'id': self.id, 'label': self.label, 'hotkeys': self.hotkeys, 'category': self.category, 'enabled': self.enabled, 'reason': self.reason});
	});}
});
export var _Actions =  __class__ ('_Actions', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, game) {
		self.g = game;
		self._exec_map = dict ({});
		self._key_to_id = dict ({});
	});},
	get available () {return __get__ (this, function (self) {
		var g = self.g;
		var w = g.world;
		var __left0__ = tuple ([g.x, g.y]);
		var x = __left0__ [0];
		var y = __left0__ [1];
		var actions = [];
		if (g.state == GameState.COMBAT) {
			var enemy = g.enemy;
			actions.extend ([Action ('combat_attack', 'Attack', ['attack', 'a'], 'combat'), Action ('combat_potion', 'Use Potion', ['potion', 'p'], 'combat', __kwargtrans__ ({enabled: g.player.potions > 0, reason: (g.player.potions > 0 ? null : 'No potions')})), Action ('combat_flee', 'Flee', ['flee', 'run', 'f'], 'combat'), Action ('look', 'Examine Enemy', ['look', 'l'], 'combat'), Action ('stats', 'Stats', ['stats', 's'], 'combat')]);
			for (var sp of g.player.known_spells) {
				if (__in__ (sp, SPELLS)) {
					var cost = int (SPELLS [sp] ['mp']);
					actions.append (Action (__kwargtrans__ ({id: 'cast::{}'.format (sp.lower ()), label: 'Cast {} (MP {})'.format (sp, cost), hotkeys: ['cast {}'.format (sp).lower ()], category: 'combat', enabled: g.player.mp >= cost, reason: (g.player.mp >= cost ? null : 'Not enough MP')})));
				}
			}
			self._exec_map = dict ({'combat_attack': g.combat_attack, 'combat_potion': g.combat_potion, 'combat_flee': g.combat_flee, 'look': g.look, 'stats': g.stats});
			for (var sp of g.player.known_spells) {
				if (__in__ (sp, SPELLS)) {
					self._exec_map ['cast::{}'.format (sp.lower ())] = (function __lambda__ (s) {
						if (typeof s == 'undefined' || (s != null && s.hasOwnProperty ("__kwargtrans__"))) {;
							var s = sp;
						};
						return g.combat_cast (s);
					});
				}
			}
		}
		else if (g.state == GameState.GAME_OVER) {
			actions.extend ([Action ('game_over_load', 'Load Game', ['load', 'l'], 'game_over'), Action ('game_over_restart', 'Restart Game', ['restart', 'r'], 'game_over')]);
			self._exec_map = dict ({'game_over_load': g.load_game, 'game_over_restart': g.restart_game});
		}
		else if (g.state == GameState.SHOP) {
			var shop = g.shop_items;
			var index = 1;
			for (var item of shop.py_keys ()) {
				actions.append (Action (__kwargtrans__ ({id: 'shop_buy::{}'.format (item), label: 'Buy {} (Gold {})'.format (item, shop [item]), hotkeys: ['buy {}'.format (item).lower (), '{}'.format (index), item], category: 'shop'})));
				index++;
			}
			actions.append (Action ('shop_exit', 'Exit Shop', ['exit', 'e'], 'shop'));
			actions.append (Action ('look', 'View Shop', ['look', 'l'], 'shop'));
			actions.append (Action ('stats', 'Stats', ['stats', 's'], 'shop'));
			self._exec_map = dict ({'shop_exit': g.shop_exit, 'look': g.look, 'stats': g.stats});
			for (var item of shop.py_keys ()) {
				self._exec_map ['shop_buy::{}'.format (item.lower ())] = (function __lambda__ (it) {
					if (typeof it == 'undefined' || (it != null && it.hasOwnProperty ("__kwargtrans__"))) {;
						var it = item;
					};
					return g.shop (it);
				});
			}
		}
		else if (g.state == GameState.START_MENU) {
			actions.extend ([Action ('start_new_game', 'New Game', ['new', 'n'], 'start_menu'), Action ('start_load_game', 'Load Game', ['load', 'l'], 'start_menu'), Action ('start_quit', 'Quit', ['quit', 'q'], 'start_menu')]);
			self._exec_map = dict ({'start_new_game': g.start_new_game, 'start_load_game': g.start_load_game, 'start_quit': g.start_quit});
		}
		else if (g.state == GameState.ASKING_QUESTION) {
			actions.extend ([Action ('answer_yes', 'Yes', ['yes', 'y'], 'question'), Action ('answer_no', 'No', ['no', 'n'], 'question'), Action ('look', 'Examine', ['look', 'l'], 'question'), Action ('stats', 'Stats', ['stats', 's'], 'question')]);
			self._exec_map = dict ({'answer_yes': (function __lambda__ () {
				return g.execute_question (true);
			}), 'answer_no': (function __lambda__ () {
				return g.execute_question (false);
			}), 'look': g.look, 'stats': g.stats});
		}
		else {
			var can_go = function (nx, ny) {
				if (nx < 0 || ny < 0 || nx >= w.width || ny >= w.height) {
					return tuple ([false, 'Edge of the world']);
				}
				return tuple ([true, null]);
			};
			var dirs = [tuple (['move_n', 'North', 'travel', tuple ([0, -(1)]), ['n', 'north', 'ArrowUp']]), tuple (['move_s', 'South', 'travel', tuple ([0, 1]), ['s', 'south', 'ArrowDown']]), tuple (['move_w', 'West', 'travel', tuple ([-(1), 0]), ['w', 'west', 'ArrowLeft', 'a']]), tuple (['move_e', 'East', 'travel', tuple ([1, 0]), ['e', 'east', 'ArrowRight', 'd']])];
			for (var [aid, label, cat, [dx, dy], py_keys] of dirs) {
				var __left0__ = can_go (x + dx, y + dy);
				var ok = __left0__ [0];
				var reason = __left0__ [1];
				actions.append (Action (aid, label, py_keys, cat, ok, reason));
			}
			actions.extend ([Action ('look', 'Look', ['look', 'l'], 'info'), Action ('map', 'Map', ['map', 'm'], 'info'), Action ('stats', 'Stats', ['stats', 'character', 'c'], 'info'), Action ('rest', 'Rest', ['rest', 'r'], 'camp'), Action ('shop', 'Shop', ['shop'], 'town', bool (getattr (g.current_tile (), 'shop', false)), (getattr (g.current_tile (), 'shop', false) ? null : 'No merchant here')), Action ('inventory', 'Inventory', ['inv', 'inventory', 'i'], 'info')]);
			self._exec_map = dict ({'move_n': (function __lambda__ () {
				return g.move (0, -(1), true);
			}), 'move_s': (function __lambda__ () {
				return g.move (0, 1, true);
			}), 'move_w': (function __lambda__ () {
				return g.move (-(1), 0, true);
			}), 'move_e': (function __lambda__ () {
				return g.move (1, 0, true);
			}), 'look': g.look, 'map': g.map, 'stats': g.stats, 'rest': g.rest, 'shop': g.shop_enter, 'inventory': (function __lambda__ () {
				return 'Inventory: Potions x{}; Gold {}'.format (g.player.potions, g.player.gold);
			})});
		}
		actions.extend ([Action ('save_game', 'Save Game', ['save', '!'], 'system'), Action ('help', 'Help', ['help', 'h', '?'], 'system'), Action ('quit_game', 'Quit Game', ['quit', 'q'], 'system'), Action ('log', 'Show Log', ['log', 'g'], 'system')]);
		self._exec_map.py_update (dict ({'save_game': g.save_game, 'help': g.help_text, 'quit_game': g.quit_game, 'log': g.get_log}));
		self._key_to_id = dict ({});
		for (var a of actions) {
			for (var k of a.hotkeys) {
				self._key_to_id [k.lower ()] = a.id;
			}
		}
		return (function () {
			var __accu0__ = [];
			for (var a of actions) {
				__accu0__.append (a.to_dict ());
			}
			return __accu0__;
		}) ();
	});},
	get execute () {return __get__ (this, function (self, action_id_or_key) {
		if (!(action_id_or_key)) {
			return null;
		}
		var key = action_id_or_key.strip ().lower ();
		if (!(self._exec_map)) {
			self.available ();
		}
		var aid = key;
		if (!__in__ (aid, self._exec_map)) {
			var aid = self._key_to_id.py_get (key, key);
		}
		var fn = self._exec_map.py_get (aid);
		if (!(fn)) {
			return null;
		}
		try {
			return fn ();
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				var reason = '';
				return "Action '{}' failed: \n{}".format (aid, reason);
			}
			else {
				throw __except0__;
			}
		}
	});}
});

//# sourceMappingURL=action.map