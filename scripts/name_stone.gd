extends Area2D
## A Keeper name-stone. Every Keeper had one, carved when they were born and
## dropped down the Starwell to sit under their star. The flood scattered them
## all through the mountain. Pick one up and the name is remembered: it goes
## in the Journal, and lights a gold star when the Great Orrery turns.

## Which Keeper (a key of JournalData.NAMES).
var name_id := ""

var _sprite: AnimatedSprite2D
var _light: PointLight2D
var _t := 0.0
var _taken := false


func _ready() -> void:
	if Game.has_flag("name:" + name_id) or not JournalData.NAMES.has(name_id):
		queue_free()
		return
	collision_layer = 0
	collision_mask = 2
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	shape.shape = circle
	shape.position = Vector2(0, -7)
	add_child(shape)
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({"pulse": ["res://assets/sprites/name_stone.png", 10, 5, true]})
	_sprite.material = Util.unlit_material()
	_sprite.play("pulse")
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_small.png")
	_light.color = Color(1.0, 0.85, 0.5)
	_light.energy = 0.45
	_light.texture_scale = 0.35
	add_child(_light)
	_t = randf() * TAU
	body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	_t += delta
	var bob := Vector2(0, -6 + roundf(sin(_t * 1.7) * 1.0))
	_sprite.position = bob
	_light.position = bob


func _on_body_entered(body: Node) -> void:
	if _taken or not body is Player:
		return
	_taken = true
	var info: Array = JournalData.NAMES[name_id]
	Game.set_flag("name:" + name_id)
	Game.save_game()
	Sound.sfx("name_stone")
	Util.burst(get_parent(), global_position + Vector2(0, -6), [Color(1, 0.95, 0.75), Color(1, 0.7, 0.3)], 18, 40.0, 180.0, -20.0, 0.9)
	var tw := create_tween()
	tw.tween_property(_sprite, "scale", Vector2(1.6, 1.6), 0.15)
	tw.parallel().tween_property(_light, "energy", 1.4, 0.15)
	tw.tween_property(_sprite, "modulate:a", 0.0, 0.5)
	tw.parallel().tween_property(_light, "energy", 0.0, 0.5)
	var first := not Game.has_flag("seen_name_stone")
	Game.set_flag("seen_name_stone")
	await Game.show_title_card(info[0], info[1], 1.8)
	if first:
		await Dialogue.run("first_name_stone")
	queue_free()
