extends Node2D
## A Keeper shadow-play plate (the Starwell). The Keepers taught their children
## the constellations with tin cut-outs held up before a lamp. The dome down
## here is dusk-glass: where a STILL light (a flame left on a hook, a lit
## star-lamp, an orrery sun) throws a plate's shadow, the shadow sets hard
## enough to stand on. It is twice the plate's size, scaled out from the light,
## so moving the light moves the shadow the other way.
## Your own lantern trembles, so its shadow only trembles too: it holds nothing.

const GROW := 2.0
const SHADOW_COLOR := Color(0.03, 0.02, 0.08, 0.9)
const PREVIEW_ALPHA := 0.32
const RIM_COLOR := Color(0.74, 0.66, 1.0, 0.95)
const ROD_COLOR := Color(0.36, 0.3, 0.22)

## Which plate: boat, fish, bird or moon (assets/sprites/caster_<shape>.png).
var shape := "boat"
## Length of the hanging rod above the plate (0 = none).
var rod := 0.0

var _tex: Texture2D
var _size: Vector2
## still-light instance id -> {body, sprite, rim}
var _shadows := {}
var _preview: Sprite2D
var _t := 0.0


func _ready() -> void:
	var path := "res://assets/sprites/caster_%s.png" % shape
	if not ResourceLoader.exists(path):
		push_warning("Missing caster: " + path)
		path = "res://assets/sprites/caster_boat.png"
	_tex = load(path)
	_size = _tex.get_size()
	if rod > 0.0:
		var line := Line2D.new()
		line.points = PackedVector2Array([Vector2(0, -_size.y / 2.0 - rod), Vector2(0, -_size.y / 2.0)])
		line.width = 1.0
		line.default_color = ROD_COLOR
		line.z_index = -4
		add_child(line)
	var plate := Sprite2D.new()
	plate.texture = _tex
	plate.z_index = -3
	add_child(plate)
	_preview = Sprite2D.new()
	_preview.texture = _tex
	_preview.centered = false
	_preview.scale = Vector2(GROW, GROW)
	_preview.modulate = Color(SHADOW_COLOR, 0.0)
	_preview.z_index = -7
	_preview.top_level = true
	add_child(_preview)


func _rect() -> Rect2:
	return Rect2(global_position - _size / 2.0, _size)


## Top-left corner of the shadow thrown from a light at `light`.
func _project(light: Vector2) -> Vector2:
	return light + (_rect().position - light) * GROW


func _physics_process(delta: float) -> void:
	_t += delta
	var centre := global_position
	var seen := {}
	for n in get_tree().get_nodes_in_group("still_light"):
		var info: Array = n.light_info()
		var r: float = info[1]
		var from: Vector2 = info[0]
		if r <= 0.0 or from.distance_to(centre) > r:
			continue
		var id := n.get_instance_id()
		seen[id] = true
		if not _shadows.has(id):
			_shadows[id] = _make_shadow()
			Sound.sfx_at("shadow_on", _project(from) + _size, -4.0)
			if not Game.has_flag("seen_shadow"):
				Game.set_flag("seen_shadow")
		var s: Dictionary = _shadows[id]
		(s["body"] as AnimatableBody2D).global_position = _project(from).round()
	for id: int in _shadows.keys():
		if not seen.has(id):
			_drop(_shadows[id])
			_shadows.erase(id)
	_update_preview()


## Your own lantern's shadow: a faint, shivering hint of where it would fall.
func _update_preview() -> void:
	var p: Player = Game.player
	var want := 0.0
	if p and not p.hung_on:
		var from: Vector2 = p.lantern.global_position
		var d := from.distance_to(global_position)
		var r := p.flame_radius()
		if d < r:
			want = PREVIEW_ALPHA * clampf((r - d) / 24.0, 0.0, 1.0)
			var shiver := Vector2(sin(_t * 31.0), cos(_t * 23.0)).round()
			_preview.global_position = _project(from).round() + shiver
	_preview.modulate.a = move_toward(_preview.modulate.a, want, get_physics_process_delta_time() * 2.0)


func _make_shadow() -> Dictionary:
	var w := _size.x * GROW
	var body := AnimatableBody2D.new()
	body.sync_to_physics = true
	body.collision_layer = 4
	body.collision_mask = 0
	body.add_to_group("platform")
	body.top_level = true
	var shape_node := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(w - 4.0, 8.0)
	shape_node.shape = rect
	shape_node.position = Vector2(w / 2.0, 4.0)
	shape_node.one_way_collision = true
	body.add_child(shape_node)
	var sprite := Sprite2D.new()
	sprite.texture = _tex
	sprite.centered = false
	sprite.scale = Vector2(GROW, GROW)
	sprite.modulate = Color(SHADOW_COLOR, 0.0)
	sprite.z_index = -7
	body.add_child(sprite)
	# the edge where the dusk-glass has set glows faintly, so you can find it in the dark
	var rim := Line2D.new()
	rim.points = PackedVector2Array([Vector2(1, 0.5), Vector2(w - 1.0, 0.5)])
	rim.width = 1.0
	rim.default_color = Color(RIM_COLOR, 0.0)
	rim.material = Util.unlit_material()
	rim.z_index = -6
	body.add_child(rim)
	add_child(body)
	var tw := body.create_tween()
	tw.tween_property(sprite, "modulate:a", SHADOW_COLOR.a, 0.25)
	tw.parallel().tween_property(rim, "default_color:a", RIM_COLOR.a, 0.4)
	return {"body": body, "sprite": sprite, "rim": rim}


func _drop(s: Dictionary) -> void:
	var body: AnimatableBody2D = s["body"]
	for c in body.get_children():
		if c is CollisionShape2D:
			(c as CollisionShape2D).set_deferred("disabled", true)
	Sound.sfx_at("shadow_off", body.global_position, -8.0)
	var tw := body.create_tween()
	tw.tween_property(s["sprite"], "modulate:a", 0.0, 0.3)
	tw.parallel().tween_property(s["rim"], "default_color:a", 0.0, 0.3)
	tw.tween_callback(body.queue_free)
