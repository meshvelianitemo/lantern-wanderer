extends Interactable
## Mossback, the ancient totem spirit. Wakes when you come close and
## talks while its lines are being typed out. What he says comes from
## Story.NPCS["mossback"].talks.

const NPC_ID := "mossback"

var _sprite: AnimatedSprite2D
var _eyes: PointLight2D
var _awake := false
var _talking := false


func _ready() -> void:
	zone_size = Vector2(76, 40)
	prompt_height = 56.0
	super()
	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = Util.make_frames({
		"sleep": ["res://assets/sprites/totem.png", 20, 1, false, [0]],
		"awake": ["res://assets/sprites/totem.png", 20, 1, false, [1]],
		"talk": ["res://assets/sprites/totem.png", 20, 9, true, [1, 2]],
	})
	_sprite.offset = Vector2(0, -22)
	_sprite.play("sleep")
	add_child(_sprite)
	_eyes = PointLight2D.new()
	_eyes.texture = preload("res://assets/fx/light_small.png")
	_eyes.color = Color(1.0, 0.75, 0.4)
	_eyes.energy = 0.0
	_eyes.texture_scale = 0.8
	_eyes.position = Vector2(0, -27)
	add_child(_eyes)
	player_entered.connect(_wake)
	Dialogue.typing_changed.connect(_on_typing_changed)


func _wake() -> void:
	if _awake:
		return
	_awake = true
	_sprite.play("awake")
	create_tween().tween_property(_eyes, "energy", 0.9, 0.6)


func interact() -> void:
	_wake()
	_talking = true
	await Dialogue.run(Story.pick(NPC_ID), NPC_ID)
	_talking = false
	_sprite.play("awake")


func _on_typing_changed(who: String, typing: bool) -> void:
	if not _talking or (who != "Mossback" and who != "???"):
		return
	_sprite.play("talk" if typing else "awake")
