extends Area2D
## A keepsake: something a wick or a Keeper left behind that still holds a memory.
## Pick it up, then lay it in the Little Hearth to play that memory (an Echo).
## Sets the flag "keepsake:<id>". See JournalData.KEEPSAKES.

var keepsake_id := ""

var _sprite: Sprite2D
var _light: PointLight2D
var _t := 0.0
var _taken := false


func _ready() -> void:
	if Game.has_flag("keepsake:" + keepsake_id) or not JournalData.KEEPSAKES.has(keepsake_id):
		queue_free()
		return
	collision_layer = 0
	collision_mask = 2
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 9.0
	shape.shape = circle
	shape.position = Vector2(0, -8)
	add_child(shape)
	_sprite = Sprite2D.new()
	var path := "res://assets/sprites/keepsake.png"
	if ResourceLoader.exists(path):
		_sprite.texture = load(path)
		_sprite.hframes = 3
		_sprite.frame = JournalData.KEEPSAKES[keepsake_id]["frame"]
	else:
		_sprite.texture = load("res://assets/sprites/name_stone.png")
		_sprite.hframes = 4
	_sprite.material = Util.unlit_material()
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_small.png")
	_light.color = Color(1.0, 0.78, 0.55)
	_light.energy = 0.55
	_light.texture_scale = 0.45
	add_child(_light)
	body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	_t += delta
	var bob := Vector2(0, -9 + roundf(sin(_t * 1.4) * 1.0))
	_sprite.position = bob
	_light.position = bob
	_light.energy = 0.5 + 0.1 * sin(_t * 2.3)


func _on_body_entered(body: Node) -> void:
	if _taken or not body is Player:
		return
	_taken = true
	var info: Dictionary = JournalData.KEEPSAKES[keepsake_id]
	Game.set_flag("keepsake:" + keepsake_id)
	Game.save_game()
	Sound.sfx("keepsake")
	Util.burst(get_parent(), global_position + Vector2(0, -9), [Color(1, 0.95, 0.8), Color(1, 0.6, 0.35)], 20, 40.0, 180.0, -20.0, 1.0)
	var tw := create_tween()
	tw.tween_property(_sprite, "scale", Vector2(1.5, 1.5), 0.15)
	tw.tween_property(_sprite, "modulate:a", 0.0, 0.6)
	tw.parallel().tween_property(_light, "energy", 0.0, 0.6)
	await Game.show_title_card(info["name"], info["card"], 2.2)
	await Dialogue.run("keepsake_" + keepsake_id)
	queue_free()
