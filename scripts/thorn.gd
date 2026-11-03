extends StaticBody2D
## Thorn-root: a knot of black roots that blocks the way until a Flare burns
## it to ash. Burnt thorns stay burnt.

## Persistence key ("level:x:y").
var key := ""

var _sprite: Sprite2D
var _shape: CollisionShape2D
var _burning := false


func _ready() -> void:
	if Game.has_flag("burnt:" + key):
		queue_free()
		return
	add_to_group("thorn")
	collision_layer = 1
	collision_mask = 0
	_shape = CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(16, 16)
	_shape.shape = rect
	_shape.position = Vector2(8, 8)
	add_child(_shape)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://assets/sprites/thorn.png")
	_sprite.hframes = maxi(1, _sprite.texture.get_width() / 16)
	_sprite.centered = false
	_sprite.z_index = 1
	add_child(_sprite)


func burn() -> void:
	if _burning:
		return
	_burning = true
	remove_from_group("thorn")
	Game.set_flag("burnt:" + key)
	Sound.sfx("thorn_burn", -4.0)
	var l := PointLight2D.new()
	l.texture = preload("res://assets/fx/light_small.png")
	l.color = Color(1.0, 0.5, 0.2)
	l.energy = 0.9
	l.position = Vector2(8, 8)
	add_child(l)
	for f in range(1, _sprite.hframes):
		_sprite.frame = f
		await get_tree().create_timer(0.14 + randf() * 0.06).timeout
	_shape.set_deferred("disabled", true)
	Util.burst(get_parent(), global_position + Vector2(8, 8), [Color(1, 0.6, 0.25), Color(0.25, 0.2, 0.25)], 10, 30.0, 180.0, 30.0, 0.6)
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.35)
	tw.tween_callback(queue_free)
