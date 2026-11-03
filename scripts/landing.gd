extends Area2D
## A landing in an Echo: walk past it and it becomes where you are sent back to
## (by the rising flood or dark, a fall, a shade). A small lamp lights to show it.

var _lamp: PointLight2D
var _reached := false


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	monitorable = false
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24, 40)
	shape.shape = rect
	shape.position = Vector2(0, -20)
	add_child(shape)
	_lamp = PointLight2D.new()
	_lamp.texture = preload("res://assets/fx/light_small.png")
	_lamp.color = Color(1.0, 0.8, 0.5)
	_lamp.energy = 0.0
	_lamp.texture_scale = 0.5
	_lamp.position = Vector2(0, -20)
	add_child(_lamp)
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if not body is Player or (body as Player).frozen:
		return
	Game.checkpoint = global_position
	if _reached:
		return
	_reached = true
	Sound.sfx("lamp", -8.0)
	Util.burst(get_parent(), global_position + Vector2(0, -16), [Color(1, 0.92, 0.6), Color(0.95, 0.5, 0.2)], 8, 30.0, 180.0, 10.0, 0.5)
	create_tween().tween_property(_lamp, "energy", 0.6, 0.5)
