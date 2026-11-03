extends Area2D
## A run of cold black water. Falling in sends you back to your last light.

var tiles := 1
## True for the top row of a pool (animated ripples, and the part that's deadly).
var surface := true
## Shallow water you can wade in is not.
var deadly := true

var _sprites: Array[Sprite2D] = []
var _t := 0.0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	monitorable = false
	var tex: Texture2D = load("res://assets/sprites/water.png" if surface else "res://assets/sprites/water_body.png")
	for i in tiles:
		var s := Sprite2D.new()
		s.texture = tex
		s.hframes = maxi(1, tex.get_width() / 16)
		s.centered = false
		s.position = Vector2(i * 16, 0)
		s.z_index = 5
		add_child(s)
		_sprites.append(s)
	if surface and deadly:
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = Vector2(tiles * 16, 10)
		shape.shape = rect
		shape.position = Vector2(tiles * 8, 11)
		add_child(shape)
		body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	if not surface:
		return
	_t += delta
	for i in _sprites.size():
		var s := _sprites[i]
		s.frame = int(_t * 4.0 + i) % s.hframes


func _on_body_entered(body: Node) -> void:
	if body is Player:
		(body as Player).drown()
