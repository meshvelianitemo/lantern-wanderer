extends Interactable
## A Wickway: an old Keeper lantern-lift between a depth of the mountain and
## Old Hollow. Its lantern can only be lit from below; once lit, ride it
## either way.

var target_level := ""
var target_door := ""
## The level at the bottom of this lift (flag: "wickway_<depth>").
var depth := ""

var _sprite: AnimatedSprite2D
var _light: PointLight2D
var _listening := false


func _ready() -> void:
	zone_size = Vector2(34, 40)
	prompt_height = 56.0
	super()
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"cold": ["res://assets/sprites/wickway.png", 24, 1, false, [0]],
		"burn": ["res://assets/sprites/wickway.png", 24, 6, true, [1, 2, 3]],
	})
	_sprite.offset = Vector2(0, -24)
	_sprite.z_index = -2
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1.0, 0.7, 0.4)
	_light.texture_scale = 0.6
	_light.position = Vector2(0, -36)
	add_child(_light)
	_show(_is_lit(), false)
	Dialogue.event.connect(_on_event)


func _is_lit() -> bool:
	return Game.has_flag("wickway_" + depth)


func _show(on: bool, animate: bool) -> void:
	_sprite.play("burn" if on else "cold")
	var e := 0.85 if on else 0.0
	if animate:
		create_tween().tween_property(_light, "energy", e, 0.8)
	else:
		_light.energy = e


func interact() -> void:
	_listening = true
	if not _is_lit():
		await Dialogue.run("wickway_light" if Game.level_id == depth else "wickway_cold")
	else:
		await Dialogue.run("wickway_ride_up" if Game.level_id == depth else "wickway_ride_down")
	_listening = false


func _on_event(ev: String) -> void:
	if not _listening:
		return
	if ev == "light_wickway":
		Game.set_flag("wickway_" + depth)
		Sound.sfx("shrine")
		Util.burst(get_parent(), global_position + Vector2(0, -36), [Color(1, 0.92, 0.6), Color(0.95, 0.4, 0.15)], 18, 55.0, 180.0, -10.0, 0.8)
		_show(true, true)
		Game.checkpoint = global_position
	elif ev == "ride":
		_listening = false
		Game.go_to(target_level, target_door, "wickway")
