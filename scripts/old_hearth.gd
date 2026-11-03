extends Node2D
## The Hearth as it was before the first cold, in Vesper's Echo: roaring and huge.
## gutter() is the moment Vesper turns back: it sinks to embers and goes out.

var _sprite: AnimatedSprite2D
var _light: PointLight2D


func _ready() -> void:
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"roar": ["res://assets/sprites/hearth_great.png", 96, 9, true, [2, 3, 4, 5]],
		"faint": ["res://assets/sprites/hearth_great.png", 96, 2, true, [0, 1]],
		"cold": ["res://assets/sprites/hearth_great.png", 96, 1, false, [0]],
	})
	_sprite.offset = Vector2(0, -40)
	_sprite.z_index = -2
	_sprite.material = Util.unlit_material()
	_sprite.play("roar")
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1.0, 0.6, 0.28)
	_light.energy = 1.4
	_light.texture_scale = 3.6
	_light.position = Vector2(0, -36)
	add_child(_light)


func _process(_delta: float) -> void:
	if _sprite.animation == "roar":
		var t := Time.get_ticks_msec() * 0.001
		_light.energy = 1.3 + 0.12 * sin(t * 7.0) + 0.08 * sin(t * 13.0)


func gutter() -> void:
	_sprite.play("faint")
	Sound.sfx("dark_rise")
	var tw := create_tween()
	tw.tween_property(_light, "energy", 0.35, 2.5).set_trans(Tween.TRANS_SINE)
	tw.parallel().tween_property(_light, "texture_scale", 1.2, 3.0)
	tw.tween_callback(func() -> void: _sprite.play("cold"))
	tw.tween_property(_light, "energy", 0.0, 2.0)
