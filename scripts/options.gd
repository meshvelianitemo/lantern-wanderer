class_name Options
extends Control
## Options (from the title screen and the pause menu): fullscreen, window size, volumes,
## text speed, and a Controls page for rebinding keys. Values live in Settings, which saves them.
## The owner calls handle_input() every frame while it is open; it returns false once closed.

const GOLD := Color(1.0, 0.91, 0.64)
const TEXT := Color(0.93, 0.9, 0.85)
const SOFT := Color(0.74, 0.8, 0.86)
const DIM := Color(0.6, 0.62, 0.7)
const OFF := Color(0.36, 0.36, 0.44)
const ITEMS := ["Display", "Window size", "Music", "Sound", "Text speed", "Controls", "Back"]
const HINTS := {
	"Display": "F11 switches it too.",
	"Window size": "Bigger windows keep the pixels sharp: always a whole number.",
	"Text speed": "How fast dialogue appears.",
	"Controls": "Choose which keys do what.",
}
const PAD_LEGEND := "Gamepad:  A jump   X / B talk   Y / RB flare   Start pause   Select journal"
const SLOT_X := 150.0
const SLOT_W := 76.0

## 0 = options, 1 = controls
var _page := 0
var _sel := 0
var _slot := 0
var _listening := false
## Frames to ignore menu input for (after a key was captured for a binding).
var _cooldown := 0
## A one-off message shown in the footer of the Controls page.
var _note := ""

var _title: Label
var _main: Control
var _controls: Control
var _names: Array[Label] = []
var _values: Array[Label] = []
var _hint: Label
var _action_labels: Array[Label] = []
var _slot_labels: Array = []
var _reset: Label
var _back: Label
var _footer: Label


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.02, 0.06, 0.82)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(shade)
	var panel := NinePatchRect.new()
	panel.texture = preload("res://assets/ui/panel.png")
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		panel.set_patch_margin(side, 7)
	panel.position = Vector2(16, 10)
	panel.size = Vector2(448, 250)
	add_child(panel)
	_title = _label(self, "", GOLD, Vector2(16, 18), 448, HORIZONTAL_ALIGNMENT_CENTER)
	_line(self, Vector2(28, 33), Vector2(424, 1))
	_line(self, Vector2(28, 234), Vector2(424, 1))
	_footer = _label(self, "", DIM, Vector2(30, 239), 420)

	_main = Control.new()
	add_child(_main)
	for i in ITEMS.size():
		_names.append(_label(_main, ITEMS[i], DIM, Vector2(110, 48 + i * 17), 130))
		_values.append(_label(_main, "", SOFT, Vector2(240, 48 + i * 17), 200))
	_hint = _label(_main, "", DIM, Vector2(30, 212), 420, HORIZONTAL_ALIGNMENT_CENTER)

	_controls = Control.new()
	add_child(_controls)
	_label(_controls, "Action", OFF, Vector2(40, 38), 100)
	_label(_controls, "Keys", OFF, Vector2(SLOT_X, 38), 100)
	for action: String in Settings.ACTIONS:
		var y := 52.0 + _action_labels.size() * 13.0
		_action_labels.append(_label(_controls, Settings.ACTIONS[action], DIM, Vector2(40, y), 108))
		var slots: Array[Label] = []
		for s in Settings.MAX_KEYS:
			slots.append(_label(_controls, "", TEXT, Vector2(SLOT_X + s * SLOT_W, y), SLOT_W))
		_slot_labels.append(slots)
	_reset = _label(_controls, "Reset to defaults", DIM, Vector2(40, 174), 200)
	_back = _label(_controls, "Back", DIM, Vector2(40, 188), 200)
	_label(_controls, PAD_LEGEND, OFF, Vector2(30, 214), 420, HORIZONTAL_ALIGNMENT_CENTER)
	Settings.changed.connect(func() -> void:
		if visible:
			_refresh())


func _label(parent: Node, text: String, color: Color, pos: Vector2, width: float,
		align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.size = Vector2(width, 12)
	l.horizontal_alignment = align
	l.add_theme_color_override("font_color", color)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(l)
	return l


func _line(parent: Node, pos: Vector2, size_: Vector2) -> void:
	var r := ColorRect.new()
	r.color = Color(0.55, 0.47, 0.36, 0.55)
	r.position = pos
	r.size = size_
	parent.add_child(r)


func open() -> void:
	visible = true
	_page = 0
	_sel = 0
	_listening = false
	_cooldown = 1
	_note = ""
	Sound.sfx("ui_select")
	_refresh()


## Call every frame while open. Returns false once closed.
func handle_input() -> bool:
	if _listening:
		return true
	if _cooldown > 0:
		_cooldown -= 1
		return true
	if _page == 0:
		return _options_input()
	_controls_input()
	return true


func _close() -> bool:
	visible = false
	Sound.sfx("ui_move")
	return false


# --- options page -------------------------------------------------------------

func _options_input() -> bool:
	if Util.menu("up"):
		_sel = wrapi(_sel - 1, 0, ITEMS.size())
		Sound.sfx("ui_move")
	elif Util.menu("down"):
		_sel = wrapi(_sel + 1, 0, ITEMS.size())
		Sound.sfx("ui_move")
	elif Util.menu("left"):
		_change(-1)
	elif Util.menu("right"):
		_change(1)
	elif Util.menu("back"):
		return _close()
	elif Util.menu("accept"):
		match ITEMS[_sel]:
			"Back":
				return _close()
			"Controls":
				_page = 1
				_sel = 0
				_slot = 0
				_note = ""
				Sound.sfx("page")
			"Music", "Sound":
				pass
			_:
				_change(1)
	else:
		return true
	_refresh()
	return true


func _change(step: int) -> void:
	match ITEMS[_sel]:
		"Display":
			Settings.fullscreen = not Settings.fullscreen
			Settings.apply_window()
		"Window size":
			if Settings.fullscreen:
				return
			Settings.window_scale = clampi(Settings.current_scale() + step, 1, Settings.max_scale())
			Settings.apply_window()
		"Music":
			Settings.music = clampf(snappedf(Settings.music + step * 0.1, 0.1), 0.0, 1.0)
			Settings.apply_audio()
		"Sound":
			Settings.sound = clampf(snappedf(Settings.sound + step * 0.1, 0.1), 0.0, 1.0)
			Settings.apply_audio()
		"Text speed":
			Settings.text_speed = wrapi(Settings.text_speed + step, 0, Settings.TEXT_SPEEDS.size())
		_:
			return
	Settings.save()
	Sound.sfx("ui_move")
	Settings.changed.emit()


func _value(item: String) -> String:
	match item:
		"Display":
			return "Fullscreen" if Settings.fullscreen else "Window"
		"Window size":
			var s := Settings.current_scale()
			return "%dx  (%d x %d)" % [s, s * Settings.BASE.x, s * Settings.BASE.y]
		"Music":
			return _bar(Settings.music)
		"Sound":
			return _bar(Settings.sound)
		"Text speed":
			return Settings.TEXT_SPEEDS[Settings.text_speed][0]
	return ""


static func _bar(v: float) -> String:
	var n := roundi(v * 10.0)
	return "|".repeat(n) + ".".repeat(10 - n)


# --- controls page ------------------------------------------------------------

func _action(row: int) -> String:
	return Settings.ACTIONS.keys()[row]


## The rightmost slot you can pick on a row: one past its last key, to add another.
func _max_slot() -> int:
	return mini(Settings.keys(_action(_sel)).size(), Settings.MAX_KEYS - 1)


func _controls_input() -> void:
	var n := Settings.ACTIONS.size()
	if Util.menu("up"):
		_sel = wrapi(_sel - 1, 0, n + 2)
		Sound.sfx("ui_move")
	elif Util.menu("down"):
		_sel = wrapi(_sel + 1, 0, n + 2)
		Sound.sfx("ui_move")
	elif Util.menu("left") and _sel < n:
		_slot = maxi(_slot - 1, 0)
		Sound.sfx("ui_move")
	elif Util.menu("right") and _sel < n:
		_slot = mini(_slot + 1, _max_slot())
		Sound.sfx("ui_move")
	elif Util.menu("back"):
		_leave_controls()
	elif Util.menu("accept"):
		if _sel < n:
			_listening = true
			_note = ""
			Sound.sfx("ui_select")
		elif _sel == n:
			Settings.reset_keys()
			_note = "Every key is back to the default."
			Sound.sfx("ui_select")
		else:
			_leave_controls()
	else:
		return
	if _sel < n:
		_slot = mini(_slot, _max_slot())
	_refresh()


func _leave_controls() -> void:
	_page = 0
	_sel = ITEMS.find("Controls")
	Sound.sfx("page")


func _input(event: InputEvent) -> void:
	if not visible or _page != 1:
		return
	if _listening and event is InputEventJoypadButton and event.pressed:
		# gamepad buttons are fixed; any button cancels
		_listening = false
		_cooldown = 2
		_refresh()
		return
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	var code: int = key.physical_keycode if key.physical_keycode != KEY_NONE else key.keycode
	if _listening:
		get_viewport().set_input_as_handled()
		_listening = false
		_cooldown = 2
		match code:
			KEY_ESCAPE:
				_note = ""
			KEY_BACKSPACE, KEY_DELETE:
				_clear_slot()
			KEY_F11:
				_note = "F11 stays the fullscreen key."
			_:
				_bind(code)
		_refresh()
	elif _sel < Settings.ACTIONS.size() and code in [KEY_BACKSPACE, KEY_DELETE]:
		get_viewport().set_input_as_handled()
		_clear_slot()
		_refresh()


func _bind(code: int) -> void:
	var action := _action(_sel)
	var list := Settings.keys(action)
	if _slot < list.size():
		list[_slot] = code
	else:
		list.append(code)
	var unique: Array[int] = []
	for k in list:
		if not unique.has(k):
			unique.append(k)
	Settings.set_keys(action, unique)
	_slot = unique.find(code)
	_note = "%s: %s" % [Settings.ACTIONS[action], Settings.key_name(code)]
	var others: PackedStringArray = []
	for other: String in Settings.ACTIONS:
		if other != action and Settings.keys(other).has(code):
			others.append(Settings.ACTIONS[other])
	if not others.is_empty():
		_note += "   (also %s)" % ", ".join(others)
	Sound.sfx("ui_select")


func _clear_slot() -> void:
	var action := _action(_sel)
	var list := Settings.keys(action)
	if _slot >= list.size():
		return
	if list.size() <= 1:
		_note = "Every action needs at least one key."
		return
	list.remove_at(_slot)
	Settings.set_keys(action, list)
	_slot = mini(_slot, _max_slot())
	Sound.sfx("ui_move")


# --- drawing ------------------------------------------------------------------

func _refresh() -> void:
	_main.visible = _page == 0
	_controls.visible = _page == 1
	var ok := Settings.key_text("interact")
	var back := Settings.key_text("pause")
	if _page == 0:
		_title.text = "Options"
		for i in ITEMS.size():
			var on := i == _sel
			var item: String = ITEMS[i]
			var off := item == "Window size" and Settings.fullscreen
			_names[i].text = ("> " if on else "  ") + item
			_names[i].add_theme_color_override("font_color", GOLD if on else (OFF if off else DIM))
			var v := "-" if off else _value(item)
			_values[i].text = ("< %s >" % v) if on and v != "" and not off else v
			_values[i].add_theme_color_override("font_color", OFF if off else (TEXT if on else SOFT))
		_hint.text = HINTS.get(ITEMS[_sel], "")
		_footer.text = "^ v choose    < > change    %s select    %s back" % [ok, back]
		return
	_title.text = "Controls"
	var n := Settings.ACTIONS.size()
	for row in n:
		var on := row == _sel
		_action_labels[row].text = ("> " if on else "  ") + Settings.ACTIONS[_action(row)]
		_action_labels[row].add_theme_color_override("font_color", GOLD if on else DIM)
		var list := Settings.keys(_action(row))
		for s in Settings.MAX_KEYS:
			var l: Label = _slot_labels[row][s]
			var text := ""
			var color := TEXT
			if s < list.size():
				text = Settings.key_name(list[s])
			elif s == list.size():
				text = "+"
				color = OFF
			if on and s == _slot:
				text = "[%s]" % ("..." if _listening else text)
				color = GOLD
			l.text = text
			l.add_theme_color_override("font_color", color)
	for pair: Array in [[_reset, n, "Reset to defaults"], [_back, n + 1, "Back"]]:
		var on: bool = _sel == pair[1]
		pair[0].text = ("> " if on else "  ") + pair[2]
		pair[0].add_theme_color_override("font_color", GOLD if on else DIM)
	if _listening:
		_footer.text = "Press a key for %s.    Esc cancels    Del clears" % Settings.ACTIONS[_action(_sel)]
	elif _note != "":
		_footer.text = _note
	else:
		_footer.text = "^ v choose    < > pick a key    %s change    Del clear    %s back" % [ok, back]
