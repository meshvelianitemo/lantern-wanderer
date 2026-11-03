class_name BarkBubble
extends Node2D
## A small speech bubble above whoever made a remark (made by Util.bark). It rides
## along with them, but slides sideways or down when it would poke off the screen,
## so remarks at the very ends of a map are never cut off.

const MARGIN := 3.0

var panel: NinePatchRect


func _process(_delta: float) -> void:
	var owner_node := get_parent() as Node2D
	if owner_node == null or panel == null:
		return
	var inv := get_viewport().get_canvas_transform().affine_inverse()
	var view := Rect2(inv * Vector2.ZERO, Vector2.ZERO).expand(inv * get_viewport_rect().size)
	# where the bubble sits if left alone
	var rect := Rect2(owner_node.global_position + panel.position, panel.size)
	var shift := Vector2.ZERO
	if rect.position.x < view.position.x + MARGIN:
		shift.x = view.position.x + MARGIN - rect.position.x
	elif rect.end.x > view.end.x - MARGIN:
		shift.x = view.end.x - MARGIN - rect.end.x
	if rect.position.y < view.position.y + MARGIN:
		shift.y = view.position.y + MARGIN - rect.position.y
	global_position = owner_node.global_position + shift.round()
