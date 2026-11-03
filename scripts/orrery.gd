extends Interactable
## An orrery sun on a brass rail (the Starwell). Light it and the old
## clockwork wakes: the sun rides its rail back and forth for good. It is a
## still light that moves, so every shadow it throws sweeps across the dome
## the other way - shadows you can ride.

const RADIUS := 92.0
const TICK := 0.7
const RAIL_COLOR := Color(0.42, 0.33, 0.2)

## Persistence key ("level:x:y"); a lit sun keeps turning.
var key := ""
## The far end of the rail, relative to where the sun starts (pixels).
var travel := Vector2(64, 0)
## Pixels per second.
var speed := 24.0
## Seconds the sun rests at each end of its rail.
var pause := 1.1
var lit := false

var _sun: Sprite2D
var _light: PointLight2D
var _u := 0.0
var _dir := 1.0
var _wait := 0.0
var _tick := 0.0
var _clock := 0.0


func _ready() -> void:
	# tall enough to reach from the ledge when the rail starts down in a pit
	zone_size = Vector2(44, 60)
	prompt_height = 40.0
	super()
	add_to_group("light_source")
	add_to_group("still_light")
	var rail := Line2D.new()
	rail.points = PackedVector2Array([Vector2(0, -8), Vector2(0, -8) + travel])
	rail.width = 1.0
	rail.default_color = RAIL_COLOR
	rail.z_index = -4
	add_child(rail)
	for end: Vector2 in [Vector2(0, -8), Vector2(0, -8) + travel]:
		var cap := ColorRect.new()
		cap.color = RAIL_COLOR
		cap.size = Vector2(3, 3)
		cap.position = end - Vector2(1.5, 1.5)
		cap.z_index = -4
		add_child(cap)
	_sun = Sprite2D.new()
	_sun.texture = load("res://assets/sprites/orrery_sun.png")
	_sun.hframes = 4
	_sun.position = Vector2(0, -8)
	_sun.z_index = -2
	add_child(_sun)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1.0, 0.82, 0.5)
	_light.texture_scale = RADIUS / 96.0 * 1.25
	_sun.add_child(_light)
	lit = Game.has_flag("orrery:" + key)
	_apply(false)


func can_interact() -> bool:
	return not lit


func interact() -> void:
	lit = true
	Game.set_flag("orrery:" + key)
	Sound.sfx("lamp_light")
	Sound.sfx_at("orrery_start", _sun.global_position)
	Util.burst(get_parent(), _sun.global_position, [Color(1, 0.95, 0.7), Color(0.95, 0.55, 0.2)], 16, 45.0, 180.0, -10.0, 0.6)
	_wait = 1.2
	_apply(true)


func _apply(animate: bool) -> void:
	_sun.frame = 1 if lit else 0
	_sun.material = Util.unlit_material() if lit else null
	var e := 0.9 if lit else 0.0
	if animate:
		create_tween().tween_property(_light, "energy", e, 0.5)
	else:
		_light.energy = e


func _physics_process(delta: float) -> void:
	if not lit:
		return
	_clock += delta
	_sun.frame = 1 + int(_clock * 6.0) % 3
	if _wait > 0.0:
		_wait -= delta
		return
	var length := travel.length()
	if length < 1.0:
		return
	_u += _dir * speed * delta / length
	if _u >= 1.0 or _u <= 0.0:
		_u = clampf(_u, 0.0, 1.0)
		_dir = -_dir
		_wait = pause
	_sun.position = Vector2(0, -8) + travel * _u
	_tick -= delta
	if _tick <= 0.0:
		_tick = TICK
		Sound.sfx_at("orrery_tick", _sun.global_position, -8.0)


func light_info() -> Array:
	return [_sun.global_position, RADIUS if lit else 0.0]
