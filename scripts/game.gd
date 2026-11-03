extends Node
## Global game state (autoload "Game"): story flags, embers, checkpoint,
## travel between levels, saving, input bindings, screen fades and title cards.

signal embers_changed(count: int)
signal ember_given(npc: String)
signal flag_set(flag: String)
signal player_hurt

## Debug runs (any command-line user args) save elsewhere so they never touch a real save.
var save_path := "user://save.json"
const FIRST_LEVEL := "mossgrave"
## Lantern gifts, in the order they are found.
const GIFTS := ["hook", "flare"]

## Default keys (physical, so they sit in the same place on any layout).
## Players can rebind these in Options > Controls (see Settings), up to four per action.
const BINDINGS := {
	"move_left": [KEY_A, KEY_LEFT],
	"move_right": [KEY_D, KEY_RIGHT],
	"move_up": [KEY_W, KEY_UP],
	"move_down": [KEY_S, KEY_DOWN],
	"jump": [KEY_SPACE, KEY_W, KEY_UP, KEY_Z],
	"interact": [KEY_E, KEY_X, KEY_ENTER],
	"flare": [KEY_F, KEY_C, KEY_L, KEY_SHIFT],
	"journal": [KEY_TAB],
	"pause": [KEY_ESCAPE, KEY_P],
	"fullscreen": [KEY_F11],
}
## Gamepad buttons (not rebindable; the first one is what prompts show).
const PAD_BUTTONS := {
	"move_left": [JOY_BUTTON_DPAD_LEFT],
	"move_right": [JOY_BUTTON_DPAD_RIGHT],
	"move_up": [JOY_BUTTON_DPAD_UP],
	"move_down": [JOY_BUTTON_DPAD_DOWN],
	"jump": [JOY_BUTTON_A],
	"interact": [JOY_BUTTON_X, JOY_BUTTON_B],
	"flare": [JOY_BUTTON_Y, JOY_BUTTON_RIGHT_SHOULDER],
	"journal": [JOY_BUTTON_BACK],
	"pause": [JOY_BUTTON_START],
}

var flags: Dictionary = {}
var embers := 0
var embers_given := 0
var level_id := FIRST_LEVEL
## Door id to arrive at in the next level ("" = the map's start).
var entry_door := ""
## When true, the next level load places the player at `spawn_pos` (continuing a save).
var use_spawn_pos := false
var spawn_pos := Vector2.ZERO
var checkpoint := Vector2.ZERO
var in_dialogue := false
var player: CharacterBody2D = null
## False until the title screen has been dismissed.
var started := false
var travelling := false

## The Echo (a playable memory) being played, or "" on the real journey.
var echo := ""
## Who the player is in this level ("" = the wick; else hero_<anim>_<skin>.png).
var hero_skin := ""
## What the Flare key does in this level: "flare" (the gift) or "bell" (Maud's handbell).
var ability := "flare"
## How bright the lantern is in this level (Maud has none: a small glow).
var lantern_scale := 1.0
## Walking speed multiplier (Vesper's fear slows them down).
var speed_mult := 1.0
## Whether the ember counter shows (not in an Echo where you carry none).
var show_embers := true
## Dialogue to play once the next level has faded in (e.g. after an Echo).
var pending_dialogue := ""
## Keepers (and Edda) walking behind the player, nearest first.
var followers: Array[Node2D] = []
## The real journey's state, kept safe while an Echo is played.
var _echo_return := {}

signal bell_rung(pos: Vector2, radius: float)

var _fade_layer: CanvasLayer
var _fade_rect: ColorRect
var _card_title: Label
var _card_sub: Label
var _key_token := RegEx.create_from_string("\\{key:(\\w+)\\}")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_setup_input()
	_build_overlay()


func new_game() -> void:
	flags.clear()
	embers = 0
	embers_given = 0
	level_id = FIRST_LEVEL
	entry_door = ""
	use_spawn_pos = false
	in_dialogue = false
	player = null
	echo = ""
	_echo_return = {}
	pending_dialogue = ""
	followers.clear()


# --- Echoes -----------------------------------------------------------------

## Who lives in Old Hollow now (Nan Tallow always does).
const RESIDENT_FLAGS := ["gave_wisp", "gave_ash", "gave_bell", "gave_gudgeon", "gave_orrin", "gave_sprig", "gave_glim"]


func residents() -> int:
	var n := 1
	for f: String in RESIDENT_FLAGS:
		if has_flag(f):
			n += 1
	return n


## Leaves the journey for a while to play Echo `id` (levels/echo_<id>.txt) from its start.
## Anything that Echo did last time is forgotten, so it can be replayed.
func start_echo(id: String) -> void:
	_echo_return = {"level": level_id, "x": checkpoint.x, "y": checkpoint.y,
		"embers": embers, "given": embers_given}
	for f: String in flags.keys():
		# its own flags, who you warmed there, gates/embers/lights in its map, its triggers
		if f.begins_with(id + ":") or f.begins_with("gave_" + id + "_") or f.begins_with("seen_" + id + "_") \
				or f.contains("echo_" + id + ":") or f == "visited_echo_" + id:
			flags.erase(f)
	echo = id
	followers.clear()
	Sound.sfx("memory_in")
	go_to("echo_" + id, "", "")


## Back from an Echo to where it was started (the Little Hearth), with everything as it was.
func end_echo() -> void:
	if echo == "":
		return
	var id := echo
	set_flag("echo_" + id)
	echo = ""
	followers.clear()
	embers = _echo_return.get("embers", embers)
	embers_given = _echo_return.get("given", embers_given)
	pending_dialogue = "after_echo_" + id
	Sound.sfx("memory_out")
	# Echoes start at the Little Hearth, so they end there too (spot "echo_return")
	go_to(_echo_return.get("level", "old_hollow"), "echo_return", "")


# --- embers -----------------------------------------------------------------

func add_ember() -> void:
	embers += 1
	embers_changed.emit(embers)


func lose_ember() -> void:
	if embers <= 0:
		return
	embers -= 1
	embers_changed.emit(embers)


## Shares one ember with an NPC. Returns false if the lantern is empty.
func give_ember(npc: String) -> bool:
	if embers <= 0:
		return false
	embers -= 1
	embers_given += 1
	set_flag("gave_" + npc)
	embers_changed.emit(embers)
	ember_given.emit(npc)
	Sound.sfx("give")
	return true


# --- flags & conditions -----------------------------------------------------

func set_flag(flag: String, value := true) -> void:
	flags[flag] = value
	flag_set.emit(flag)


func clear_flag(flag: String) -> void:
	flags.erase(flag)


func has_flag(flag: String) -> bool:
	return flags.get(flag, false)


func has_gift(gift: String) -> bool:
	# the wicks in the Echoes never had your gifts
	return echo == "" and has_flag("gift_" + gift)


## Evaluates a condition string. Terms are comma-separated and must all hold:
##   flag   !flag   embers>=N   given>=N   names>=N   home>=N   new_names   in:<level>
## A term may list alternatives with '|' (any one is enough): gave_tallow|ending_many
## (names>=N: Keeper name-stones found; new_names: some not yet shown to Orrin;
##  home>=N: people living in Old Hollow, Tallow included)
func check(cond: String) -> bool:
	if cond == "":
		return true
	for raw in cond.split(","):
		if "|" in raw:
			var any := false
			for alt in raw.split("|"):
				if check(alt):
					any = true
					break
			if not any:
				return false
			continue
		var term := raw.strip_edges()
		var negate := term.begins_with("!")
		if negate:
			term = term.substr(1)
		var ok: bool
		if term.begins_with("embers>="):
			ok = embers >= int(term.trim_prefix("embers>="))
		elif term.begins_with("given>="):
			ok = embers_given >= int(term.trim_prefix("given>="))
		elif term.begins_with("names>="):
			ok = name_count() >= int(term.trim_prefix("names>="))
		elif term.begins_with("home>="):
			ok = residents() >= int(term.trim_prefix("home>="))
		elif term == "new_names":
			ok = not new_names().is_empty()
		elif term.begins_with("in:"):
			ok = level_id == term.trim_prefix("in:")
		else:
			ok = has_flag(term)
		if ok == negate:
			return false
	return true


# --- Keeper names -------------------------------------------------------------

## How many Keeper name-stones you have found.
func name_count() -> int:
	var n := 0
	for id: String in JournalData.NAMES:
		if has_flag("name:" + id):
			n += 1
	return n


## Names found but not yet told to Orrin (his own is his business).
func new_names() -> PackedStringArray:
	var out: PackedStringArray = []
	for id: String in JournalData.NAMES:
		if id != "orrin" and has_flag("name:" + id) and not has_flag("star:" + id):
			out.append(JournalData.NAMES[id][0])
	return out


## Marks every name found so far as told to Orrin.
func tell_names() -> void:
	for id: String in JournalData.NAMES:
		if has_flag("name:" + id):
			flags["star:" + id] = true


## Fills {names}, {new_names}, {embers}, {followers} and {key:<action>} (the key or
## button to press, e.g. "[E]") in dialogue and title-card text.
func format_text(text: String) -> String:
	if not "{" in text:
		return text
	for m in _key_token.search_all(text):
		text = text.replace(m.get_string(), Settings.key_text(m.get_string(1)))
	var fresh := new_names()
	var listed := ""
	if fresh.size() == 1:
		listed = fresh[0]
	elif fresh.size() > 1:
		listed = ", ".join(fresh.slice(0, fresh.size() - 1)) + " and " + fresh[-1]
	return text.replace("{names}", str(name_count())).replace("{new_names}", listed) \
		.replace("{embers}", str(embers)).replace("{followers}", str(followers.size()))


# --- travel & saving --------------------------------------------------------

## Fades out and loads `level`, arriving at door `door`.
func go_to(level: String, door: String, sfx := "door") -> void:
	if travelling:
		return
	travelling = true
	if player:
		player.frozen = true
	if sfx != "":
		Sound.sfx(sfx)
	await fade_out(0.5)
	level_id = level
	entry_door = door
	use_spawn_pos = false
	in_dialogue = false
	get_tree().paused = false
	get_tree().reload_current_scene.call_deferred()


## Called by the level once it is built.
func arrived() -> void:
	travelling = false


func save_game() -> void:
	var data := {
		"version": 1,
		"level": level_id,
		"x": checkpoint.x,
		"y": checkpoint.y,
		"flags": flags,
		"embers": embers,
		"given": embers_given,
	}
	if echo != "":
		# mid-Echo, the save is the real journey, back at the Little Hearth
		for k: String in ["level", "x", "y", "embers", "given"]:
			data[k] = _echo_return.get(k, data[k])
	var f := FileAccess.open(save_path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data, "\t"))


func has_save() -> bool:
	return FileAccess.file_exists(save_path)


func load_game() -> bool:
	if not has_save():
		return false
	var data = JSON.parse_string(FileAccess.get_file_as_string(save_path))
	if not data is Dictionary:
		return false
	new_game()
	flags = data.get("flags", {})
	embers = int(data.get("embers", 0))
	embers_given = int(data.get("given", 0))
	level_id = data.get("level", FIRST_LEVEL)
	spawn_pos = Vector2(data.get("x", 0.0), data.get("y", 0.0))
	use_spawn_pos = true
	return true


## Lantern-light sources that wake glimmer and push back shades.
## Each entry: [global position, radius].
func light_sources() -> Array:
	var out: Array = []
	for n in get_tree().get_nodes_in_group("light_source"):
		if n.has_method("light_info"):
			var info: Array = n.light_info()
			if info[1] > 0.0:
				out.append(info)
	return out


## Returns how strongly `pos` is lit (0 = dark, 1 = at the light's centre).
func light_at(pos: Vector2, pad := 0.0) -> float:
	var best := 0.0
	for info: Array in light_sources():
		var d: float = (info[0] as Vector2).distance_to(pos) - pad
		var r: float = info[1]
		if d < r:
			best = maxf(best, 1.0 - maxf(d, 0.0) / r)
	return best


# --- screen effects ---------------------------------------------------------

func fade_out(time := 0.4) -> void:
	var tw := create_tween()
	tw.tween_property(_fade_rect, "color:a", 1.0, time)
	await tw.finished


func fade_in(time := 0.6) -> void:
	var tw := create_tween()
	tw.tween_property(_fade_rect, "color:a", 0.0, time)
	await tw.finished


func set_black(alpha: float) -> void:
	_fade_rect.color.a = alpha


func show_title_card(title: String, subtitle := "", hold := 2.2) -> void:
	_card_title.text = format_text(title)
	_card_sub.text = format_text(subtitle)
	Sound.sfx("title_card")
	var tw := create_tween()
	tw.tween_property(_card_title, "modulate:a", 1.0, 0.8)
	tw.parallel().tween_property(_card_sub, "modulate:a", 1.0, 1.2)
	tw.tween_interval(hold)
	tw.tween_property(_card_title, "modulate:a", 0.0, 0.8)
	tw.parallel().tween_property(_card_sub, "modulate:a", 0.0, 0.8)
	await tw.finished


func _build_overlay() -> void:
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = 50
	add_child(_fade_layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0.03, 0.02, 0.06, 1.0)
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_layer.add_child(_fade_rect)

	_card_title = _make_card_label(Color(1.0, 0.91, 0.64), 2, 96)
	_card_sub = _make_card_label(Color(0.72, 0.78, 0.86), 1, 124)


func _make_card_label(color: Color, scale_factor: int, y: int) -> Label:
	var label := Label.new()
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.size = Vector2(480.0 / scale_factor, 12)
	label.position = Vector2(0, y)
	label.scale = Vector2(scale_factor, scale_factor)
	label.add_theme_color_override("font_color", color)
	label.modulate.a = 0.0
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_layer.add_child(label)
	return label


# --- input ------------------------------------------------------------------

func _setup_input() -> void:
	for action: String in BINDINGS:
		if not InputMap.has_action(action):
			InputMap.add_action(action, 0.35)
		for key: Key in BINDINGS[action]:
			var ev := InputEventKey.new()
			ev.physical_keycode = key
			InputMap.action_add_event(action, ev)
	for action: String in PAD_BUTTONS:
		for button: JoyButton in PAD_BUTTONS[action]:
			var ev := InputEventJoypadButton.new()
			ev.button_index = button
			InputMap.action_add_event(action, ev)
	for pair: Array in [["move_left", -1.0], ["move_right", 1.0]]:
		var ev := InputEventJoypadMotion.new()
		ev.axis = JOY_AXIS_LEFT_X
		ev.axis_value = pair[1]
		InputMap.action_add_event(pair[0], ev)
	for pair: Array in [["move_up", -1.0], ["move_down", 1.0]]:
		var ev := InputEventJoypadMotion.new()
		ev.axis = JOY_AXIS_LEFT_Y
		ev.axis_value = pair[1]
		InputMap.action_add_event(pair[0], ev)
