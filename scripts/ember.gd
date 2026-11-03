extends Area2D
## A drifting ember mote. Touch it to feed your lantern.
## `loose` embers were knocked out of your lantern by a shade: they float
## away and fade unless you catch them quickly.

const LOOSE_LIFE := 3.2

## Persistence key ("level:x:y"); collected embers stay collected.
var key := ""
var loose := false
var drift := Vector2.ZERO

var _sprite: AnimatedSprite2D
var _light: PointLight2D
var _t := 0.0
var _taken := false
var _life := LOOSE_LIFE


func _ready() -> void:
	_t = randf() * TAU
	collision_layer = 0
	collision_mask = 2
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 7.0 if not loose else 9.0
	shape.shape = circle
	shape.position = Vector2(0, -8)
	add_child(shape)
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({"pulse": ["res://assets/sprites/ember.png", 11, 7, true]})
	_sprite.material = Util.unlit_material()
	_sprite.play("pulse")
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_small.png")
	_light.color = Color(1.0, 0.6, 0.25)
	_light.energy = 0.9
	add_child(_light)
	body_entered.connect(_on_body_entered)
	if loose:
		# can't be re-caught in the first instant, or it would bounce straight back
		monitoring = false
		get_tree().create_timer(0.35).timeout.connect(func() -> void: monitoring = true)


func _process(delta: float) -> void:
	_t += delta
	var bob := Vector2(0, -8 + roundf(sin(_t * 2.2) * 2.0))
	_sprite.position = bob
	_light.position = bob
	if loose and not _taken:
		position += drift * delta
		drift *= 1.0 - 0.6 * delta
		_life -= delta
		_sprite.visible = _life > 1.0 or fmod(_life, 0.2) > 0.08
		if _life <= 0.0:
			_taken = true
			var tw := create_tween()
			tw.tween_property(_light, "energy", 0.0, 0.3)
			tw.tween_callback(queue_free)


func _on_body_entered(body: Node) -> void:
	if _taken or not body is Player:
		return
	_taken = true
	Game.add_ember()
	Sound.sfx("ember")
	if key != "":
		Game.set_flag("taken:" + key)
	Util.burst(get_parent(), global_position + Vector2(0, -8), [Color(1, 0.95, 0.7), Color(1, 0.45, 0.15)], 16, 50.0, 180.0, -15.0, 0.7)
	var tw := create_tween()
	tw.tween_property(_sprite, "scale", Vector2(1.6, 1.6), 0.12)
	tw.parallel().tween_property(_light, "energy", 2.0, 0.12)
	tw.tween_property(_sprite, "scale", Vector2.ZERO, 0.18)
	tw.parallel().tween_property(_light, "energy", 0.0, 0.25)
	tw.tween_callback(queue_free)
	if not loose and not Game.has_flag("seen_first_ember"):
		Game.set_flag("seen_first_ember")
		Dialogue.run("first_ember")
