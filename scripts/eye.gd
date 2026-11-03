extends Node2D
## A Keeper eye-stone. It opens every eye-gate with the same id while light
## rests on it (see gate.gd) - usually a flame left on a nearby hook.

var gate_id := ""

var _sprite: Sprite2D
var _glow: PointLight2D
var lit := false


func _ready() -> void:
	add_to_group("eye_" + gate_id)
	_sprite = Sprite2D.new()
	var atlas := AtlasTexture.new()
	atlas.atlas = load("res://assets/sprites/eye_gate.png")
	atlas.region = Rect2(0, 0, 16, 16)
	_sprite.texture = atlas
	_sprite.offset = Vector2(0, -8)
	_sprite.z_index = -1
	add_child(_sprite)
	_glow = PointLight2D.new()
	_glow.texture = preload("res://assets/fx/light_small.png")
	_glow.color = Color(1.0, 0.85, 0.45)
	_glow.texture_scale = 0.5
	_glow.energy = 0.0
	_glow.position = Vector2(0, -7)
	add_child(_glow)


func _physics_process(_delta: float) -> void:
	var now := Game.light_at(global_position + Vector2(0, -7)) > 0.0
	if now == lit:
		return
	lit = now
	(_sprite.texture as AtlasTexture).region = Rect2(16 if lit else 0, 0, 16, 16)
	_sprite.material = Util.unlit_material() if lit else null
	create_tween().tween_property(_glow, "energy", 0.8 if lit else 0.0, 0.3)
