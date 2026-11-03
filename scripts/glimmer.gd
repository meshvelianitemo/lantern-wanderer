extends StaticBody2D
## A run of glimmer crystal: it drinks light. Solid only while lantern light
## touches it (and for a breath after). Violet glimmer (`need` > 0) only wakes
## for a strong flame - at least `need` embers in your lantern.

const LINGER := 0.7
const CYAN := Color(0.45, 0.8, 1.0)
const VIOLET := Color(0.78, 0.5, 1.0)

var tiles := 1
var need := 0

var _lit := false
var _linger := 0.0
var _t := 0.0
var _shape: CollisionShape2D
var _sprites: Array[Sprite2D] = []
var _light: PointLight2D
var _dormant_mat: CanvasItemMaterial


func _ready() -> void:
	add_to_group("platform")
	collision_layer = 4
	collision_mask = 0
	_shape = CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(tiles * 16, 16)
	_shape.shape = rect
	_shape.position = Vector2(tiles * 8, 8)
	_shape.one_way_collision = true
	_shape.disabled = true
	add_child(_shape)
	_dormant_mat = Util.unlit_material()
	var tex: Texture2D = preload("res://assets/sprites/glimmer.png")
	for i in tiles:
		var s := Sprite2D.new()
		s.texture = tex
		s.hframes = tex.get_width() / 16
		s.centered = false
		s.position = Vector2(i * 16, 0)
		s.z_index = 1
		if need > 0:
			s.modulate = Color(1.15, 0.72, 1.3)
		add_child(s)
		_sprites.append(s)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_small.png")
	_light.color = VIOLET if need > 0 else CYAN
	_light.energy = 0.0
	_light.texture_scale = 0.45 + tiles * 0.18
	_light.position = Vector2(tiles * 8, 6)
	add_child(_light)
	_apply(false)


func _physics_process(delta: float) -> void:
	_t += delta
	var on := false
	if Game.embers >= need:
		var rect := Rect2(global_position, Vector2(tiles * 16, 16))
		for info: Array in Game.light_sources():
			var p: Vector2 = info[0]
			var closest := Vector2(clampf(p.x, rect.position.x, rect.end.x), clampf(p.y, rect.position.y, rect.end.y))
			if p.distance_to(closest) < info[1]:
				on = true
				break
	_linger = LINGER if on else _linger - delta
	var want := _linger > 0.0
	if want != _lit:
		_lit = want
		_apply(true)
	if _lit:
		for i in _sprites.size():
			var f := 1 + int(_t * 3.0 + i * 1.7) % 3
			_sprites[i].frame = mini(f, _sprites[i].hframes - 1)
	else:
		# dormant glimmer breathes faintly so you can just make it out
		var a := 0.55 + 0.25 * sin(_t * 1.8)
		for s in _sprites:
			s.self_modulate.a = a


func _apply(animate: bool) -> void:
	_shape.set_deferred("disabled", not _lit)
	for s in _sprites:
		s.frame = 1 if _lit else 0
		s.material = null if _lit else _dormant_mat
		s.self_modulate.a = 1.0
	var e := 0.7 if _lit else 0.0
	if animate:
		create_tween().tween_property(_light, "energy", e, 0.25)
		Sound.sfx("glimmer_on" if _lit else "glimmer_off", -10.0)
		if _lit and not Game.has_flag("seen_glimmer"):
			Game.set_flag("seen_glimmer")
	else:
		_light.energy = e
