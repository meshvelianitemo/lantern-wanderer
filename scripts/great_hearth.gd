extends Interactable
## The Hearth at the root of the mountain, and the endings it decides.
##   turn back             -> The Long Dark
##   step in, shared < 4   -> The Last Wick
##   step in, shared >= 4  -> Many Hands (everyone you warmed comes and gives it back)
##   ...and FIRST_PAGE holds -> The First Page (Vesper, the Hollow One, steps in with you)

const MANY_HANDS := 4
## All three Echoes seen, and the Hollow One warmed.
const FIRST_PAGE := "echo_lark,echo_maud,echo_vesper,gave_hollow_one"
## Who comes down, in this order, if you shared an ember with them.
const ARRIVALS := ["ash", "tallow", "wisp", "glim", "bell", "gudgeon", "orrin", "sprig", "hollow_one"]
## Feet of the hero in the Cradle, relative to the Hearth's base.
const CRADLE := Vector2(0, -20)

var _sprite: AnimatedSprite2D
var _light: PointLight2D
var _glow: PointLight2D
var _pending := ""
var _done := false
var _listening := false
var _warmth := 0.0


func _ready() -> void:
	zone_size = Vector2(70, 60)
	prompt_height = 86.0
	super()
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"cold": ["res://assets/sprites/hearth_great.png", 96, 1, false, [0]],
		"faint": ["res://assets/sprites/hearth_great.png", 96, 2, true, [0, 1]],
		"roar": ["res://assets/sprites/hearth_great.png", 96, 9, true, [2, 3, 4, 5]],
	})
	_sprite.offset = Vector2(0, -40)
	_sprite.z_index = -2
	_sprite.play("cold")
	add_child(_sprite)
	_light = PointLight2D.new()
	_light.texture = preload("res://assets/fx/light_lantern.png")
	_light.color = Color(1.0, 0.55, 0.25)
	_light.energy = 0.0
	_light.texture_scale = 1.0
	_light.position = Vector2(0, -36)
	add_child(_light)
	_glow = PointLight2D.new()
	_glow.texture = preload("res://assets/fx/light_small.png")
	_glow.color = Color(0.9, 0.25, 0.1)
	_glow.energy = 0.35
	_glow.texture_scale = 1.4
	_glow.position = Vector2(0, -30)
	add_child(_glow)
	Dialogue.event.connect(_on_event)
	player_entered.connect(func() -> void:
		if not _done:
			_sprite.play("faint"))


func can_interact() -> bool:
	return not _done


func interact() -> void:
	_listening = true
	_pending = ""
	await Dialogue.run("hearth_final")
	_listening = false
	match _pending:
		"ending_dark":
			_ending_dark()
		"ending_burn":
			_ending_burn()


func _on_event(ev: String) -> void:
	if _listening and ev.begins_with("ending_"):
		_pending = ev


func _process(delta: float) -> void:
	super(delta)
	var t := Time.get_ticks_msec() * 0.001
	_glow.energy = 0.3 + 0.15 * sin(t * 1.3) + _warmth * 0.6


func _grow() -> void:
	_warmth = minf(_warmth + 0.15, 1.0)
	var tw := create_tween()
	tw.tween_property(_light, "energy", 0.3 + _warmth * 0.6, 0.8)
	tw.parallel().tween_property(_light, "texture_scale", 1.0 + _warmth * 1.5, 0.8)


func _ending_dark() -> void:
	_done = true
	Game.set_flag("ending_dark")
	var p: Player = Game.player
	p.frozen = true
	p.facing = -1
	var tw := create_tween()
	tw.tween_property(p, "global_position:x", p.global_position.x - 120.0, 3.0)
	await Game.fade_out(2.5)
	_sprite.play("cold")
	_light.energy = 0.0
	await Dialogue.run("dark_end")


func _ending_burn() -> void:
	_done = true
	Game.set_flag("ending_light")
	var p: Player = Game.player
	p.frozen = true
	# the wanderer climbs into the Cradle
	var cradle := global_position + CRADLE
	p.facing = 1 if cradle.x > p.global_position.x else -1
	var tw := create_tween()
	tw.tween_property(p, "global_position", cradle, 1.4).set_trans(Tween.TRANS_SINE)
	await tw.finished
	p.z_index = -1
	await Util.spark_arc(get_parent(), p.lantern.global_position, global_position + Vector2(0, -36))
	_grow()
	Sound.sfx("hearth")
	if Game.embers_given >= MANY_HANDS:
		await Dialogue.run("many_begin")
		var slot := 0
		var last: Node2D = null
		for id: String in ARRIVALS:
			if Game.has_flag("gave_" + id):
				last = await _arrive(id, slot)
				slot += 1
		if Game.check(FIRST_PAGE) and last:
			await _first_page(last)
			_roar()
			await Dialogue.run("first_page_end")
			return
		_roar()
		await Dialogue.run("many_end")
	else:
		_roar()
		await get_tree().create_timer(1.5).timeout
		await Game.fade_out(2.0)
		await Dialogue.run("alone_end")


func _roar() -> void:
	_sprite.play("roar")
	Sound.sfx("hearth")
	Sound.sfx("flare")
	var tw := create_tween()
	tw.tween_property(_light, "energy", 1.6, 1.5)
	tw.parallel().tween_property(_light, "texture_scale", 4.0, 2.5)
	Util.burst(get_parent(), global_position + Vector2(0, -40), [Color(1, 0.95, 0.7), Color(1, 0.4, 0.1)], 60, 160.0, 180.0, -40.0, 1.6)
	var level := get_tree().get_first_node_in_group("level")
	if level:
		var cm: CanvasModulate = level.get_node_or_null("CanvasModulate")
		if cm == null:
			for c in level.get_children():
				if c is CanvasModulate:
					cm = c
		if cm:
			level.set_process(false)
			create_tween().tween_property(cm, "color", Color(1.0, 0.86, 0.72), 3.0)


## The Hollow One (the last to arrive) walks on into the Cradle beside you, and the
## dark burns off it: Vesper, the first wick, finishing their walk.
func _first_page(hollow: Node2D) -> void:
	var beside := global_position + CRADLE + Vector2(-18, 0)
	var tw := create_tween()
	tw.tween_property(hollow, "global_position", beside, 2.4).set_trans(Tween.TRANS_SINE)
	await tw.finished
	var unveil := func(ev: String) -> void:
		if ev != "vesper_unveil":
			return
		var vesper := AnimatedSprite2D.new()
		vesper.sprite_frames = Util.make_frames({"idle": ["res://assets/sprites/hero_idle_vesper.png", 32, 6, true]})
		vesper.offset = Vector2(0, -16)
		vesper.modulate.a = 0.0
		vesper.z_index = hollow.z_index
		get_parent().add_child(vesper)
		vesper.global_position = beside
		vesper.play("idle")
		Sound.sfx("hearth")
		Util.burst(get_parent(), beside + Vector2(0, -20), [Color(0.25, 0.15, 0.35), Color(1, 0.85, 0.5)], 40, 70.0, 180.0, -30.0, 1.6)
		var t := create_tween()
		t.tween_property(hollow, "modulate:a", 0.0, 2.0)
		t.parallel().tween_property(vesper, "modulate:a", 1.0, 2.0)
		_grow()
	Dialogue.event.connect(unveil)
	await Dialogue.run("first_page_vesper")
	Dialogue.event.disconnect(unveil)


## Someone you warmed walks down the bridge and gives your ember back.
func _arrive(id: String, slot: int) -> Node2D:
	var data: Dictionary = Story.NPCS[id]
	var s := AnimatedSprite2D.new()
	var tex: Texture2D = load(data["sprite"])
	var anims := {}
	for anim: String in data["anims"]:
		var a: Array = data["anims"][anim]
		anims[anim] = [data["sprite"], data["frame"], a[1], true, a[0]]
	s.sprite_frames = Util.make_frames(anims)
	s.offset = Vector2(0, data.get("y", -tex.get_height() / 2.0))
	s.play("idle_lit" if s.sprite_frames.has_animation("idle_lit") else "idle")
	if data.get("unlit", false):
		s.material = Util.unlit_material()
	var stand := global_position + Vector2(-70.0 - slot * 20.0, 0)
	get_parent().add_child(s)
	s.z_index = 1
	s.modulate.a = 0.0
	if id == "gudgeon":
		# he surfaces in the dark beneath the bridge
		var pool := global_position + Vector2(-264, 46)
		s.global_position = pool
		create_tween().tween_property(s, "global_position:y", pool.y - 18.0, 1.8)
	else:
		s.global_position = stand + Vector2(-120, 0)
		create_tween().tween_property(s, "global_position", stand, 2.0)
	var tw := create_tween()
	tw.tween_property(s, "modulate:a", 1.0, 1.0)
	await get_tree().create_timer(2.0).timeout
	await Dialogue.run("arrive_" + id, data.get("voice", id))
	var from := s.global_position + Vector2(0, -12)
	await Util.spark_arc(get_parent(), from, global_position + Vector2(0, -36))
	Sound.sfx("give")
	_grow()
	return s
