extends Area2D
## Invisible trigger, placed by the level. Modes:
##   door    - walk in to travel to `target_door` in `target_level`
##             (plays `dialogue_id` the first time, if set)
##   trigger - plays `dialogue_id` once, when `condition` holds
##   end     - the end of the road for now: plays `dialogue_id`, then steps you back
##   count   - lets you through with `need` followers behind you (plays `dialogue_id`
##             once), otherwise plays `not_yet` and steps you back (Maud's door)

var mode := "door"
var door_id := ""
var target_level := ""
var target_door := ""
var dialogue_id := ""
var condition := ""
var need := 0
var not_yet := ""
## A door you just arrived through stays quiet until you step out of it.
var armed := true

var _busy := false


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	monitorable = false
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(14, 56) if mode == "door" else Vector2(16, 72)
	shape.shape = rect
	shape.position = Vector2(0, -rect.size.y / 2.0)
	add_child(shape)
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


func _on_body_entered(body: Node) -> void:
	if not body is Player or not armed or _busy or Game.travelling or (body as Player).frozen:
		return
	match mode:
		"door":
			_busy = true
			if dialogue_id != "" and not Game.has_flag("seen_" + dialogue_id):
				Game.set_flag("seen_" + dialogue_id)
				await Dialogue.run(dialogue_id)
			Game.go_to(target_level, target_door)
		"trigger":
			if Game.has_flag("seen_" + dialogue_id) or not Game.check(condition):
				return
			Game.set_flag("seen_" + dialogue_id)
			_busy = true
			await Dialogue.run(dialogue_id)
			_busy = false
		"end":
			_busy = true
			armed = false
			var player := body as Player
			await Dialogue.run(dialogue_id)
			_step_back(player)
			_busy = false
		"count":
			if Game.has_flag("seen_" + dialogue_id):
				return
			_busy = true
			var player := body as Player
			if Game.followers.size() >= need:
				Game.set_flag("seen_" + dialogue_id)
				await Dialogue.run(dialogue_id)
			else:
				armed = false
				await Dialogue.run(not_yet)
				_step_back(player)
			_busy = false


func _step_back(player: Player) -> void:
	var back := signf(player.global_position.x - global_position.x)
	player.velocity = Vector2.ZERO
	player.global_position.x += (back if back != 0.0 else -1.0) * 22.0


func _on_body_exited(body: Node) -> void:
	if body is Player:
		armed = true
