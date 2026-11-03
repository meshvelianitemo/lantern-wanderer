extends StaticBody2D
## A Keeper eye-gate: a stone door three tiles tall with a carved eye.
## On its own, it opens once light has rested on its eye for a moment.
## With eye-stones (eye.gd, same id) it is open only while one of them is lit,
## until you have walked through - then it remembers, and stays open for good.

const DRINK_TIME := 1.2

## Gate id within the level (shared with its eye-stones).
var gate_id := ""
## Persistence key ("level:id").
var key := ""

var _drink := 0.0
var _open := false
var _raised := false
var _side := 0.0
var _sprite: Sprite2D
var _shape: CollisionShape2D
var _eye: PointLight2D
var _linked := false


func _ready() -> void:
	if Game.has_flag("open:" + key):
		queue_free()
		return
	collision_layer = 1
	collision_mask = 0
	_shape = CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(16, 48)
	_shape.shape = rect
	_shape.position = Vector2(8, 24)
	add_child(_shape)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://assets/sprites/eye_gate.png")
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.z_index = -1
	add_child(_sprite)
	_eye = PointLight2D.new()
	_eye.texture = preload("res://assets/fx/light_small.png")
	_eye.color = Color(1.0, 0.85, 0.45)
	_eye.energy = 0.0
	_eye.texture_scale = 0.5
	_eye.position = Vector2(8, 9)
	add_child(_eye)
	_linked = not get_tree().get_nodes_in_group("eye_" + gate_id).is_empty()


func _physics_process(delta: float) -> void:
	if _open:
		return
	var p: Player = Game.player
	if _linked:
		var any := false
		for e in get_tree().get_nodes_in_group("eye_" + gate_id):
			if e.lit:
				any = true
		_sprite.frame = 1 if any else 0
		_eye.energy = 0.8 if any else 0.0
		_set_raised(any)
		# once you have walked through, it remembers
		if p and _raised:
			var side := signf(p.global_position.x - (global_position.x + 8.0))
			if _side == 0.0:
				_side = side
			elif side != _side and absf(p.global_position.x - global_position.x - 8.0) > 14.0:
				_remember()
		elif p:
			_side = signf(p.global_position.x - (global_position.x + 8.0))
		return
	var l := Game.light_at(global_position + Vector2(8, 9))
	if l > 0.0:
		_drink += delta
	else:
		_drink = maxf(0.0, _drink - delta * 0.5)
	_sprite.frame = 1 if l > 0.0 else 0
	_sprite.material = Util.unlit_material() if l > 0.0 else null
	_eye.energy = _drink / DRINK_TIME
	if _drink >= DRINK_TIME:
		_set_raised(true)
		_remember()


func _set_raised(up: bool) -> void:
	if up == _raised:
		return
	_raised = up
	Sound.sfx("gate_open", -2.0 if up else -6.0, 1.0 if up else 0.8)
	_shape.set_deferred("disabled", up)
	create_tween().tween_property(_sprite, "position:y", -46.0 if up else 0.0, 0.9 if up else 0.5).set_trans(Tween.TRANS_SINE)


func _remember() -> void:
	_open = true
	Game.set_flag("open:" + key)
	var tw := create_tween()
	tw.tween_interval(0.6)
	tw.tween_property(_sprite, "modulate:a", 0.0, 1.0)
	tw.tween_callback(queue_free)
