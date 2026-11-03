extends Interactable
## A Keeper star-lamp (the Starwell). Touch your flame to it - even the spark
## you keep while your flame hangs on a hook will do - and it burns for good.
## It is a still light, so shadow-play plates throw solid shadows from it.

const RADIUS := 84.0
const FLAME := Vector2(0, -24)

## Persistence key ("level:x:y"); a lit lamp stays lit.
var key := ""
var lit := false

var _sprite: Sprite2D
var _light: PointLight2D
var _glow: PointLight2D


func _ready() -> void:
	zone_size = Vector2(26, 36)
	prompt_height = 42.0
	super()
	add_to_group("light_source")
	add_to_group("still_light")
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://assets/sprites/starlamp.png")
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -16)
	_sprite.z_index = -1
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(0.95, 0.9, 0.76)
	_light.texture_scale = RADIUS / 96.0 * 1.25
	_light.position = FLAME
	add_child(_light)
	_glow = PointLight2D.new()
	_glow.texture = preload("res://assets/fx/light_small.png")
	_glow.color = Color(1.0, 0.85, 0.55)
	_glow.texture_scale = 0.4
	_glow.position = FLAME
	add_child(_glow)
	lit = Game.has_flag("lamp:" + key)
	_apply(false)


func can_interact() -> bool:
	return not lit


func interact() -> void:
	lit = true
	Game.set_flag("lamp:" + key)
	Sound.sfx("lamp_light")
	Util.burst(get_parent(), global_position + FLAME, [Color(1, 0.95, 0.75), Color(0.95, 0.6, 0.25)], 14, 40.0, 180.0, -10.0, 0.6)
	_apply(true)


func _apply(animate: bool) -> void:
	_sprite.frame = 1 if lit else 0
	_sprite.material = Util.unlit_material() if lit else null
	var e := 0.85 if lit else 0.0
	if animate:
		create_tween().tween_property(_light, "energy", e, 0.6)
	else:
		_light.energy = e


func _process(delta: float) -> void:
	super(delta)
	var t := Time.get_ticks_msec() * 0.001
	_glow.energy = (0.55 + 0.08 * sin(t * 9.0) + 0.05 * sin(t * 15.0)) if lit else 0.0


func light_info() -> Array:
	return [global_position + FLAME, RADIUS if lit else 0.0]
