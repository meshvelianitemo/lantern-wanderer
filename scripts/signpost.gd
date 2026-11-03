extends Interactable
## A readable wooden sign, or (with `stone`) a Keeper tablet carved in stone.

@export var dialogue_id := "sign_start"
@export var stone := false


func _ready() -> void:
	zone_size = Vector2(28, 26)
	prompt_height = 30.0
	super()
	var s := Sprite2D.new()
	s.texture = preload("res://assets/deco/tablet.png") if stone else preload("res://assets/deco/sign.png")
	s.offset = Vector2(0, -s.texture.get_height() / 2.0 + 1)
	add_child(s)
	if stone:
		# the carved letters hold a little old light
		var l := PointLight2D.new()
		l.texture = preload("res://assets/fx/light_small.png")
		l.color = Color(0.9, 0.85, 0.6)
		l.energy = 0.35
		l.texture_scale = 0.4
		l.position = Vector2(0, -10)
		add_child(l)


func interact() -> void:
	Game.set_flag("read:" + dialogue_id)  # for the Journal
	await Dialogue.run(dialogue_id)
