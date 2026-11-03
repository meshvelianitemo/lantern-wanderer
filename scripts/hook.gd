extends Interactable
## A Keeper lantern-hook. With the Hook gift you can leave your flame burning
## here while you walk on into the dark - glimmer, eye-gates and shades all
## answer to it just as they would to your lantern. Come back to take it.

const LAMP := Vector2(5, -28)

var hung := false
var _sprite: Sprite2D
var _light: PointLight2D


func _ready() -> void:
	zone_size = Vector2(30, 40)
	prompt_height = 48.0
	super()
	add_to_group("light_source")
	add_to_group("still_light")  # shadow-play plates throw solid shadows from it
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://assets/sprites/hook.png")
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -20)
	_sprite.z_index = -1
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1, 0.78, 0.5)
	_light.energy = 0.0
	_light.position = LAMP
	add_child(_light)


func can_interact() -> bool:
	var p: Player = Game.player
	if p == null:
		return false
	if not Game.has_gift("hook"):
		return not Game.in_dialogue
	return hung or p.hung_on == null


func interact() -> void:
	if not Game.has_gift("hook"):
		await Dialogue.run("hook_no_gift")
		return
	if hung:
		take_back()
	else:
		_hang()


func _hang() -> void:
	var p: Player = Game.player
	hung = true
	p.hung_on = self
	_sprite.frame = 1
	_light.texture_scale = p.flame_radius() / 96.0 * 1.25
	create_tween().tween_property(_light, "energy", 0.8, 0.3)
	Sound.sfx("hook")
	Util.burst(get_parent(), global_position + LAMP, [Color(1, 0.92, 0.6), Color(0.95, 0.4, 0.15)], 10, 40.0, 180.0, -10.0, 0.5)


func take_back() -> void:
	var p: Player = Game.player
	hung = false
	if p and p.hung_on == self:
		p.hung_on = null
	_sprite.frame = 0
	create_tween().tween_property(_light, "energy", 0.0, 0.25)
	Sound.sfx("hook", -4.0, 1.2)


func light_info() -> Array:
	var p: Player = Game.player
	if not hung or p == null:
		return [global_position, 0.0]
	return [global_position + LAMP, p.flame_radius()]
