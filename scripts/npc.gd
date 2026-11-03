class_name NPC
extends Interactable
## A character defined in Story.NPCS: sprite, animations, light, voice, and
## which dialogue to play (the first `talks` entry whose condition holds).
## Characters with a `lit_if` condition switch to their *_lit animations and a
## brighter light once it holds - usually after you share an ember with them.
## With a `radius` they then count as a light (glimmer, eye-gates, shades): Lark's Echo.
## `grow` swaps the sprite sheet by condition: [[cond, sheet, frame width], ...] (Sprig).
## A little speech bubble floats over them while they have something new to say (Story.is_news).

@export var npc_id := ""

var data: Dictionary
var sprite: AnimatedSprite2D
var light: PointLight2D
var lit := false
var talking := false
var _news: NewsBubble
var _has_news := false


## The "something new to say" bubble: cream, with three warm dots.
class NewsBubble extends Node2D:
	const PIXELS := [
		" ########## ",
		"#cccccccccc#",
		"#c..c..c..c#",
		"#c..c..c..c#",
		"#cccccccccc#",
		" #c######## ",
		" ##         ",
	]
	const COLORS := {"#": Color(0.07, 0.05, 0.09), "c": Color(1.0, 0.94, 0.8), ".": Color(0.9, 0.45, 0.18)}

	func _draw() -> void:
		for y in PIXELS.size():
			var row: String = PIXELS[y]
			for x in row.length():
				if COLORS.has(row[x]):
					draw_rect(Rect2(x - 6, y - 4, 1, 1), COLORS[row[x]])


func _ready() -> void:
	data = Story.NPCS[npc_id]
	add_to_group("npc")
	add_to_group("npc_" + npc_id)
	zone_size = data.get("zone", Vector2(40, 34))
	prompt_height = data.get("prompt", 40.0)
	super()
	sprite = AnimatedSprite2D.new()
	var sheet: String = data["sprite"]
	var frame_w: int = data["frame"]
	for stage: Array in data.get("grow", []):
		if Game.check(stage[0]) and ResourceLoader.exists(stage[1]):
			sheet = stage[1]
			frame_w = stage[2]
			break
	var tex: Texture2D = load(sheet)
	var anims := {}
	for anim: String in data["anims"]:
		var a: Array = data["anims"][anim]
		anims[anim] = [sheet, frame_w, a[1], true, a[0]]
	sprite.sprite_frames = Util.make_frames(anims)
	sprite.offset = Vector2(0, data.get("y", -tex.get_height() / 2.0))
	sprite.scale = Vector2.ONE * float(data.get("scale", 1.0))  # young Burrow is smaller
	sprite.z_index = data.get("z", 0)
	if data.get("unlit", false):
		sprite.material = Util.unlit_material()
	add_child(sprite)
	if data.has("light"):
		var l: Dictionary = data["light"]
		light = PointLight2D.new()
		light.texture = preload("res://assets/fx/light_small.png")
		light.color = l.get("color", Color(1.0, 0.7, 0.4))
		light.texture_scale = l.get("scale", 0.6)
		light.position = l.get("pos", Vector2(0, -16))
		add_child(light)
	lit = data.has("lit_if") and Game.check(data["lit_if"])
	if data.has("radius"):
		add_to_group("light_source")
		light.texture = preload("res://assets/fx/light_lantern.png")
	_apply_look(false)
	_news = NewsBubble.new()
	_news.material = Util.unlit_material()
	_news.z_index = 20
	_news.visible = false
	add_child(_news)
	_update_news()
	Dialogue.typing_changed.connect(_on_typing_changed)
	Game.ember_given.connect(_on_ember_given)
	Game.flag_set.connect(_on_flag_set)
	if data.has("auto_if"):
		player_entered.connect(_auto_talk)


func _process(delta: float) -> void:
	super(delta)
	var frozen: bool = Game.player != null and Game.player.frozen
	_news.visible = _has_news and not _prompt.visible and not talking and not Game.in_dialogue and not frozen
	_news.position = Vector2(0, -prompt_height + roundf(sin(_t * 3.0)))


func _update_news() -> void:
	_has_news = Story.is_news(Story.pick(npc_id))


func _on_flag_set(_flag: String) -> void:
	_update_news()


## Some meetings are not optional.
func _auto_talk() -> void:
	if not talking and not Game.in_dialogue and Game.check(data["auto_if"]):
		interact()


func _anim(base: String) -> String:
	var frames := sprite.sprite_frames
	if lit and frames.has_animation(base + "_lit"):
		return base + "_lit"
	return base if frames.has_animation(base) else "idle"


func _apply_look(animate: bool) -> void:
	sprite.play(_anim("idle"))
	if light:
		var l: Dictionary = data["light"]
		var e: float = l.get("lit", 0.8) if lit else l.get("dim", 0.0)
		var s: float = l.get("scale", 0.6)
		if data.has("radius"):
			# a light of their own now: as wide as it reaches
			s = (data["radius"] / Player.LIGHT_RADIUS) if lit else 0.3
		if animate:
			var tw := create_tween()
			tw.tween_property(light, "energy", e, 1.2)
			tw.parallel().tween_property(light, "texture_scale", s, 2.0).set_trans(Tween.TRANS_SINE)
		else:
			light.energy = e
			light.texture_scale = s


## Looks again at `lit_if` (after a story flag changed it without an ember changing hands).
func refresh() -> void:
	var now := data.has("lit_if") and Game.check(data["lit_if"])
	if now != lit:
		lit = now
		_apply_look(true)


## As a light (only with a `radius`): where it shines from and how far, once lit.
func light_info() -> Array:
	var offset: Vector2 = data.get("light", {}).get("pos", Vector2(0, -16))
	var from := global_position + offset
	return [from, float(data.get("radius", 0.0)) if lit else 0.0]


func can_interact() -> bool:
	return Story.pick(npc_id) != ""


func interact() -> void:
	var id := Story.pick(npc_id)
	if id == "":
		return
	talking = true
	_face_player()
	await Dialogue.run(id, data.get("voice", npc_id))
	talking = false
	sprite.play(_anim("idle"))
	if not Game.check(data.get("where", {}).get(Game.level_id, "")):
		_leave()


func _face_player() -> void:
	if not data.get("face", true) or Game.player == null:
		return
	sprite.flip_h = Game.player.global_position.x < global_position.x


func _on_typing_changed(who: String, typing: bool) -> void:
	if not talking or who == "":
		return
	if who != data.get("name", "") and who != "???":
		return
	sprite.play(_anim("talk" if typing else "idle"))


func _on_ember_given(id: String) -> void:
	if id != npc_id or Game.player == null:
		return
	# the ember flies from your lantern to them in a little arc
	var to: Vector2 = global_position + data.get("light", {}).get("pos", Vector2(0, -16))
	await Util.spark_arc(get_parent(), Game.player.lantern.global_position, to)
	lit = data.has("lit_if") and Game.check(data["lit_if"])
	_apply_look(true)


## Fades away (home to Old Hollow, usually) once they no longer belong here.
func _leave() -> void:
	set_process(false)
	_prompt_hide()
	_news.visible = false
	await get_tree().create_timer(0.8).timeout
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 2.0)
	tw.tween_callback(queue_free)
