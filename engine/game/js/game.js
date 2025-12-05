// Transcrypt'ed from Python, 2025-12-04 16:09:33
var random = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, delattr, dict, dir, divmod, filter, float, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {GameLog} from './game_log.js';
import {_Actions} from './action.js';
import {GameState} from './game_state.js';
import {_clamp_int, _enemy_defense_effect, _hp_line} from './util.js';
import {render_room} from './ascii_renderer.js';
import {SPELLS, calc_damage, generate_enemy} from './combat.js';
import {Tile, World} from './world.js';
import {Player, clamp, xp_to_next_level} from './player.js';
import {Weapon} from './weapon.js';
import {Armor} from './armor.js';
import {Enemy as EnemyModel} from './enemy.js';
import {Player as PlayerModel} from './player.js';
import * as __module_random__ from './random.js';
__nest__ (random, '', __module_random__);
var __name__ = '__main__';
export var Game =  __class__ ('Game', [object], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, world, player, x, y) {
		self.world = world;
		self.player = player;
		self.x = x;
		self.y = y;
		self.explored = set ();
		self._mark_explored (self.x, self.y);
		self.actions = _Actions (self);
		self.state = GameState.EXPLORING;
		self.enemy = null;
		self._combat_log = [];
		self._player_regen_turns = 0;
		self._player_regen_amount = 0;
		self._enemy_stunned_turns = 0;
		self._enemy_def_down = 0;
		self._enemy_def_turns = 0;
		self.pending_move = null;
		self.question = '';
		self.pending_weapon = null;
		self.pending_move = null;
		self.ended = false;
		self.log = GameLog ();
		self.shop_items = null;
		self.save_file = null;
		self.save_fn = (function __lambda__ () {
			return 'Save game not implemented.';
		});
		self.load_fn = (function __lambda__ () {
			return false;
		});
		self.ascii_tiles = true;
		self.data_loader = (function __lambda__ () {
			return null;
		});
		self.ascii_loader = (function __lambda__ () {
			return null;
		});
		self.enemy_archetypes = [];
	});},
	get load_configurations () {return __get__ (this, function (self, enemies) {
		self.enemy_archetypes = self.data_loader.load (enemies);
	});},
	get current_tile () {return __get__ (this, function (self) {
		return self.world.get_tile (self.x, self.y);
	});},
	get new_random () {return function (size, tileset, seed) {
		if (typeof seed == 'undefined' || (seed != null && seed.hasOwnProperty ("__kwargtrans__"))) {;
			var seed = null;
		};
		var w = World.generate_random (size, tileset, seed);
		var cx = Math.floor (w.width / 2);
		var cy = Math.floor (w.height / 2);
		return Game (__kwargtrans__ ({world: w, player: Player (__kwargtrans__ ({py_name: 'Hero', level: 1, xp: 0, gold: 50, max_hp: 20, hp: 20, max_mp: 10, mp: 10, attack: 5, defense: 2, potions: 1, known_spells: [], weapon: Weapon (__kwargtrans__ ({py_name: 'Wooden Sword', attack_bonus: 2})), armor: Armor (__kwargtrans__ ({py_name: 'Cloth Armor', defense_bonus: 1}))})), x: cx, y: cy}));
	};},
	get help_text () {return __get__ (this, function (self) {
		var actions = self.available_actions ();
		var lines = ['Available actions:'];
		for (var act of actions) {
			var label = act.py_get ('label', act.py_get ('id', ''));
			var hotkeys = (act.py_get ('hotkeys') ? ' [{}]'.format (', '.join (act.py_get ('hotkeys', []))) : '');
			var enabled = (act.py_get ('enabled', true) ? '' : ' (disabled)');
			var reason = (!(act.py_get ('enabled', true)) && act.py_get ('reason') ? ' — {}'.format (act ['reason']) : '');
			lines.append ('  - {}{}{}{}'.format (label, hotkeys, enabled, reason));
		}
		return '\n'.join (lines);
	});},
	get get_log () {return __get__ (this, function (self) {
		return '{}'.format (self.log);
	});},
	get save_game () {return __get__ (this, function (self, filename) {
		if (typeof filename == 'undefined' || (filename != null && filename.hasOwnProperty ("__kwargtrans__"))) {;
			var filename = null;
		};
		var file = (filename ? filename : self.save_file);
		var result = self.save_fn (self.to_dict (), file);
		return result;
	});},
	get restart_game () {return __get__ (this, function (self) {
		var fresh = Game.new_random (__kwargtrans__ ({size: self.world.get_size ()}));
		self.copy_from (fresh);
		var message = 'Game restarted.';
		message += '\n' + self.look ();
		return message;
	});},
	get load_game () {return __get__ (this, function (self, filename) {
		if (typeof filename == 'undefined' || (filename != null && filename.hasOwnProperty ("__kwargtrans__"))) {;
			var filename = null;
		};
		var loaded = self.load_fn ((filename ? filename : self.save_file));
		if (loaded) {
			self.copy_from (Game.from_dict (loaded));
			var message = 'Game loaded.';
		}
		else {
			var message = 'No save found or save file invalid.';
		}
		return message;
	});},
	get quit_game () {return __get__ (this, function (self) {
		self.ended = true;
		var message = 'Game ended by player.';
		return message;
	});},
	get execute_question () {return __get__ (this, function (self, answer) {
		if (self.state != GameState.ASKING_QUESTION) {
			return 'No question pending.';
		}
		if (self.pending_move) {
			return self.execute_pending_move (answer);
		}
		if (self.pending_weapon) {
			if (answer) {
				self.player.weapon = self.pending_weapon;
				var response = 'You equip the {}.'.format (self.pending_weapon.py_name);
			}
			else {
				var response = 'You leave the weapon behind.';
			}
			delete self.pending_weapon;
			self.change_state (GameState.EXPLORING);
			return response;
		}
		else {
			return 'No question pending.';
		}
	});},
	get move () {return __get__ (this, function (self, dx, dy, ask) {
		self.log.add_entry ('Attempting to move from ({},{}) by delta ({},{})'.format (self.x, self.y, dx, dy));
		var nx = clamp (self.x + dx, 0, self.world.width - 1);
		var ny = clamp (self.y + dy, 0, self.world.height - 1);
		if (nx == self.x && ny == self.y) {
			return "You can't go that way.";
		}
		var dest_tile = self.world.get_tile (nx, ny);
		dest_tile.weather.change ();
		try {
			var danger_threshold = 0.6;
			if ((!(dest_tile.safe) && dest_tile.danger >= danger_threshold) && ask) {
				self.change_state (GameState.ASKING_QUESTION);
				self.pending_move = tuple ([nx, ny]);
				self.question = "Warning: '{}' seems very dangerous (danger {}). Proceed? [y/N]".format (dest_tile.py_name, dest_tile.danger);
				return self.question;
			}
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				// pass;
			}
			else {
				throw __except0__;
			}
		}
		self.change_state (GameState.EXPLORING);
		var weather_move_mod = self.current_tile ().weather.effect ().py_get ('movement_penalty', 0);
		if (weather_move_mod > 0 && random.random () < min (0.5, 0.1 * weather_move_mod)) {
			var desc = "f{} and can't move this turn!".format (self.current_tile ().weather.stuck_message ());
		}
		else {
			var __left0__ = tuple ([nx, ny]);
			self.x = __left0__ [0];
			self.y = __left0__ [1];
			self._mark_explored (self.x, self.y);
			var tile = self.current_tile ();
			var art = (self.ascii_tiles ? render_room (tile, self.ascii_loader) : '');
			var desc = '{}\nYou arrive at {}. {}'.format (art, tile.py_name, tile.description);
			if (tile.shop) {
				desc += '\nYou see a merchant here (type shop to enter).';
			}
		}
		var tile = self.current_tile ();
		var weather_enc_mod = tile.weather.effect ().py_get ('encounter_rate', 0.0);
		if (!(tile.safe) && random.random () < tile.danger + weather_enc_mod) {
			var enemy = generate_enemy (self.enemy_archetypes, self.player.level, self.x, self.y);
			var intro = self.enter_combat (enemy);
			return (desc + '\n\n') + intro;
		}
		try {
			var found = self._maybe_field_find (tile);
			if (found) {
				desc += '\n\n' + found;
			}
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				// pass;
			}
			else {
				throw __except0__;
			}
		}
		return desc;
	});},
	get execute_pending_move () {return __get__ (this, function (self, confirm) {
		if (self.state != GameState.ASKING_QUESTION || !(hasattr (self, 'pending_move'))) {
			return 'No move pending confirmation.';
		}
		if (confirm) {
			var __left0__ = self.pending_move;
			var nx = __left0__ [0];
			var ny = __left0__ [1];
			delete self.pending_move;
			self.change_state (GameState.EXPLORING);
			return self.move (nx - self.x, ny - self.y, false);
		}
		else {
			delete self.pending_move;
			self.change_state (GameState.EXPLORING);
			return 'You decide not to proceed there.';
		}
	});},
	get look () {return __get__ (this, function (self) {
		if (self.state == GameState.COMBAT) {
			return self._combat_status ();
		}
		if (self.state == GameState.SHOP) {
			return self.shop ('');
		}
		if (self.state == GameState.ASKING_QUESTION) {
			return self.question;
		}
		if (self.state == GameState.GAME_OVER) {
			return 'Game Over. You can load a saved game or restart.';
		}
		var t = self.current_tile ();
		var art = (self.ascii_tiles ? render_room (t, self.ascii_loader) : '');
		return '{}\n{}: {} \n{}'.format (art, t.py_name, t.description, (t.shop ? 'You see a merchant here (type shop to enter).' : ''));
	});},
	get available_actions () {return __get__ (this, function (self) {
		return self.actions.available ();
	});},
	get execute_action () {return __get__ (this, function (self, action_id_or_key) {
		var log = self.actions.execute (action_id_or_key);
		self.log.add_entry (log);
		return log;
	});},
	get _mark_explored () {return __get__ (this, function (self, x, y) {
		try {
			self.explored.add (tuple ([int (x), int (y)]));
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				// pass;
			}
			else {
				throw __except0__;
			}
		}
	});},
	get map () {return __get__ (this, function (self) {
		var rows = [];
		for (var y = 0; y < self.world.height; y++) {
			var line_chars = [];
			for (var x = 0; x < self.world.width; x++) {
				if (x == self.x && y == self.y) {
					var ch = '@';
				}
				else if (__in__ (tuple ([x, y]), self.explored)) {
					var ch = '.';
				}
				else {
					var ch = '?';
				}
				line_chars.append (ch);
			}
			rows.append (''.join (line_chars));
		}
		var title = 'Map ({}x{}) — @ you, . explored, ? unknown'.format (self.world.width, self.world.height);
		return (title + '\n') + '\n'.join (rows);
	});},
	get stats () {return __get__ (this, function (self) {
		var p = self.player;
		return '{} Lv {}\nXP: {}/{} | Gold: {}\nHP: {}/{} | MP: {}/{} | ATK: {} | DEF: {} | Potions: {} | Spells: {}\nWeapon: {}\nArmor: {}\nSpells Known: {}\nLocation: ({},{}) - {}\nState: {}'.format (p.py_name, p.level, p.xp, xp_to_next_level (p.level), p.gold, p.hp, p.max_hp, p.mp, p.max_mp, p.attack, p.defense, p.potions, len ((function () {
			var __accu0__ = [];
			for (var s of p.known_spells) {
				if (__in__ (s, SPELLS)) {
					__accu0__.append (s);
				}
			}
			return __accu0__;
		}) ()), (p.weapon ? p.weapon : 'None'), (p.armor ? p.armor : 'None'), (p.known_spells ? ', '.join (p.known_spells) : 'None'), self.x, self.y, self.current_tile ().py_name, self.state);
	});},
	get shop_exit () {return __get__ (this, function (self) {
		self.change_state (GameState.EXPLORING);
		return 'You leave the shop.\n' + self.look ();
	});},
	get shop_enter () {return __get__ (this, function (self) {
		var tile = self.current_tile ();
		if (!(getattr (tile, 'shop', false))) {
			return 'There is no shop here.';
		}
		return 'You enter the shop!\n' + self.shop ('');
	});},
	get shop () {return __get__ (this, function (self, selection) {
		var tile = self.current_tile ();
		if (!(getattr (tile, 'shop', false))) {
			return 'There is no shop here.';
		}
		var spells = dict ({'Firebolt': 25, 'Heal': 30, 'Ice Shard': 45, 'Shock': 40, 'Regen': 35, 'Guard Break': 30});
		var available = (function () {
			var __accu0__ = [];
			for (var s of spells.py_keys ()) {
				if (__in__ (s, SPELLS) && !__in__ (s, self.player.known_spells)) {
					__accu0__.append (s);
				}
			}
			return __accu0__;
		}) ();
		self.shop_items = (function () {
			var __accu0__ = [];
			for (var s of available) {
				__accu0__.append ([s, spells [s]]);
			}
			return dict (__accu0__);
		}) ();
		self.change_state (GameState.SHOP);
		if (!(available)) {
			return "The merchant smiles: 'You've learned all I can teach you for now.'";
		}
		if (selection === null || selection == '') {
			var lines = ["\nMerchant's Caravan — Spells for sale:"];
			for (var [idx, py_name] of py_enumerate (available, 1)) {
				lines.append ('  {}. {} — {}g (MP {})'.format (idx, py_name, spells [py_name], SPELLS [py_name] ['mp']));
			}
			lines.append ('Player gold: {}'.format (self.player.gold));
			lines.append ('Type a number or spell name to buy, or press Enter to leave.');
			return '\n'.join (lines);
		}
		var sel = null;
		if (selection.isdigit ()) {
			var i = int (selection) - 1;
			if ((0 <= i && i < len (available))) {
				var sel = available [i];
			}
		}
		else {
			for (var s of available) {
				if (s.lower () == selection.lower ()) {
					var sel = s;
					break;
				}
			}
		}
		if (!(sel)) {
			return "The merchant shrugs. 'I don't have that.'";
		}
		var price = spells [sel];
		if (self.player.gold < price) {
			return "You don't have enough gold.";
		}
		self.player.gold -= price;
		self.player.known_spells = list (self.player.known_spells) + [sel];
		return 'You learn the spell {}!'.format (sel);
	});},
	get rest () {return __get__ (this, function (self) {
		var tile = self.current_tile ();
		if (tile.safe) {
			var healed = self.player.heal (8 + self.player.level * 2);
			if (random.random () < 0.15) {
				self.player.potions++;
				return 'You rest at the village and heal {} HP. The healer gifts you a potion.'.format (healed);
			}
			return 'You rest at the village and heal {} HP.'.format (healed);
		}
		else {
			var healed = self.player.heal (4 + self.player.level);
			var note = 'You rest cautiously and heal {} HP.'.format (healed);
			if (random.random () < min (0.2 + tile.danger / 2, 0.75)) {
				var enemy = generate_enemy (self.player.level, self.x, self.y);
				note += '\nYou are ambushed in your sleep!';
				var intro = self.enter_combat (enemy);
				return (note + '\n\n') + intro;
			}
			return note;
		}
	});},
	get debug_pos () {return __get__ (this, function (self) {
		return 'Pos: ({},{})'.format (self.x, self.y);
	});},
	get to_dict () {return __get__ (this, function (self) {
		var p = self.player;
		return dict ({'player': dict ({'name': p.py_name, 'level': p.level, 'xp': p.xp, 'gold': p.gold, 'max_hp': p.max_hp, 'hp': p.hp, 'max_mp': p.max_mp, 'mp': p.mp, 'attack': p.attack, 'defense': p.defense, 'potions': p.potions, 'known_spells': list (p.known_spells), 'weapon': (p.weapon ? dict ({'name': p.weapon.py_name, 'attack_bonus': p.weapon.attack_bonus}) : null), 'armor': (p.armor ? dict ({'name': p.armor.py_name, 'defense_bonus': p.armor.defense_bonus}) : null)}), 'world': self.world.to_dict (), 'pos': dict ({'x': self.x, 'y': self.y}), 'explored': (function () {
			var __accu0__ = [];
			for (var [x, y] of sorted (self.explored)) {
				__accu0__.append ([x, y]);
			}
			return __accu0__;
		}) (), 'state': str (self.state), 'combat': (self.state == GameState.COMBAT ? dict ({'enemy': (self.enemy ? self.enemy.to_4dict () : null), 'regen_turns': self._player_regen_turns, 'regen_amount': self._player_regen_amount, 'enemy_stunned': self._enemy_stunned_turns, 'enemy_def_down': self._enemy_def_down, 'enemy_def_turns': self._enemy_def_turns}) : null)});
	});},
	get from_dict () {return function (d) {
		var w = World.from_dict (d ['world']);
		var pd = d ['player'];
		var wpn_d = pd.py_get ('weapon');
		var arm_d = pd.py_get ('armor');
		var wpn_obj = (isinstance (wpn_d, dict) ? Weapon (__kwargtrans__ ({py_name: wpn_d ['name'], attack_bonus: int (wpn_d ['attack_bonus'])})) : null);
		var arm_obj = (isinstance (arm_d, dict) ? Armor (__kwargtrans__ ({py_name: arm_d ['name'], defense_bonus: int (arm_d ['defense_bonus'])})) : null);
		var p = PlayerModel (__kwargtrans__ ({py_name: pd ['name'], level: int (pd ['level']), xp: int (pd ['xp']), gold: int (pd ['gold']), max_hp: int (pd ['max_hp']), hp: int (pd ['hp']), max_mp: int (pd.py_get ('max_mp', 10)), mp: int (pd.py_get ('mp', pd.py_get ('max_mp', 10))), attack: int (pd ['attack']), defense: int (pd ['defense']), potions: int (pd.py_get ('potions', 0)), known_spells: pd.py_get ('known_spells', tuple ([])), weapon: wpn_obj, armor: arm_obj}));
		var pos = d.py_get ('pos', dict ({'x': 0, 'y': 0}));
		var x = int (pos.py_get ('x', 0));
		var y = int (pos.py_get ('y', 0));
		var g = Game (__kwargtrans__ ({world: w, player: p, x: x, y: y}));
		var explored_list = d.py_get ('explored') || [];
		try {
			for (var item of explored_list) {
				if (isinstance (item, tuple ([list, tuple])) && len (item) == 2) {
					var __left0__ = tuple ([int (item [0]), int (item [1])]);
					var gx = __left0__ [0];
					var gy = __left0__ [1];
					if ((0 <= gx && gx < w.width) && (0 <= gy && gy < w.height)) {
						g._mark_explored (gx, gy);
					}
				}
			}
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				// pass;
			}
			else {
				throw __except0__;
			}
		}
		g._mark_explored (g.x, g.y);
		g.state = str (d.py_get ('state') || GameState.EXPLORING);
		var cmb = d.py_get ('combat') || null;
		try {
			if (isinstance (cmb, dict) && cmb.py_get ('enemy')) {
				var ed = cmb ['enemy'];
				g.enemy = EnemyModel (__kwargtrans__ ({py_name: ed ['name'], ascii: ed ['ascii'], level: int (ed ['level']), max_hp: int (ed ['max_hp']), hp: int (ed ['hp']), attack: int (ed ['attack']), defense: int (ed ['defense']), xp_reward: int (ed ['xp_reward']), gold_reward: int (ed ['gold_reward'])}));
				g._player_regen_turns = int (cmb.py_get ('regen_turns', 0));
				g._player_regen_amount = int (cmb.py_get ('regen_amount', 0));
				g._enemy_stunned_turns = int (cmb.py_get ('enemy_stunned', 0));
				g._enemy_def_down = int (cmb.py_get ('enemy_def_down', 0));
				g._enemy_def_turns = int (cmb.py_get ('enemy_def_turns', 0));
			}
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				// pass;
			}
			else {
				throw __except0__;
			}
		}
		return g;
	};},
	get copy_from () {return __get__ (this, function (self, other) {
		self.world = other.world;
		self.player = other.player;
		self.x = other.x;
		self.y = other.y;
		try {
			self.explored = set (other.explored);
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				self.explored = new set ([tuple ([self.x, self.y])]);
			}
			else {
				throw __except0__;
			}
		}
		self.state = other.state;
		self.enemy = other.enemy;
		self._player_regen_turns = other._player_regen_turns;
		self._player_regen_amount = other._player_regen_amount;
		self._enemy_stunned_turns = other._enemy_stunned_turns;
		self._enemy_def_down = other._enemy_def_down;
		self._enemy_def_turns = other._enemy_def_turns;
		self.available_actions ();
	});},
	get change_state () {return __get__ (this, function (self, state) {
		self.state = state;
		self.actions.available ();
	});},
	get _weapon_pool () {return __get__ (this, function (self) {
		return [Weapon ('Rusty Dagger', 1), Weapon ('Wooden Sword', 2), Weapon ('Iron Sword', 3), Weapon ('Steel Axe', 4), Weapon ("Knight's Blade", 5), Weapon ('Runed Spear', 6)];
	});},
	get _random_weapon_for_level () {return __get__ (this, function (self) {
		var pool = self._weapon_pool ();
		var idx = min (len (pool) - 1, max (0, Math.floor ((self.player.level - 1) / 2) + random.randint (-(1), 1)));
		var choices = pool.__getslice__ (max (0, idx - 1), min (len (pool), idx + 2), 1) || pool;
		return random.choice (choices);
	});},
	get _offer_weapon_pickup () {return __get__ (this, function (self, found, source) {
		var cur = self.player.weapon;
		var cur_bonus = (cur ? cur.attack_bonus : 0);
		var diff = found.attack_bonus - cur_bonus;
		self.pending_weapon = found;
		self.change_state (GameState.ASKING_QUESTION);
		self.question = 'You find {} (ATK +{}) from {}.'.format (found.py_name, found.attack_bonus, source);
		self.question += (cur ? '\nCurrent: {} (ATK +{}).'.format (cur.py_name, cur.attack_bonus) : '\nYou have no weapon equipped.');
		self.question += '\nIt seems {}. Take it? [y/N]'.format ((diff > 0 ? 'better' : (diff == 0 ? 'the same' : 'worse')));
		return self.question;
	});},
	get _maybe_field_find () {return __get__ (this, function (self, tile) {
		var base = (tile.safe ? 0.03 : 0.1);
		var visibility_mod = tile.weather.effect ().py_get ('visibility', 1.0);
		if (random.random () < base * visibility_mod) {
			var wpn = self._random_weapon_for_level ();
			return self._offer_weapon_pickup (wpn, 'the area');
		}
		return '';
	});},
	get _maybe_offer_weapon () {return __get__ (this, function (self, source) {
		var drop_chance = 0.25;
		if (random.random () < drop_chance) {
			var wpn = self._random_weapon_for_level ();
			self._offer_weapon_pickup (wpn, source);
		}
	});},
	get enter_combat () {return __get__ (this, function (self, enemy) {
		self.change_state (GameState.COMBAT);
		self.enemy = enemy;
		self._combat_log = [];
		self._enemy_stunned_turns = 0;
		self._enemy_def_down = 0;
		self._enemy_def_turns = 0;
		var intro = 'A {} appears! Prepare for battle.'.format (enemy.py_name);
		return (intro + '\n') + self._combat_status ();
	});},
	get _combat_status () {return __get__ (this, function (self) {
		if (!(self.enemy)) {
			return '';
		}
		var e = self.enemy;
		var lines = [_hp_line ('You', self.player.hp, self.player.max_hp) + ' | MP {}/{}'.format (self.player.mp, self.player.max_mp), _hp_line (e.py_name, e.hp, e.max_hp), '\n{}\n'.format (e.ascii), '[Enemy Stats] ATK: {} | DEF: {}'.format (e.attack, e.defense)];
		return '\n'.join (lines);
	});},
	get _end_combat () {return __get__ (this, function (self, victory) {
		var out_lines = [];
		if (victory) {
			var e = self.enemy;
			if (e) {
				self.player.gold += max (0, int (e.gold_reward));
				out_lines.append ('You defeated {}! You loot {} gold.'.format (e.py_name, e.gold_reward));
				var notes = self.player.add_xp (max (0, int (e.xp_reward)));
				out_lines.extend (notes);
				try {
					self._maybe_offer_weapon ('the fallen {}'.format (e.py_name));
				}
				catch (__except0__) {
					if (isinstance (__except0__, Exception)) {
						// pass;
					}
					else {
						throw __except0__;
					}
				}
			}
		}
		else {
			out_lines.append ('You were defeated...');
		}
		self.enemy = null;
		self._player_regen_turns = 0;
		self._player_regen_amount = 0;
		self._enemy_stunned_turns = 0;
		self._enemy_def_down = 0;
		self._enemy_def_turns = 0;
		if (!(self.player.is_alive ())) {
			self.change_state (GameState.GAME_OVER);
			return '\n'.join (out_lines);
		}
		self.change_state (GameState.EXPLORING);
		return '\n'.join (out_lines);
	});},
	get _player_regen_tick () {return __get__ (this, function (self) {
		if (self._player_regen_turns > 0 && self._player_regen_amount > 0) {
			var healed = self.player.heal (self._player_regen_amount);
			self._player_regen_turns--;
			return 'Regen restores {} HP.'.format (healed);
		}
		return null;
	});},
	get _enemy_turn () {return __get__ (this, function (self) {
		var msgs = [];
		if (!(self.enemy)) {
			return msgs;
		}
		var e = self.enemy;
		if (self._enemy_stunned_turns > 0) {
			msgs.append ('{} is stunned and cannot act!'.format (e.py_name));
			self._enemy_stunned_turns--;
		}
		else {
			var dmg = calc_damage (int (e.attack), int (self.player.total_defense));
			var dmg = max (1, dmg);
			self.player.hp = _clamp_int (self.player.hp - dmg, 0, self.player.max_hp);
			msgs.append ('{} strikes you for {} damage.'.format (e.py_name, dmg));
		}
		if (self._enemy_def_turns > 0) {
			self._enemy_def_turns--;
			if (self._enemy_def_turns == 0 && self._enemy_def_down > 0) {
				msgs.append ("The enemy's defenses recover.");
				self._enemy_def_down = 0;
			}
		}
		var reg = self._player_regen_tick ();
		if (reg) {
			msgs.append (reg);
		}
		if (!(self.player.is_alive ())) {
			msgs.append (self._end_combat (false));
		}
		return msgs;
	});},
	get combat_attack () {return __get__ (this, function (self) {
		if (self.state != GameState.COMBAT || !(self.enemy)) {
			return "There's nothing to attack.";
		}
		var e = self.enemy;
		var eff_def = _enemy_defense_effect (int (e.defense), self._enemy_def_down, self._enemy_def_turns);
		var dmg = calc_damage (int (self.player.total_attack), eff_def);
		e.hp = _clamp_int (e.hp - dmg, 0, e.max_hp);
		var msgs = ['You strike the {} for {} damage.'.format (e.py_name, dmg)];
		if (e.hp <= 0) {
			msgs.append (self._end_combat (true));
			return '\n'.join ((function () {
				var __accu0__ = [];
				for (var m of msgs) {
					if (m) {
						__accu0__.append (m);
					}
				}
				return __accu0__;
			}) ());
		}
		msgs.extend (self._enemy_turn ());
		msgs.append (self._combat_status ());
		return '\n'.join ((function () {
			var __accu0__ = [];
			for (var m of msgs) {
				if (m) {
					__accu0__.append (m);
				}
			}
			return __accu0__;
		}) ());
	});},
	get combat_cast () {return __get__ (this, function (self, spell) {
		if (self.state != GameState.COMBAT || !(self.enemy)) {
			return "You can't cast that now.";
		}
		if (!__in__ (spell, SPELLS)) {
			return "You don't know that spell.";
		}
		var cost = int (SPELLS [spell] ['mp']);
		if (self.player.mp < cost) {
			return 'Not enough MP!';
		}
		self.player.mp -= cost;
		var e = self.enemy;
		var msgs = [];
		var power = int (SPELLS [spell] ['pow']);
		if (spell == 'Heal') {
			var healed = self.player.heal (power + self.player.level);
			msgs.append ('You cast Heal and restore {} HP.'.format (healed));
		}
		else if (spell == 'Regen') {
			self._player_regen_turns = 3;
			self._player_regen_amount = power;
			msgs.append ("You cast Regen. You'll recover {} HP for 3 turns.".format (power));
		}
		else if (spell == 'Guard Break') {
			self._enemy_def_down = power + Math.floor (self.player.level / 4);
			self._enemy_def_turns = 2;
			msgs.append ("You cast Guard Break! The enemy's defenses falter.");
		}
		else {
			var dmg = max (1, ((power + Math.floor (self.player.level / 2)) + random.randint (0, 2)) - Math.floor (int (e.defense) / 4));
			e.hp = _clamp_int (e.hp - dmg, 0, e.max_hp);
			msgs.append ('You cast {}! It hits {} for {} damage.'.format (spell, e.py_name, dmg));
			if (e.hp <= 0) {
				msgs.append (self._end_combat (true));
				return '\n'.join ((function () {
					var __accu0__ = [];
					for (var m of msgs) {
						if (m) {
							__accu0__.append (m);
						}
					}
					return __accu0__;
				}) ());
			}
		}
		msgs.extend (self._enemy_turn ());
		msgs.append (self._combat_status ());
		return '\n'.join ((function () {
			var __accu0__ = [];
			for (var m of msgs) {
				if (m) {
					__accu0__.append (m);
				}
			}
			return __accu0__;
		}) ());
	});},
	get combat_potion () {return __get__ (this, function (self) {
		if (self.state != GameState.COMBAT) {
			return "You don't need to use a potion now.";
		}
		if (self.player.potions <= 0) {
			return 'You have no potions.';
		}
		self.player.potions--;
		var healed = self.player.heal (12 + self.player.level);
		var msgs = ['You quaff a potion and recover {} HP.'.format (healed)];
		msgs.extend (self._enemy_turn ());
		msgs.append (self._combat_status ());
		return '\n'.join ((function () {
			var __accu0__ = [];
			for (var m of msgs) {
				if (m) {
					__accu0__.append (m);
				}
			}
			return __accu0__;
		}) ());
	});},
	get combat_flee () {return __get__ (this, function (self) {
		if (self.state != GameState.COMBAT || !(self.enemy)) {
			return 'There is nothing to flee from.';
		}
		var chance = 0.5;
		try {
			if (self.enemy.level > self.player.level) {
				var chance = 0.35;
			}
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				// pass;
			}
			else {
				throw __except0__;
			}
		}
		if (random.random () < chance) {
			self.change_state (GameState.EXPLORING);
			self.enemy = null;
			self._player_regen_turns = 0;
			self._player_regen_amount = 0;
			self._enemy_stunned_turns = 0;
			self._enemy_def_down = 0;
			self._enemy_def_turns = 0;
			return 'You successfully flee back to safety.';
		}
		else {
			var msgs = ['You fail to flee!'];
			msgs.extend (self._enemy_turn ());
			msgs.append (self._combat_status ());
			return '\n'.join ((function () {
				var __accu0__ = [];
				for (var m of msgs) {
					if (m) {
						__accu0__.append (m);
					}
				}
				return __accu0__;
			}) ());
		}
	});}
});

//# sourceMappingURL=game.map