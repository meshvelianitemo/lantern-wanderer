class_name KeyPrompt
extends Node2D
## A button prompt for an input action, centred on this node: a keycap showing the
## key it is bound to, or the gamepad button while the player is using a pad.
## Redraws itself when bindings or the input device change.

const INK := Color(0.07, 0.05, 0.09)
const FONT_SIZE := 9

@export var action := "interact"

var _cap: StyleBoxTexture
var _font: Font


func _ready() -> void:
	_cap = StyleBoxTexture.new()
	_cap.texture = load("res://assets/ui/key_blank.png")
	_cap.texture_margin_left = 3
	_cap.texture_margin_right = 3
	_cap.texture_margin_top = 3
	_cap.texture_margin_bottom = 4
	_font = preload("res://assets/ui/pixel_font.fnt")
	Settings.changed.connect(queue_redraw)


func _draw() -> void:
	var glyph := Settings.pad_glyph(action)
	if glyph:
		draw_texture(glyph, -(glyph.get_size() / 2.0).floor())
		return
	var text := Settings.label(action)
	var w := maxf(11.0, ceilf(_font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SIZE).x) + 5.0)
	var rect := Rect2(-floorf(w / 2.0), -6.0, w, 12.0)
	draw_style_box(_cap, rect)
	draw_string(_font, rect.position + Vector2(3, 8), text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SIZE, INK)
