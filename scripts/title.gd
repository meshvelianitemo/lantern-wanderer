extends CanvasLayer
## Title screen shown once on launch, over the first level:
## Continue / New Journey / Options / Credits / Quit.
## Starting over when there is a save asks first, because it replaces that save.

const GOLD := Color(1.0, 0.91, 0.64)
const DIM := Color(0.6, 0.62, 0.7)
const MENU_Y := 166

var _options: Array[String] = []
var _labels: Array[Label] = []
var _sel := 0
var _done := false
var _root: Control
var _note: Label
var _hint: Label
var _t := 0.0
var _options_ui: Options
var _credits: Credits


func _ready() -> void:
	layer = 30
	get_tree().paused = false
	if Game.started:
		queue_free()
		return
	Game.in_dialogue = true
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.02, 0.06, 0.55)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(shade)

	var title := _label("LANTERN WANDERER", GOLD, 3, 58)
	title.modulate.a = 0.0
	var sub := _label("a small light, a long way down", Color(0.72, 0.78, 0.86), 1, 100)
	sub.modulate.a = 0.0
	_note = _label("", Color(0.93, 0.9, 0.85), 1, MENU_Y - 20)
	var tw := create_tween()
	tw.tween_interval(0.6)
	tw.tween_property(title, "modulate:a", 1.0, 1.6)
	tw.tween_property(sub, "modulate:a", 1.0, 1.2)
	_set_menu(_main_menu())
	for l in _labels:
		l.modulate.a = 0.0
		tw.parallel().tween_property(l, "modulate:a", 1.0, 0.8)
	_hint = _label("", Color(0.4, 0.42, 0.5), 1, 252)
	_options_ui = Options.new()
	add_child(_options_ui)
	_credits = Credits.new()
	add_child(_credits)
	Settings.changed.connect(_update_hint)
	_update_hint()
	Sound.music("title", 2.0)


func _main_menu() -> Array[String]:
	if Game.has_save():
		return ["Continue", "New Journey", "Options", "Credits", "Quit"]
	return ["Begin", "Options", "Credits", "Quit"]


func _set_menu(options: Array[String], note := "") -> void:
	for l in _labels:
		l.queue_free()
	_labels.clear()
	_options = options
	_sel = 0
	_note.text = note
	for i in _options.size():
		_labels.append(_label(_options[i], DIM, 1, MENU_Y + i * 16))
	_refresh()


func _update_hint() -> void:
	_hint.text = "" if Settings.using_pad else "F11 fullscreen"


func _label(text: String, color: Color, scale_factor: int, y: int) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.size = Vector2(480.0 / scale_factor, 12)
	l.position = Vector2(0, y)
	l.scale = Vector2(scale_factor, scale_factor)
	l.add_theme_color_override("font_color", color)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(l)
	return l


func _refresh() -> void:
	for i in _labels.size():
		var on := i == _sel
		_labels[i].text = ("- %s -" if on else "%s") % _options[i]
		_labels[i].add_theme_color_override("font_color", GOLD if on else DIM)


func _process(delta: float) -> void:
	_t += delta
	if _done or _t < 1.0 or _credits.visible:
		return
	if _options_ui.visible:
		if not _options_ui.handle_input():
			_root.visible = true
		return
	if Util.menu("up"):
		_sel = (_sel - 1 + _options.size()) % _options.size()
		Sound.sfx("ui_move")
		_refresh()
	elif Util.menu("down"):
		_sel = (_sel + 1) % _options.size()
		Sound.sfx("ui_move")
		_refresh()
	elif Util.menu("accept"):
		_pick(_options[_sel])
	elif Util.menu("back") and _note.text != "":
		_set_menu(_main_menu())


func _pick(option: String) -> void:
	Sound.sfx("ui_select")
	match option:
		"Quit":
			get_tree().quit()
			return
		"Options":
			_root.visible = false
			_options_ui.open()
			return
		"Credits":
			_root.visible = false
			_credits.open(false)
			await _credits.closed
			_root.visible = true
			return
		"New Journey":
			_set_menu(["Keep my journey", "Start over"], "Starting over replaces your saved journey.")
			return
		"Keep my journey":
			_set_menu(_main_menu())
			_sel = 1
			_refresh()
			return
		"Continue":
			if not Game.load_game():
				Game.new_game()
		_:
			Game.new_game()
	_done = true
	Game.started = true
	Sound.music("")
	await Game.fade_out(1.0)
	Game.in_dialogue = false
	get_tree().reload_current_scene()
