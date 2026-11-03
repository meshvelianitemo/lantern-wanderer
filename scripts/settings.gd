extends Node
## Player settings (autoload "Settings"), kept in user://settings.cfg: volumes, window,
## text speed and keyboard bindings. Also knows whether the player is on a keyboard
## or a gamepad, so prompts can show the right button.
##   Settings.label("flare")     "F" (its first key), or "Y" while using a gamepad
##   Settings.key_text("flare")  "[F]"; dialogue text writes this as {key:flare}
## Debug runs keep their own settings file and leave the test window alone
## (pass --window to apply the window settings anyway, --pad to start on gamepad prompts).

## A setting, a key binding or the input device changed.
signal changed

## Actions the player can rebind, in menu order, with their names.
const ACTIONS := {
	"move_left": "Move left", "move_right": "Move right", "move_up": "Up", "move_down": "Down",
	"jump": "Jump", "interact": "Talk / use", "flare": "Flare", "journal": "Journal", "pause": "Pause",
}
const MAX_KEYS := 4
## [name, characters per second]; 0 shows the whole line at once.
const TEXT_SPEEDS := [["Slow", 24.0], ["Normal", 42.0], ["Fast", 90.0], ["Instant", 0.0]]
const BASE := Vector2i(480, 270)
const DEFAULT_SCALE := 3
const PAD_NAMES := {
	JOY_BUTTON_A: "A", JOY_BUTTON_B: "B", JOY_BUTTON_X: "X", JOY_BUTTON_Y: "Y",
	JOY_BUTTON_BACK: "Select", JOY_BUTTON_START: "Start",
	JOY_BUTTON_LEFT_SHOULDER: "LB", JOY_BUTTON_RIGHT_SHOULDER: "RB",
	JOY_BUTTON_DPAD_UP: "D-pad up", JOY_BUTTON_DPAD_DOWN: "D-pad down",
	JOY_BUTTON_DPAD_LEFT: "D-pad left", JOY_BUTTON_DPAD_RIGHT: "D-pad right",
}
const PAD_GLYPHS := {
	JOY_BUTTON_A: "res://assets/ui/pad_a.png",
	JOY_BUTTON_B: "res://assets/ui/pad_b.png",
	JOY_BUTTON_X: "res://assets/ui/pad_x.png",
	JOY_BUTTON_Y: "res://assets/ui/pad_y.png",
}
const SHORT_NAMES := {"Escape": "Esc", "BackSpace": "Backspace", "PageUp": "PgUp", "PageDown": "PgDn"}

var music := 0.8
var sound := 0.8
var fullscreen := false
## Window size as a multiple of 480x270; 0 = the default (3x, or less on a small screen).
var window_scale := 0
var text_speed := 1
var using_pad := false

var _path := "user://settings.cfg"
var _apply_window := true
var _glyphs := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		_path = "user://debug_settings.cfg"
		_apply_window = "--window" in args
		using_pad = "--pad" in args
	_load()
	apply_audio()
	apply_window()


# --- saving -------------------------------------------------------------------

func _load() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(_path) != OK:
		return
	music = cfg.get_value("audio", "music", music)
	sound = cfg.get_value("audio", "sound", sound)
	fullscreen = cfg.get_value("display", "fullscreen", fullscreen)
	window_scale = cfg.get_value("display", "scale", window_scale)
	text_speed = clampi(cfg.get_value("game", "text_speed", text_speed), 0, TEXT_SPEEDS.size() - 1)
	for action: String in ACTIONS:
		if not cfg.has_section_key("keys", action):
			continue
		var list = cfg.get_value("keys", action)
		if list is Array and not list.is_empty():
			_set_events(action, list)


func save() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("audio", "music", music)
	cfg.set_value("audio", "sound", sound)
	cfg.set_value("display", "fullscreen", fullscreen)
	cfg.set_value("display", "scale", window_scale)
	cfg.set_value("game", "text_speed", text_speed)
	# only bindings that differ from the defaults, so new defaults still reach old saves
	for action: String in ACTIONS:
		var list := keys(action)
		if not _same(list, Game.BINDINGS[action]):
			cfg.set_value("keys", action, list)
	cfg.save(_path)


static func _same(a: Array, b: Array) -> bool:
	if a.size() != b.size():
		return false
	for i in a.size():
		if int(a[i]) != int(b[i]):
			return false
	return true


# --- audio, window, text ------------------------------------------------------

func apply_audio() -> void:
	Sound.set_volume("Music", music)
	Sound.set_volume("Ambience", music)
	Sound.set_volume("SFX", sound)
	Sound.set_volume("Voice", sound)


## The biggest whole-number window scale that fits on this screen.
func max_scale() -> int:
	var usable := DisplayServer.screen_get_usable_rect(DisplayServer.window_get_current_screen()).size
	return clampi(mini(floori(usable.x / float(BASE.x)), floori((usable.y - 40) / float(BASE.y))), 1, 6)


func current_scale() -> int:
	return clampi(window_scale if window_scale > 0 else DEFAULT_SCALE, 1, max_scale())


func apply_window() -> void:
	if not _apply_window:
		return
	if fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
		return
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	var size := BASE * current_scale()
	var screen := DisplayServer.screen_get_usable_rect(DisplayServer.window_get_current_screen())
	DisplayServer.window_set_size(size)
	DisplayServer.window_set_position(screen.position + (screen.size - size) / 2)


func chars_per_sec() -> float:
	return TEXT_SPEEDS[text_speed][1]


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("fullscreen"):
		fullscreen = not fullscreen
		apply_window()
		save()
		changed.emit()


# --- keyboard or gamepad --------------------------------------------------------

func _input(event: InputEvent) -> void:
	var pad := using_pad
	if event is InputEventJoypadButton and event.pressed:
		pad = true
	elif event is InputEventJoypadMotion and absf(event.axis_value) > 0.5:
		pad = true
	elif (event is InputEventKey and event.pressed) or event is InputEventMouseButton:
		pad = false
	if pad != using_pad:
		using_pad = pad
		changed.emit()


# --- bindings -------------------------------------------------------------------

## Physical keycodes bound to an action, in order.
func keys(action: String) -> Array[int]:
	var out: Array[int] = []
	for ev in InputMap.action_get_events(action):
		if ev is InputEventKey:
			out.append(ev.physical_keycode if ev.physical_keycode != KEY_NONE else ev.keycode)
	return out


func set_keys(action: String, list: Array) -> void:
	_set_events(action, list)
	save()
	changed.emit()


func reset_keys() -> void:
	for action: String in ACTIONS:
		_set_events(action, Game.BINDINGS[action])
	save()
	changed.emit()


func _set_events(action: String, list: Array) -> void:
	for ev in InputMap.action_get_events(action):
		if ev is InputEventKey:
			InputMap.action_erase_event(action, ev)
	for code in list.slice(0, MAX_KEYS):
		var ev := InputEventKey.new()
		ev.physical_keycode = int(code)
		InputMap.action_add_event(action, ev)


# --- names for prompts ----------------------------------------------------------

## A key's name as printed on this keyboard's layout ("E", "Space", "Esc").
func key_name(physical: int) -> String:
	var shown := KEY_NONE
	if DisplayServer.get_name() != "headless":  # headless test runs have no keyboard layout
		shown = DisplayServer.keyboard_get_label_from_physical(physical)
	var text := OS.get_keycode_string(shown if shown != KEY_NONE else physical)
	return SHORT_NAMES.get(text, text)


## What to press for an action right now: its first key, or its gamepad button.
func label(action: String) -> String:
	if using_pad:
		var buttons: Array = Game.PAD_BUTTONS.get(action, [])
		if not buttons.is_empty():
			return PAD_NAMES.get(buttons[0], "?")
	var list := keys(action)
	return key_name(list[0]) if not list.is_empty() else "-"


func key_text(action: String) -> String:
	return "[%s]" % label(action)


## A picture of the gamepad button for an action, or null on a keyboard.
func pad_glyph(action: String) -> Texture2D:
	if not using_pad:
		return null
	var buttons: Array = Game.PAD_BUTTONS.get(action, [])
	if buttons.is_empty() or not PAD_GLYPHS.has(buttons[0]):
		return null
	# kept here: a texture nothing holds on to is freed before the frame draws it
	if not _glyphs.has(buttons[0]):
		_glyphs[buttons[0]] = load(PAD_GLYPHS[buttons[0]])
	return _glyphs[buttons[0]]
