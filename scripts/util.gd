class_name Util
## Small shared helpers.

## Menu input: the game's own actions, plus Godot's built-in ui_* ones (arrow keys,
## Enter, pad), so menus keep working whatever the player rebinds.
const MENU := {
	"up": ["move_up", "ui_up"], "down": ["move_down", "ui_down"],
	"left": ["move_left", "ui_left"], "right": ["move_right", "ui_right"],
	"accept": ["interact", "jump", "ui_accept"], "back": ["pause"],
}


## True on the frame a menu direction or button ("up", "accept", "back"...) is pressed.
## Check directions before "accept": W and Up are also Jump.
static func menu(what: String) -> bool:
	for action: String in MENU[what]:
		if Input.is_action_just_pressed(action):
			return true
	return false


## Builds SpriteFrames from horizontal sprite-sheet strips.
## anims: { name: [texture_path, frame_width, fps, loop] }
static func make_frames(anims: Dictionary) -> SpriteFrames:
	var frames := SpriteFrames.new()
	for anim_name: String in anims:
		var spec: Array = anims[anim_name]
		var tex: Texture2D = load(spec[0])
		var fw: int = spec[1]
		if not frames.has_animation(anim_name):
			frames.add_animation(anim_name)
		frames.set_animation_speed(anim_name, spec[2])
		frames.set_animation_loop(anim_name, spec[3])
		var picks: Array = spec[4] if spec.size() > 4 else range(tex.get_width() / fw)
		for i: int in picks:
			var atlas := AtlasTexture.new()
			atlas.atlas = tex
			atlas.region = Rect2(i * fw, 0, fw, tex.get_height())
			frames.add_frame(anim_name, atlas)
	if frames.has_animation("default") and not anims.has("default"):
		frames.remove_animation("default")
	return frames


## One-shot burst of square pixel particles (dust, sparks).
static func burst(parent: Node, pos: Vector2, colors: Array, amount := 8,
		speed := 30.0, spread := 180.0, gravity := 60.0, life := 0.45, direction := Vector2.UP) -> void:
	var p := CPUParticles2D.new()
	p.one_shot = true
	p.emitting = false
	p.amount = amount
	p.lifetime = life
	p.explosiveness = 0.95
	p.direction = direction
	p.spread = spread
	p.initial_velocity_min = speed * 0.5
	p.initial_velocity_max = speed
	p.gravity = Vector2(0, gravity)
	p.scale_amount_min = 1.0
	p.scale_amount_max = 2.0
	var grad := Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 1.0])
	grad.colors = PackedColorArray([colors[0], Color(colors[-1], 0.0)])
	p.color_ramp = grad
	p.z_index = 5
	p.position = pos
	parent.add_child(p)
	p.emitting = true
	p.finished.connect(p.queue_free)


## Additive, unlit material so things glow even in darkness.
static func glow_material() -> CanvasItemMaterial:
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	return m


static func unlit_material() -> CanvasItemMaterial:
	var m := CanvasItemMaterial.new()
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	return m


## A small speech bubble above `parent` that fades away on its own
## (and stays on screen, see BarkBubble).
static func bark(parent: Node2D, text: String, height := 12.0, life := 3.4) -> void:
	for c in parent.get_children():
		if c.has_meta("bark"):
			c.queue_free()
	var root := BarkBubble.new()
	root.set_meta("bark", true)
	root.z_index = 40
	root.z_as_relative = false
	var label := Label.new()
	label.text = text
	label.add_theme_color_override("font_color", Color(0.96, 0.93, 0.86))
	label.material = unlit_material()
	var size := label.get_minimum_size()
	var panel := NinePatchRect.new()
	panel.texture = preload("res://assets/ui/nameplate.png")
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		panel.set_patch_margin(side, 4)
	panel.size = (size + Vector2(10, 3)).round()
	panel.position = Vector2(-panel.size.x / 2.0, -height - panel.size.y).round()
	panel.material = unlit_material()
	label.position = panel.position + Vector2(5, 1)
	root.add_child(panel)
	root.add_child(label)
	root.panel = panel
	parent.add_child(root)
	root.modulate.a = 0.0
	var tw := root.create_tween()
	tw.tween_property(root, "modulate:a", 1.0, 0.2)
	tw.tween_interval(life)
	tw.tween_property(root, "modulate:a", 0.0, 0.5)
	tw.tween_callback(root.queue_free)


## An ember that flies from `from` to `to` in a little arc, then bursts.
## `await` it to wait until it lands.
static func spark_arc(parent: Node, from: Vector2, to: Vector2, time := 0.9) -> void:
	var mid := (from + to) / 2.0 + Vector2(0, -36)
	var spark := Sprite2D.new()
	var atlas := AtlasTexture.new()
	atlas.atlas = preload("res://assets/sprites/ember.png")
	atlas.region = Rect2(0, 0, 11, 11)
	spark.texture = atlas
	spark.material = unlit_material()
	spark.z_index = 10
	var glow := PointLight2D.new()
	glow.texture = preload("res://assets/fx/light_small.png")
	glow.color = Color(1.0, 0.6, 0.25)
	spark.add_child(glow)
	parent.add_child(spark)
	spark.global_position = from
	var tw := spark.create_tween()
	tw.tween_method(func(t: float) -> void:
		spark.global_position = from.lerp(mid, t).lerp(mid.lerp(to, t), t), 0.0, 1.0, time).set_trans(Tween.TRANS_SINE)
	await tw.finished
	burst(parent, to, [Color(1, 0.95, 0.7), Color(1, 0.45, 0.15)], 22, 60.0, 180.0, -10.0, 0.9)
	spark.queue_free()
