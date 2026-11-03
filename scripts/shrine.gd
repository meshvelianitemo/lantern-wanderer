extends Interactable
## Ember shrine: light it with your lantern to make it your respawn point.
## Lit shrines stay lit (and resting at one saves the game).

## Persistence key ("level:x:y").
var key := ""
var lit := false
var _sprite: AnimatedSprite2D
var _light: PointLight2D


func _ready() -> void:
	zone_size = Vector2(34, 30)
	prompt_height = 34.0
	super()
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"cold": ["res://assets/sprites/shrine.png", 16, 1, false, [0]],
		"burn": ["res://assets/sprites/shrine.png", 16, 8, true, [1, 2, 3, 4]],
	})
	_sprite.offset = Vector2(0, -11)
	_sprite.play("cold")
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1.0, 0.66, 0.35)
	_light.energy = 0.0
	_light.texture_scale = 0.8
	_light.position = Vector2(0, -16)
	add_child(_light)
	if Game.has_flag("lit:" + key):
		lit = true
		_sprite.play("burn")
		_light.energy = 1.0


func can_interact() -> bool:
	return not lit


func interact() -> void:
	lit = true
	_sprite.play("burn")
	Game.set_flag("lit:" + key)
	Game.checkpoint = global_position
	Game.save_game()
	Sound.sfx("shrine")
	Util.burst(get_parent(), global_position + Vector2(0, -14), [Color(1, 0.92, 0.6), Color(0.95, 0.4, 0.15)], 18, 55.0, 60.0, -20.0, 0.9)
	create_tween().tween_property(_light, "energy", 1.0, 0.8)
	if not Game.has_flag("lit_first_shrine"):
		Game.set_flag("lit_first_shrine")
		await Dialogue.run("shrine_lit")


func _process(delta: float) -> void:
	super(delta)
	if lit:
		_light.energy = 0.95 + 0.07 * sin(Time.get_ticks_msec() * 0.019) + 0.05 * sin(Time.get_ticks_msec() * 0.031)
		# walking past a lit shrine makes it your checkpoint again
		if player_inside and Game.checkpoint != global_position:
			Game.checkpoint = global_position
