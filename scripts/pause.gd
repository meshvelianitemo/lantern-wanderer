extends CanvasLayer
## Pause menu (Esc / P / Start): resume, the Journal, Options, back to title.
## Tab / Select opens the Journal straight from play.

const GOLD := Color(1.0, 0.91, 0.64)
const DIM := Color(0.6, 0.62, 0.7)
const ITEMS := ["Resume", "Journal", "Options", "Quit to Title"]

var _root: Control
var _labels: Array[Label] = []
var _sel := 0
var _journal: Journal
var _options: Options
## The Journal was opened straight from play, so closing it resumes play too.
var _journal_direct := false


func _ready() -> void:
	layer = 40
	process_mode = Node.PROCESS_MODE_ALWAYS
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.visible = false
	add_child(_root)
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.02, 0.06, 0.7)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(shade)
	var panel := NinePatchRect.new()
	panel.texture = preload("res://assets/ui/panel.png")
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		panel.set_patch_margin(side, 7)
	panel.position = Vector2(160, 70)
	panel.size = Vector2(160, 118)
	_root.add_child(panel)
	var title := Label.new()
	title.text = "Resting"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.size = Vector2(160, 12)
	title.position = Vector2(160, 80)
	title.add_theme_color_override("font_color", GOLD)
	_root.add_child(title)
	for i in ITEMS.size():
		var l := Label.new()
		l.position = Vector2(190, 104 + i * 18)
		_root.add_child(l)
		_labels.append(l)
	_journal = Journal.new()
	add_child(_journal)
	_options = Options.new()
	add_child(_options)


func _can_pause() -> bool:
	var p: Player = Game.player
	return Game.started and not Game.in_dialogue and not Game.travelling \
		and is_instance_valid(p) and not p.frozen


func _open() -> void:
	_root.visible = true
	_sel = 0
	get_tree().paused = true
	Sound.sfx("ui_select")
	_refresh()


func _close() -> void:
	_root.visible = false
	get_tree().paused = false


func _process(_delta: float) -> void:
	if _journal.visible:
		if not _journal.handle_input():
			if _journal_direct:
				_close()
			else:
				_root.visible = true
		return
	if _options.visible:
		if not _options.handle_input():
			_root.visible = true
			_refresh()
		return
	if Input.is_action_just_pressed("journal") and not _root.visible and _can_pause():
		_open()
		_root.visible = false
		_journal_direct = true
		_journal.open()
		return
	if Input.is_action_just_pressed("pause"):
		if _root.visible:
			_close()
		elif _can_pause():
			_open()
		return
	if not _root.visible:
		return
	if Util.menu("up"):
		_sel = (_sel - 1 + ITEMS.size()) % ITEMS.size()
		Sound.sfx("ui_move")
	elif Util.menu("down"):
		_sel = (_sel + 1) % ITEMS.size()
		Sound.sfx("ui_move")
	elif Util.menu("accept"):
		match ITEMS[_sel]:
			"Resume":
				_close()
			"Journal":
				_journal_direct = false
				_root.visible = false
				_journal.open()
				return
			"Options":
				_root.visible = false
				_options.open()
				return
			"Quit to Title":
				_root.visible = false
				_to_title()
	_refresh()


func _refresh() -> void:
	for i in ITEMS.size():
		_labels[i].text = ("> " if i == _sel else "  ") + ITEMS[i]
		_labels[i].add_theme_color_override("font_color", GOLD if i == _sel else DIM)


func _to_title() -> void:
	await Game.fade_out(0.6)
	Sound.music("", 1.0)
	Sound.ambience("", 1.0)
	Game.new_game()
	Game.started = false
	get_tree().paused = false
	get_tree().reload_current_scene()
