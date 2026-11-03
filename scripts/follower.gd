class_name Follower
extends Node2D
## Someone who walks behind the player along their trail, in a line (Game.followers).
## Used by the sleeping Keepers in Maud's Echo (asleep until her bell wakes them)
## and by Edda in Vesper's. Sprite sheet frames: 0-1 asleep, 2-3 idle, 4-7 walk
## (Edda's sheet: 0-1 idle, 2-3 talk, 4-7 walk; she is never asleep).

signal joined

## Trail points between one follower and the next.
const SPACING := 18
const WAKE_TIME := 0.9

## Story.NPCS id (sprite sheet, name, voice).
var npc_id := ""
## Starts asleep, waiting for a bell.
var asleep := false
var following := false

var _sprite: AnimatedSprite2D
var _data: Dictionary
var _z: Label
var _t := 0.0


func _ready() -> void:
	_data = Story.NPCS.get(npc_id, {})
	add_to_group("follower")
	_sprite = AnimatedSprite2D.new()
	var path: String = _data.get("sprite", "")
	if path != "" and ResourceLoader.exists(path):
		var tex: Texture2D = load(path)
		var anims := {}
		for anim: String in _data["anims"]:
			var a: Array = _data["anims"][anim]
			anims[anim] = [path, _data["frame"], a[1], true, a[0]]
		_sprite.sprite_frames = Util.make_frames(anims)
		_sprite.offset = Vector2(0, -tex.get_height() / 2.0)
	else:
		# art not drawn yet: a ghostly Keeper stands in
		_sprite.sprite_frames = Util.make_frames({"idle": ["res://assets/sprites/keeper_ghost.png", 14, 2, true]})
		_sprite.offset = Vector2(0, -11)
	_sprite.material = Util.unlit_material()
	add_child(_sprite)
	var light := PointLight2D.new()
	light.texture = preload("res://assets/fx/light_small.png")
	light.color = Color(1.0, 0.82, 0.55)
	light.energy = 0.35
	light.texture_scale = 0.35
	light.position = Vector2(0, -10)
	add_child(light)
	_play("asleep" if asleep else "idle")
	if asleep:
		_z = Label.new()
		_z.text = "z"
		_z.add_theme_color_override("font_color", Color(0.75, 0.8, 0.95))
		_z.position = Vector2(4, -30)
		_z.material = Util.unlit_material()
		add_child(_z)
		Game.bell_rung.connect(_on_bell)


func _play(anim: String) -> void:
	if _sprite.sprite_frames.has_animation(anim):
		if _sprite.animation != anim:
			_sprite.play(anim)
	elif _sprite.animation != "idle" and _sprite.sprite_frames.has_animation("idle"):
		_sprite.play("idle")


func _on_bell(pos: Vector2, radius: float) -> void:
	if not asleep or global_position.distance_to(pos) > radius:
		return
	asleep = false
	Game.bell_rung.disconnect(_on_bell)
	if _z:
		_z.queue_free()
	await get_tree().create_timer(0.35).timeout
	Sound.sfx_at("keeper_wake", global_position)
	_play("idle")
	Util.bark(self, _data.get("wake", "Mm? Supper?"), 22.0, 1.8)
	await get_tree().create_timer(WAKE_TIME).timeout
	follow()


## Joins the end of the line behind the player.
func follow() -> void:
	if following:
		return
	following = true
	Game.followers.append(self)
	joined.emit()


## Leaves the line and stays where they are.
func stay() -> void:
	following = false
	Game.followers.erase(self)


func _process(delta: float) -> void:
	_t += delta
	if _z:
		_z.position.y = -30 + roundf(sin(_t * 2.0) * 2.0)
	var p: Player = Game.player
	if not following or p == null:
		return
	var place := Game.followers.find(self) + 1
	var trail := p.trail
	var i := maxi(trail.size() - 1 - place * SPACING, 0)
	var target := trail[i]
	if trail.size() - 1 < place * SPACING:
		# not enough trail yet: queue up just behind the player
		target = p.global_position + Vector2(-p.facing * 12.0 * place, 0)
	var step := target - global_position
	if step.length() > 160.0:
		global_position = target  # left far behind (a respawn): catch up at once
	else:
		global_position = global_position.lerp(target, 1.0 - exp(-14.0 * delta))
	if absf(step.x) > 0.3:
		_sprite.flip_h = step.x < 0.0
	_play("walk" if step.length() > 0.6 else "idle")
