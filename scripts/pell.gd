extends NPC
## Pell the moth. Flutters around the cold hearth in Old Hollow until you
## talk to it, then follows your lantern everywhere and makes remarks
## (Story.BARKS["pell"]) about what happens.

var follow_on_spawn := false
var following := false

var _home := Vector2.ZERO
var _fly_t := 0.0
var _idle_timer := 0.0
var _bark_turn := 0


func _ready() -> void:
	super()
	_home = position
	sprite.offset = Vector2.ZERO
	sprite.z_index = 7
	following = follow_on_spawn or Game.has_flag("pell_follows")
	_fly_t = randf() * TAU
	_idle_timer = randf_range(50.0, 80.0)
	Game.flag_set.connect(_on_flag)
	Game.player_hurt.connect(func() -> void: _bark_random("hit", 0.0))
	if following:
		_greet_level.call_deferred()


func can_interact() -> bool:
	return not following and super()


func _on_flag(flag: String) -> void:
	if flag == "pell_follows":
		following = true
	elif flag == "seen_glimmer":
		_bark_once("glimmer")
	elif flag == "seen_shadow":
		_bark_once("shadow")
	elif flag == "seen_name_stone":
		_bark_once("name")


## Pell never leaves - it just starts following the light.
func _leave() -> void:
	pass


func _on_ember_given(id: String) -> void:
	super(id)
	if following:
		var key := "gave_first" if Game.embers_given == 1 else "gave"
		_bark_random(key, 2.5)


func _greet_level() -> void:
	await get_tree().create_timer(2.6).timeout
	_bark_once("enter_" + Game.level_id)


func _process(delta: float) -> void:
	super(delta)
	_fly_t += delta
	var target: Vector2
	if following and Game.player:
		var p: Player = Game.player
		var anchor: Vector2 = p.lantern_global_position()
		if p.hung_on:
			_bark_once("hook")
		target = anchor + Vector2(cos(_fly_t * 1.3) * 13.0, sin(_fly_t * 2.1) * 7.0 - 9.0)
		global_position = global_position.lerp(target, 1.0 - exp(-4.0 * delta))
		_idle_timer -= delta
		if _idle_timer <= 0.0 and not Game.in_dialogue:
			_idle_timer = randf_range(70.0, 120.0)
			_bark_random("idle_dim" if Game.embers <= 1 else "idle", 0.0)
	else:
		target = _home + Vector2(sin(_fly_t * 0.9) * 12.0, -22.0 + cos(_fly_t * 1.7) * 6.0)
		position = position.lerp(target, 1.0 - exp(-3.0 * delta))


func _bark_once(key: String) -> void:
	if Game.has_flag("pell_said_" + key):
		return
	if not Story.BARKS["pell"].has(key):
		return
	Game.set_flag("pell_said_" + key)
	_bark_random(key, 0.0)


func _bark_random(key: String, delay: float) -> void:
	var lines: Array = Story.BARKS["pell"].get(key, [])
	if lines.is_empty() or not following:
		return
	# only the newest remark waits to be said; older ones are dropped
	_bark_turn += 1
	var turn := _bark_turn
	if delay > 0.0:
		await get_tree().create_timer(delay).timeout
	# Pell never talks over a conversation or a cutscene: it waits, then speaks up
	var quiet := 0.0
	while quiet < 0.8:
		await get_tree().create_timer(0.2, false).timeout
		quiet = 0.0 if _busy() else quiet + 0.2
		if turn != _bark_turn or not is_inside_tree():
			return
	Sound.sfx("bark")
	Util.bark(self, lines[randi() % lines.size()])


func _busy() -> bool:
	var p: Player = Game.player
	return Game.in_dialogue or Game.travelling or (p != null and p.frozen)
