class_name Interactable
extends Area2D
## Base for anything the player can walk up to and press "interact" on.
## Shows a bobbing button prompt (the bound key, or the pad button) while the player is in range.

signal player_entered
signal player_exited

@export var zone_size := Vector2(36, 32)
@export var prompt_height := 40.0

var player_inside := false
var _prompt: KeyPrompt
var _t := 0.0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	monitorable = false
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = zone_size
	shape.shape = rect
	shape.position = Vector2(0, -zone_size.y / 2.0)
	add_child(shape)
	_prompt = KeyPrompt.new()
	_prompt.material = Util.unlit_material()
	_prompt.z_index = 20
	_prompt.visible = false
	add_child(_prompt)
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


func can_interact() -> bool:
	return true


func _prompt_hide() -> void:
	_prompt.visible = false


func interact() -> void:
	pass


func _process(delta: float) -> void:
	_t += delta
	# never mid-cutscene (the player is frozen through fades, suppers and travel)
	var frozen: bool = Game.player != null and Game.player.frozen
	var show := player_inside and not Game.in_dialogue and not frozen and can_interact()
	_prompt.visible = show
	_prompt.position = Vector2(0, -prompt_height + roundf(sin(_t * 4.0) * 1.5))
	if show and Input.is_action_just_pressed("interact"):
		interact()


func _on_body_entered(body: Node) -> void:
	if body is Player:
		player_inside = true
		player_entered.emit()


func _on_body_exited(body: Node) -> void:
	if body is Player:
		player_inside = false
		player_exited.emit()
