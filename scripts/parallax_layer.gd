extends Sprite2D
## Screen-anchored background layer that repeats horizontally and scrolls at
## `factor` times the camera speed.

@export var factor := Vector2(0.2, 0.05)
## Screen y of the texture's top edge while the camera sits at `reference_y`.
@export var screen_y := 0.0
@export var reference_y := 0.0
@export var autoscroll := 0.0
## Colour drawn below the texture so the layer never shows a gap.
@export var fill_below := Color(0, 0, 0, 0)

var _scroll := 0.0


func _ready() -> void:
	add_to_group("parallax")
	centered = false
	region_enabled = true
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	light_mask = 2


func _process(delta: float) -> void:
	var cam := get_viewport().get_camera_2d()
	if cam == null or texture == null:
		return
	var view := get_viewport_rect().size
	var center := cam.get_screen_center_position()
	_scroll += autoscroll * delta
	var top_left := center - view * 0.5
	var y := screen_y - (center.y - reference_y) * factor.y
	global_position = Vector2(top_left.x, top_left.y + y).round()
	region_rect = Rect2(roundf(center.x * factor.x + _scroll), 0, view.x, texture.get_height())


func _draw() -> void:
	if fill_below.a > 0.0 and texture:
		draw_rect(Rect2(0, texture.get_height(), 480, 400), fill_below)
