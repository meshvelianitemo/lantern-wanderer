class_name Journal
extends Control
## The Journal (Pause > Journal, or Tab / Select): the places you have been,
## the people you have met, the tablets you have read, and the Keeper names
## you have found. Left/right turns the page, up/down picks an entry.
## Content lives in JournalData.

const GOLD := Color(1.0, 0.91, 0.64)
const TEXT := Color(0.93, 0.9, 0.85)
const SOFT := Color(0.74, 0.8, 0.86)
const DIM := Color(0.6, 0.62, 0.7)
const OFF := Color(0.36, 0.36, 0.44)
const PAGES := ["Places", "People", "Tablets", "Names", "Echoes"]
const ROWS := 13

var _page := 0
var _sel := 0
var _scroll := 0
## [{title, known, sub, body}]
var _entries: Array = []
var _page_labels: Array[Label] = []
var _rows: Array[Label] = []
var _title: Label
var _sub: Label
var _body: Label
var _count: Label
var _help: Label
var _ember: TextureRect


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
	_label("Journal", GOLD, Vector2(16, 18), 448, HORIZONTAL_ALIGNMENT_CENTER)
	var x := 55.0
	for i in PAGES.size():
		_page_labels.append(_label(PAGES[i], DIM, Vector2(x, 34), 72, HORIZONTAL_ALIGNMENT_CENTER))
		x += 74.0
	_line(Vector2(28, 49), Vector2(424, 1))
	_line(Vector2(150, 54), Vector2(1, 176))
	for i in ROWS:
		_rows.append(_label("", DIM, Vector2(30, 55 + i * 13), 118))
	_title = _label("", GOLD, Vector2(160, 55), 290)
	_sub = _label("", SOFT, Vector2(160, 68), 290)
	_body = _label("", TEXT, Vector2(160, 84), 288)
	_body.size.y = 146
	_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_body.clip_text = true
	_line(Vector2(28, 234), Vector2(424, 1))
	_help = _label("", DIM, Vector2(30, 239), 240)
	_count = _label("", SOFT, Vector2(250, 239), 200, HORIZONTAL_ALIGNMENT_RIGHT)
	_ember = TextureRect.new()
	_ember.texture = load("res://assets/ui/icon_ember.png") if ResourceLoader.exists("res://assets/ui/icon_ember.png") else null
	_ember.position = Vector2(160, 57)
	_ember.visible = false
	add_child(_ember)


func _label(text: String, color: Color, pos: Vector2, width: float, align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.size = Vector2(width, 12)
	l.horizontal_alignment = align
	l.add_theme_color_override("font_color", color)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l


func _line(pos: Vector2, size_: Vector2) -> void:
	var r := ColorRect.new()
	r.color = Color(0.55, 0.47, 0.36, 0.55)
	r.position = pos
	r.size = size_
	add_child(r)


func open() -> void:
	visible = true
	Sound.sfx("journal_open")
	_help.text = "< > page    ^ v entry    %s back" % Settings.key_text("interact")
	_build()
	_refresh()


## Call every frame while open (the tree is paused). Returns false once closed.
func handle_input() -> bool:
	if Input.is_action_just_pressed("interact") or Input.is_action_just_pressed("pause") \
			or Input.is_action_just_pressed("journal"):
		visible = false
		Sound.sfx("ui_move")
		return false
	var page_step := 0
	if Util.menu("left"):
		page_step = -1
	elif Util.menu("right"):
		page_step = 1
	if page_step != 0:
		_page = (_page + page_step + PAGES.size()) % PAGES.size()
		_sel = 0
		_scroll = 0
		Sound.sfx("page")
		_build()
		_refresh()
		return true
	var step := 0
	if Util.menu("up"):
		step = -1
	elif Util.menu("down"):
		step = 1
	if step != 0 and not _entries.is_empty():
		_sel = clampi(_sel + step, 0, _entries.size() - 1)
		if _sel < _scroll:
			_scroll = _sel
		elif _sel >= _scroll + ROWS:
			_scroll = _sel - ROWS + 1
		Sound.sfx("ui_move")
		_refresh()
	return true


# --- content ------------------------------------------------------------------

func _build() -> void:
	_entries.clear()
	match PAGES[_page]:
		"Places":
			for p: Dictionary in JournalData.PLACES:
				var known: bool = Game.has_flag("visited_" + p["id"]) or Game.level_id == p["id"]
				var body: String = p["text"]
				if Game.has_flag("pell_follows"):
					body += "\n\nPell: \"%s\"" % p["pell"]
				_entries.append({"title": p["name"], "known": known, "sub": p["sub"], "body": body})
		"People":
			for p: Dictionary in JournalData.PEOPLE:
				var known := Game.check(p["met"])
				var body: String = p["text"]
				for more: Array in p.get("more", []):
					if Game.check(more[0]):
						body += "\n\n" + more[1]
				var sub := ""
				var gave := false
				if p.has("gave") and Game.has_flag(p["gave"]):
					sub = "    You shared an ember."
					gave = true
				_entries.append({"title": p["name"], "known": known, "sub": sub, "body": body, "ember": gave})
		"Tablets":
			for t: Array in JournalData.TABLETS:
				var id: String = t[0]
				var known := Game.has_flag("read:" + id)
				var lines: PackedStringArray = []
				for entry: Dictionary in Story.DIALOGUES.get(id, []):
					if entry.has("text"):
						lines.append(entry["text"])
				_entries.append({"title": t[1], "known": known, "sub": "", "body": "\n\n".join(lines)})
		"Names":
			for id: String in JournalData.NAMES:
				var info: Array = JournalData.NAMES[id]
				var known := Game.has_flag("name:" + id)
				var body := "Name-stone found in %s." % JournalData.place_name(info[2])
				if not known and Game.has_flag("orrin_looked"):
					# Orrin's telescope has spotted it, roughly
					known = true
					info = ["???", "Orrin's telescope: somewhere in %s." % JournalData.place_name(info[2]), info[2]]
					body = "Not found yet. Orrin pointed his telescope at the ground for you."
				_entries.append({"title": info[0], "known": known, "sub": info[1], "body": body,
					"found": Game.has_flag("name:" + id)})
		"Echoes":
			for e: Dictionary in JournalData.ECHOES:
				var seen := Game.has_flag("echo_" + e["id"])
				var held := Game.has_flag("keepsake:" + e["keepsake"])
				var keepsake: Dictionary = JournalData.KEEPSAKES[e["keepsake"]]
				var body: String = e["text"] if seen else ("Lay %s in the Little Hearth to remember." % keepsake["name"] if held else e["hint"])
				var sub: String = e["sub"] if seen else "Keepsake: %s%s" % [keepsake["name"], "" if held else " (not found)"]
				_entries.append({"title": e["name"], "known": seen or held or Game.check(e["hint_if"]),
					"sub": sub, "body": body})


func _refresh() -> void:
	for i in _page_labels.size():
		var on := i == _page
		_page_labels[i].text = ("[%s]" if on else "%s") % PAGES[i]
		_page_labels[i].add_theme_color_override("font_color", GOLD if on else DIM)
	var known := 0
	for e: Dictionary in _entries:
		if e["known"]:
			known += 1
	for i in ROWS:
		var idx := _scroll + i
		var l := _rows[i]
		if idx >= _entries.size():
			l.text = ""
			continue
		var e: Dictionary = _entries[idx]
		var title: String = e["title"] if e["known"] else "???"
		l.text = ("> " if idx == _sel else "  ") + title
		var color := OFF
		if idx == _sel:
			color = GOLD
		elif e["known"]:
			color = DIM
		l.add_theme_color_override("font_color", color)
	_ember.visible = false
	if _entries.is_empty():
		_title.text = ""
		_sub.text = ""
		_body.text = ""
	else:
		var e: Dictionary = _entries[_sel]
		if e["known"]:
			_title.text = e["title"]
			_sub.text = e["sub"]
			_body.text = e["body"]
			if e.get("ember", false) and _ember.texture:
				_ember.visible = true
				_ember.position = Vector2(160, 70)
		else:
			_title.text = "???"
			_sub.text = ""
			_body.text = _unknown_text()
	match PAGES[_page]:
		"Names":
			_count.text = "Names remembered: %d / %d" % [Game.name_count(), _entries.size()]
		"Echoes":
			var seen := 0
			for e: Dictionary in JournalData.ECHOES:
				if Game.has_flag("echo_" + e["id"]):
					seen += 1
			_count.text = "Memories seen: %d / %d" % [seen, JournalData.ECHOES.size()]
		"People":
			_count.text = "Embers shared: %d" % Game.embers_given
		_:
			_count.text = "%d / %d" % [known, _entries.size()]


func _unknown_text() -> String:
	match PAGES[_page]:
		"Places":
			return "Somewhere you have not been yet."
		"People":
			return "Someone you have not met yet."
		"Tablets":
			return "A tablet you have not read yet."
		"Echoes":
			return "A memory you have not found yet. Some things people leave behind still remember."
		_:
			return "A name not yet found. The flood scattered the name-stones all through the mountain."
