extends Interactable
## The Little Hearth of Old Hollow. Cold until Nan Tallow gets an ember; after
## that a place to rest (checkpoint + save) that burns brighter with every
## ember you share. Lay a keepsake in it to play its memory (an Echo), and
## once three or more people live here, resting can turn into supper
## (StoryHome.SUPPERS: everyone gathers round and talks).

## Anything to lay in the fire, or remember again.
const MENU_IF := "keepsake:lantern|keepsake:bell|keepsake:page|echo_lark|echo_maud|echo_vesper"
## Who comes to supper, if they live here (Gudgeon stays in his well, Sprig is a tree).
const DINERS := ["tallow", "wisp", "glim", "ash", "bell", "orrin"]
## Seats round the fire, relative to it (the player takes the first).
const SEATS := [-24.0, 26.0, -40.0, 42.0, -56.0, 58.0, -72.0]

var lit := false
var _busy := false
var _sprite: AnimatedSprite2D
var _light: PointLight2D
var _glow: PointLight2D


func _ready() -> void:
	zone_size = Vector2(44, 34)
	prompt_height = 40.0
	super()
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"cold": ["res://assets/sprites/hearth_small.png", 32, 1, false, [0]],
		"burn": ["res://assets/sprites/hearth_small.png", 32, 9, true, [1, 2, 3, 4]],
	})
	_sprite.offset = Vector2(0, -14)
	_sprite.z_index = -1
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1.0, 0.64, 0.32)
	_light.position = Vector2(0, -16)
	add_child(_light)
	_glow = PointLight2D.new()
	_glow.texture = preload("res://assets/fx/light_small.png")
	_glow.color = Color(1.0, 0.55, 0.25)
	_glow.position = Vector2(0, -14)
	add_child(_glow)
	lit = Game.has_flag("gave_tallow") or Game.has_flag("ending_many")
	_sprite.play("burn" if lit else "cold")
	_light.energy = _target_energy() if lit else 0.0
	_light.texture_scale = _target_scale()
	Game.flag_set.connect(_on_flag)
	Game.ember_given.connect(func(_npc: String) -> void: _grow())


func _target_energy() -> float:
	return 0.9 + minf(Game.embers_given, 6) * 0.06


func _target_scale() -> float:
	return 1.0 + minf(Game.embers_given, 6) * 0.15


func _on_flag(flag: String) -> void:
	if flag != "gave_tallow" or lit:
		return
	await get_tree().create_timer(1.1).timeout
	lit = true
	_sprite.play("burn")
	Sound.sfx("hearth")
	Util.burst(get_parent(), global_position + Vector2(0, -14), [Color(1, 0.95, 0.7), Color(0.95, 0.4, 0.15)], 30, 70.0, 70.0, -30.0, 1.1)
	_grow()


func _grow() -> void:
	if not lit:
		return
	var tw := create_tween()
	tw.tween_property(_light, "energy", _target_energy(), 1.5)
	tw.parallel().tween_property(_light, "texture_scale", _target_scale(), 2.5)


func can_interact() -> bool:
	return lit and not _busy


func interact() -> void:
	_busy = true
	Game.checkpoint = Game.player.global_position
	Game.save_game()
	# (after an ending too: keepsakes found late can still be remembered. "Just rest" ends the game then.)
	await Dialogue.run("hearth_menu" if Game.check(MENU_IF) else "hearth_rest")
	if not Game.travelling:  # (or off into an Echo)
		var supper := StoryHome.next_supper()
		if supper != "":
			await _supper(supper)
	_busy = false


## Everyone who lives here gathers round the fire, and they talk.
func _supper(id: String) -> void:
	var p: Player = Game.player
	p.frozen = true
	await Game.fade_out(0.6)
	var moved: Array = []
	var seat := 1
	for npc_id: String in DINERS:
		for npc: NPC in get_tree().get_nodes_in_group("npc_" + npc_id):
			if seat >= SEATS.size():
				break
			moved.append([npc, npc.global_position, npc.sprite.flip_h])
			npc.global_position = global_position + Vector2(SEATS[seat], 0)
			npc.sprite.flip_h = SEATS[seat] > 0.0
			npc.talking = true
			seat += 1
	var home := p.global_position
	p.global_position = global_position + Vector2(SEATS[0], 0)
	p.facing = 1
	await Game.fade_in(0.8)
	Sound.sfx("supper")
	Game.set_flag("supper:" + id)
	await Dialogue.run("supper_" + id)
	await Game.fade_out(0.6)
	for m: Array in moved:
		var npc: NPC = m[0]
		npc.global_position = m[1]
		npc.sprite.flip_h = m[2]
		npc.talking = false
		npc.sprite.play(npc._anim("idle"))
	p.global_position = home
	await Game.fade_in(0.6)
	p.frozen = false


func _process(delta: float) -> void:
	super(delta)
	if lit:
		var t := Time.get_ticks_msec()
		_glow.energy = 0.7 + 0.12 * sin(t * 0.017) + 0.08 * sin(t * 0.029)
	else:
		_glow.energy = 0.0
