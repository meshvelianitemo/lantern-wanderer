extends Interactable
## The Great Orrery, at the top of the Starwell. Light it and the dusk-glass
## dome fills with stars, the way the Keepers' sky looked before the water
## came - with a gold star for every Keeper whose name-stone you have found.

## Roughly one star for every this many tiles of dome wall.
const STAR_EVERY := 11
const MAX_STARS := 260
const SUN := Vector2(0, -52)

var lit := false

var _sprite: AnimatedSprite2D
var _light: PointLight2D
var _glow: PointLight2D
## [sprite, phase, speed, base alpha, distance from here]
var _stars: Array = []
## name id -> sprite
var _named := {}
var _cells: Array[Vector2i] = []
var _reveal := 1e9
var _clock := 0.0


func _ready() -> void:
	zone_size = Vector2(80, 60)
	prompt_height = 104.0
	super()
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"cold": ["res://assets/sprites/great_orrery.png", 112, 1, false, [0]],
		"turn": ["res://assets/sprites/great_orrery.png", 112, 4, true, [1, 2, 3, 4]],
	})
	_sprite.offset = Vector2(0, -48)
	_sprite.z_index = -2
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1.0, 0.86, 0.6)
	_light.texture_scale = 2.2
	_light.position = SUN
	add_child(_light)
	_glow = PointLight2D.new()
	_glow.texture = preload("res://assets/fx/light_small.png")
	_glow.color = Color(1.0, 0.75, 0.4)
	_glow.texture_scale = 0.7
	_glow.position = SUN
	add_child(_glow)
	lit = Game.has_flag("orrery_lit")
	_sprite.play("turn" if lit else "cold")
	_light.energy = 0.9 if lit else 0.0
	Dialogue.event.connect(_on_event)
	if lit:
		_build_stars.call_deferred()


func can_interact() -> bool:
	return not lit


func interact() -> void:
	if lit:
		return
	lit = true
	var p: Player = Game.player
	if p:
		p.frozen = true
		if p.hung_on:
			p.hung_on.take_back()
	Sound.sfx("orrery_start")
	_sprite.play("turn")
	create_tween().tween_property(_light, "energy", 0.9, 1.5)
	await get_tree().create_timer(1.4).timeout
	Game.set_flag("orrery_lit")
	Game.save_game()
	Sound.sfx("stars")
	_reveal = 0.0
	_build_stars()
	create_tween().tween_property(self, "_reveal", 2600.0, 7.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	await get_tree().create_timer(3.0).timeout
	await Dialogue.run("orrery_lit")
	await _visit_orrin()
	if p:
		p.frozen = false


## Down the well to Orrin, who has waited a very long time to see this.
func _visit_orrin() -> void:
	var level := get_tree().get_first_node_in_group("level")
	var orrin := get_tree().get_first_node_in_group("npc_orrin")
	if level == null or orrin == null or not level.spots.has("orrin"):
		return
	var p: Player = Game.player
	await Game.fade_out(0.8)
	p.global_position = level.spots["orrin"]
	p.velocity = Vector2.ZERO
	p.facing = 1 if orrin.global_position.x > p.global_position.x else -1
	Game.checkpoint = p.global_position
	var cam := get_viewport().get_camera_2d()
	if cam and cam.has_method("snap_to_target"):
		cam.snap_to_target()
	await get_tree().create_timer(0.5).timeout
	await Game.fade_in(1.4)
	await orrin.interact()


func _on_event(ev: String) -> void:
	if ev == "stars_named" and lit:
		_add_named_stars(true)


func _process(delta: float) -> void:
	super(delta)
	_clock += delta
	if lit:
		_glow.energy = 0.7 + 0.1 * sin(_clock * 2.3)
	for s: Array in _stars:
		var sprite: Sprite2D = s[0]
		var shown := clampf((_reveal - float(s[4])) / 60.0, 0.0, 1.0)
		sprite.modulate.a = shown * (float(s[3]) + 0.25 * sin(_clock * float(s[2]) + float(s[1])))


# --- the sky ----------------------------------------------------------------

func _dome_cells() -> Array[Vector2i]:
	if not _cells.is_empty():
		return _cells
	var level := get_tree().get_first_node_in_group("level")
	if level == null:
		return _cells
	for y in level.height:
		for x in level.width:
			if level.ch(x, y) != "#" and level.is_wall(x, y):
				_cells.append(Vector2i(x, y))
	return _cells


func _build_stars() -> void:
	if not _stars.is_empty():
		return
	var cells := _dome_cells()
	if cells.is_empty():
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = 1977
	var count := mini(cells.size() / STAR_EVERY, MAX_STARS)
	var tex: Texture2D = load("res://assets/fx/star.png")
	var mat := Util.glow_material()
	for i in count:
		var c: Vector2i = cells[rng.randi() % cells.size()]
		var s := Sprite2D.new()
		s.texture = tex
		s.hframes = 3
		var r := rng.randf()
		s.frame = 0 if r < 0.62 else (1 if r < 0.92 else 2)
		s.material = mat
		s.z_index = -6
		s.top_level = true
		s.modulate = Color(0.75, 0.85, 1.0, 0.0) if rng.randf() < 0.7 else Color(1.0, 0.95, 0.8, 0.0)
		add_child(s)
		s.global_position = Vector2(c.x * 16 + rng.randi_range(2, 14), c.y * 16 + rng.randi_range(2, 14))
		_stars.append([s, rng.randf() * TAU, rng.randf_range(0.6, 2.4), rng.randf_range(0.45, 0.75),
			s.global_position.distance_to(global_position + SUN)])
	_add_named_stars(false)


## A gold star for every Keeper name you have found, always in the same place.
func _add_named_stars(sparkle: bool) -> void:
	var cells := _dome_cells()
	if cells.is_empty():
		return
	var tex: Texture2D = load("res://assets/fx/star.png")
	for id: String in JournalData.NAMES:
		if _named.has(id) or not Game.has_flag("name:" + id):
			continue
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(id)
		var c: Vector2i = cells[rng.randi() % cells.size()]
		var s := Sprite2D.new()
		s.texture = tex
		s.hframes = 3
		s.frame = 2
		s.scale = Vector2(2, 2)
		s.material = Util.glow_material()
		s.z_index = -6
		s.top_level = true
		s.modulate = Color(1.0, 0.85, 0.45, 0.0)
		add_child(s)
		s.global_position = Vector2(c.x * 16 + 8, c.y * 16 + 8)
		var l := PointLight2D.new()
		l.texture = preload("res://assets/fx/light_small.png")
		l.color = Color(1.0, 0.85, 0.5)
		l.energy = 0.5
		l.texture_scale = 0.4
		s.add_child(l)
		_named[id] = s
		_stars.append([s, rng.randf() * TAU, 1.3, 0.85, s.global_position.distance_to(global_position + SUN)])
		if sparkle:
			Util.burst(get_parent(), s.global_position, [Color(1, 0.95, 0.7), Color(1, 0.7, 0.3)], 12, 30.0, 180.0, 0.0, 0.8)
