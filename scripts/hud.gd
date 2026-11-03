extends CanvasLayer
## Ember counter in the top-left corner.

var _icon: TextureRect
var _label: Label


func _ready() -> void:
	layer = 10
	visible = Game.started
	var box := Control.new()
	box.position = Vector2(8, 7)
	add_child(box)
	_icon = TextureRect.new()
	var atlas := AtlasTexture.new()
	atlas.atlas = preload("res://assets/sprites/ember.png")
	atlas.region = Rect2(0, 0, 11, 11)
	_icon.texture = atlas
	_icon.pivot_offset = Vector2(5.5, 5.5)
	box.add_child(_icon)
	_label = Label.new()
	_label.position = Vector2(14, 1)
	_label.add_theme_color_override("font_color", Color(1.0, 0.91, 0.64))
	box.add_child(_label)
	Game.embers_changed.connect(_on_embers)
	_on_embers(Game.embers)


func _process(_delta: float) -> void:
	visible = Game.started and Game.show_embers


func _on_embers(count: int) -> void:
	_label.text = "x %d" % count
	if count > 0:
		_icon.scale = Vector2(1.6, 1.6)
		create_tween().tween_property(_icon, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK)
