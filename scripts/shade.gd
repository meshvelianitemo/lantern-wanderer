extends Area2D
## A shade: cold that remembers being warm. It drifts toward you through the
## dark and thins away while lantern light touches it. A strong shade can push
## through a small flame - its touch knocks an ember out of your lantern.

const SPEED := 30.0
const CHASE_RANGE := 130.0
const LEASH := 170.0
const RESPAWN := 9.0

## Seconds of full light it can bear. Strong shades are also bolder in light.
var strength := 1.6

var _life := 0.0
var _home := Vector2.ZERO
var _vel := Vector2.ZERO
var _t := 0.0
var _gone := false
var _respawn := 0.0
var _whisper := 0.0
var _chasing := false
var _sprite: AnimatedSprite2D
var _dark: PointLight2D


func _ready() -> void:
	add_to_group("shade")
	_home = position
	_life = strength
	_t = randf() * TAU
	collision_layer = 0
	collision_mask = 2
	monitorable = false
	var big := strength > 2.5
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 9.0 if big else 5.0
	shape.shape = circle
	add_child(shape)
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"drift": ["res://assets/sprites/shade.png", 16, 6, true, [0, 1, 2, 3]],
		"recoil": ["res://assets/sprites/shade.png", 16, 8, true, [4, 5]],
	})
	_sprite.material = Util.unlit_material()
	_sprite.z_index = 6
	if big:
		_sprite.scale = Vector2(2, 2)
	_sprite.play("drift")
	add_child(_sprite)
	# shades carry a little darkness with them
	_dark = PointLight2D.new()
	_dark.texture = preload("res://assets/fx/light_small.png")
	_dark.blend_mode = Light2D.BLEND_MODE_SUB
	_dark.energy = 0.45
	_dark.texture_scale = 1.3 if big else 0.75
	add_child(_dark)
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	_t += delta
	_whisper -= delta
	if _gone:
		_respawn -= delta
		var p0 := Game.player
		if _respawn <= 0.0 and (p0 == null or p0.global_position.distance_to(_home) > 220.0):
			_reform()
		return

	var p: Player = Game.player
	var light := Game.light_at(global_position, 4.0)
	var lit := light > 0.0
	if lit:
		_life -= delta * (0.6 + 1.6 * light)
		if _life <= 0.0:
			dissolve()
			return
	else:
		_life = minf(strength, _life + delta * 0.4)

	var target: Vector2
	var chase := p != null and not p.frozen and not Game.in_dialogue \
		and global_position.distance_to(p.body_center()) < CHASE_RANGE \
		and p.global_position.distance_to(_home) < LEASH + 80.0
	if chase:
		if not _chasing and _whisper <= 0.0:
			Sound.sfx("shade_near", -8.0)
			_whisper = 5.0
		var bold := 26.0 if strength > 2.5 else 18.0
		target = (p.body_center() - global_position).normalized() * (bold if lit else SPEED)
	else:
		var hover := _home + Vector2(sin(_t * 0.6) * 14.0, cos(_t * 0.9) * 6.0)
		target = (hover - global_position) * 1.2
	_chasing = chase
	_vel = _vel.lerp(target, 1.0 - exp(-3.0 * delta))
	global_position += _vel * delta
	var off := global_position - _home
	if off.length() > LEASH:
		global_position = _home + off.limit_length(LEASH)

	_sprite.play("recoil" if lit else "drift")
	if absf(_vel.x) > 2.0:
		_sprite.flip_h = _vel.x < 0.0
	modulate.a = 0.3 + 0.7 * (_life / strength)


func _on_body_entered(body: Node) -> void:
	if _gone or not body is Player:
		return
	if (body as Player).hurt_by_shade(global_position):
		dissolve(false)


## Thins away into nothing (it will gather itself again later, out of sight).
func dissolve(sound := true) -> void:
	if _gone:
		return
	_gone = true
	_respawn = RESPAWN
	if sound:
		Sound.sfx("shade_poof", -4.0)
	Util.burst(get_parent(), global_position, [Color(0.35, 0.25, 0.5), Color(0.05, 0.03, 0.1)], 14, 30.0, 180.0, -12.0, 0.8)
	set_deferred("monitoring", false)
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.3)
	tw.tween_callback(func() -> void: visible = false)


func _reform() -> void:
	_gone = false
	_life = strength
	global_position = _home
	_vel = Vector2.ZERO
	visible = true
	monitoring = true
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 1.5)
