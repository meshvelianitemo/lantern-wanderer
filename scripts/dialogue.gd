extends CanvasLayer
## Dialogue box (autoload "Dialogue").
##   await Dialogue.run("some_id")            or  Dialogue.run("some_id", "tallow") to voice "???" lines
## Entries come from Story.DIALOGUES. Each entry is a dictionary:
##   {who, text}                    a line (empty `who` = narration)
##   {..., choices: [...]}          line followed by a choice; each choice: {text, goto?, set?,
##                                  if?, give?: npc (share an ember; disabled with none), event?,
##                                  locked?: true (shown greyed out, can never be chosen)}
##   {if: "cond"}                   on any entry: skip it unless the condition holds (see Game.check)
##   {set: "flag"}                  set a story flag ({unset: "flag"} forgets one)
##   {goto: "other_id"}             continue with another sequence
##   {event: "name"}                emit `event` (NPCs, the level and cutscenes listen)
##   {card: "Title", sub: "..."}    show a title card with the box hidden
##   {music: "id"} {sfx: "id"} {wait: seconds}
## Text may contain {names}, {new_names}, {embers} or {key:<action>} (see Game.format_text).
## Typing speed is the player's Text speed setting.

signal typing_changed(who: String, typing: bool)
signal event(name: String)
signal finished

const NAME_COLOR := Color(1.0, 0.91, 0.64)
const TEXT_COLOR := Color(0.93, 0.9, 0.85)
const NARRATION_COLOR := Color(0.74, 0.8, 0.86)
const CHOICE_DIM := Color(0.6, 0.62, 0.7)
const CHOICE_OFF := Color(0.36, 0.36, 0.44)
## Typed characters between two voice syllables.
const VOICE_EVERY := 3

var active := false

var _root: Control
var _panel: NinePatchRect
var _name_plate: NinePatchRect
var _name: Label
var _text: Label
var _arrow: TextureRect
var _choice_panel: NinePatchRect
var _choice_box: VBoxContainer
var _t := 0.0
var _voice_hint := ""


func _ready() -> void:
	layer = 60  # above the fade, so endings can speak over black
	process_mode = Node.PROCESS_MODE_ALWAYS
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.visible = false
	add_child(_root)

	_panel = _nine("res://assets/ui/panel.png", 7, Vector2(52, 198), Vector2(376, 64))
	_name_plate = _nine("res://assets/ui/nameplate.png", 4, Vector2(64, 190), Vector2(60, 14))
	_name = Label.new()
	_name.position = Vector2(6, 1)
	_name.add_theme_color_override("font_color", NAME_COLOR)
	_name_plate.add_child(_name)

	_text = Label.new()
	_text.position = Vector2(66, 208)
	_text.size = Vector2(348, 48)
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING
	_root.add_child(_text)

	_arrow = TextureRect.new()
	_arrow.texture = preload("res://assets/ui/arrow.png")
	_arrow.position = Vector2(412, 252)
	_root.add_child(_arrow)

	_choice_panel = _nine("res://assets/ui/panel.png", 7, Vector2(296, 140), Vector2(132, 50))
	_choice_box = VBoxContainer.new()
	_choice_box.position = Vector2(10, 8)
	_choice_box.add_theme_constant_override("separation", 3)
	_choice_panel.add_child(_choice_box)
	_choice_panel.visible = false


func _nine(path: String, margin: int, pos: Vector2, size: Vector2) -> NinePatchRect:
	var n := NinePatchRect.new()
	n.texture = load(path)
	n.patch_margin_left = margin
	n.patch_margin_right = margin
	n.patch_margin_top = margin
	n.patch_margin_bottom = margin
	n.position = pos
	n.size = size
	_root.add_child(n)
	return n


func _process(delta: float) -> void:
	_t += delta
	_arrow.position.y = 252 + roundf(sin(_t * 6.0))


func run(id: String, voice_hint := "") -> void:
	if active:
		return
	if not Story.DIALOGUES.has(id):
		push_warning("Unknown dialogue: %s" % id)
		return
	active = true
	_voice_hint = voice_hint
	Game.in_dialogue = true
	_show_box(true)
	await get_tree().process_frame

	var seq: Array = Story.DIALOGUES[id]
	var i := 0
	while i < seq.size():
		var entry: Dictionary = seq[i]
		i += 1
		if not Game.check(entry.get("if", "")):
			continue
		if entry.has("set"):
			Game.set_flag(entry["set"])
		if entry.has("unset"):
			Game.clear_flag(entry["unset"])
		if entry.has("event"):
			event.emit(entry["event"])
		if entry.has("music"):
			Sound.music(entry["music"])
		if entry.has("sfx"):
			Sound.sfx(entry["sfx"])
		if entry.has("wait"):
			await get_tree().create_timer(float(entry["wait"])).timeout
		if entry.has("card"):
			await _hide_box()
			await Game.show_title_card(entry["card"], entry.get("sub", ""), entry.get("hold", 2.2))
			if i < seq.size():
				_show_box(false)
		if entry.has("goto") and not entry.has("text"):
			seq = Story.DIALOGUES[entry["goto"]]
			i = 0
			continue
		if not entry.has("text"):
			continue
		if not _root.visible:
			_show_box(false)
		var who: String = entry.get("who", "")
		await _type_line(who, entry["text"])
		if entry.has("choices"):
			var choices: Array = entry["choices"].filter(func(c: Dictionary) -> bool: return Game.check(c.get("if", "")))
			var choice: Dictionary = choices[await _choose(choices)]
			Sound.sfx("ui_select")
			if choice.has("give"):
				Game.give_ember(choice["give"])
			if choice.has("set"):
				Game.set_flag(choice["set"])
			if choice.has("event"):
				event.emit(choice["event"])
			if choice.has("goto"):
				seq = Story.DIALOGUES[choice["goto"]]
				i = 0
		else:
			_arrow.visible = true
			await _wait_confirm()
			_arrow.visible = false

	if _root.visible:
		await _hide_box()
	await get_tree().process_frame
	Game.in_dialogue = false
	active = false
	finished.emit()


func _show_box(fade: bool) -> void:
	_root.visible = true
	_root.modulate.a = 0.0 if fade else 1.0
	_text.text = ""
	_name_plate.visible = false
	_arrow.visible = false
	if fade:
		create_tween().tween_property(_root, "modulate:a", 1.0, 0.15)


func _hide_box() -> void:
	var tw := create_tween()
	tw.tween_property(_root, "modulate:a", 0.0, 0.12)
	await tw.finished
	_root.visible = false


func _voice_for(who: String) -> String:
	if who == "":
		return "narration"
	if who == "???":
		return _voice_hint
	for id: String in Story.NPCS:
		var data: Dictionary = Story.NPCS[id]
		if data.get("name", "") == who:
			return data.get("voice", id)
	# the wicks of the Echoes (Lark, Maud, Vesper) speak without being NPCs
	var own := Sound.voice_for(who)
	return own if Sound.has_voice(own) else _voice_hint


func _type_line(who: String, text: String) -> void:
	text = Game.format_text(text)
	_arrow.visible = false
	_name_plate.visible = who != ""
	_name.text = who
	_name_plate.size.x = _name.get_minimum_size().x + 12
	_text.add_theme_color_override("font_color", TEXT_COLOR if who != "" else NARRATION_COLOR)
	_text.text = text
	_text.visible_characters = 0
	typing_changed.emit(who, true)
	var voice := _voice_for(who)
	var total := _text.get_total_character_count()
	var shown := 0.0
	var last_voiced := -VOICE_EVERY
	var speed := Settings.chars_per_sec()
	if speed <= 0.0 and voice != "":
		Sound.voice(voice)  # instant text still gets one syllable
	while _text.visible_characters < total:
		await get_tree().process_frame
		if _confirm_pressed() or speed <= 0.0:
			break
		shown += speed * get_process_delta_time()
		_text.visible_characters = int(shown)
		var n := _text.visible_characters
		if voice != "" and n - last_voiced >= VOICE_EVERY and n < total:
			var c := text[mini(n, text.length() - 1)]
			if c != " " and c != "." and c != ",":
				Sound.voice(voice)
				last_voiced = n
	_text.visible_characters = -1
	typing_changed.emit(who, false)
	await get_tree().process_frame


func _choice_enabled(choice: Dictionary) -> bool:
	if choice.get("locked", false):
		return false
	return not choice.has("give") or Game.embers > 0


func _choice_text(choice: Dictionary) -> String:
	if choice.has("give") and Game.embers <= 0:
		return choice["text"] + " (no embers)"
	return choice["text"]


func _choose(choices: Array) -> int:
	for c in _choice_box.get_children():
		c.queue_free()
	var labels: Array[Label] = []
	var widest := 0.0
	for choice: Dictionary in choices:
		var l := Label.new()
		l.text = "  " + _choice_text(choice)
		_choice_box.add_child(l)
		labels.append(l)
		widest = maxf(widest, l.get_minimum_size().x)
	_choice_panel.size = Vector2(widest + 26, choices.size() * 14 + 14)
	_choice_panel.position = Vector2(428 - _choice_panel.size.x, 196 - _choice_panel.size.y)
	_choice_panel.visible = true
	var sel := 0
	while sel < choices.size() - 1 and not _choice_enabled(choices[sel]):
		sel += 1
	while true:
		for j in labels.size():
			var on := _choice_enabled(choices[j])
			labels[j].text = ("> " if j == sel else "  ") + _choice_text(choices[j])
			labels[j].add_theme_color_override("font_color", NAME_COLOR if j == sel else (CHOICE_DIM if on else CHOICE_OFF))
		await get_tree().process_frame
		var step := 0
		if Util.menu("up"):
			step = -1
		elif Util.menu("down"):
			step = 1
		elif Input.is_action_just_pressed("interact") or Input.is_action_just_pressed("ui_accept"):
			break
		if step != 0:
			Sound.sfx("ui_move")
			for _k in choices.size():
				sel = (sel + step + choices.size()) % choices.size()
				if _choice_enabled(choices[sel]):
					break
	_choice_panel.visible = false
	await get_tree().process_frame
	return sel


func _wait_confirm() -> void:
	while true:
		await get_tree().process_frame
		if _confirm_pressed():
			return


func _confirm_pressed() -> bool:
	return Input.is_action_just_pressed("interact") or Input.is_action_just_pressed("jump") \
		or Input.is_action_just_pressed("ui_accept")
