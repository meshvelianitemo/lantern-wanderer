class_name Credits
extends Control
## The credits. open(true) rolls them by itself after an ending (any button skips);
## open(false) is the title-screen version: it scrolls slowly, up/down scroll faster,
## and the licenses of Godot and its parts follow (the engine's MIT license asks for this).
## Emits `closed` when done.

signal closed

## Fill these in before release. A section with no names is left out.
const MADE_BY := "Temo Meshveliani"
const PLAYTESTERS: Array[String] = []
const THANKS: Array[String] = []

const GOLD := Color(1.0, 0.91, 0.64)
const TEXT := Color(0.93, 0.9, 0.85)
const SOFT := Color(0.74, 0.8, 0.86)
const DIM := Color(0.6, 0.62, 0.7)
const WIDTH := 400.0
## Pixels per second while rolling, and while holding up/down.
const SPEED := 20.0
const FAST := 160.0
## Letters the pixel font lacks, spelled with ones it has.
const PLAIN := {
	"©": "(c)", "é": "e", "è": "e", "ë": "e", "á": "a", "à": "a", "ä": "a", "å": "a", "ã": "a",
	"í": "i", "ï": "i", "ó": "o", "ö": "o", "ø": "o", "ő": "o", "ú": "u", "ü": "u", "ű": "u",
	"ñ": "n", "ç": "c", "č": "c", "ć": "c", "ł": "l", "ś": "s", "š": "s", "ž": "z", "ß": "ss",
	"Á": "A", "É": "E", "Ö": "O", "Ø": "O", "Ü": "U", "Š": "S", "Ž": "Z", "Ł": "L",
	"—": "-", "–": "-", "’": "'", "‘": "'", "“": "\"", "”": "\"", "…": "...", "\t": "    ",
}

var _view: Control
var _content: VBoxContainer
var _help: Label
var _roll := false
## Where the content stops: the last line of the credits sits mid-screen (roll),
## or the end of the licenses reaches the bottom (menu).
var _end_y := 0.0
var _wait := 0.0
var _holding := false
var _age := 0.0


func _ready() -> void:
	# the game is always 480x270, so the screen is sized outright
	size = Vector2(480, 270)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	var back := ColorRect.new()
	back.color = Color(0.03, 0.02, 0.06, 1.0)
	back.size = size
	add_child(back)
	_view = Control.new()
	_view.position = Vector2((480 - WIDTH) / 2.0, 0)
	_view.size = Vector2(WIDTH, 254)
	_view.clip_contents = true
	add_child(_view)
	_help = Label.new()
	_help.position = Vector2(0, 256)
	_help.size = Vector2(480, 12)
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_help.add_theme_color_override("font_color", Color(0.4, 0.42, 0.5))
	add_child(_help)


func open(roll: bool) -> void:
	_roll = roll
	_age = 0.0
	visible = true
	if _content:
		_content.queue_free()
	_content = VBoxContainer.new()
	_content.add_theme_constant_override("separation", 3)
	_content.size = Vector2(WIDTH, 0)
	_view.add_child(_content)
	_line("LANTERN WANDERER", GOLD, 2)
	_gap(24)
	_section("A game by", [MADE_BY])
	_section("Playtesters", PLAYTESTERS)
	_section("Special thanks", THANKS)
	_section("Made with", ["Godot Engine", "godotengine.org"])
	_gap(30)
	var last := _line("Thank you for playing.", GOLD)
	if not roll:
		_gap(60)
		_line("Licenses", DIM)
		_gap(8)
		for paragraph in _licenses().split("\n\n", false):
			_block(paragraph)
	_help.text = "" if roll else "^ v scroll    %s back" % Settings.key_text("interact")
	_content.position.y = 270.0 if roll else 40.0
	_wait = 1.0 if roll else 1.5
	_holding = false
	# sizes settle once the labels have been laid out
	await get_tree().process_frame
	await get_tree().process_frame
	_content.size.y = 0
	_content.reset_size()
	_end_y = (127.0 - last.position.y) if roll else minf(40.0, 250.0 - _content.size.y)


func _process(delta: float) -> void:
	if not visible or _content == null:
		return
	_age += delta
	# the press that opened the credits must not close them again
	if _age > 0.3 and (Util.menu("accept") or Util.menu("back")):
		_close()
		return
	var speed := SPEED
	if not _roll:
		if Input.is_action_pressed("move_down") or Input.is_action_pressed("ui_down"):
			speed = FAST
			_wait = 0.0
		elif Input.is_action_pressed("move_up") or Input.is_action_pressed("ui_up"):
			speed = -FAST
			_wait = 0.0
	if _wait > 0.0:
		_wait -= delta
		return
	if _holding:
		_close()
		return
	_content.position.y = clampf(_content.position.y - speed * delta, _end_y, 270.0 if _roll else 40.0)
	if _roll and _content.position.y <= _end_y:
		# hold on the last line for a moment, then finish
		_wait = 3.5
		_holding = true


func _close() -> void:
	if not visible:
		return
	visible = false
	Sound.sfx("ui_move")
	closed.emit()


func _section(head: String, names: Array) -> void:
	if names.is_empty():
		return
	_line(head, DIM)
	for n: String in names:
		_line(n, TEXT)
	_gap(18)


func _line(text: String, color: Color, scale_factor := 1) -> Control:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_color_override("font_color", color)
	if scale_factor == 1:
		l.custom_minimum_size = Vector2(WIDTH, 12)
		_content.add_child(l)
		return l
	# Labels don't scale inside containers, so a big line sits in its own holder
	var holder := Control.new()
	holder.custom_minimum_size = Vector2(WIDTH, 12 * scale_factor)
	l.size = Vector2(WIDTH / scale_factor, 12)
	l.scale = Vector2(scale_factor, scale_factor)
	holder.add_child(l)
	_content.add_child(holder)
	return holder


func _block(text: String) -> void:
	var l := Label.new()
	l.text = text
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(WIDTH, 0)
	l.add_theme_color_override("font_color", SOFT)
	_content.add_child(l)


func _gap(h: float) -> void:
	var c := Control.new()
	c.custom_minimum_size = Vector2(0, h)
	_content.add_child(c)


## Godot's license, then every third-party part of the engine with its copyright
## and license, then the full text of each of those licenses.
static func _licenses() -> String:
	var out := "This game uses Godot Engine, available under the following license:\n\n"
	out += Engine.get_license_text() + "\n\n"
	out += "Portions of this software are copyright (c) The FreeType Project (www.freetype.org). All rights reserved.\n\n"
	out += "Godot Engine includes these third-party parts:\n\n"
	for info: Dictionary in Engine.get_copyright_info():
		var lines: PackedStringArray = [info["name"]]
		for part: Dictionary in info["parts"]:
			for c: String in part["copyright"]:
				lines.append("(c) " + c)
			lines.append("License: " + part["license"])
		out += "\n".join(lines) + "\n\n"
	var texts := Engine.get_license_info()
	for license: String in texts:
		out += "License: " + license + "\n\n" + texts[license] + "\n\n"
	return _plain(out)


static func _plain(text: String) -> String:
	for c: String in PLAIN:
		text = text.replace(c, PLAIN[c])
	return RegEx.create_from_string("[^\\x0A\\x20-\\x7E]").sub(text, "?", true)
