class_name Player
extends CharacterBody2D
## The hooded lantern wanderer (or, in an Echo, whoever Game.hero_skin says:
## Lark, Maud or Vesper). Leaves a trail that followers walk along.

const RUN_SPEED := 92.0
const ACCEL := 900.0
const FRICTION := 1300.0
const AIR_ACCEL := 650.0
const GRAVITY := 820.0
const FALL_GRAVITY_MULT := 1.6
const JUMP_VELOCITY := -252.0
const MAX_FALL := 330.0
const COYOTE_TIME := 0.1
const JUMP_BUFFER := 0.12
const PLATFORM_LAYER := 3  # physics layer used by one-way platforms
## Radius (px) of the light that counts for glimmer and shades, at scale 1.
const LIGHT_RADIUS := 66.0
const FLARE_COOLDOWN := 3.0
const HURT_TIME := 1.6
const BELL_COOLDOWN := 1.1
## How far Maud's bell carries: it lights the halls and wakes sleepers this far out.
const BELL_RADIUS := 150.0
## Positions kept for followers (one per pixel or so of movement).
const TRAIL_MAX := 900

const DUST := [Color(0.85, 0.8, 0.72), Color(0.55, 0.5, 0.5)]
const SPARK := [Color(1.0, 0.9, 0.55), Color(0.95, 0.45, 0.2)]
const ANIMS := ["idle", "run", "jump", "fall", "land"]

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var lantern: PointLight2D = $Lantern
@onready var glow: PointLight2D = $LanternGlow

## Sent back to the last checkpoint (fall, water, a shade, the rising flood or dark).
signal respawned

var facing := 1
var frozen := false
var fall_limit := 100000.0
## The Keeper hook currently holding your flame (Drowned Halls), or null.
var hung_on: Node2D = null

var _coyote := 0.0
var _buffer := 0.0
var _was_on_floor := true
var _landing := 0.0
var _drop_timer := 0.0
var _t := 0.0
var _light_scale := 1.0
var _flare := 0.0
var _flare_cd := 0.0
var _hurt := 0.0
var _step := 0.0
var _last_embers := 0
## Where the player has been, newest last (followers walk this path).
var trail: PackedVector2Array = []


func _ready() -> void:
	Game.player = self
	Game.checkpoint = global_position
	add_to_group("light_source")
	sprite.sprite_frames = _make_frames(_scarf())
	trail.append(global_position)
	# every wick's scarf burns: Lark's shortens with each ember Lark gives away
	Game.ember_given.connect(func(_npc: String) -> void:
		var anim := sprite.animation
		sprite.sprite_frames = _make_frames(_scarf())
		sprite.play(anim))
	sprite.play("idle")
	_last_embers = Game.embers
	_light_scale = _scale_for(Game.embers)
	Game.embers_changed.connect(_on_embers_changed)


## How far this wick's scarf has burned (0 full, 1 singed, 2 a stub).
func _scarf() -> int:
	match Game.hero_skin:
		"":
			return Story.scarf_stage()
		"lark":
			return 0 if Game.embers_given == 0 else (1 if Game.embers_given < 3 else 2)
	return 0


func _make_frames(stage: int) -> SpriteFrames:
	var suffix := "" if stage == 0 else "_s%d" % stage
	if Game.hero_skin != "":
		suffix = "_" + Game.hero_skin + suffix
	var spec := {
		"idle": [6, true], "run": [12, true], "jump": [8, true], "fall": [8, true], "land": [14, false],
	}
	var anims := {}
	for a: String in spec:
		var path := "res://assets/sprites/hero_%s%s.png" % [a, suffix]
		if not ResourceLoader.exists(path) and Game.hero_skin != "":
			path = "res://assets/sprites/hero_%s_%s.png" % [a, Game.hero_skin]
		if not ResourceLoader.exists(path):
			path = "res://assets/sprites/hero_%s.png" % a
		anims[a] = [path, 32, spec[a][0], spec[a][1]]
	return Util.make_frames(anims)


func _physics_process(delta: float) -> void:
	var controllable := not Game.in_dialogue and not frozen
	var input_x := Input.get_axis("move_left", "move_right") if controllable else 0.0
	var on_floor := is_on_floor()

	if on_floor:
		_coyote = COYOTE_TIME
	else:
		_coyote -= delta
		var g := GRAVITY
		if velocity.y > 0.0 or not Input.is_action_pressed("jump"):
			g *= FALL_GRAVITY_MULT
		velocity.y = minf(velocity.y + g * delta, MAX_FALL)

	_buffer -= delta
	if controllable and Input.is_action_just_pressed("jump"):
		if Input.is_action_pressed("move_down") and on_floor and _on_platform():
			_drop_timer = 0.22
			set_collision_mask_value(PLATFORM_LAYER, false)
		else:
			_buffer = JUMP_BUFFER
	if _buffer > 0.0 and _coyote > 0.0:
		velocity.y = JUMP_VELOCITY
		_buffer = 0.0
		_coyote = 0.0
		Sound.sfx("jump", -6.0)
		Util.burst(get_parent(), global_position, DUST, 6, 22.0, 70.0, 20.0, 0.35)

	if _drop_timer > 0.0:
		_drop_timer -= delta
		if _drop_timer <= 0.0:
			set_collision_mask_value(PLATFORM_LAYER, true)

	if controllable and Input.is_action_just_pressed("flare"):
		if Game.ability == "bell":
			ring()
		else:
			flare()
	_flare_cd -= delta

	var accel := ACCEL if on_floor else AIR_ACCEL
	if is_zero_approx(input_x) and on_floor:
		accel = FRICTION
	velocity.x = move_toward(velocity.x, input_x * RUN_SPEED * Game.speed_mult, accel * delta)
	if not is_zero_approx(input_x):
		facing = 1 if input_x > 0.0 else -1

	var fall_speed := velocity.y
	move_and_slide()

	if is_on_floor() and not _was_on_floor and fall_speed > 140.0:
		_landing = 0.14
		sprite.play("land")
		Sound.sfx("land", -8.0)
		Util.burst(get_parent(), global_position, DUST, 8, 30.0, 80.0, 30.0, 0.4)
	_was_on_floor = is_on_floor()
	if is_on_floor() and absf(velocity.x) > 40.0:
		_step -= delta
		if _step <= 0.0:
			_step = 0.3
			Sound.sfx("step", -16.0)

	if global_position.y > fall_limit and not frozen:
		respawn()

	if trail[-1].distance_squared_to(global_position) >= 1.0:
		trail.append(global_position)
		if trail.size() > TRAIL_MAX:
			trail = trail.slice(trail.size() - TRAIL_MAX)

	_animate(delta)


func _on_platform() -> bool:
	for i in get_slide_collision_count():
		var col := get_slide_collision(i)
		var body := col.get_collider()
		if body is Node and (body as Node).is_in_group("platform"):
			return true
		if body is TileMapLayer:
			var layer := body as TileMapLayer
			var cell := layer.local_to_map(layer.to_local(col.get_position() + Vector2(0, 2)))
			var data := layer.get_cell_tile_data(cell)
			if data and data.get_collision_polygons_count(1) > 0:
				return true
	return false


func _animate(delta: float) -> void:
	_t += delta
	sprite.flip_h = facing < 0
	if _landing > 0.0:
		_landing -= delta
	elif not is_on_floor():
		sprite.play("jump" if velocity.y < -20.0 else "fall")
	elif absf(velocity.x) > 8.0:
		sprite.play("run")
	else:
		sprite.play("idle")

	if _hurt > 0.0:
		_hurt -= delta
		sprite.visible = fmod(_hurt, 0.16) > 0.07 or _hurt <= 0.0

	# lantern sway + flicker
	var sway := sin(_t * 3.1) * 0.6
	lantern.position = Vector2(9 * facing + sway, -6)
	glow.position = lantern.position
	var flicker := 0.06 * sin(_t * 23.0) + 0.04 * sin(_t * 41.0 + 1.7) + 0.03 * sin(_t * 7.3)
	var dim := 0.25 if hung_on else 1.0
	lantern.energy = (0.72 + flicker) * dim + _flare * 0.6
	lantern.texture_scale = (_light_scale * Game.lantern_scale * (0.35 if hung_on else 1.0)) \
		* (1.0 + flicker * 0.15) * (1.0 + _flare * 1.2)
	glow.energy = (0.4 + flicker * 1.5) * minf(Game.lantern_scale * 1.5, 1.0) + _flare


# --- light ------------------------------------------------------------------

static func _scale_for(count: int) -> float:
	return minf(1.0 + count * 0.12, 1.9)


## The radius your full flame reaches (also used by a hook holding it).
func flame_radius() -> float:
	return LIGHT_RADIUS * _light_scale * Game.lantern_scale


func light_info() -> Array:
	var r := flame_radius() * (1.0 + _flare * 1.2)
	if hung_on:
		r = 0.0
	return [lantern.global_position, r]


## Where your flame is: in your lantern, or on the hook holding it.
func lantern_global_position() -> Vector2:
	if hung_on:
		return hung_on.global_position + hung_on.LAMP
	return lantern.global_position


func body_center() -> Vector2:
	return global_position + Vector2(0, -8)


func flare() -> void:
	if not Game.has_gift("flare") or _flare_cd > 0.0 or hung_on:
		return
	_flare_cd = FLARE_COOLDOWN
	Sound.sfx("flare")
	Util.burst(get_parent(), lantern.global_position, SPARK, 30, 120.0, 180.0, 0.0, 0.6)
	var tw := create_tween()
	tw.tween_property(self, "_flare", 1.0, 0.08)
	tw.tween_property(self, "_flare", 0.0, 0.7).set_trans(Tween.TRANS_SINE)
	var reach := flame_radius() * 1.6
	for t in get_tree().get_nodes_in_group("thorn"):
		if (t as Node2D).global_position.distance_to(lantern.global_position) < reach * 0.75:
			t.burn()
	for s in get_tree().get_nodes_in_group("shade"):
		if (s as Node2D).global_position.distance_to(lantern.global_position) < reach:
			s.dissolve()
	Game.set_flag("used_flare")


## Maud's handbell (the Flare key in her Echo): a ring of sound that lights the halls
## for a moment and wakes anyone asleep within BELL_RADIUS.
func ring() -> void:
	if _flare_cd > 0.0:
		return
	_flare_cd = BELL_COOLDOWN
	Sound.sfx("bell_ring")
	var from := lantern.global_position
	var pulse := Node2D.new()
	pulse.z_index = 30
	get_parent().add_child(pulse)
	pulse.global_position = from
	var ring_tex: Texture2D = load("res://assets/fx/ring.png") if ResourceLoader.exists("res://assets/fx/ring.png") else null
	if ring_tex:
		var wave := Sprite2D.new()
		wave.texture = ring_tex
		wave.material = Util.unlit_material()
		wave.modulate = Color(1.0, 0.92, 0.7, 0.8)
		wave.scale = Vector2.ONE * 0.1
		pulse.add_child(wave)
		var target := BELL_RADIUS * 2.0 / ring_tex.get_width()
		var tw := pulse.create_tween()
		tw.tween_property(wave, "scale", Vector2.ONE * target, 0.7).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
		tw.parallel().tween_property(wave, "modulate:a", 0.0, 0.8)
	# the sound lights the halls for a breath
	var flash := PointLight2D.new()
	flash.texture = preload("res://assets/fx/light_lantern.png")
	flash.color = Color(0.85, 0.85, 1.0)
	flash.energy = 0.0
	flash.texture_scale = 0.4
	pulse.add_child(flash)
	var lt := pulse.create_tween()
	lt.tween_property(flash, "energy", 0.9, 0.12)
	lt.parallel().tween_property(flash, "texture_scale", BELL_RADIUS / LIGHT_RADIUS * 1.3, 0.5).set_ease(Tween.EASE_OUT)
	lt.tween_property(flash, "energy", 0.0, 1.3).set_trans(Tween.TRANS_SINE)
	lt.tween_callback(pulse.queue_free)
	Game.bell_rung.emit(from, BELL_RADIUS)


## Followers stop where they are and pick the trail up again from here.
func reset_trail() -> void:
	trail = PackedVector2Array([global_position])


func _on_embers_changed(count: int) -> void:
	var tw := create_tween()
	tw.tween_property(self, "_light_scale", _scale_for(count), 0.8).set_trans(Tween.TRANS_SINE)
	if count > _last_embers:
		Util.burst(get_parent(), lantern.global_position, SPARK, 14, 45.0, 180.0, -10.0, 0.7)
	_last_embers = count


# --- harm -------------------------------------------------------------------

## A shade touched you. Returns true if it took something.
func hurt_by_shade(from: Vector2) -> bool:
	if _hurt > 0.0 or frozen or Game.in_dialogue:
		return false
	Sound.sfx("shade_hit")
	Game.player_hurt.emit()
	if hung_on:
		hung_on.take_back()
	if Game.embers <= 0:
		respawn()
		return true
	Game.lose_ember()
	_hurt = HURT_TIME
	var away := signf(global_position.x - from.x)
	velocity = Vector2(away * 140.0, -150.0)
	var loose: Node2D = preload("res://scripts/ember.gd").new()
	loose.loose = true
	loose.position = global_position + Vector2(0, -8)
	loose.drift = Vector2(-away * 26.0, -22.0)
	# deferred: a shade's touch arrives mid-physics, when new areas can't be added
	get_parent().add_child.call_deferred(loose)
	Sound.sfx("ember_lost")
	return true


func drown() -> void:
	if frozen:
		return
	Sound.sfx("splash")
	Util.burst(get_parent(), global_position, [Color(0.75, 0.9, 0.95), Color(0.2, 0.35, 0.45)], 14, 60.0, 60.0, 120.0, 0.6)
	respawn()


func respawn() -> void:
	frozen = true
	velocity = Vector2.ZERO
	await Game.fade_out(0.35)
	global_position = Game.checkpoint
	velocity = Vector2.ZERO
	reset_trail()
	respawned.emit()
	if hung_on:
		hung_on.take_back()
	await get_tree().create_timer(0.15).timeout
	frozen = false
	Sound.sfx("respawn", -6.0)
	await Game.fade_in(0.5)
