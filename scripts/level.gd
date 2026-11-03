extends Node2D
## Builds the current level (Game.level_id) from res://levels/<id>.txt.
##
## Header lines start with '@' (anywhere in the file):
##   @name Mossgrave Woods            area name for the title card
##   @subtitle Chapter I
##   @theme forest                    tileset, backdrop, particles (see THEMES)
##   @light <dusk> <deep> <from> <to> [x|y]   darkness fades dusk -> deep between tile columns (or rows)
##   @warm <color>                    darkness warms toward this as you share embers (Old Hollow)
##   @glow <color> <cond>             darkness lifts toward this while <cond> holds (the Starwell's sky)
##   @music <id> [<cond> <id> ...]    track; later pairs override while their condition holds
##   @ambience <id>
##   @seed 7                          decoration RNG seed
##   Echoes (playable memories, see Game.start_echo):
##   @echo <id>                       this map is an Echo: memory filter, no Pell, its own embers
##   @hero <skin>  @embers <n>  @lantern <scale>  @ability bell
##   @fear <from_row> <to_row>        fear grows between these rows (Vesper)
##   @char <c> <kind> <args...>       what a character means in this level:
##       npc <id>                           a character from Story.NPCS
##       door <id> <level> <door> [dialogue]   walk in to travel; also an arrival point
##       wickway <id> <level> <door> <depth>   lantern-lift between <depth> and Old Hollow
##       sign <dialogue> [stone]            wooden sign or Keeper tablet
##       trigger <dialogue> [cond]          plays once when walked into
##       end <dialogue>                     the end of the road (for now)
##       hearth                             the Little Hearth of Old Hollow
##       lamp                               a hanging lamp, lit as the Hollow fills
##       hut <npc>                          a round door, lit once <npc> lives here
##       hook                               Keeper lantern-hook (needs the Hook gift)
##       gate <id>                          Keeper eye-gate (3 tiles tall, placed at its top tile)
##       eye <id>                           eye-stone: gate <id> is open only while this is lit
##       prop <texture> [z] [top]           any image from assets/deco
##       great_hearth                       the Hearth at the root of the mountain
##       spot <id>                          a named position (used by cutscenes)
##       caster <shape> [dx dy]             shadow-play plate (boat/fish/bird/moon), hung at its tile's centre (+ px nudge)
##       starlamp                           Keeper star-lamp: light it once, a still light for good
##       orrery <dx> <dy> [speed] [pause]   orrery sun riding a rail <dx>,<dy> tiles long, once lit
##       great_orrery                       the Great Orrery (the Starwell's sky)
##       name <id>                          a Keeper name-stone (JournalData.NAMES)
##       keepsake <id>                      a keepsake (JournalData.KEEPSAKES): lay it in the Little Hearth
##       propif <cond> <texture> [z] [top]  a prop that is only there while <cond> holds
##       landing                            Echo checkpoint: you are sent back here
##       sleeper <npc>                      asleep until Maud's bell rings near, then follows you
##       follower <npc>                     walks behind you from the start (Edda)
##       rising <water|dark> <speed> [now]  rises from this row; starts on event "rising_start"
##       headcount <n> <ok> <not_yet>       lets you by with <n> followers (plays <ok>), else <not_yet>
##       old_hearth                         the Hearth as it was, roaring (Vesper's Echo)
##
## Built-in legend:
##   #  ground (auto-tiled, solid)      w  background wall (no collision)
##   =  one-way platform                |  wooden pillar        o  pillar knob
##   *  glimmer (solid while lit)       %  violet glimmer (wakes only for 3+ embers)
##   ~  cold water (sends you back)     _  shallow water (harmless)
##   &  thorn-root (burns away in a Flare)
##   P  player start                    T  Mossback the totem   S  ember shrine
##   e  ember mote                      g  Mossgrave signpost   x/X  shade / strong shade
##   forest: t/i/y pines  b/B bushes  r/R rocks  m mushrooms  n fern  f flower  v vine
##   cave:   k/K crystals  q violet crystal  a stalagmite  u glow-shrooms  j bones  ^/' stalactites
## Grass tufts and flowers are scattered automatically on forest grass.

const T := 16
const U := 1
const R := 2
const D := 4
const L := 8

const THEMES := {
	"forest": {
		"ground": "res://assets/tiles/forest_ground.png", "wall": "res://assets/tiles/forest_wall.png",
		"backdrop": "res://scenes/backdrops/forest.tscn", "wall_tint": Color(0.52, 0.47, 0.62),
		"particles": "fireflies", "grass": true, "music": "mossgrave", "ambience": "forest",
	},
	"cave": {
		"ground": "res://assets/tiles/cave_ground.png", "wall": "res://assets/tiles/cave_wall.png",
		"backdrop": "res://scenes/backdrops/cave.tscn", "wall_tint": Color(0.52, 0.47, 0.62),
		"particles": "motes", "mote_color": Color(0.55, 0.85, 1.0), "music": "glimmerdeep", "ambience": "cave",
	},
	"drowned": {
		"ground": "res://assets/tiles/drowned_ground.png", "wall": "res://assets/tiles/drowned_wall.png",
		"backdrop": "res://scenes/backdrops/drowned.tscn", "wall_tint": Color(0.48, 0.56, 0.58),
		"particles": "motes", "mote_color": Color(0.85, 0.95, 0.85), "music": "drowned", "ambience": "water",
	},
	"rootdark": {
		"ground": "res://assets/tiles/rootdark_ground.png", "wall": "res://assets/tiles/rootdark_wall.png",
		"backdrop": "res://scenes/backdrops/rootdark.tscn", "wall_tint": Color(0.62, 0.5, 0.62),
		"particles": "motes", "mote_color": Color(0.8, 0.55, 1.0), "music": "rootdark", "ambience": "roots",
	},
	"hearth": {
		"ground": "res://assets/tiles/hearth_ground.png", "wall": "res://assets/tiles/hearth_wall.png",
		"backdrop": "res://scenes/backdrops/hearth.tscn", "wall_tint": Color(0.62, 0.48, 0.5),
		"particles": "cinders", "mote_color": Color(1.0, 0.55, 0.25), "music": "hearth", "ambience": "hearth",
	},
	"starwell": {
		"ground": "res://assets/tiles/starwell_ground.png", "wall": "res://assets/tiles/starwell_wall.png",
		"backdrop": "res://scenes/backdrops/starwell.tscn", "wall_tint": Color(0.5, 0.56, 0.68),
		"particles": "bubbles", "mote_color": Color(0.7, 0.9, 1.0), "music": "starwell", "ambience": "underlake",
	},
}

## char: [texture, z_index, extra y offset, hangs from ceiling]
const PROPS := {
	"t": ["pine_big", -6, 4, false], "i": ["pine_med", -6, 4, false], "y": ["pine_small", -6, 3, false],
	"b": ["bush_a", 3, 2, false], "B": ["bush_b", -2, 2, false], "r": ["rock_a", -2, 1, false],
	"R": ["rock_b", 3, 1, false], "m": ["mushrooms", -2, 1, false], "n": ["fern", 3, 1, false],
	"f": ["flower_0", -2, 1, false],
	"k": ["crystal_small", -2, 1, false], "K": ["crystal_big", -3, 1, false], "q": ["crystal_violet", -2, 1, false],
	"a": ["stalagmite", -3, 1, false], "u": ["cave_shroom", 3, 1, false], "j": ["bones", -2, 1, false],
	"^": ["stalactite_a", -3, 0, true], "'": ["stalactite_b", -3, 0, true],
}
## Props that give off a little light of their own: texture -> [color, energy, scale, y]
const PROP_LIGHTS := {
	"crystal_small": [Color(0.45, 0.8, 1.0), 0.45, 0.5, -6],
	"crystal_big": [Color(0.45, 0.8, 1.0), 0.7, 0.8, -12],
	"crystal_violet": [Color(0.75, 0.5, 1.0), 0.6, 0.6, -8],
	"cave_shroom": [Color(0.55, 1.0, 0.85), 0.4, 0.45, -3],
	"lily": [Color(0.8, 1.0, 0.9), 0.4, 0.45, -2],
	"fungus_tall": [Color(0.75, 0.45, 1.0), 0.6, 0.6, -12],
	"fungus_cluster": [Color(0.75, 0.45, 1.0), 0.45, 0.5, -4],
	"spore_pod": [Color(0.8, 0.5, 1.0), 0.5, 0.5, -5],
	"obsidian": [Color(1.0, 0.35, 0.2), 0.35, 0.45, -8],
	"porthole": [Color(0.5, 0.8, 0.95), 0.4, 0.6, -16],
	"keeper_lamp": [Color(1.0, 0.72, 0.4), 0.75, 0.75, -11],
	"lamp_string": [Color(1.0, 0.75, 0.42), 0.6, 1.1, 10],
	"supper_table": [Color(1.0, 0.7, 0.4), 0.35, 0.5, -14],
}

const SCRIPTS := {
	"T": preload("res://scripts/totem.gd"),
	"S": preload("res://scripts/shrine.gd"),
	"e": preload("res://scripts/ember.gd"),
	"g": preload("res://scripts/signpost.gd"),
}
const NpcScript := preload("res://scripts/npc.gd")
const PellScript := preload("res://scripts/pell.gd")
const DoorScript := preload("res://scripts/door.gd")
const WickwayScript := preload("res://scripts/wickway.gd")
const HearthScript := preload("res://scripts/hearth.gd")
const GlimmerScript := preload("res://scripts/glimmer.gd")
const ShadeScript := preload("res://scripts/shade.gd")
const WaterScript := preload("res://scripts/water.gd")
const ThornScript := preload("res://scripts/thorn.gd")
const HookScript := preload("res://scripts/hook.gd")
const GateScript := preload("res://scripts/gate.gd")
const EyeScript := preload("res://scripts/eye.gd")
const GreatHearthScript := preload("res://scripts/great_hearth.gd")
const CasterScript := preload("res://scripts/caster.gd")
const StarlampScript := preload("res://scripts/starlamp.gd")
const OrreryScript := preload("res://scripts/orrery.gd")
const GreatOrreryScript := preload("res://scripts/great_orrery.gd")
const NameStoneScript := preload("res://scripts/name_stone.gd")
const KeepsakeScript := preload("res://scripts/keepsake.gd")
const LandingScript := preload("res://scripts/landing.gd")
## Echo whispers as fear passes these levels (Vesper).
const WHISPERS := [[0.3, "whisper_1"], [0.55, "whisper_2"], [0.8, "whisper_3"]]

@export var player_scene: PackedScene = preload("res://scenes/player.tscn")

var rows: PackedStringArray = []
var width := 0
var height := 0
var player: Player
var meta := {}
var chars := {}
## door id -> world position (bottom centre of the door's tile)
var doors := {}
var _door_nodes := {}
## spot id -> world position
var spots := {}
var theme: Dictionary

var _ground: TileMapLayer
var _wall: TileMapLayer
var _deco: TileMapLayer
var _props: Node2D
var _modulate: CanvasModulate
var _rng := RandomNumberGenerator.new()
var _start := Vector2(-1, -1)
## gates are added after everything else, so they can find their eye-stones
var _gates: Array[Node2D] = []
var _lamp_count := 0
var _dusk := Color(0.78, 0.78, 0.94)
var _deep := Color(0.2, 0.2, 0.33)
var _warm := Color(0, 0, 0, 0)
var _dark_from := 72.0
var _dark_to := 106.0
var _dark_axis := "x"
var _warmth := 0.0
var _glow_color := Color(0, 0, 0, 0)
var _glow_cond := ""
var _glow := 0.0
## Echo: the memory filter, and fear (Vesper).
var _memory: ShaderMaterial
var _fear_rows := Vector2.ZERO
var _fear := 0.0
var _comfort := 0.0
var _beat := 0.0
var _whispered := 0
var _old_hearth: Node2D


func _ready() -> void:
	add_to_group("level")
	_load_map()
	theme = THEMES.get(meta.get("theme", "forest"), THEMES["forest"])
	_rng.seed = int(meta.get("seed", "7"))
	_parse_light()
	_setup_echo()
	_build()
	if meta.has("echo"):
		_add_memory_filter()
	Dialogue.event.connect(_on_dialogue_event)
	Game.flag_set.connect(_on_flag_set)
	Game.ember_given.connect(func(_npc: String) -> void: _update_warmth(true))
	_intro.call_deferred()


func _intro() -> void:
	Game.arrived()
	Game.entry_door = ""
	_update_music()
	if not Game.started:
		Game.fade_in(1.2)
		return
	Game.save_game()
	if Debug.skip_intro:
		Game.fade_in(0.01)
		_play_pending()
		return
	Game.fade_in(1.6 if meta.has("echo") else 0.8)
	var visited := "visited_" + Game.level_id
	if not Game.has_flag(visited):
		Game.set_flag(visited)
		await get_tree().create_timer(0.5).timeout
		await Game.show_title_card(meta.get("name", ""), meta.get("subtitle", ""))
	_play_pending()


## A dialogue waiting for this level (after an Echo), or the Echo's opening lines.
func _play_pending() -> void:
	var id := Game.pending_dialogue
	Game.pending_dialogue = ""
	if id == "" and meta.has("echo"):
		id = "echo_%s_start" % meta["echo"]
	if id != "" and Story.DIALOGUES.has(id):
		await get_tree().create_timer(0.3).timeout
		Dialogue.run(id)


# --- Echoes -------------------------------------------------------------------

## Who you are and what you carry here. Outside Echoes everything is back to normal.
func _setup_echo() -> void:
	Game.hero_skin = meta.get("hero", "")
	Game.ability = meta.get("ability", "flare")
	Game.lantern_scale = float(meta.get("lantern", "1"))
	Game.speed_mult = 1.0
	Game.followers.clear()
	Game.show_embers = not meta.has("echo") or meta.has("embers")
	if not meta.has("echo"):
		return
	if Game.echo == "":
		Game.echo = meta["echo"]  # reached directly (debug runs)
	Game.embers = int(meta.get("embers", "0"))
	Game.embers_given = 0
	if meta.has("fear"):
		var f: PackedStringArray = meta["fear"].split(" ", false)
		_fear_rows = Vector2(float(f[0]), float(f[1]))
	Dialogue.finished.connect(func() -> void: _comfort = 1.0)


func _add_memory_filter() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 20  # over the world and the HUD, under menus and dialogue
	add_child(layer)
	var rect := ColorRect.new()
	rect.size = Vector2(480, 270)  # the game is always 480x270
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_memory = ShaderMaterial.new()
	_memory.shader = preload("res://shaders/memory.gdshader")
	rect.material = _memory
	layer.add_child(rect)


## Vesper's fear: deeper is worse; talking to someone, or Edda beside you, helps.
func _update_fear(delta: float) -> void:
	if _fear_rows == Vector2.ZERO or player == null:
		return
	var off := Game.has_flag(meta["echo"] + ":fear_off")
	var row := player.global_position.y / T
	var raw := clampf((row - _fear_rows.x) / (_fear_rows.y - _fear_rows.x), 0.0, 1.0)
	_comfort = maxf(_comfort - delta / 25.0, 0.0)
	var edda := Game.followers.size() > 0
	var target := 0.0 if off else raw * (1.0 - 0.45 * _comfort) * (0.5 if edda else 1.0)
	_fear = move_toward(_fear, target, delta * 0.25)
	Game.speed_mult = 1.0 - 0.5 * _fear
	_memory.set_shader_parameter("fear", _fear)
	if _fear > 0.3 and not Game.in_dialogue:
		_beat -= delta
		if _beat <= 0.0:
			_beat = lerpf(1.5, 0.55, _fear)
			Sound.sfx("fear_beat", lerpf(-16.0, -4.0, _fear))
	while _whispered < WHISPERS.size() and _fear >= WHISPERS[_whispered][0] and not Game.in_dialogue:
		var key: String = WHISPERS[_whispered][1]
		_whispered += 1
		var lines: Array = Story.BARKS.get("dark", {}).get(key, [])
		if not lines.is_empty():
			Util.bark(player, lines[0], 26.0, 2.6)


# --- map file ---------------------------------------------------------------

func _load_map() -> void:
	var path := "res://levels/%s.txt" % Game.level_id
	if not FileAccess.file_exists(path):
		push_error("Missing level: " + path)
		Game.level_id = Game.FIRST_LEVEL
		path = "res://levels/%s.txt" % Game.level_id
	var text := FileAccess.get_file_as_string(path)
	for line in text.replace("\r", "").split("\n"):
		if line.begins_with(";"):
			continue  # comment
		if line.begins_with("@"):
			_parse_header(line.substr(1).strip_edges())
			continue
		if line.strip_edges() == "" and rows.is_empty():
			continue
		rows.append(line)
	while not rows.is_empty() and rows[-1].strip_edges() == "":
		rows.remove_at(rows.size() - 1)
	height = rows.size()
	for r in rows:
		width = maxi(width, r.length())
	for i in rows.size():
		rows[i] = rows[i].rpad(width, ".")


func _parse_header(line: String) -> void:
	var parts := line.split(" ", false)
	if parts.is_empty():
		return
	var key := parts[0]
	if key == "char" and parts.size() >= 3:
		chars[parts[1]] = parts.slice(2)
	elif key in ["name", "subtitle"]:
		meta[key] = line.substr(key.length()).strip_edges()
	else:
		meta[key] = " ".join(parts.slice(1))


func _parse_light() -> void:
	if meta.has("light"):
		var p: PackedStringArray = meta["light"].split(" ", false)
		_dusk = _color(p[0])
		_deep = _color(p[1])
		_dark_from = float(p[2])
		_dark_to = float(p[3])
		_dark_axis = p[4] if p.size() > 4 else "x"
	if meta.has("warm"):
		_warm = _color(meta["warm"])
	if meta.has("glow"):
		var g: PackedStringArray = meta["glow"].split(" ", false)
		_glow_color = _color(g[0])
		_glow_cond = g[1] if g.size() > 1 else ""
		_glow = 1.0 if Game.check(_glow_cond) else 0.0


static func _color(s: String) -> Color:
	var c := s.split(",")
	return Color(float(c[0]), float(c[1]), float(c[2]))


func ch(x: int, y: int) -> String:
	if x < 0 or y < 0 or x >= width or y >= height:
		return ""
	return rows[y][x]


func solid(x: int, y: int) -> bool:
	if y < 0:
		return false
	if x < 0 or x >= width or y >= height:
		return true
	return rows[y][x] == "#"


func is_wall(x: int, y: int) -> bool:
	var c := ch(x, y)
	if c == "w" or c == "#":
		return true
	if c == "" or c == ".":
		return false
	if c == "~" or c == "_":
		return is_wall(x, y - 1)
	# entities standing in front of a wall keep the wall behind them
	var n := 0
	for o: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
		var cc := ch(x + o.x, y + o.y)
		if cc == "w" or cc == "#":
			n += 1
	return n >= 3


func tile_base(x: int, y: int) -> Vector2:
	return Vector2(x * T + T / 2.0, (y + 1) * T)


# --- building ---------------------------------------------------------------

func _build() -> void:
	var backdrop_path: String = theme["backdrop"]
	if ResourceLoader.exists(backdrop_path):
		var backdrop: Node = load(backdrop_path).instantiate()
		add_child(backdrop)

	var tileset := _make_tileset()
	_wall = _make_layer("Wall", tileset, -8)
	_wall.modulate = theme["wall_tint"]
	_props = Node2D.new()
	_props.name = "Props"
	add_child(_props)
	_ground = _make_layer("Ground", tileset, 0)
	_deco = _make_layer("Deco", tileset, 4)

	for y in height:
		for x in width:
			var c := ch(x, y)
			if c == "#":
				var m := _mask(x, y, solid)
				_ground.set_cell(Vector2i(x, y), 0, Vector2i((y % 4) * 4 + x % 4, m))
				_decorate_edges(x, y, m)
			elif c == "=":
				var left := ch(x - 1, y) != "="
				var right := ch(x + 1, y) != "="
				var col := 0 if left else (3 if right else 1 + x % 2)
				_ground.set_cell(Vector2i(x, y), 0, Vector2i(col, 17))
			if c != "#" and is_wall(x, y):
				var wm := _mask(x, y, is_wall)
				_wall.set_cell(Vector2i(x, y), 1, Vector2i((y % 4) * 4 + x % 4, wm))
			_place(c, x, y)

	for gate in _gates:
		_props.add_child(gate)
	_order_lamps()
	_build_pillars()
	_build_runs("*", func(x: int, y: int, n: int) -> void: _add_glimmer(x, y, n, 0))
	_build_runs("%", func(x: int, y: int, n: int) -> void: _add_glimmer(x, y, n, 3))
	_build_runs("~", func(x: int, y: int, n: int) -> void: _add_water(x, y, n, true))
	_build_runs("_", func(x: int, y: int, n: int) -> void: _add_water(x, y, n, false))
	_apply_depth_shader()
	if theme.get("grass", false):
		_scatter_grass()
	_add_particles()
	_spawn_player()

	_modulate = CanvasModulate.new()
	_modulate.color = _dusk
	add_child(_modulate)
	_update_warmth(false)

	_add_edge_walls()

	var cam := get_parent().get_node_or_null("Camera") as Camera2D
	if cam:
		cam.limit_left = 0
		cam.limit_top = 0
		cam.limit_right = width * T
		cam.limit_bottom = height * T
	if player:
		player.fall_limit = height * T + 48
		for layer in get_tree().get_nodes_in_group("parallax"):
			layer.reference_y = player.global_position.y - 22.0


## Invisible walls at the left and right edges of the map.
func _add_edge_walls() -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	for side: Array in [[Vector2.RIGHT, 0.0], [Vector2.LEFT, width * T * 1.0]]:
		var shape := CollisionShape2D.new()
		var b := WorldBoundaryShape2D.new()
		b.normal = side[0]
		shape.shape = b
		shape.position = Vector2(side[1], 0)
		body.add_child(shape)
	add_child(body)


func _spawn_player() -> void:
	var pos := _start
	if Game.use_spawn_pos:
		pos = Game.spawn_pos
		Game.use_spawn_pos = false
	elif Game.entry_door != "" and doors.has(Game.entry_door):
		pos = doors[Game.entry_door]
	elif Game.entry_door != "" and spots.has(Game.entry_door):
		pos = spots[Game.entry_door]
	elif pos.x < 0 and not doors.is_empty():
		pos = doors.values()[0]
	# never arrive standing in a door that would whisk you straight away again
	for door: Node2D in _door_nodes.values():
		if absf(door.position.x - pos.x) < 20.0 and absf(door.position.y - pos.y) < 40.0:
			door.armed = false
	player = player_scene.instantiate()
	player.position = pos
	player.z_index = 2
	add_child(player)
	if Game.has_flag("pell_follows") and not meta.has("echo"):
		var pell: Node2D = PellScript.new()
		pell.npc_id = "pell"
		pell.follow_on_spawn = true
		pell.position = pos + Vector2(-14, -26)
		add_child(pell)


func _process(delta: float) -> void:
	_update_fear(delta)
	if player and _modulate:
		var p := player.global_position.x if _dark_axis == "x" else player.global_position.y
		var t := clampf((p - _dark_from * T) / ((_dark_to - _dark_from) * T), 0.0, 1.0)
		t = t * t * (3.0 - 2.0 * t)
		var c := _dusk.lerp(_deep, t)
		if _warm.a > 0.0:
			c = c.lerp(_warm, _warmth)
		if _glow > 0.0:
			c = c.lerp(_glow_color, _glow)
		_modulate.color = c


func _update_warmth(animate: bool) -> void:
	if _warm.a == 0.0:
		return
	var target := clampf(Game.embers_given / 5.0, 0.0, 1.0) * 0.85
	if Game.has_flag("gave_tallow"):
		target = maxf(target, 0.3)
	if animate:
		create_tween().tween_property(self, "_warmth", target, 3.0)
	else:
		_warmth = target


func _update_music() -> void:
	var spec: PackedStringArray = meta.get("music", theme.get("music", "")).split(" ", false)
	var track := spec[0] if spec.size() > 0 else ""
	var i := 1
	while i + 1 < spec.size():
		if Game.check(spec[i]):
			track = spec[i + 1]
		i += 2
	if track == "-":
		track = ""
	if Game.started:
		Sound.music(track)
		Sound.ambience(meta.get("ambience", theme.get("ambience", "")))


func _on_flag_set(_flag: String) -> void:
	_update_music()
	if _glow_color.a > 0.0 and _glow == 0.0 and Game.check(_glow_cond):
		create_tween().tween_property(self, "_glow", 1.0, 6.0).set_trans(Tween.TRANS_SINE)


func _on_dialogue_event(ev: String) -> void:
	var parts := ev.split(":")
	match parts[0]:
		"warp":  # warp:<door or spot> - move the player within this level
			_warp(parts[1])
		"go":  # go:<level>:<door>
			Game.go_to(parts[1], parts[2])
		"the_end":
			_the_end()
		"stars_named":  # Orrin has heard the names you found
			Game.tell_names()
		# --- Echoes ---
		"echo":  # echo:<id> - start an Echo (from the Little Hearth)
			_start_echo_after_dialogue(parts[1])
		"echo_end":
			_end_echo_after_dialogue()
		"rising_start":
			for r: Rising in get_tree().get_nodes_in_group("rising"):
				r.start()
		"stay", "follow":  # stay:<npc> / follow:<npc> - a follower leaves or joins the line
			for f: Follower in get_tree().get_nodes_in_group("follower"):
				if f.npc_id != parts[1]:
					continue
				if parts[0] == "stay":
					f.stay()
				else:
					f.follow()
		"darken":  # the lamps go out: the level falls to its deepest dark
			var tw := create_tween()
			tw.tween_property(self, "_dusk", _deep * 0.55, 3.0)
			tw.parallel().tween_property(self, "_deep", _deep * 0.55, 3.0)
		"hearth_gutter":
			if _old_hearth:
				_old_hearth.call("gutter")
		"lantern_out":  # Lark's lantern goes cold
			var tw := create_tween()
			tw.tween_property(Game, "lantern_scale", 0.0, 3.0).set_trans(Tween.TRANS_SINE)
		"become_hollow":
			_become_hollow()
		"refresh":  # characters look again at whether they are lit
			for npc: NPC in get_tree().get_nodes_in_group("npc"):
				npc.refresh()


func _start_echo_after_dialogue(id: String) -> void:
	await Dialogue.finished
	if player:
		player.frozen = true
	Game.start_echo(id)


func _end_echo_after_dialogue() -> void:
	await Dialogue.finished
	if player:
		player.frozen = true
	await get_tree().create_timer(0.6).timeout
	Game.end_echo()


## The dark that followed Vesper up gathers around them: the Hollow One stands there.
func _become_hollow() -> void:
	if player == null:
		return
	Sound.sfx("dark_rise")
	var shape := AnimatedSprite2D.new()
	shape.sprite_frames = Util.make_frames({"idle": ["res://assets/sprites/hollow_one.png", 48, 5, true, [0, 1, 2, 3]]})
	shape.offset = Vector2(0, -28)
	shape.material = Util.unlit_material()
	shape.modulate.a = 0.0
	shape.z_index = 3
	shape.flip_h = player.facing < 0
	_props.add_child(shape)
	shape.global_position = player.global_position
	shape.play("idle")
	var tw := create_tween()
	tw.tween_property(shape, "modulate:a", 1.0, 2.5)
	tw.parallel().tween_property(player, "modulate:a", 0.0, 2.5)
	Util.burst(_props, player.global_position + Vector2(0, -12), [Color(0.2, 0.1, 0.3), Color(0.05, 0.0, 0.1)], 40, 60.0, 180.0, -30.0, 1.6)


## The credits roll after an ending, then back to the title screen.
func _the_end() -> void:
	if player:
		player.frozen = true
	await Game.fade_out(2.0)
	var layer := CanvasLayer.new()
	layer.layer = 55  # over the fade
	add_child(layer)
	var credits := Credits.new()
	layer.add_child(credits)
	credits.open(true)
	await credits.closed
	Sound.music("", 2.0)
	Sound.ambience("", 2.0)
	await get_tree().create_timer(1.0).timeout
	Game.new_game()
	Game.started = false
	get_tree().paused = false
	get_tree().reload_current_scene()


func _warp(id: String) -> void:
	var pos: Vector2 = doors.get(id, spots.get(id, Vector2(-1, -1)))
	if pos.x < 0 or player == null:
		return
	player.frozen = true
	await Game.fade_out(0.5)
	player.global_position = pos
	player.velocity = Vector2.ZERO
	Game.checkpoint = pos
	var cam := get_parent().get_node_or_null("Camera")
	if cam and cam.has_method("snap_to_target"):
		cam.snap_to_target()
	await get_tree().create_timer(0.3).timeout
	player.frozen = false
	Game.fade_in(0.6)


func _mask(x: int, y: int, filled: Callable) -> int:
	var m := 0
	if not filled.call(x, y - 1):
		m |= U
	if not filled.call(x + 1, y):
		m |= R
	if not filled.call(x, y + 1):
		m |= D
	if not filled.call(x - 1, y):
		m |= L
	return m


func _decorate_edges(x: int, y: int, m: int) -> void:
	var above := ch(x, y - 1)
	if m & U and y > 0 and not above in ["=", "~", "_"]:
		_deco.set_cell(Vector2i(x, y - 1), 0, Vector2i(x % 4, 16))
		if m & L and ch(x - 1, y) in [".", "w"]:
			_deco.set_cell(Vector2i(x - 1, y), 0, Vector2i(8, 16))
		if m & R and ch(x + 1, y) in [".", "w"]:
			_deco.set_cell(Vector2i(x + 1, y), 0, Vector2i(9, 16))
	if m & D and ch(x, y + 1) in [".", "w"] and _rng.randf() < 0.4:
		_deco.set_cell(Vector2i(x, y + 1), 0, Vector2i(4 + x % 4, 16))


func _make_layer(layer_name: String, tileset: TileSet, z: int) -> TileMapLayer:
	var layer := TileMapLayer.new()
	layer.name = layer_name
	layer.tile_set = tileset
	layer.z_index = z
	add_child(layer)
	return layer


func _make_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(T, T)
	ts.add_physics_layer()
	ts.set_physics_layer_collision_layer(0, 1)
	ts.set_physics_layer_collision_mask(0, 0)
	ts.add_physics_layer()
	ts.set_physics_layer_collision_layer(1, 4)
	ts.set_physics_layer_collision_mask(1, 0)

	var ground_src := TileSetAtlasSource.new()
	ground_src.texture = load(theme["ground"])
	ground_src.texture_region_size = Vector2i(T, T)
	ts.add_source(ground_src, 0)
	var h := T / 2.0
	var full := PackedVector2Array([Vector2(-h, -h), Vector2(h, -h), Vector2(h, h), Vector2(-h, h)])
	var plank := PackedVector2Array([Vector2(-h, -h), Vector2(h, -h), Vector2(h, -h + 5), Vector2(-h, -h + 5)])
	for row in 18:
		for col in 16:
			var coords := Vector2i(col, row)
			ground_src.create_tile(coords)
			var data := ground_src.get_tile_data(coords, 0)
			if row < 16:
				data.add_collision_polygon(0)
				data.set_collision_polygon_points(0, 0, full)
			elif row == 17 and col < 4:
				data.add_collision_polygon(1)
				data.set_collision_polygon_points(1, 0, plank)
				data.set_collision_polygon_one_way(1, 0, true)

	var wall_src := TileSetAtlasSource.new()
	wall_src.texture = load(theme["wall"])
	wall_src.texture_region_size = Vector2i(T, T)
	ts.add_source(wall_src, 1)
	for row in 16:
		for col in 16:
			wall_src.create_tile(Vector2i(col, row))
	return ts


func _apply_depth_shader() -> void:
	# distance (in tiles) from every ground tile to open air -> darkness map
	var img := Image.create(width, height, false, Image.FORMAT_L8)
	var dist := {}
	var frontier: Array[Vector2i] = []
	for y in height:
		for x in width:
			if not solid(x, y):
				dist[Vector2i(x, y)] = 0
				frontier.append(Vector2i(x, y))
	while not frontier.is_empty():
		var next: Array[Vector2i] = []
		for p in frontier:
			for oy in range(-1, 2):
				for ox in range(-1, 2):
					var q := p + Vector2i(ox, oy)
					if q.x < 0 or q.y < 0 or q.x >= width or q.y >= height or dist.has(q):
						continue
					dist[q] = dist[p] + 1
					next.append(q)
		frontier = next
	for y in height:
		for x in width:
			var d: int = dist.get(Vector2i(x, y), 6)
			img.set_pixel(x, y, Color.from_hsv(0, 0, clampf((d - 1.3) / 2.4, 0.0, 1.0)))
	var mat := ShaderMaterial.new()
	mat.shader = preload("res://shaders/ground_depth.gdshader")
	mat.set_shader_parameter("depth_map", ImageTexture.create_from_image(img))
	mat.set_shader_parameter("map_tiles", Vector2(width, height))
	_ground.material = mat


# --- placing things ---------------------------------------------------------

func _place(c: String, x: int, y: int) -> void:
	var base := tile_base(x, y)
	if chars.has(c):
		_place_custom(chars[c], x, y, base)
	elif c == "P":
		_start = base
	elif SCRIPTS.has(c):
		var node: Node2D = SCRIPTS[c].new()
		node.position = base
		if c == "e" or c == "S":
			node.key = "%s:%d:%d" % [Game.level_id, x, y]
			if c == "e" and Game.has_flag("taken:" + node.key):
				node.free()
				return
		_props.add_child(node)
	elif c == "x" or c == "X":
		var shade: Node2D = ShadeScript.new()
		shade.strength = 1.6 if c == "x" else 4.0
		shade.position = base + Vector2(0, -6)
		_props.add_child(shade)
	elif c == "&":
		var thorn: Node2D = ThornScript.new()
		thorn.position = Vector2(x * T, y * T)
		thorn.key = "%s:%d:%d" % [Game.level_id, x, y]
		_props.add_child(thorn)
	elif PROPS.has(c):
		var spec: Array = PROPS[c]
		var tex_name: String = spec[0]
		if c == "f":
			tex_name = "flower_%d" % _rng.randi_range(0, 2)
		if spec[3]:
			add_prop(tex_name, Vector2(x * T + 8, y * T), spec[1], false, true)
		else:
			add_prop(tex_name, base + Vector2(0, spec[2]), spec[1], _rng.randf() < 0.5 and c != "t")
	elif c == "v":
		var vine := "vine_a" if _rng.randf() < 0.5 else "vine_b"
		add_prop(vine, Vector2(x * T + 8, y * T), -1, false, true)
	elif c == "o":
		var s := _add_sprite("res://assets/deco/knob.png", base - Vector2(0, 8), -3, false)
		s.offset.y = 0


func _place_custom(spec: Array, x: int, y: int, base: Vector2) -> void:
	var kind: String = spec[0]
	var args: Array = spec.slice(1)
	match kind:
		"npc":
			var id: String = args[0]
			var data: Dictionary = Story.NPCS.get(id, {})
			if data.is_empty():
				push_warning("Unknown NPC: " + id)
				return
			if not Game.check(data.get("where", {}).get(Game.level_id, "")):
				return
			var npc: Node2D = (PellScript if id == "pell" else NpcScript).new()
			npc.npc_id = id
			npc.position = base
			_props.add_child(npc)
		"door":
			doors[args[0]] = base
			var door: Node2D = DoorScript.new()
			door.door_id = args[0]
			door.target_level = args[1]
			door.target_door = args[2]
			door.dialogue_id = args[3] if args.size() > 3 else ""
			door.armed = args[0] != Game.entry_door
			door.position = base
			_door_nodes[args[0]] = door
			_props.add_child(door)
		"wickway":
			doors[args[0]] = base
			var ww: Node2D = WickwayScript.new()
			ww.target_level = args[1]
			ww.target_door = args[2]
			ww.depth = args[3]
			ww.position = base
			_props.add_child(ww)
		"sign":
			var board: Node2D = SCRIPTS["g"].new()
			board.dialogue_id = args[0]
			board.stone = args.size() > 1 and args[1] == "stone"
			board.position = base
			_props.add_child(board)
		"trigger", "end":
			var trig: Node2D = DoorScript.new()
			trig.dialogue_id = args[0]
			trig.condition = args[1] if args.size() > 1 else ""
			trig.mode = kind
			trig.position = base
			_props.add_child(trig)
		"hearth":
			var hearth: Node2D = HearthScript.new()
			hearth.position = base
			_props.add_child(hearth)
		"lamp":
			_add_lamp(x, y)
		"hut":
			var lit: bool = Game.has_flag("gave_" + args[0])
			var hut := _add_sprite("res://assets/deco/%s.png" % ("hut_door_lit" if lit else "hut_door"), base + Vector2(0, 1), -4, false)
			if lit:
				_add_light(hut, Color(1.0, 0.7, 0.35), 0.6, 0.45, Vector2(0, -17 - hut.offset.y))
		"hook":
			var hook: Node2D = HookScript.new()
			hook.position = base
			_props.add_child(hook)
		"gate":
			var gate: Node2D = GateScript.new()
			gate.gate_id = args[0]
			gate.key = "%s:%s" % [Game.level_id, args[0]]
			gate.position = Vector2(x * T, y * T)
			_gates.append(gate)
		"eye":
			var eye: Node2D = EyeScript.new()
			eye.gate_id = args[0]
			eye.position = base
			_props.add_child(eye)
		"prop":
			var z := int(args[1]) if args.size() > 1 else -2
			var top: bool = args.size() > 2 and args[2] == "top"
			if top:
				add_prop(args[0], Vector2(x * T + 8, y * T), z, false, true)
			else:
				add_prop(args[0], base + Vector2(0, 1), z, false)
		"great_hearth":
			var gh: Node2D = GreatHearthScript.new()
			gh.position = base
			_props.add_child(gh)
			spots["hearth"] = base
		"spot":  # spot <id> [dialogue condition] - optionally also a trigger
			spots[args[0]] = base
			if args.size() > 1:
				var t: Node2D = DoorScript.new()
				t.dialogue_id = args[1]
				t.condition = args[2] if args.size() > 2 else ""
				t.mode = "trigger"
				t.position = base
				_props.add_child(t)
		"caster":
			var plate: Node2D = CasterScript.new()
			plate.shape = args[0] if args.size() > 0 else "boat"
			var top := y
			while top > 0 and not solid(x, top - 1) and y - top < 10:
				top -= 1
			var nudge := Vector2(float(args[1]), float(args[2])) if args.size() > 2 else Vector2.ZERO
			if solid(x, top - 1):
				plate.rod = (y - top) * T + 8.0 + nudge.y - 5.0
			plate.position = Vector2(x * T + 8, y * T + 8) + nudge
			_props.add_child(plate)
		"starlamp":
			var lamp: Node2D = StarlampScript.new()
			lamp.key = "%s:%d:%d" % [Game.level_id, x, y]
			lamp.position = base
			_props.add_child(lamp)
		"orrery":
			var sun: Node2D = OrreryScript.new()
			sun.key = "%s:%d:%d" % [Game.level_id, x, y]
			sun.travel = Vector2(float(args[0]), float(args[1])) * T
			if args.size() > 2:
				sun.speed = float(args[2])
			if args.size() > 3:
				sun.pause = float(args[3])
			sun.position = base
			_props.add_child(sun)
		"great_orrery":
			var go: Node2D = GreatOrreryScript.new()
			go.position = base
			_props.add_child(go)
			spots["great_orrery"] = base
		"name":
			var stone: Node2D = NameStoneScript.new()
			stone.name_id = args[0]
			stone.position = base
			_props.add_child(stone)
		"keepsake":
			var ks: Node2D = KeepsakeScript.new()
			ks.keepsake_id = args[0]
			ks.position = base
			_props.add_child(ks)
		"propif":
			if Game.check(args[0]):
				_place_custom(["prop"] + args.slice(1), x, y, base)
		"landing":
			var landing: Node2D = LandingScript.new()
			landing.position = base
			_props.add_child(landing)
		"sleeper", "follower":
			var f := Follower.new()
			f.npc_id = args[0]
			f.asleep = kind == "sleeper"
			f.position = base
			_props.add_child(f)
			if kind == "follower":
				f.follow.call_deferred()
		"rising":
			var r := Rising.new()
			r.mode = args[0]
			r.speed = float(args[1])
			r.surface_y = (y + 1) * T
			r.width_px = width * T
			r.running = args.size() > 2 and args[2] == "now"
			add_child(r)
		"headcount":
			var hc: Node2D = DoorScript.new()
			hc.mode = "count"
			hc.need = int(args[0])
			hc.dialogue_id = args[1]
			hc.not_yet = args[2]
			hc.position = base
			_props.add_child(hc)
		"old_hearth":
			_old_hearth = _make_old_hearth(base)
			spots["hearth"] = base


func _make_old_hearth(base: Vector2) -> Node2D:
	var h: Node2D = preload("res://scripts/old_hearth.gd").new()
	h.position = base
	_props.add_child(h)
	return h


func add_prop(tex_name: String, pos: Vector2, z: int, flip: bool, top := false) -> Sprite2D:
	var path := "res://assets/deco/%s.png" % tex_name
	if not ResourceLoader.exists(path):
		push_warning("Missing prop: " + path)
		return null
	var s := _add_sprite(path, pos, z, flip)
	if top:
		s.offset.y = s.texture.get_height() / 2.0
	if PROP_LIGHTS.has(tex_name):
		var l: Array = PROP_LIGHTS[tex_name]
		_add_light(s, l[0], l[1], l[2], Vector2(0, l[3]))
		s.material = Util.unlit_material()
	return s


func _add_light(parent: Node2D, color: Color, energy: float, scale_: float, pos: Vector2) -> PointLight2D:
	var light := PointLight2D.new()
	light.texture = preload("res://assets/fx/light_small.png")
	light.color = color
	light.energy = energy
	light.texture_scale = scale_
	light.position = pos
	parent.add_child(light)
	return light


func _add_sprite(path: String, bottom_center: Vector2, z: int, flip: bool) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load(path)
	s.position = bottom_center
	s.offset = Vector2(0, -s.texture.get_height() / 2.0)
	s.z_index = z
	s.flip_h = flip
	_props.add_child(s)
	return s


func _add_lamp(x: int, y: int) -> void:
	var top := y
	while top > 0 and not solid(x, top - 1):
		top -= 1
	var hook_y := y * T + 4.0
	var line := Line2D.new()
	line.points = PackedVector2Array([Vector2(x * T + 8, top * T), Vector2(x * T + 8, hook_y)])
	line.width = 1.0
	line.default_color = Color(0.1, 0.07, 0.1)
	line.z_index = -3
	_props.add_child(line)
	var lamp := Sprite2D.new()
	lamp.texture = preload("res://assets/sprites/hollow_lamp.png")
	lamp.hframes = 2
	lamp.position = Vector2(x * T + 8, hook_y + 6)
	lamp.z_index = -2
	lamp.set_meta("index", _lamp_count)
	lamp.add_to_group("hollow_lamp")
	_lamp_count += 1
	var light := _add_light(lamp, Color(1.0, 0.72, 0.38), 0.0, 0.55, Vector2.ZERO)
	lamp.set_meta("light", light)
	_props.add_child(lamp)
	_refresh_lamp(lamp, false)
	Game.ember_given.connect(func(_npc: String) -> void: _refresh_lamp(lamp, true))


## Lamps are numbered left to right once they are all placed.
func _order_lamps() -> void:
	var lamps := get_tree().get_nodes_in_group("hollow_lamp")
	lamps.sort_custom(func(a: Node2D, b: Node2D) -> bool: return a.position.x < b.position.x)
	for i in lamps.size():
		lamps[i].set_meta("index", i)
		_refresh_lamp(lamps[i], false)


## Lamps light two per gift, in order across the Hollow.
func _refresh_lamp(lamp: Sprite2D, animate: bool) -> void:
	var lit: bool = lamp.get_meta("index") < Game.embers_given * 2
	if lit == (lamp.frame == 1):
		return
	var light: PointLight2D = lamp.get_meta("light")
	if not lit:
		lamp.frame = 0
		light.energy = 0.0
		return
	if animate:
		await get_tree().create_timer(1.2 + lamp.get_meta("index") * 0.25).timeout
		Sound.sfx("lamp")
		Util.burst(_props, lamp.position, [Color(1, 0.92, 0.6), Color(0.95, 0.4, 0.15)], 8, 30.0, 180.0, 10.0, 0.5)
	lamp.frame = 1
	lamp.material = Util.unlit_material()
	create_tween().tween_property(light, "energy", 0.7, 0.6 if animate else 0.01)


func _build_pillars() -> void:
	var tex: Texture2D = preload("res://assets/deco/pillar.png")
	for x in width:
		var y := 0
		while y < height:
			if ch(x, y) == "|":
				var y0 := y
				while ch(x, y) == "|":
					y += 1
				var s := Sprite2D.new()
				s.texture = tex
				s.centered = false
				s.region_enabled = true
				s.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
				s.region_rect = Rect2(0, y0 * 7 % 16, tex.get_width(), (y - y0) * T + 4)
				s.position = Vector2(x * T + 2, y0 * T)
				s.z_index = -3
				_props.add_child(s)
			else:
				y += 1


## Calls `make(x, y, length)` for every horizontal run of `c`.
func _build_runs(c: String, make: Callable) -> void:
	for y in height:
		var x := 0
		while x < width:
			if ch(x, y) == c:
				var x0 := x
				while ch(x, y) == c:
					x += 1
				make.call(x0, y, x - x0)
			else:
				x += 1


func _add_glimmer(x: int, y: int, n: int, need: int) -> void:
	var g: Node2D = GlimmerScript.new()
	g.tiles = n
	g.need = need
	g.position = Vector2(x * T, y * T)
	_props.add_child(g)


func _add_water(x: int, y: int, n: int, deadly: bool) -> void:
	var w: Node2D = WaterScript.new()
	w.tiles = n
	w.deadly = deadly
	w.surface = not ch(x, y - 1) in ["~", "_"]
	w.position = Vector2(x * T, y * T)
	_props.add_child(w)


func _scatter_grass() -> void:
	var tufts := ["tuft_0", "tuft_1", "tuft_2"]
	for y in range(1, height):
		for x in width:
			if ch(x, y) != "#" or ch(x, y - 1) != ".":
				continue
			var r := _rng.randf()
			var pos := Vector2(x * T + _rng.randi_range(3, 13), y * T + 1)
			if r < 0.22:
				_add_sprite("res://assets/deco/%s.png" % tufts[_rng.randi() % 3], pos, 3 if _rng.randf() < 0.4 else -1, _rng.randf() < 0.5)
			elif r < 0.30:
				_add_sprite("res://assets/deco/flower_%d.png" % _rng.randi_range(0, 2), pos, -1, _rng.randf() < 0.5)


func _add_particles() -> void:
	var kind: String = theme.get("particles", "")
	if kind == "":
		return
	var tex: Texture2D = preload("res://assets/fx/firefly.png")
	var x := 6
	while x < width - 4:
		var top := 0
		while top < height - 1 and not solid(x, top):
			top += 1
		var p := CPUParticles2D.new()
		p.texture = tex
		p.material = Util.glow_material()
		p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		p.gravity = Vector2.ZERO
		p.spread = 180.0
		var grad := Gradient.new()
		grad.offsets = PackedFloat32Array([0.0, 0.2, 0.5, 0.8, 1.0])
		grad.colors = PackedColorArray([Color(1, 1, 1, 0), Color(1, 1, 1, 1), Color(1, 1, 1, 0.3), Color(1, 1, 1, 1), Color(1, 1, 1, 0)])
		p.color_ramp = grad
		p.z_index = 6
		if kind == "fireflies":
			p.amount = 5
			p.lifetime = 7.0
			p.preprocess = 7.0
			p.emission_rect_extents = Vector2(110, 40)
			p.direction = Vector2(1, -0.3)
			p.initial_velocity_min = 3.0
			p.initial_velocity_max = 9.0
			p.orbit_velocity_min = -0.02
			p.orbit_velocity_max = 0.02
			p.position = Vector2(x * T, top * T - 52)
		else:
			# drifting motes / cinders spread through the whole height of the map
			p.amount = 6
			p.lifetime = 9.0
			p.preprocess = 9.0
			p.emission_rect_extents = Vector2(120, height * T / 2.0)
			p.direction = {"cinders": Vector2(0.3, -1), "bubbles": Vector2(0.1, -1)}.get(kind, Vector2(1, 0.2))
			p.initial_velocity_min = 2.0 if kind != "bubbles" else 5.0
			p.initial_velocity_max = 7.0 if kind == "motes" else 14.0
			p.scale_amount_min = 0.6
			p.scale_amount_max = 1.0
			p.color = theme.get("mote_color", Color.WHITE)
			p.position = Vector2(x * T, height * T / 2.0)
		add_child(p)
		x += 15
